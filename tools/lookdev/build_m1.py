"""Build the M1 (Birch Bend) models into assets/models_v3/birch/ and the item models into
assets/models_v3/items/, with the same bake as build_v3.py (albedo x soft height gradient x AO with a
ground plane, one mesh, one material, one embedded texture per GLB).

Usage (headless):
  /home/mm/.local/bin/blender -b --python tools/lookdev/build_m1.py -- [only_name ...]

Everything here is built from primitives in this file (own work, CC0). Units:
  - trees + nature props ("kenney" units): same convention as models_v3/nature, World scales them ~2.2-3.6
  - machines, buildings, items ("world" units): metres, use at scale 1.0
"""
import bpy, bmesh, sys, os, math, json, random
from mathutils import Vector, Matrix, noise

_here = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(_here, "build_v3.py")).read().rsplit("\nmain()", 1)[0]
exec(compile(_src, "build_v3.py", "exec"), globals())  # helpers: reset, join_meshes, bake_model, finish_material, ...

OUT_M1 = f"{REPO}/assets/models_v3"

# ------------------------------------------------------------------ palette (sRGB, see docs/DESIGN.md)
BIRCH_BARK = (0.94, 0.92, 0.87)
BIRCH_LEAF = (0.64, 0.82, 0.34)        # lighter, yellower than the V1 canopy #89c43f
BIRCH_LEAF2 = (0.55, 0.77, 0.30)
RIVER_BLUE = (0.25, 0.54, 0.76)        # Birch Bend machine/roof accent (V1 uses orange/green)
YELLOW = (1.0, 0.76, 0.18)
CREAM = (0.95, 0.90, 0.80)
WARM_GREY = (0.60, 0.555, 0.50)
STEEL = (0.74, 0.74, 0.72)
PLANK = (0.93, 0.74, 0.47)
FURN = (0.90, 0.66, 0.42)
DARK_WOOD = (0.55, 0.36, 0.22)
VENEER = (0.98, 0.89, 0.70)
CANOE_RED = (0.86, 0.34, 0.24)
NAUST_RED = (0.74, 0.22, 0.17)
SLATE = (0.38, 0.35, 0.34)
DOOR_DARK = (0.30, 0.22, 0.17)
GLASS = (0.62, 0.82, 0.92)
GREEN_BTN = (0.2, 0.78, 0.36)

# ------------------------------------------------------------------ extra procedural albedo kinds
_base_color_socket_v3 = base_color_socket


def base_color_socket(nt, mat, src_uv):  # noqa: F811  (overrides the v3 one for new kinds)
    kind = mat.get("proc", "")
    if kind not in ("birch", "plyedge", "boards"):
        return _base_color_socket_v3(nt, mat, src_uv)
    nodes, links = nt.nodes, nt.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    rgb = nodes.new("ShaderNodeRGB"); rgb.outputs[0].default_value = bsdf.inputs["Base Color"].default_value
    tc = nodes.new("ShaderNodeTexCoord")
    mix = nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1
    links.new(rgb.outputs[0], mix.inputs["A"])
    ramp = nodes.new("ShaderNodeValToRGB")
    if kind == "birch":
        # white bark with soft dark horizontal dashes (lenticels), big and few
        mp = nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = mat.get("mscale", (3.0, 3.0, 26.0))
        n = nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 1.0; n.inputs["Detail"].default_value = 1.0
        links.new(tc.outputs["Object"], mp.inputs["Vector"]); links.new(mp.outputs[0], n.inputs["Vector"])
        links.new(n.outputs["Fac"], ramp.inputs["Fac"])
        e0, e1 = ramp.color_ramp.elements
        e0.position = 0.56; e0.color = (1, 1, 1, 1)
        e1.position = 0.60; e1.color = (0.26, 0.24, 0.23, 1)
    elif kind == "plyedge":
        # layered plywood edge: soft light/dark bands stacked in Z
        w = nodes.new("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = "Z"
        w.inputs["Scale"].default_value = mat.get("bands", 14.0); w.inputs["Distortion"].default_value = 0.0
        links.new(tc.outputs["Object"], w.inputs["Vector"]); links.new(w.outputs["Fac"], ramp.inputs["Fac"])
        e0, e1 = ramp.color_ramp.elements
        e0.position = 0.45; e0.color = (0.62, 0.50, 0.40, 1)
        e1.position = 0.55; e1.color = (1, 1, 1, 1)
    else:  # boards: vertical board seams + soft streaks (painted wall boards)
        w = nodes.new("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = mat.get("dir", "X")
        w.inputs["Scale"].default_value = mat.get("bands", 20.0); w.wave_profile = "SAW"
        links.new(tc.outputs["Object"], w.inputs["Vector"]); links.new(w.outputs["Fac"], ramp.inputs["Fac"])
        e0, e1 = ramp.color_ramp.elements
        e0.position = 0.0; e0.color = (0.84, 0.84, 0.84, 1)
        e1.position = 0.12; e1.color = (1, 1, 1, 1)
    links.new(ramp.outputs["Color"], mix.inputs["B"])
    return mix.outputs["Result"]


# ------------------------------------------------------------------ primitives

def M(name, rgb, kind="plain", **kw):
    m = flat_mat(name, srgb(rgb), kind)
    for k, v in kw.items():
        m[k] = v
    return m


def rbox(sx, sy, sz, loc, mat, bev=0.03, seg=2, rot=(0, 0, 0), smooth=False):
    ob = _add("primitive_cube_add", size=1, location=(0, 0, 0))
    ob.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    if bev > 0:
        b = ob.modifiers.new("b", "BEVEL"); b.width = min(bev, 0.49 * min(sx, sy, sz)); b.segments = seg
        bpy.ops.object.modifier_apply(modifier="b")
    ob.rotation_euler = rot
    ob.location = loc
    _assign(ob, mat)
    if smooth:
        _smooth(ob)
    return ob


def cyl(r, depth, loc, mat, verts=12, rot=(0, 0, 0), bev=0.0, r2=None, smooth=True):
    if r2 is None:
        ob = _add("primitive_cylinder_add", vertices=verts, radius=r, depth=depth, location=(0, 0, 0))
    else:
        ob = _add("primitive_cone_add", vertices=verts, radius1=r, radius2=r2, depth=depth, location=(0, 0, 0))
    if bev > 0:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bev; b.segments = 2; b.limit_method = "ANGLE"
        bpy.ops.object.modifier_apply(modifier="b")
    for p in ob.data.polygons:
        p.use_smooth = smooth and abs(p.normal.z) < 0.9
    ob.rotation_euler = rot
    ob.location = loc
    _assign(ob, mat)
    return ob


def blob(r, loc, scl, mat, seed, seg=11, rings=7, ico=0, amp=0.12):
    """Soft lumpy canopy blob: sphere with low-frequency noise, smooth shaded."""
    if ico:
        ob = _add("primitive_ico_sphere_add", subdivisions=ico, radius=r, location=(0, 0, 0))
    else:
        ob = _add("primitive_uv_sphere_add", segments=seg, ring_count=rings, radius=r, location=(0, 0, 0))
    off = Vector((seed * 3.1, seed * 1.7, seed * 4.3))
    for v in ob.data.vertices:
        n = v.co.normalized()
        v.co *= 1.0 + amp * noise.noise(n * 1.4 + off)
        if n.z < -0.3:   # flatter underside, like a cloud
            v.co.z *= 0.8
    ob.scale = scl
    bpy.ops.object.transform_apply(scale=True)
    ob.location = loc
    _assign(ob, mat); _smooth(ob)
    return ob


def tube(points, radii, sides, mat, cap_top=True):
    """Tapered trunk along a polyline (list of Vector), one ring per point."""
    bm = bmesh.new()
    rings = []
    for i, (p, r) in enumerate(zip(points, radii)):
        d = (points[min(i + 1, len(points) - 1)] - points[max(i - 1, 0)]).normalized()
        a = Vector((1, 0, 0)) if abs(d.x) < 0.9 else Vector((0, 1, 0))
        u = d.cross(a).normalized(); w = d.cross(u).normalized()
        rings.append([bm.verts.new(p + r * (math.cos(2 * math.pi * k / sides) * u + math.sin(2 * math.pi * k / sides) * w)) for k in range(sides)])
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k]))
    if cap_top:
        bm.faces.new(list(reversed(rings[-1])))
    me = bpy.data.meshes.new("tube"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("tube", me); bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True)
    _assign(ob, mat); _smooth(ob)
    return ob


