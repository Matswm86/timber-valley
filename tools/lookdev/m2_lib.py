"""Shared bootstrap for build_leftover.py and build_m2.py (exec'd, not imported).

Pulls in every helper from build_m1.py (which pulls in build_v3.py): primitives (rbox, cyl, blob, tube, M, ...),
the bake (albedo x height gradient x AO with a ground plane) and finish_material. Adds:
  - Cycles on the GPU (OptiX, then CUDA) when LOOKDEV_GPU=1 (default); falls back to CPU and says so
  - prism(): a profile extruded along Y with flat ends, for parts the game stretches along their length
  - staged builds: a builder may return {"stage1": [objs], "stage2": [...]} -> ONE bake (shared texture),
    exported as one GLB with one child node per stage (for BuildSite stages)
  - emissive builds (no bake): opt emissive=(r, g, b, energy)
"""
import bpy, bmesh, sys, os, math, json, random
from mathutils import Vector, Matrix, noise

_here = os.path.dirname(os.path.abspath(__file__))
_src_m1 = open(os.path.join(_here, "build_m1.py")).read().rsplit("\nmain_m1()", 1)[0]
exec(compile(_src_m1, "build_m1.py", "exec"), globals())

GPU_STATE = {"device": None}
_reset_v3 = reset


def reset():  # noqa: F811  (GPU on top of the v3 reset)
    sc = _reset_v3()
    if os.environ.get("LOOKDEV_GPU", "1") != "1":
        GPU_STATE["device"] = "CPU (LOOKDEV_GPU=0)"
        return sc
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for kind in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = kind
            except TypeError:
                continue
            prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type == kind]
            if gpus:
                for d in prefs.devices:
                    d.use = d.type == kind
                sc.cycles.device = "GPU"
                GPU_STATE["device"] = f"{kind}: {gpus[0].name}"
                return sc
    except Exception as e:  # noqa: BLE001
        print("GPU setup failed, CPU bake:", e)
    GPU_STATE["device"] = "CPU (no GPU found)"
    sc.cycles.device = "CPU"
    return sc


# ------------------------------------------------------------------ extra primitives