def trapezoid_wall(p0, p1, p2, p3, thick, mat):
    """Quad (p0..p3, CCW seen from outside) extruded by thick along its normal."""
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in (p0, p1, p2, p3)]
    f = bm.faces.new(vs)
    bm.normal_update()
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=-f.normal * thick, verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("wall"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("wall", me); bpy.context.collection.objects.link(ob)
    _assign(ob, mat)
    return ob


# ------------------------------------------------------------------ trees (kenney units)

def birch_tree(variant, far=False):
    """Birch: slim white trunk (the read at distance) under an oval, cloud-like light-green canopy."""
    rnd = random.Random({"A": 11, "B": 23, "C": 37}[variant])
    bark = M("birch", BIRCH_BARK, "birch", mscale=(5.0, 5.0, 16.0))
    leaf = M("leaf", BIRCH_LEAF if variant != "C" else BIRCH_LEAF2)
    parts = []
    sides = (4 if variant == "C" else 5) if far else (7 if variant == "C" else 8)
    # trunks: (x, y, r_base, r_top, height); canopy ellipsoid: centre z, radii
    if variant == "A":
        trunks = [(0.0, 0.0, 0.05, 0.03, 1.35)]
        cz, rx, ry, rz = 1.28, 0.3, 0.28, 0.5
    elif variant == "B":   # tall, slim
        trunks = [(0.0, 0.0, 0.045, 0.028, 1.55)]
        cz, rx, ry, rz = 1.42, 0.25, 0.24, 0.58
    else:                  # twin trunk, wider
        trunks = [(-0.06, 0.0, 0.042, 0.026, 1.25), (0.07, 0.02, 0.036, 0.022, 1.1)]
        cz, rx, ry, rz = 1.2, 0.36, 0.3, 0.46
    for (x, y, r0, r1, h) in trunks:
        lean = Vector((x * 1.6, y * 1.6, 0))
        n = 1 if far else (3 if variant == "C" else 4)
        pts = [Vector((x, y, -0.04)) + lean * (i / n) ** 1.5 + Vector((0, 0, (h + 0.04) * i / n)) for i in range(n + 1)]
        rad = [r0 + (r1 - r0) * i / n for i in range(n + 1)]
        parts.append(tube(pts, rad, sides, bark))
    if not far and variant == "A":
        pts = [Vector((0.0, 0.0, 0.62)), Vector((0.1, -0.02, 0.76)), Vector((0.17, -0.03, 0.86))]
        parts.append(tube(pts, [0.016, 0.012, 0.008], 5, bark))
    if far:
        parts.append(blob(1.0, (0, 0, cz), (rx * 0.95, ry * 0.95, rz * 0.9), leaf, 1, ico=2, amp=0.1))
        parts.append(blob(1.0, (rx * 0.35, -ry * 0.2, cz + rz * 0.35), (rx * 0.6, ry * 0.6, rz * 0.5), leaf, 2, ico=2, amp=0.1))
    else:
        # one core blob + five lumps sitting on the canopy ellipsoid: a cloud, not a stack of balls
        parts.append(blob(1.0, (0, 0, cz), (rx * 0.82, ry * 0.82, rz * 0.8), leaf, 0.5, seg=10, rings=7, amp=0.08))
        az0 = rnd.uniform(0, 6.28)
        for i in range(5):
            az = az0 + i * 2 * math.pi / 5 + rnd.uniform(-0.3, 0.3)
            el = [-0.35, 0.1, 0.45, -0.05, 0.3][i]
            px = rx * 0.5 * math.cos(az) * math.cos(el); py = ry * 0.5 * math.sin(az) * math.cos(el)
            pz = cz + rz * 0.7 * math.sin(el)
            r = rx * rnd.uniform(0.56, 0.66)
            parts.append(blob(1.0, (px, py, pz), (r, r, r * 1.1), leaf, i + 1.3, seg=8, rings=6, amp=0.1))
        parts.append(blob(1.0, (0.02, 0.0, cz + rz * 0.72), (rx * 0.5, rx * 0.5, rx * 0.55), leaf, 7.7, seg=8, rings=6, amp=0.1))
    return parts


# ------------------------------------------------------------------ nature props (kenney units)

def birch_stump():
    side = M("bark", BIRCH_BARK, "birch", mscale=(6.0, 6.0, 40.0))
    end = M("rings", (0.95, 0.84, 0.64), "rings")
    parts = [_log(0.16, 0.2, (0, 0, 0.1), (0, 0, 0), side, end, verts=14)]
    for i in range(4):
        a = i * math.pi / 2 + 0.4
        rt = _add("primitive_uv_sphere_add", segments=8, ring_count=4, radius=0.07, location=(0.15 * math.cos(a), 0.15 * math.sin(a), 0.02))
        rt.scale = (1.4, 0.7, 0.6); rt.rotation_euler = (0, 0, a); _assign(rt, side); _smooth(rt); parts.append(rt)
    return parts


def birch_log_stack():
    side = M("bark", BIRCH_BARK, "birch", mscale=(5.0, 16.0, 5.0))  # logs lie along Y: dashes run across them
    end = M("rings", (0.95, 0.84, 0.64), "rings")
    parts = []
    r = 0.075
    for count, row in [(4, 0.0), (3, 1.0), (2, 2.0)]:
        for i in range(count):
            x = (i - (count - 1) / 2) * 2 * r * 1.02
            z = r + row * r * 1.75
            parts.append(_log(r * (0.96 + 0.04 * ((i * 7) % 3)), 0.66, (x, 0, z), (math.pi / 2, 0, 0), side, end, verts=9, seg=1))
    return parts


def reeds():
    blade = M("reed", (0.46, 0.66, 0.30))
    head = M("cattail", (0.50, 0.32, 0.20))
    parts = []
    rnd = random.Random(5)
    for i in range(9):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.0, 0.09)
        h = rnd.uniform(0.32, 0.5)
        c = cyl(0.014, h, (0, 0, 0), blade, verts=4, r2=0.0)
        c.data.transform(Matrix.Translation((0, 0, h / 2)))
        c.rotation_euler = (rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), a)
        c.location = (d * math.cos(a), d * math.sin(a), 0)
        bpy.ops.object.select_all(action="DESELECT"); c.select_set(True); bpy.context.view_layer.objects.active = c
        parts.append(c)
    for i in range(3):
        a = i * 2.1 + 0.3
        x, y = 0.05 * math.cos(a), 0.05 * math.sin(a)
        h = 0.5 + 0.06 * i
        parts.append(cyl(0.006, h, (x, y, h / 2), blade, verts=4))
        hd = _add("primitive_uv_sphere_add", segments=6, ring_count=4, radius=0.022, location=(x, y, h - 0.04))
        hd.scale.z = 2.4; _assign(hd, head); _smooth(hd); parts.append(hd)
    return parts


def lilypads():
    pad = M("pad", (0.36, 0.64, 0.30))
    petal = M("lily", (0.98, 0.86, 0.88))
    centre = M("lilyc", (0.98, 0.84, 0.25))
    parts = []
    for (x, y, r, rot) in ((0, 0, 0.13, 0.3), (0.2, 0.08, 0.09, 2.0), (-0.1, 0.18, 0.08, 4.1)):
        c = _add("primitive_cylinder_add", vertices=16, radius=r, depth=0.012, location=(x, y, 0.006))
        bm = bmesh.new(); bm.from_mesh(c.data)
        # notch: pull two rim verts to the centre
        rim = sorted([v for v in bm.verts if v.co.z > 0], key=lambda v: math.atan2(v.co.y, v.co.x))
        for v in rim[:1]:
            v.co.x *= 0.1; v.co.y *= 0.1
        bm.to_mesh(c.data); bm.free()
        c.rotation_euler.z = rot; _assign(c, pad); parts.append(c)
    for i in range(6):
        a = i * math.pi / 3
        p = _add("primitive_uv_sphere_add", segments=6, ring_count=4, radius=0.03, location=(0.035 * math.cos(a), 0.035 * math.sin(a), 0.03))
        p.scale = (1.5, 0.7, 0.6); p.rotation_euler = (0, -0.5, a); _assign(p, petal); _smooth(p); parts.append(p)
    ce = _add("primitive_uv_sphere_add", segments=6, ring_count=4, radius=0.018, location=(0, 0, 0.04)); _assign(ce, centre); parts.append(ce)
    return parts


# ------------------------------------------------------------------ items (world metres, scale 1)

def _log_along_x(r, length, side, end, verts=12):
    return _log(r, length, (0, 0, r), (0, math.pi / 2, 0), side, end, verts=verts, seg=2)


def item_log():
    return [_log_along_x(0.16, 0.95, M("bark", (0.62, 0.40, 0.24), "bark"), M("rings", (0.93, 0.76, 0.52), "rings"))]


def item_birch_log():
    return [_log_along_x(0.16, 0.95, M("bark", BIRCH_BARK, "birch", mscale=(16.0, 5.0, 5.0)), M("rings", (0.95, 0.84, 0.64), "rings"))]


def item_plank():
    return [rbox(0.95, 0.34, 0.1, (0, 0, 0.05), M("plank", PLANK, "planks"), bev=0.025)]


def item_veneer():
    """Thin pale sheet with the peeled end curling up: the shape tells it apart from plank and plywood."""
    ob = _add("primitive_grid_add", x_subdivisions=10, y_subdivisions=2, size=1.0, location=(0, 0, 0))
    ob.scale = (0.95, 0.48, 1); bpy.ops.object.transform_apply(scale=True)
    for v in ob.data.vertices:
        if v.co.x > 0.15:
            t = (v.co.x - 0.15) / 0.325
            v.co.z = 0.07 * t * t
            v.co.x = 0.15 + (v.co.x - 0.15) * (1 - 0.12 * t)
    sd = ob.modifiers.new("s", "SOLIDIFY"); sd.thickness = 0.022; sd.offset = 1
    bpy.ops.object.modifier_apply(modifier="s")
    ob.location.z = 0.0
    _assign(ob, M("veneer", (0.99, 0.92, 0.76), "planks")); _smooth(ob)
    return [ob]


def item_plywood():
    top = M("plytop", (0.90, 0.74, 0.50), "planks")
    edge = M("plyedge", (0.97, 0.86, 0.64), "plyedge", bands=14.0)
    ob = rbox(0.95, 0.56, 0.11, (0, 0, 0.055), top, bev=0.012)
    ob.data.materials.append(edge)
    for p in ob.data.polygons:
        p.material_index = 0 if abs(p.normal.z) > 0.7 else 1
    return [ob]