def prism(profile, y0, y1, mat, smooth=False):
    """Closed 2D profile [(x, z), ...] (CCW seen from -Y) extruded from y0 to y1. Flat ends: safe to stretch along Y."""
    bm = bmesh.new()
    a = [bm.verts.new((x, y0, z)) for x, z in profile]
    b = [bm.verts.new((x, y1, z)) for x, z in profile]
    n = len(profile)
    for i in range(n):
        bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(list(reversed(a)))
    bm.faces.new(b)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("prism"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("prism", me); bpy.context.collection.objects.link(ob)
    _assign(ob, mat)
    if smooth:
        for p in ob.data.polygons:
            p.use_smooth = abs(p.normal.y) < 0.9
    return ob


def rrect(w, h, r, cx=0.0, cz=0.0, seg=3):
    """Rounded rectangle profile (width w along x, height h along z, corner radius r)."""
    pts = []
    for (sx, sz, a0) in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
        ox, oz = cx + sx * (w / 2 - r), cz + sz * (h / 2 - r)
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((ox + r * math.cos(a), oz + r * math.sin(a)))
    return pts


def wedge_roof(w, d, z0, rise, over, mat, thick=0.14, axis="X"):
    """Gable roof as two bevelled slabs; ridge along `axis`. Returns parts."""
    parts, _ = _gable_roof(w, d, z0, math.degrees(math.atan2(rise, (d if axis == "X" else w) / 2)), over, mat, thick=thick, ridge_axis=axis)
    return parts


def gpos(x, y, z):
    """Godot (x, y, z) -> Blender location. Godot +Z (toward the camera) = Blender -Y."""
    return (x, -z, y)


# ------------------------------------------------------------------ Godot-coordinate wrappers

def grot(r):
    """Godot rotation in degrees (single axis or X then Y) -> Blender Euler."""
    rx, ry, rz = (math.radians(a) for a in r)
    return (rx, -rz, ry)


def gb(size, pos, mat, bev=0.03, seg=1, rot=(0, 0, 0)):
    """Rounded box: size (x, height, depth) and position in Godot axes."""
    sx, sy, sz = size
    return rbox(sx, sz, sy, gpos(*pos), mat, bev=bev, seg=seg, rot=grot(rot))


def gc(r, length, pos, mat, axis="y", verts=12, r2=None, bev=0.0, smooth=True):
    """Cylinder along a Godot axis."""
    rot = {"y": (0, 0, 0), "x": (0, math.pi / 2, 0), "z": (math.pi / 2, 0, 0)}[axis]
    return cyl(r, length, gpos(*pos), mat, verts=verts, rot=rot, bev=bev, r2=r2, smooth=smooth)


def gl(r, length, pos, side, end, axis="x", verts=9, seg=1):
    """Log (bark side, ring ends) along a Godot axis."""
    rot = {"y": (0, 0, 0), "x": (0, math.pi / 2, 0), "z": (math.pi / 2, 0, 0)}[axis]
    return _log(r, length, gpos(*pos), rot, side, end, verts=verts, seg=seg)


def gll(r, length, pos, side, end, axis="x", verts=7):
    """Light log: unbevelled cylinder, bark side + ring ends (about 4 * verts tris). For walls of many logs."""
    rot = {"y": (0, 0, 0), "x": (0, math.pi / 2, 0), "z": (math.pi / 2, 0, 0)}[axis]
    ob = _add("primitive_cylinder_add", vertices=verts, radius=r, depth=length, location=(0, 0, 0))
    ob.data.materials.append(side); ob.data.materials.append(end)
    for p in ob.data.polygons:
        p.material_index = 1 if abs(p.normal.z) > 0.9 else 0
        p.use_smooth = abs(p.normal.z) < 0.9
    ob.rotation_euler = rot
    ob.location = gpos(*pos)
    return ob


def gmove(objs, dx=0.0, dy=0.0, dz=0.0, rot_y_deg=0.0):
    """Move/turn already-built parts in Godot axes (rotation about the Godot origin)."""
    R = Matrix.Rotation(math.radians(rot_y_deg), 4, "Z")
    T = Matrix.Translation(gpos(dx, dy, dz))
    for o in objs:
        o.matrix_world = T @ R @ o.matrix_world
    return objs



def gseg(a, b, r, mat, verts=6):
    """Cylinder between two Godot points."""
    pa, pb = Vector(gpos(*a)), Vector(gpos(*b))
    d = pb - pa
    ob = _add("primitive_cylinder_add", vertices=verts, radius=r, depth=d.length, location=(0, 0, 0))
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = d.to_track_quat("Z", "Y")
    ob.location = (pa + pb) / 2
    _assign(ob, mat); _smooth(ob)
    return ob


def gpoly(points, thick, mat):
    """Flat polygon through Godot points (any count >= 3, CCW seen from the side it faces), extruded by thick."""
    bm = bmesh.new()
    vs = [bm.verts.new(gpos(*p)) for p in points]
    f = bm.faces.new(vs)
    bm.normal_update()
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=-f.normal * thick, verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("poly"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("poly", me); bpy.context.collection.objects.link(ob)
    _assign(ob, mat)
    return ob


# ------------------------------------------------------------------ generic build + export

def _export(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
                              export_image_format="AUTO", export_yup=True)


def _emissive_build(name, objs, rgb, energy):
    ob = join_meshes(objs, name)
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*srgb(rgb), 1)
    b.inputs["Emission Color"].default_value = (*srgb(rgb), 1)
    b.inputs["Emission Strength"].default_value = energy
    b.inputs["Roughness"].default_value = 0.6
    ob.data.materials.clear(); ob.data.materials.append(m)
    return ob


def build_any(name, spec, report, root):
    folder, builder, tex, units, opt = spec
    reset()
    res = builder()
    stage_names = None
    if isinstance(res, dict):
        stage_names = list(res.keys())
        groups = []
        for k, sn in enumerate(stage_names):
            g = join_meshes(res[sn], sn)
            at = g.data.attributes.new("stage", "INT", "FACE")
            for i in range(len(g.data.polygons)):
                at.data[i].value = k
            groups.append(g)
        ob = join_meshes(groups, name)
    else:
        ob = join_meshes(res, name)
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    mn, mx = bbox(ob)
    if "emissive" in opt:
        r, g, b, e = opt["emissive"]
        ob = _emissive_build(name, [ob], (r, g, b), e)
    else:
        height = mx.z - max(mn.z, 0)
        if opt.get("no_ground"):
            ob.location.z += 100.0
        img = bake_model(ob, tex, (1, 1, 1), opt.get("grad", 0.8), opt.get("ao", 0.3), max(height, 0.05), name)
        ob.location.z = 0.0
        finish_material(ob, img, name, opt.get("double", False))
    for o in list(bpy.data.objects):
        if o != ob:
            bpy.data.objects.remove(o, do_unlink=True)
    parts = [ob]
    stage_tris = None
    if stage_names:
        parts, stage_tris = [], {}
        for k, sn in enumerate(stage_names):
            d = ob.copy(); d.data = ob.data.copy(); bpy.context.collection.objects.link(d)
            bm = bmesh.new(); bm.from_mesh(d.data)
            lay = bm.faces.layers.int.get("stage")
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[lay] != k], context="FACES")
            bm.to_mesh(d.data); bm.free()
            d.data.attributes.remove(d.data.attributes["stage"])
            d.name = sn; d.data.name = f"{name}_{sn}"
            parts.append(d); stage_tris[sn] = tris(d)
        bpy.data.objects.remove(ob, do_unlink=True)
    elif "stage" in ob.data.attributes:
        ob.data.attributes.remove(ob.data.attributes["stage"])
    os.makedirs(f"{root}/{folder}", exist_ok=True)
    path = f"{root}/{folder}/{name}.glb"
    _export(parts, path)
    mn = Vector((min(bbox(p)[0].x for p in parts), min(bbox(p)[0].y for p in parts), min(bbox(p)[0].z for p in parts)))
    mx = Vector((max(bbox(p)[1].x for p in parts), max(bbox(p)[1].y for p in parts), max(bbox(p)[1].z for p in parts)))
    size_b = mx - mn
    report[name] = dict(folder=folder, units=units, tris=sum(tris(p) for p in parts), tex=0 if "emissive" in opt else tex,
                        size_godot=[round(size_b.x, 3), round(size_b.z, 3), round(size_b.y, 3)],
                        min_godot=[round(mn.x, 3), round(mn.z, 3), round(-mx.y, 3)],
                        max_godot=[round(mx.x, 3), round(mx.z, 3), round(-mn.y, 3)],
                        bytes=os.path.getsize(path), device=GPU_STATE["device"])
    if stage_tris:
        report[name]["stages"] = stage_tris
    print("BUILT", name, report[name])


def run_plan(plan, rep_path, root):
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    report = json.load(open(rep_path)) if os.path.exists(rep_path) else {}
    for name, spec in plan.items():
        if args and name not in args:
            continue
        try:
            build_any(name, spec, report, root)
        except Exception as e:  # noqa: BLE001  (keep going, report the failure)
            import traceback; traceback.print_exc()
            report[name] = dict(error=str(e))
            print("FAILED", name, e)
        json.dump(report, open(rep_path, "w"), indent=1)