def _canoe_hull(L, W, D, outer, inner, seg=14, rings=8):
    """Open canoe hull, long along Y, keel at z=0, gunwale at z=D."""
    ob = _add("primitive_uv_sphere_add", segments=seg, ring_count=rings, radius=1.0, location=(0, 0, 0))
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 0.02], context="VERTS")
    for v in bm.verts:
        v.co.z = min(v.co.z, 0.0)
    bm.to_mesh(ob.data); bm.free()
    # sphere lies with poles on Z; turn so the poles become bow/stern along Y
    for v in ob.data.vertices:
        x, y, z = v.co
        v.co = Vector((x, y, z))
    ob.scale = (W / 2, L / 2, D)
    bpy.ops.object.transform_apply(scale=True)
    for v in ob.data.vertices:   # pointier ends, upswept bow and stern
        t = abs(v.co.y) / (L / 2)
        v.co.x *= (1 - t ** 3) ** 0.6 if t < 1 else 0
        v.co.z += D * 0.22 * t ** 3
    ob.location.z = D
    bpy.ops.object.transform_apply(location=True)
    s = ob.modifiers.new("s", "SOLIDIFY"); s.thickness = 0.03; s.offset = 1
    bpy.ops.object.modifier_apply(modifier="s")
    ob.data.materials.clear(); ob.data.materials.append(outer); ob.data.materials.append(inner)
    c = Vector((0, 0, D * 1.2))
    for p in ob.data.polygons:
        p.material_index = 1 if p.normal.dot(p.center - c) < 0 or p.normal.z > 0.8 else 0
    _smooth(ob)
    return ob


def item_canoe(L=1.95, W=0.65, D=0.3, thwarts=True, seg=14, rings=8):
    outer = M("hull", CANOE_RED)
    inner = M("inner", (0.93, 0.76, 0.52), "planks")
    parts = [_canoe_hull(L, W, D, outer, inner, seg=seg, rings=rings)]
    if thwarts:
        for y in (-0.42, 0.0, 0.42):
            w = W * (1 - (abs(y) / (L / 2)) ** 3) ** 0.6 * 0.92
            parts.append(rbox(w, 0.06, 0.03, (0, y * L / 1.95, D * 0.92), inner, bev=0.01))
    return parts


def item_chair():
    wood = M("wood", FURN, "planks")
    parts = [rbox(0.38, 0.36, 0.06, (0, 0, 0.45), wood, bev=0.02, seg=1)]
    for x in (-0.16, 0.16):
        for y in (-0.15, 0.15):
            parts.append(cyl(0.022, 0.43, (x, y, 0.215), wood, verts=6))
    for x in (-0.16, 0.16):   # back posts (back at +Y, like the Kenney chair)
        parts.append(cyl(0.022, 0.44, (x, 0.165, 0.67), wood, verts=6))
    parts.append(rbox(0.36, 0.035, 0.12, (0, 0.165, 0.83), wood, bev=0.015, seg=1))
    parts.append(rbox(0.36, 0.03, 0.06, (0, 0.165, 0.66), wood, bev=0.012, seg=1))
    return parts


def item_table():
    wood = M("wood", FURN, "planks")
    parts = [rbox(0.88, 0.47, 0.06, (0, 0, 0.313), wood, bev=0.025)]
    for x in (-0.38, 0.38):
        for y in (-0.18, 0.18):
            parts.append(cyl(0.03, 0.29, (x, y, 0.145), wood, verts=8))
    return parts


def item_bookcase():
    wood = M("wood", FURN, "planks")
    dark = M("back", (0.62, 0.42, 0.26))
    books = [M("b1", (0.93, 0.33, 0.30)), M("b2", (0.98, 0.84, 0.25)), M("b3", RIVER_BLUE), M("b4", (0.35, 0.62, 0.35))]
    W, D, H = 0.5, 0.31, 1.06
    parts = [rbox(W, 0.02, H, (0, D / 2 - 0.01, H / 2), dark, bev=0.005)]           # back (+Y)
    for x in (-W / 2 + 0.02, W / 2 - 0.02):
        parts.append(rbox(0.04, D, H, (x, 0, H / 2), wood, bev=0.012, seg=1))
    shelves = [0.02, 0.36, 0.7, 1.04]
    for z in shelves:
        parts.append(rbox(W, D, 0.04, (0, 0, z), wood, bev=0.0))
    rnd = random.Random(3)
    for si, z in enumerate(shelves[:-1]):
        x = -W / 2 + 0.05
        k = si
        while x < W / 2 - 0.1:
            bw = rnd.uniform(0.09, 0.12); bh = rnd.uniform(0.2, 0.27)
            parts.append(rbox(bw, D * 0.75, bh, (x + bw / 2, 0.02, z + 0.02 + bh / 2), books[k % 4], bev=0.0))
            x += bw + 0.008; k += 1
    return parts


# ------------------------------------------------------------------ machines + buildings (world metres)

def _mats():
    return dict(blue=M("blue", RIVER_BLUE), yellow=M("yellow", YELLOW), grey=M("grey", WARM_GREY),
                steel=M("steel", STEEL), cream=M("cream", CREAM), plank=M("plank", PLANK, "planks"),
                post=M("post", DARK_WOOD, "bark"), green=M("btn", GREEN_BTN), veneer=M("veneer", VENEER, "planks"))


def veneer_lathe():
    m = _mats()
    p = []
    p.append(rbox(3.0, 1.5, 0.35, (0, 0, 0.175), m["grey"], bev=0.08, seg=3))
    p.append(rbox(0.6, 0.95, 1.3, (-1.15, 0.05, 0.95), m["blue"], bev=0.12, seg=3))       # headstock
    p.append(rbox(0.5, 0.8, 1.1, (1.15, 0.05, 0.85), m["blue"], bev=0.1, seg=3))          # tailstock
    for x in (-0.8, 0.8):                                                                   # chucks (log spins between)
        p.append(cyl(0.2, 0.1, (x, 0.0, 0.98), m["yellow"], verts=16, rot=(0, math.pi / 2, 0), bev=0.02))
    p.append(rbox(1.5, 0.12, 0.12, (0, 0.38, 0.72), m["yellow"], bev=0.04))              # knife bar behind the log
    # peeled veneer sheet sliding forward (towards the camera, -Y) onto a tray
    sh = rbox(1.4, 0.7, 0.03, (0, -0.52, 0.66), m["veneer"], bev=0.01, rot=(math.radians(-28), 0, 0))
    p.append(sh)
    p.append(rbox(1.6, 0.5, 0.1, (0, -0.78, 0.42), m["steel"], bev=0.03))
    p.append(rbox(0.45, 0.4, 0.5, (-1.15, 0.72, 0.6), m["yellow"], bev=0.08))             # motor
    p.append(cyl(0.12, 0.2, (-1.15, 0.72, 0.95), m["steel"], verts=10))
    p.append(rbox(0.3, 0.12, 0.26, (1.2, -0.45, 1.05), m["cream"], bev=0.04))             # control box
    p.append(cyl(0.05, 0.04, (1.2, -0.52, 1.08), m["green"], verts=10, rot=(math.pi / 2, 0, 0)))
    return p


def veneer_lathe_log():
    side = M("bark", BIRCH_BARK, "birch", mscale=(20.0, 2.5, 2.5))
    end = M("rings", (0.95, 0.84, 0.64), "rings")
    ob = _log(0.24, 1.5, (0, 0, 0), (0, math.pi / 2, 0), side, end, verts=14)
    return [ob]


def plywood_press():
    m = _mats()
    edge = M("plyedge", (0.97, 0.86, 0.64), "plyedge", bands=40.0)
    p = [rbox(2.0, 1.5, 0.6, (0, 0, 0.3), m["grey"], bev=0.1, seg=3)]
    for x in (-0.85, 0.85):
        for y in (-0.58, 0.58):
            p.append(cyl(0.09, 2.2, (x, y, 1.5), m["blue"], verts=12))
    p.append(rbox(2.1, 1.55, 0.36, (0, 0, 2.45), m["blue"], bev=0.12, seg=3))            # crown
    p.append(cyl(0.3, 0.45, (0, 0, 2.85), m["yellow"], verts=16, bev=0.05))               # hydraulic ram
    p.append(cyl(0.12, 0.12, (0, 0, 3.12), m["steel"], verts=12))
    for i in range(3):                                                                      # plywood waiting on the bed
        s = rbox(1.25, 0.95, 0.06, (0.02 * i, 0.02 * (i % 2), 0.63 + i * 0.065), edge, bev=0.01)
        p.append(s)
    for x in (-0.85, 0.85):                                                                 # yellow collars on columns
        for y in (-0.58, 0.58):
            p.append(cyl(0.12, 0.1, (x, y, 0.65), m["yellow"], verts=12))
    p.append(rbox(0.3, 0.12, 0.26, (1.0, -0.8, 0.95), m["cream"], bev=0.04))
    p.append(cyl(0.05, 0.04, (1.0, -0.87, 0.98), m["green"], verts=10, rot=(math.pi / 2, 0, 0)))
    return p


def plywood_press_plate():
    m = _mats()
    return [rbox(1.45, 1.05, 0.14, (0, 0, -0.07), m["steel"], bev=0.04),
            cyl(0.09, 0.9, (0, 0, 0.45), m["steel"], verts=12)]


def _gable_roof(w, d, z_eave, pitch_deg, over, mat, thick=0.14, ridge_axis="X"):
    """Two roof slabs meeting at a ridge along ridge_axis."""
    parts = []
    half = (d if ridge_axis == "X" else w) / 2 + over
    slope = math.radians(pitch_deg)
    panel = half / math.cos(slope)
    rise = half * math.tan(slope)
    length = (w if ridge_axis == "X" else d) + 2 * over
    for s in (-1, 1):
        if ridge_axis == "X":
            ob = rbox(length, panel, thick, (0, s * half / 2, z_eave + rise / 2 - over * math.tan(slope) + thick / 2), mat, bev=0.05,
                      rot=(-s * slope, 0, 0))
        else:
            ob = rbox(panel, length, thick, (s * half / 2, 0, z_eave + rise / 2 - over * math.tan(slope) + thick / 2), mat, bev=0.05,
                      rot=(0, s * slope, 0))
        parts.append(ob)
    return parts, rise - over * math.tan(slope)


def _gable_fill(w, z0, rise, y, mat, thick=0.1):
    """Triangle gable wall in the XZ plane at depth y."""
    bm = bmesh.new()
    a = bm.verts.new((-w / 2, y, z0)); b = bm.verts.new((w / 2, y, z0)); c = bm.verts.new((0, y, z0 + rise))
    f = bm.faces.new((a, b, c))
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, thick, 0), verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("gable"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("gable", me); bpy.context.collection.objects.link(ob)
    _assign(ob, mat)
    return ob


def _gable_fill_x(d, z0, rise, x, mat, thick=0.1):
    """Triangle gable wall in the YZ plane at x (for a ridge along X)."""
    ob = _gable_fill(d, z0, rise, 0.0, mat, thick)
    ob.data.transform(Matrix.Rotation(math.pi / 2, 4, "Z"))
    ob.location.x = x
    return ob


def boat_workshop():
    m = _mats()
    roof = M("roof", RIVER_BLUE, "boards", bands=12.0, dir="Y")
    W, D, H = 4.0, 3.0, 2.3
    p = [rbox(W, D, 0.15, (0, 0, 0.075), m["plank"], bev=0.04)]
    for x in (-W / 2 + 0.15, W / 2 - 0.15):
        for y in (-D * 0.1, D / 2 - 0.15):
            p.append(cyl(0.1, H + 0.2, (x, y, H / 2 + 0.2), m["post"], verts=8))
    p.append(rbox(W - 0.3, 0.12, 1.2, (0, D / 2 - 0.15, 0.75), m["plank"], bev=0.03, seg=1))      # low back wall
    # lean-to roof over the back 60% only: the portrait camera looks down at ~52 deg and must see the canoe
    p.append(rbox(W + 0.5, D * 0.62, 0.14, (0, D * 0.2, H + 0.35), roof, bev=0.05, rot=(math.radians(-8), 0, 0)))
    p.append(rbox(W + 0.3, 0.16, 0.2, (0, -D * 0.1, H + 0.45), m["post"], bev=0.04))
    for x in (-0.8, 0.8):                                                                   # trestles
        p.append(rbox(0.12, 0.9, 0.08, (x, -0.6, 0.62), m["post"], bev=0.02, seg=1))
        for y in (-0.95, -0.25):
            p.append(rbox(0.08, 0.08, 0.5, (x, y, 0.38), m["post"], bev=0.02, seg=1))
    hull = item_canoe(L=2.6, W=0.72, D=0.34, thwarts=False, seg=12, rings=6)                                 # canoe being built, lengthwise along X
    for h in hull:
        h.rotation_euler.z = math.pi / 2; h.location = (0, -0.6, 0.66)
    p += hull
    p.append(rbox(1.2, 0.5, 0.12, (1.3, 1.0, 0.85), m["plank"], bev=0.03, seg=1))                  # bench at the back
    for x in (0.8, 1.8):
        p.append(rbox(0.08, 0.4, 0.8, (x, 1.0, 0.45), m["post"], bev=0.02, seg=1))
    for i, x in enumerate((-1.5, -1.3)):                                                     # paddles on the back wall
        p.append(rbox(0.05, 0.03, 1.0, (x, 1.3, 1.3), m["post"], bev=0.01, seg=1, rot=(0, 0.15 * (1 - 2 * i), 0)))
        p.append(rbox(0.14, 0.03, 0.34, (x - 0.09 * (1 - 2 * i), 1.3, 0.72), m["yellow"], bev=0.02, rot=(0, 0.15 * (1 - 2 * i), 0)))
    return p


def riverside_office():
    m = _mats()
    walls = M("walls", CREAM, "boards", bands=16.0, dir="Z")
    roof = M("roof", RIVER_BLUE, "boards", bands=12.0, dir="Y")
    door = M("door", DOOR_DARK, "planks")
    glass = M("glass", GLASS)
    stone = M("stone", WARM_GREY)
    W, D, H = 3.2, 2.4, 2.1
    p = [rbox(W + 0.3, D + 0.3, 0.2, (0, 0, 0.1), stone, bev=0.06)]
    p.append(rbox(W, D, H, (0, 0, 0.2 + H / 2), walls, bev=0.04))
    for x in (-W / 2, W / 2):                                                               # corner trims
        for y in (-D / 2, D / 2):
            p.append(rbox(0.14, 0.14, H, (x, y, 0.2 + H / 2), m["blue"], bev=0.03))
    rp, rise = _gable_roof(W, D, 0.2 + H, 28, 0.35, roof)
    p += rp
    for x in (-W / 2 + 0.05, W / 2 + 0.05):
        p.append(_gable_fill_x(D, 0.2 + H, D / 2 * math.tan(math.radians(28)), x, walls))
    p.append(rbox(0.8, 0.08, 1.45, (-0.6, -D / 2 - 0.02, 0.2 + 0.725), door, bev=0.03))    # door (front = -Y)
    p.append(cyl(0.04, 0.05, (-0.35, -D / 2 - 0.07, 0.95), m["yellow"], verts=8, rot=(math.pi / 2, 0, 0)))
    p.append(rbox(0.8, 0.08, 0.65, (0.75, -D / 2 - 0.02, 1.35), glass, bev=0.02))          # window
    p.append(rbox(0.95, 0.1, 0.1, (0.75, -D / 2 - 0.05, 1.0), m["blue"], bev=0.03))
    p.append(rbox(1.6, 0.9, 0.12, (-0.2, -D / 2 - 0.55, 0.12), m["plank"], bev=0.03))      # porch step
    p.append(rbox(1.3, 0.1, 0.45, (0.0, -D / 2 - 0.08, 2.05), m["yellow"], bev=0.05))      # sign board (text via Label3D)
    p.append(rbox(0.45, 0.45, 0.9, (0.9, 0.5, 2.7), stone, bev=0.08))                      # chimney
    return p


def barge():
    m = _mats()
    hullm = M("hull", (0.22, 0.42, 0.58))
    deck = M("deck", PLANK, "planks")
    tyre = M("tyre", (0.24, 0.23, 0.22))
    walls = M("walls", CREAM, "boards", bands=16.0, dir="Z")
    glass = M("glass", GLASS)
    L, W = 6.0, 2.6
    h = rbox(W, L, 0.75, (0, 0, 0.08), hullm, bev=0.22, seg=3)   # waterline z=0, deck ~z 0.45
    for v in h.data.vertices:                                     # raked bow/stern: pull the bottom in at the ends
        if v.co.z < 0 and abs(v.co.y) > L / 2 - 0.9:
            v.co.y *= 0.9
    p = [h]
    p.append(rbox(W - 0.2, L - 0.2, 0.06, (0, 0, 0.46), deck, bev=0.02))
    p.append(rbox(W + 0.04, L + 0.04, 0.1, (0, 0, 0.38), m["cream"], bev=0.04))           # cream rub strake
    for y in (-2.0, -0.6, 0.8, 2.2):                                                        # tyre fenders
        for s in (-1, 1):
            t = _add("primitive_torus_add", major_radius=0.14, minor_radius=0.06, major_segments=10, minor_segments=6,
                     location=(s * (W / 2 + 0.05), y, 0.2), rotation=(0, math.pi / 2, 0))
            _assign(t, tyre); _smooth(t); p.append(t)
    # wheelhouse at the stern (-Y); bow (+Y) points downstream/north (Godot -Z)
    p.append(rbox(1.5, 1.2, 1.1, (0, -2.25, 1.04), walls, bev=0.06))
    p.append(rbox(1.8, 1.5, 0.14, (0, -2.25, 1.66), m["blue"], bev=0.06))
    p.append(rbox(1.1, 0.06, 0.45, (0, -1.63, 1.2), glass, bev=0.02))
    p.append(cyl(0.1, 0.5, (0.45, -2.5, 1.95), m["post"], verts=10))                        # stove pipe
    for y in (2.75, -2.95):                                                                  # bollards
        p.append(cyl(0.08, 0.25, (0, y, 0.6), m["yellow"], verts=10))
    return p


def barge_landing():
    m = _mats()
    p = [rbox(4.2, 5.0, 0.14, (0, 0, 0.33), m["plank"], bev=0.03)]
    for i in range(6):                                                                       # board seams
        p.append(rbox(4.22, 0.04, 0.02, (0, -2.1 + i * 0.84, 0.405), m["post"], bev=0.0))
    for x in (-1.9, 0.0, 1.9):
        for y in (-2.3, 2.3):
            p.append(cyl(0.12, 0.45 if x < 1.9 else 0.95, (x, y, (0.45 if x < 1.9 else 0.95) / 2), m["post"], verts=10))
    for y in (-1.2, 1.2):                                                                     # bollards on the river edge (+X)
        p.append(cyl(0.12, 0.3, (1.85, y, 0.55), m["yellow"], verts=12))
        p.append(cyl(0.16, 0.06, (1.85, y, 0.72), m["yellow"], verts=12))
    p.append(cyl(0.05, 1.6, (-1.8, -2.1, 1.2), m["post"], verts=8))                           # lantern post
    p.append(rbox(0.22, 0.22, 0.28, (-1.8, -2.1, 2.1), m["yellow"], bev=0.05))
    return p


FLUME_Z = 0.75   # trough floor height (world m); water surface sits at FLUME_Z + 0.20


def _trough(x0, x1, m, legs=True, floor_tilt=0.0):
    L = x1 - x0; cx = (x0 + x1) / 2
    p = [rbox(L, 0.8, 0.08, (cx, 0, FLUME_Z - 0.04), m["plank"], bev=0.02, seg=1, rot=(0, floor_tilt, 0))]
    for s in (-1, 1):
        p.append(rbox(L, 0.1, 0.36, (cx, s * 0.35, FLUME_Z + 0.14), m["plank"], bev=0.03, seg=1, rot=(0, floor_tilt, 0)))
    if legs:
        for s in (-1, 1):
            p.append(rbox(0.1, 0.1, FLUME_Z + 0.05, (cx, s * 0.45, (FLUME_Z - 0.05) / 2), m["post"], bev=0.02, seg=1, rot=(s * 0.12, 0, 0)))
        p.append(rbox(0.08, 0.9, 0.08, (cx, 0, 0.3), m["post"], bev=0.02, seg=1))
        p.append(rbox(0.12, 1.0, 0.1, (cx, 0, FLUME_Z - 0.12), m["post"], bev=0.02, seg=1))
    return p


def flume_straight():
    m = _mats()
    return _trough(-1.0, 1.0, m)


def flume_chute():
    m = _mats()
    # hopper over the start (x in -1.4..0), trough continues to +1.0
    p = _trough(-0.2, 1.0, m)
    top, bot, zt = 0.75, 0.3, 1.35
    walls = [((-0.7 - top, -top, zt), (-0.7 + top, -top, zt), (-0.7 + bot, -bot, FLUME_Z), (-0.7 - bot, -bot, FLUME_Z)),
             ((-0.7 + top, top, zt), (-0.7 - top, top, zt), (-0.7 - bot, bot, FLUME_Z), (-0.7 + bot, bot, FLUME_Z)),
             ((-0.7 - top, top, zt), (-0.7 - top, -top, zt), (-0.7 - bot, -bot, FLUME_Z), (-0.7 - bot, bot, FLUME_Z))]
    for w in walls:
        ob = trapezoid_wall(*w, 0.07, m["plank"]); p.append(ob)
    p.append(rbox(0.7, 0.7, 0.06, (-0.7, 0, FLUME_Z - 0.03), m["plank"], bev=0.02, seg=1))
    for x in (-1.3, -0.1):
        for y in (-0.6, 0.6):
            p.append(rbox(0.1, 0.1, zt, (x, y, zt / 2), m["post"], bev=0.02, seg=1))
    p.append(rbox(1.6, 0.1, 0.1, (-0.7, -0.78, zt + 0.02), m["yellow"], bev=0.03, seg=1))            # yellow rim = drop here
    p.append(rbox(1.6, 0.1, 0.1, (-0.7, 0.78, zt + 0.02), m["yellow"], bev=0.03, seg=1))
    return p


def flume_end():
    m = _mats()
    p = _trough(-1.0, 0.2, m)
    # spout: short tilted trough dropping to the pile
    p += _trough(0.2, 0.9, m, legs=False, floor_tilt=math.radians(18))
    for i in p[-3:]:
        i.location.z -= 0.1
    return p


def boathouse():
    m = _mats()
    walls = M("walls", NAUST_RED, "boards", bands=18.0, dir="X")
    walls_side = M("walls2", NAUST_RED, "boards", bands=18.0, dir="Y")
    roof = M("roof", SLATE, "boards", bands=10.0, dir="Y")
    white = M("trim", (0.97, 0.95, 0.9))
    dark = M("inside", DOOR_DARK)
    stone = M("stone", WARM_GREY)
    W, D, H = 6.0, 8.0, 2.6         # gable faces -Y (the camera / the water side)
    p = [rbox(W + 0.4, D + 0.4, 0.35, (0, 0, 0.175), stone, bev=0.1, seg=3)]
    body = rbox(W, D, H, (0, 0, 0.35 + H / 2), walls_side, bev=0.05)
    body.data.materials.append(walls)
    for f in body.data.polygons:
        f.material_index = 1 if abs(f.normal.y) > 0.5 else 0
    p.append(body)
    rp, rise = _gable_roof(W, D, 0.35 + H, 38, 0.45, roof, thick=0.2, ridge_axis="Y")
    p += rp
    g_rise = W / 2 * math.tan(math.radians(38))
    for y in (-D / 2 - 0.02, D / 2 - 0.08):
        p.append(_gable_fill(W, 0.35 + H, g_rise, y, walls))
    # big boat door on the front gable: dark opening + white frame + open door leaf
    p.append(rbox(2.6, 0.06, 2.4, (0, -D / 2 - 0.04, 0.35 + 1.2), dark, bev=0.02, seg=1))
    for x in (-1.36, 1.36):
        p.append(rbox(0.14, 0.12, 2.5, (x, -D / 2 - 0.07, 0.35 + 1.25), white, bev=0.03, seg=1))
    p.append(rbox(2.86, 0.12, 0.14, (0, -D / 2 - 0.07, 0.35 + 2.5), white, bev=0.03, seg=1))
    p.append(rbox(1.3, 0.1, 2.3, (-2.0, -D / 2 - 0.62, 0.35 + 1.15), walls, bev=0.03, seg=1, rot=(0, 0, math.radians(-70))))
    # white corner boards and barge boards along the gable
    for x in (-W / 2, W / 2):
        for y in (-D / 2, D / 2):
            p.append(rbox(0.16, 0.16, H, (x, y, 0.35 + H / 2), white, bev=0.03, seg=1))
    bl = math.hypot(W / 2 + 0.45, (W / 2 + 0.45) * math.tan(math.radians(38)))
    for s in (-1, 1):
        p.append(rbox(bl, 0.12, 0.2, (s * (W / 4), -D / 2 - 0.5, 0.35 + H + g_rise / 2 - 0.05), white, bev=0.03, seg=1,
                      rot=(0, s * math.radians(38), 0)))
    # small round window high in the gable
    p.append(cyl(0.3, 0.08, (0, -D / 2 - 0.06, 0.35 + H + 0.75), white, verts=14, rot=(math.pi / 2, 0, 0)))
    p.append(cyl(0.22, 0.1, (0, -D / 2 - 0.07, 0.35 + H + 0.75), M("glass", GLASS), verts=14, rot=(math.pi / 2, 0, 0)))
    # crossed oars over the door
    for s in (-1, 1):
        p.append(rbox(0.06, 0.05, 1.6, (0, -D / 2 - 0.1, 0.35 + 2.95), m["post"], bev=0.01, seg=1, rot=(0, s * 0.9, 0)))
    # jetty in front with a canoe
    p.append(rbox(2.2, 2.4, 0.12, (0, -D / 2 - 1.4, 0.3), m["plank"], bev=0.03, seg=1))
    for x in (-1.0, 1.0):
        p.append(cyl(0.1, 0.55, (x, -D / 2 - 2.5, 0.28), m["post"], verts=8))
    c = item_canoe(L=1.95, W=0.65, D=0.3, thwarts=False, seg=12, rings=6)
    for h in c:
        h.rotation_euler.z = 0.25; h.location = (2.2, -D / 2 - 1.6, 0.0)
    p += c
    return p


# ------------------------------------------------------------------ plan
# name: (folder, builder, tex, units, opts)   opts: ao (fraction of height), grad (bottom brightness), double
T = dict(ao=0.22, grad=0.86)
PLAN = {
    "tree_birchA":        ("birch", lambda: birch_tree("A"), 512, "kenney", T),
    "tree_birchB":        ("birch", lambda: birch_tree("B"), 512, "kenney", T),
    "tree_birchC":        ("birch", lambda: birch_tree("C"), 512, "kenney", T),
    "tree_birchA_far":    ("birch", lambda: birch_tree("A", far=True), 256, "kenney", T),
    "tree_birchB_far":    ("birch", lambda: birch_tree("B", far=True), 256, "kenney", T),
    "tree_birchC_far":    ("birch", lambda: birch_tree("C", far=True), 256, "kenney", T),
    "stump_birch":        ("birch", birch_stump, 256, "kenney", dict(ao=0.45, grad=0.8)),
    "log_stack_birch":    ("birch", birch_log_stack, 256, "kenney", dict(ao=0.4, grad=0.82)),
    "reeds":              ("birch", reeds, 128, "kenney", dict(ao=0.5, grad=0.62, double=True)),
    "lilypads":           ("birch", lilypads, 128, "kenney", dict(ao=0.5, grad=0.9)),
    "veneer_lathe":       ("birch", veneer_lathe, 512, "world", dict(ao=0.25, grad=0.82)),
    "veneer_lathe_log":   ("birch", veneer_lathe_log, 256, "world", dict(ao=0.3, grad=0.9, no_ground=True)),
    "plywood_press":      ("birch", plywood_press, 512, "world", dict(ao=0.18, grad=0.82)),
    "plywood_press_plate": ("birch", plywood_press_plate, 128, "world", dict(ao=0.3, grad=0.9, no_ground=True)),
    "boat_workshop":      ("birch", boat_workshop, 512, "world", dict(ao=0.18, grad=0.82)),
    "riverside_office":   ("birch", riverside_office, 512, "world", dict(ao=0.18, grad=0.82)),
    "barge":              ("birch", barge, 512, "world", dict(ao=0.2, grad=0.8)),
    "barge_landing":      ("birch", barge_landing, 512, "world", dict(ao=0.35, grad=0.85)),
    "flume_straight":     ("birch", flume_straight, 256, "world", dict(ao=0.25, grad=0.82)),
    "flume_chute":        ("birch", flume_chute, 256, "world", dict(ao=0.22, grad=0.82)),
    "flume_end":          ("birch", flume_end, 256, "world", dict(ao=0.25, grad=0.82)),
    "boathouse":          ("birch", boathouse, 512, "world", dict(ao=0.14, grad=0.82)),
    "item_log":           ("items", item_log, 256, "world", dict(ao=0.5, grad=0.85)),
    "item_plank":         ("items", item_plank, 256, "world", dict(ao=0.6, grad=0.85)),
    "item_chair":         ("items", item_chair, 256, "world", dict(ao=0.3, grad=0.85)),
    "item_table":         ("items", item_table, 256, "world", dict(ao=0.4, grad=0.85)),
    "item_bookcase":      ("items", item_bookcase, 256, "world", dict(ao=0.25, grad=0.85)),
    "item_birch_log":     ("items", item_birch_log, 256, "world", dict(ao=0.5, grad=0.85)),
    "item_veneer":        ("items", item_veneer, 128, "world", dict(ao=0.9, grad=0.9)),
    "item_plywood":       ("items", item_plywood, 256, "world", dict(ao=0.8, grad=0.85)),
    "item_canoe":         ("items", item_canoe, 256, "world", dict(ao=0.4, grad=0.85)),
}


def build_m1(name, spec, report):
    folder, builder, tex, units, opt = spec
    reset()
    objs = builder()
    ob = join_meshes(objs, name)
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    mn, mx = bbox(ob)
    height = mx.z - max(mn.z, 0)
    if opt.get("no_ground"):   # floating moving parts: lift far above the AO ground plane while baking
        ob.location.z += 100.0
    img = bake_model(ob, tex, (1, 1, 1), opt.get("grad", 0.8), opt.get("ao", 0.3), max(height, 0.05), name)
    ob.location.z = 0.0
    finish_material(ob, img, name, opt.get("double", False))
    for o in list(bpy.data.objects):
        if o != ob:
            bpy.data.objects.remove(o, do_unlink=True)
    os.makedirs(f"{OUT_M1}/{folder}", exist_ok=True)
    path = f"{OUT_M1}/{folder}/{name}.glb"
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
                              export_image_format="AUTO", export_yup=True)
    mn, mx = bbox(ob)
    report[name] = dict(folder=folder, units=units, tris=tris(ob), tex=tex,
                        size=[round(v, 3) for v in (mx - mn)], min=[round(v, 3) for v in mn], bytes=os.path.getsize(path))
    print("BUILT", name, report[name])


def main_m1():
    only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    rep_path = f"{REPO}/tools/lookdev/build_m1_report.json"
    report = json.load(open(rep_path)) if os.path.exists(rep_path) else {}
    for name, spec in PLAN.items():
        if only and name not in only:
            continue
        build_m1(name, spec, report)
        json.dump(report, open(rep_path, "w"), indent=1)


main_m1()
