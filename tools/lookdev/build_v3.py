"""Build assets/models_v3: import CC0 stylised models (or build simple ones), fit them to the
Kenney model they replace, bake albedo x soft height gradient x ambient occlusion (with a ground
plane, so contact shadows ship in the texture) into one small texture per model, export GLB.

Usage (headless, Cycles CPU):
  /home/mm/.local/bin/blender -b --python tools/lookdev/build_v3.py -- [only_name ...]
Sources are expected under $LOOKDEV_SRC (default /home/mm/MWM/data/lookdev_src), see SOURCES.md.

Every output is ONE mesh with ONE material (World._multimesh uses only the first mesh).
"""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.environ.get("LOOKDEV_SRC", "/home/mm/MWM/data/lookdev_src")
KK = f"{SRC}/kkf/KayKit_Forest_Nature_Pack_1.0_FREE/Assets/gltf"
HEX = f"{SRC}/hexprops"
KEN = f"{REPO}/assets/models"
OUT = f"{REPO}/assets/models_v3"
TEXDIR = f"{REPO}/tools/lookdev/tex"  # baked PNGs for review; the GLBs embed them
SAMPLES = int(os.environ.get("LOOKDEV_SAMPLES", "96"))

# name: (kit, source, fit, tex, options)
#  source: path to a glTF, or "proc:<builder>"
#  fit: height | inside | mean | length   (how to match the Kenney bounding box)
#  options: tint (rgb multiply), maxw (clamp width vs Kenney), rotz (deg), pivot ("source"|"match"),
#           decimate (target tris), ao (distance as fraction of height), grad (bottom brightness)
TREE = dict(maxw=1.35, pivot="source", ao=0.22, grad=0.86, far=170)
# broadleaf chop trees (round-2 review: 1.35x too wide, hid the path + guide arrow): full Kenney height,
# canopy squeezed in X/Y to at most 1.05x the Kenney width, so they stay round but read taller
BROAD = dict(TREE, maxw=None, sqz=1.05)
PLAN = {
    # broadleaf chop trees + border forest
    "tree_default":            ("nature", f"{KK}/Tree_1_A_Color1.gltf", "height", 512, dict(BROAD)),
    "tree_oak":                ("nature", f"{KK}/Tree_1_B_Color1.gltf", "height", 512, dict(BROAD)),
    "tree_detailed":           ("nature", f"{KK}/Tree_3_A_Color1.gltf", "height", 512, dict(BROAD, decimate=700, far=170)),
    "tree_fat":                ("nature", f"{KK}/Tree_3_B_Color1.gltf", "height", 512, dict(BROAD, decimate=700, far=170)),
    "tree_default_dark":       ("nature", f"{KK}/Tree_1_A_Color1.gltf", "height", 512, dict(BROAD, tint=(0.72, 0.84, 0.74))),
    # pines: own procedural stacked soft cones (KayKit's cube-pines read too blocky)
    "tree_pineTallA_detailed": ("nature", "proc:pine:5:0.46:1.53:0.9:0", "height", 512, dict(TREE)),
    "tree_pineTallB_detailed": ("nature", "proc:pine:5:0.46:1.93:0.9:1", "height", 512, dict(TREE)),
    "tree_pineTallC_detailed": ("nature", "proc:pine:4:0.56:1.67:1.0:2", "height", 512, dict(TREE)),
    "tree_pineTallD_detailed": ("nature", "proc:pine:5:0.56:2.08:1.0:3", "height", 512, dict(TREE)),
    "tree_pineRoundA":         ("nature", "proc:pine:3:0.74:1.37:1.6:4", "height", 512, dict(TREE)),
    "tree_pineRoundB":         ("nature", "proc:pine:3:0.64:1.20:1.6:5", "height", 512, dict(TREE)),
    "tree_pineRoundC":         ("nature", "proc:pine:3:0.58:1.25:1.6:6", "height", 512, dict(TREE)),
    "tree_pineDefaultA":       ("nature", "proc:pine:4:0.62:1.55:1.2:7", "height", 512, dict(TREE)),
    "tree_pineDefaultB":       ("nature", "proc:pine:4:0.62:1.55:1.2:8", "height", 512, dict(TREE, tint=(0.86, 0.94, 0.9))),
    # scatter
    "plant_bush":              ("nature", f"{KK}/Bush_1_C_Color1.gltf", "mean", 256, dict(pivot="source", ao=0.35, grad=0.72)),
    "plant_bushDetailed":      ("nature", f"{KK}/Bush_1_E_Color1.gltf", "mean", 256, dict(pivot="source", ao=0.35, grad=0.72, decimate=300)),
    "grass":                   ("nature", f"{KK}/Grass_1_C_Singlesided_Color1.gltf", "mean", 128, dict(pivot="source", ao=0.5, grad=0.62, double=True)),
    "grass_large":             ("nature", f"{KK}/Grass_1_D_Singlesided_Color1.gltf", "mean", 128, dict(pivot="source", ao=0.5, grad=0.62, double=True)),
    "grass_leafs":             ("nature", f"{KK}/Grass_1_B_Singlesided_Color1.gltf", "mean", 128, dict(pivot="source", ao=0.5, grad=0.62, double=True)),
    # rocks (round-2 review: KayKit's stepped hex slabs read boxy and went navy in shadow): own rounded pebbles
    "rock_smallA":             ("nature", "proc:pebbles:1", "mean", 256, dict(pivot="source", ao=0.4, grad=0.7)),
    "rock_smallC":             ("nature", "proc:pebbles:2", "mean", 256, dict(pivot="source", ao=0.4, grad=0.7)),
    "rock_smallD":             ("nature", "proc:pebbles:3", "mean", 256, dict(pivot="source", ao=0.4, grad=0.7)),
    "rock_largeA":             ("nature", "proc:pebbles:4", "mean", 256, dict(pivot="source", ao=0.4, grad=0.7)),
    "flower_redA":             ("nature", "proc:flower_red", "mean", 128, dict(pivot="source", ao=0.5, grad=0.7, double=True)),
    "flower_redC":             ("nature", "proc:flower_red", "mean", 128, dict(pivot="source", ao=0.5, grad=0.7, double=True, tint=(1.0, 0.8, 0.85))),
    "flower_yellowA":          ("nature", "proc:flower_yellow", "mean", 128, dict(pivot="source", ao=0.5, grad=0.7, double=True)),
    "flower_yellowB":          ("nature", "proc:flower_white", "mean", 128, dict(pivot="source", ao=0.5, grad=0.7, double=True)),
    "mushroom_redGroup":       ("nature", "proc:mushrooms_red", "mean", 128, dict(pivot="source", ao=0.5, grad=0.75)),
    "mushroom_tanGroup":       ("nature", "proc:mushrooms_tan", "mean", 128, dict(pivot="source", ao=0.5, grad=0.75)),
    "stump_roundDetailed":     ("nature", "proc:stump", "mean", 256, dict(pivot="source", ao=0.45, grad=0.8)),
    # starting-yard props
    "log_stackLarge":          ("nature", "proc:log_stack", "mean", 256, dict(pivot="match", ao=0.4, grad=0.82)),
    "campfire_logs":           ("nature", "proc:campfire", "length", 256, dict(pivot="match", ao=0.5, grad=0.85)),
    "fence_simple":            ("nature", "proc:fence", "length", 256, dict(pivot="match", ao=0.35, grad=0.82)),
    "barrel":                  ("survival", f"{HEX}/barrel.gltf", "mean", 256, dict(pivot="match", ao=0.35, grad=0.8)),
    "box-large":               ("survival", "proc:crate", "inside", 256, dict(pivot="match", ao=0.35, grad=0.82)),
    "signpost":                ("survival", "proc:signpost", "height", 256, dict(pivot="match", ao=0.35, grad=0.82)),
}

# ------------------------------------------------------------------ helpers

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    return sc


def import_gltf(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def join_meshes(objs, name):
    meshes = [o for o in objs if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    # bake parent transforms into the mesh
    for o in meshes:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    if len(meshes) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    keep = ob.name
    for o in list(bpy.data.objects):
        if o.name != keep and o.type != "MESH" and o.name not in ("ken",):
            try:
                bpy.data.objects.remove(o, do_unlink=True)
            except ReferenceError:
                pass
    ob.name = name
    ob.data.name = name
    return ob


def bbox(ob):
    vs = [ob.matrix_world @ v.co for v in ob.data.vertices]
    mn = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    mx = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    return mn, mx


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def kenney_box(kit, name):
    objs = import_gltf(f"{KEN}/{kit}/{name}.glb")
    ob = join_meshes(objs, "ken")
    mn, mx = bbox(ob)
    bpy.data.objects.remove(ob, do_unlink=True)
    return mn, mx


def flat_mat(name, rgb, kind="plain"):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1)
    m["proc"] = kind
    return m


def srgb(c):
    """hex-ish sRGB triple (0..1) to linear for Blender colour sockets"""
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

# ------------------------------------------------------------------ procedural builders (own work, CC0)

WOOD_SIDE = srgb((0.62, 0.40, 0.24))
WOOD_END = srgb((0.93, 0.76, 0.52))
LEAF = srgb((0.40, 0.72, 0.30))


def _add(prim, **kw):
    getattr(bpy.ops.mesh, prim)(**kw)
    return bpy.context.object


def _smooth(ob):
    for p in ob.data.polygons:
        p.use_smooth = True


def _assign(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)


def _log(r, length, loc, rot, side, end, verts=10, seg=2):
    """Rounded log lying along its local Z: side material on the barrel, end material on the caps."""
    ob = _add("primitive_cylinder_add", vertices=verts, radius=r, depth=length, location=(0, 0, 0))
    ob.data.materials.append(side)
    ob.data.materials.append(end)
    for p in ob.data.polygons:
        p.material_index = 1 if abs(p.normal.z) > 0.9 else 0
        p.use_smooth = abs(p.normal.z) < 0.9
    bev = ob.modifiers.new("b", "BEVEL"); bev.width = r * 0.18; bev.segments = seg; bev.limit_method = "ANGLE"
    bpy.ops.object.modifier_apply(modifier="b")
    ob.rotation_euler = rot
    ob.location = loc
    return ob


def proc_flower(petal):
    pm = flat_mat("petal", srgb(petal))
    cm = flat_mat("centre", srgb((0.98, 0.78, 0.22)) if petal != (0.98, 0.84, 0.25) else srgb((0.72, 0.42, 0.16)))
    lm = flat_mat("leaf", LEAF)
    parts = []
    h = 0.24
    st = _add("primitive_cylinder_add", vertices=5, radius=0.012, depth=h, location=(0, 0, h / 2)); _assign(st, lm); parts.append(st)
    # petal disc: 5 rounded lobes, slightly cupped
    bm = bmesh.new()
    c = bm.verts.new((0, 0, h + 0.012))
    ring = []
    n = 20
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 0.055 + 0.03 * math.cos(5 * a)
        ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), h + 0.02 * (r / 0.085))))
    for i in range(n):
        bm.faces.new((c, ring[i], ring[(i + 1) % n]))
    me = bpy.data.meshes.new("petals"); bm.to_mesh(me); bm.free()
    pd = bpy.data.objects.new("petals", me); bpy.context.collection.objects.link(pd); _assign(pd, pm); _smooth(pd); parts.append(pd)
    ce = _add("primitive_uv_sphere_add", segments=8, ring_count=4, radius=0.024, location=(0, 0, h + 0.02)); ce.scale.z = 0.6; _assign(ce, cm); _smooth(ce); parts.append(ce)
    for s in (-1, 1):
        lf = _add("primitive_uv_sphere_add", segments=6, ring_count=3, radius=0.05, location=(s * 0.04, 0, 0.07))
        lf.scale = (1.0, 0.35, 0.12); lf.rotation_euler = (0, s * -0.5, 0); _assign(lf, lm); _smooth(lf); parts.append(lf)
    return parts


def proc_mushrooms(cap):
    capm = flat_mat("cap", srgb(cap), "spots" if cap[1] < 0.5 else "plain")
    stm = flat_mat("stem", srgb((0.95, 0.91, 0.8)))
    parts = []
    for (x, y, s) in ((0, 0, 1.0), (0.09, 0.05, 0.7), (-0.06, 0.08, 0.55)):
        st = _add("primitive_cylinder_add", vertices=8, radius=0.025 * s, depth=0.12 * s, location=(x, y, 0.06 * s)); _assign(st, stm); _smooth(st); parts.append(st)
        cp = _add("primitive_uv_sphere_add", segments=10, ring_count=5, radius=0.07 * s, location=(x, y, 0.11 * s))
        bm = bmesh.new(); bm.from_mesh(cp.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.02 * s], context="VERTS")
        bm.to_mesh(cp.data); bm.free()
        cp.scale.z = 0.75; _assign(cp, capm); _smooth(cp); parts.append(cp)
    return parts


def proc_stump():
    side = flat_mat("bark", WOOD_SIDE, "bark")
    end = flat_mat("rings", WOOD_END, "rings")
    parts = []
    ob = _log(0.16, 0.2, (0, 0, 0.1), (0, 0, 0), side, end, verts=14)
    # drop the bottom cap below ground so it never shows
    parts.append(ob)
    for i in range(4):
        a = i * math.pi / 2 + 0.4
        rt = _add("primitive_uv_sphere_add", segments=8, ring_count=4, radius=0.07, location=(0.15 * math.cos(a), 0.15 * math.sin(a), 0.02))
        rt.scale = (1.4, 0.7, 0.6); rt.rotation_euler = (0, 0, a); _assign(rt, side); _smooth(rt); parts.append(rt)
    return parts


def proc_log_stack():
    side = flat_mat("bark", WOOD_SIDE, "bark")
    end = flat_mat("rings", WOOD_END, "rings")
    parts = []
    r = 0.075
    rows = [(4, 0.0), (3, 1.0), (2, 2.0)]
    for count, row in rows:
        for i in range(count):
            x = (i - (count - 1) / 2) * 2 * r * 1.02
            z = r + row * r * 1.75
            parts.append(_log(r * (0.96 + 0.04 * ((i * 7) % 3)), 0.66, (x, 0, z), (math.pi / 2, 0, 0), side, end, verts=9, seg=1))
    return parts


def proc_campfire():
    side = flat_mat("bark", srgb((0.45, 0.28, 0.17)), "bark")
    end = flat_mat("char", srgb((0.25, 0.16, 0.1)))
    stone = flat_mat("stone", srgb((0.62, 0.64, 0.66)))
    ember = flat_mat("ember", srgb((1.0, 0.55, 0.15)))
    parts = []
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.3
        lg = _log(0.02, 0.19, (0.045 * math.cos(a), 0.045 * math.sin(a), 0.075), (0, -math.radians(32), a), side, end, verts=7, seg=1)
        parts.append(lg)
    for i in range(8):
        a = i * 2 * math.pi / 8
        s = _add("primitive_uv_sphere_add", segments=6, ring_count=3, radius=0.03, location=(0.115 * math.cos(a), 0.115 * math.sin(a), 0.012))
        s.scale = (1.2, 1.0, 0.6); _assign(s, stone); _smooth(s); parts.append(s)
    e = _add("primitive_uv_sphere_add", segments=8, ring_count=4, radius=0.045, location=(0, 0, 0.0)); e.scale.z = 0.35; _assign(e, ember); _smooth(e); parts.append(e)
    return parts


def proc_signpost():
    side = flat_mat("wood", srgb((0.86, 0.62, 0.38)), "planks")
    dark = flat_mat("post", srgb((0.66, 0.44, 0.27)), "bark")
    parts = []
    post = _add("primitive_cylinder_add", vertices=10, radius=0.026, depth=0.46, location=(0, 0, 0.23)); _assign(post, dark); _smooth(post); parts.append(post)
    # arrow board: extruded pentagon, bevelled
    bm = bmesh.new()
    pts = [(-0.1, -0.05), (0.07, -0.05), (0.115, 0.0), (0.07, 0.05), (-0.1, 0.05)]
    vs = [bm.verts.new((x, 0, z)) for x, z in pts]
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, 0.024, 0), verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)])
    me = bpy.data.meshes.new("board"); bm.to_mesh(me); bm.free()
    bd = bpy.data.objects.new("board", me); bpy.context.collection.objects.link(bd)
    bpy.context.view_layer.objects.active = bd
    bev = bd.modifiers.new("b", "BEVEL"); bev.width = 0.008; bev.segments = 3
    bpy.ops.object.modifier_apply(modifier="b")
    bd.location = (0.035, -0.037, 0.37); _assign(bd, side); _smooth(bd); parts.append(bd)
    return parts


def proc_pine(tiers, w, h, roundness, seed):
    import random
    rnd = random.Random(seed)
    leaf = flat_mat("pine", srgb((0.25, 0.58, 0.33)))
    bark = flat_mat("bark", srgb((0.50, 0.32, 0.20)), "bark")
    R = w / 2
    parts = []
    tr = _add("primitive_cylinder_add", vertices=8, radius=R * 0.13, depth=h * 0.35, location=(0, 0, h * 0.175)); _assign(tr, bark); _smooth(tr); parts.append(tr)
    z0 = h * 0.16
    th = (h - z0) / (1 + (tiers - 1) * 0.62)
    for i in range(tiers):
        f = i / max(1, tiers - 1)
        r = R * (1.0 - 0.58 * f) * rnd.uniform(0.94, 1.04)
        zb = z0 + i * th * 0.62
        top = i == tiers - 1
        c = _add("primitive_cone_add", vertices=14, radius1=r, radius2=(r * 0.12 if top else 0.0), depth=th, location=(0, 0, zb + th / 2))
        c.rotation_euler.z = rnd.uniform(0, 1)
        bev = c.modifiers.new("b", "BEVEL"); bev.limit_method = "ANGLE"; bev.angle_limit = math.radians(40)
        bev.width = min(r * 0.22 * roundness, th * 0.3); bev.segments = 3
        bpy.ops.object.modifier_apply(modifier="b")
        # soft drooping rim: pull the rim ring slightly down
        for v in c.data.vertices:
            if v.co.z < -th * 0.35:
                v.co.z -= th * 0.06 * roundness
        _assign(c, leaf); _smooth(c); parts.append(c)
    return parts


def proc_fence():
    wood = flat_mat("rail", srgb((0.80, 0.56, 0.34)), "planks")
    post = flat_mat("post", srgb((0.62, 0.41, 0.25)), "bark")
    parts = []
    for x in (-0.46, 0.46):
        p = _add("primitive_cylinder_add", vertices=10, radius=0.035, depth=0.34, location=(x, 0, 0.17))
        bev = p.modifiers.new("b", "BEVEL"); bev.width = 0.015; bev.segments = 2; bev.limit_method = "ANGLE"
        bpy.ops.object.modifier_apply(modifier="b"); _assign(p, post); _smooth(p); parts.append(p)
    for z in (0.12, 0.25):
        r = _add("primitive_cube_add", size=1, location=(0, 0.005, z)); r.scale = (0.98, 0.03, 0.06)
        bpy.ops.object.transform_apply(scale=True)
        bev = r.modifiers.new("b", "BEVEL"); bev.width = 0.012; bev.segments = 2
        bpy.ops.object.modifier_apply(modifier="b"); _assign(r, wood); parts.append(r)
    return parts


def proc_crate():
    board = flat_mat("board", srgb((0.86, 0.64, 0.40)), "planks")
    frame = flat_mat("frame", srgb((0.60, 0.40, 0.24)), "bark")
    parts = []
    b = _add("primitive_cube_add", size=1, location=(0, 0, 0.12)); b.scale = (0.23, 0.48, 0.23)
    bpy.ops.object.transform_apply(scale=True)
    bev = b.modifiers.new("b", "BEVEL"); bev.width = 0.02; bev.segments = 3
    bpy.ops.object.modifier_apply(modifier="b"); _assign(b, board); _smooth(b); parts.append(b)
    # darker battens around both ends and the middle
    for y in (-0.225, 0.0, 0.225):
        f = _add("primitive_cube_add", size=1, location=(0, y, 0.12)); f.scale = (0.245, 0.035, 0.245)
        bpy.ops.object.transform_apply(scale=True)
        bm = bmesh.new(); bm.from_mesh(f.data)
        inner = [fc for fc in bm.faces if abs(fc.normal.y) > 0.9]
        bmesh.ops.delete(bm, geom=inner, context="FACES"); bm.to_mesh(f.data); bm.free()
        bev = f.modifiers.new("b", "BEVEL"); bev.width = 0.01; bev.segments = 2
        bpy.ops.object.modifier_apply(modifier="b"); _assign(f, frame); parts.append(f)
    return parts


STONE = srgb((0.60, 0.555, 0.50))  # warm grey-brown: stays grey, not navy, under the blue sky ambient


def _pebble(r, squash, loc, seed, rotz=0.0):
    """Soft rounded stone: subdivided icosphere, low-frequency noise bulge, flattened base, no hard edges."""
    from mathutils import noise
    ob = _add("primitive_ico_sphere_add", subdivisions=3, radius=r, location=(0, 0, 0))
    off = Vector((seed * 3.7, seed * 1.3, seed * 5.1))
    for v in ob.data.vertices:
        n = v.co.normalized()
        v.co *= 1.0 + 0.16 * noise.noise(n * 1.3 + off) + 0.05 * noise.noise(n * 3.0 + off)
        v.co.x *= 1.0 + 0.12 * math.sin(seed)
        v.co.z *= squash
        floor = -r * squash * 0.35
        if v.co.z < floor:  # flatten the underside so it sits on the ground
            v.co.z = floor + (v.co.z - floor) * 0.15
    ob.rotation_euler.z = rotz
    ob.location = Vector(loc) + Vector((0, 0, r * squash * 0.3))
    dec = ob.modifiers.new("d", "DECIMATE"); dec.ratio = 0.45
    bpy.ops.object.modifier_apply(modifier="d")
    return ob


def proc_pebbles(kind):
    m = flat_mat("stone", STONE)
    spec = {1: [(0.18, 0.55, (0, 0, 0), 1)],
            2: [(0.16, 0.5, (0.03, 0, 0), 2), (0.08, 0.6, (-0.15, 0.06, 0), 5)],
            3: [(0.18, 0.8, (0, 0, 0), 3), (0.085, 0.6, (0.17, -0.07, 0), 6)],
            4: [(0.3, 0.55, (0, 0.05, 0), 4), (0.2, 0.6, (0.3, -0.18, 0), 7), (0.12, 0.6, (-0.27, -0.2, 0), 8)]}[kind]
    parts = []
    for r, sq, loc, seed in spec:
        p = _pebble(r, sq, loc, seed, rotz=seed * 0.9); _assign(p, m); _smooth(p); parts.append(p)
    return parts


PROC = {
    "flower_red": lambda: proc_flower((0.93, 0.33, 0.30)),
    "flower_yellow": lambda: proc_flower((0.98, 0.84, 0.25)),
    "flower_white": lambda: proc_flower((0.97, 0.95, 0.9)),
    "mushrooms_red": lambda: proc_mushrooms((0.86, 0.26, 0.2)),
    "mushrooms_tan": lambda: proc_mushrooms((0.82, 0.62, 0.4)),
    "stump": proc_stump,
    "log_stack": proc_log_stack,
    "campfire": proc_campfire,
    "signpost": proc_signpost,
    "fence": proc_fence,
    "crate": proc_crate,
}

# ------------------------------------------------------------------ bake


def base_color_socket(nt, mat, src_uv):
    """Return an output socket giving this material's albedo (image via source UV, or constant, or a procedural pattern)."""
    nodes, links = nt.nodes, nt.links
    bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    kind = mat.get("proc", "")
    if bsdf is not None and bsdf.inputs["Base Color"].is_linked:
        src = bsdf.inputs["Base Color"].links[0].from_node
        if src.type == "TEX_IMAGE":
            uv = nodes.new("ShaderNodeUVMap"); uv.uv_map = src_uv
            links.new(uv.outputs["UV"], src.inputs["Vector"])
            return src.outputs["Color"]
        return bsdf.inputs["Base Color"].links[0].from_socket
    col = bsdf.inputs["Base Color"].default_value if bsdf else (0.8, 0.8, 0.8, 1)
    rgb = nodes.new("ShaderNodeRGB"); rgb.outputs[0].default_value = col
    if kind in ("rings", "bark", "planks", "spots"):
        tc = nodes.new("ShaderNodeTexCoord")
        mix = nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        links.new(rgb.outputs[0], mix.inputs["A"])
        ramp = nodes.new("ShaderNodeValToRGB")
        if kind == "rings":
            w = nodes.new("ShaderNodeTexWave"); w.wave_type = "RINGS"; w.rings_direction = "Z"
            w.inputs["Scale"].default_value = 9.0; w.inputs["Distortion"].default_value = 3.0
            links.new(tc.outputs["Object"], w.inputs["Vector"]); links.new(w.outputs["Fac"], ramp.inputs["Fac"])
            ramp.color_ramp.elements[0].color = (0.78, 0.72, 0.66, 1)
        elif kind == "spots":
            w = nodes.new("ShaderNodeTexVoronoi"); w.inputs["Scale"].default_value = 11.0
            links.new(tc.outputs["Object"], w.inputs["Vector"]); links.new(w.outputs["Distance"], ramp.inputs["Fac"])
            ramp.color_ramp.elements[0].position = 0.3; ramp.color_ramp.elements[1].position = 0.33
            ramp.color_ramp.elements[0].color = (4.0, 3.6, 3.4, 1)  # multiply red towards cream = white spots
        else:  # bark / planks: soft vertical streaks
            w = nodes.new("ShaderNodeTexNoise"); w.inputs["Scale"].default_value = 6.0
            mp = nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (6.0, 6.0, 0.6) if kind == "bark" else (0.5, 8.0, 8.0)
            links.new(tc.outputs["Object"], mp.inputs["Vector"]); links.new(mp.outputs[0], w.inputs["Vector"])
            links.new(w.outputs["Fac"], ramp.inputs["Fac"])
            ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[0].color = (0.8, 0.8, 0.8, 1)
            ramp.color_ramp.elements[1].position = 0.65
        links.new(ramp.outputs["Color"], mix.inputs["B"])
        return mix.outputs["Result"]
    return rgb.outputs[0]


def bake_model(ob, tex, tint, grad_lo, ao_frac, height, name):
    sc = bpy.context.scene
    src_uv = ob.data.uv_layers[0].name if ob.data.uv_layers else None
    if src_uv is None:
        ob.data.uv_layers.new(name="src"); src_uv = "src"
    bake_uv = ob.data.uv_layers.new(name="bake")
    ob.data.uv_layers.active = bake_uv
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.03, area_weight=0.6)
    bpy.ops.object.mode_set(mode="OBJECT")

    img_a = bpy.data.images.new(name + "_alb", tex, tex, alpha=False)
    img_o = bpy.data.images.new(name + "_ao", tex, tex, alpha=False); img_o.colorspace_settings.name = "Non-Color"
    mats = [s.material for s in ob.material_slots if s.material]
    for m in mats:
        nt = m.node_tree; nodes, links = nt.nodes, nt.links
        base = base_color_socket(nt, m, src_uv)
        tc = nodes.new("ShaderNodeTexCoord"); sep = nodes.new("ShaderNodeSeparateXYZ")
        links.new(tc.outputs["Object"], sep.inputs[0])
        mr = nodes.new("ShaderNodeMapRange"); mr.clamp = True
        mr.inputs["From Min"].default_value = 0.0; mr.inputs["From Max"].default_value = height
        mr.inputs["To Min"].default_value = grad_lo; mr.inputs["To Max"].default_value = 1.0
        links.new(sep.outputs["Z"], mr.inputs["Value"])
        m1 = nodes.new("ShaderNodeMix"); m1.data_type = "RGBA"; m1.blend_type = "MULTIPLY"; m1.inputs["Factor"].default_value = 1
        links.new(base, m1.inputs["A"]); m1.inputs["B"].default_value = (*tint, 1)
        m2 = nodes.new("ShaderNodeMix"); m2.data_type = "RGBA"; m2.blend_type = "MULTIPLY"; m2.inputs["Factor"].default_value = 1
        links.new(m1.outputs["Result"], m2.inputs["A"])
        cmb = nodes.new("ShaderNodeCombineColor")
        for k in ("Red", "Green", "Blue"):
            links.new(mr.outputs["Result"], cmb.inputs[k])
        links.new(cmb.outputs[0], m2.inputs["B"])
        em = nodes.new("ShaderNodeEmission"); links.new(m2.outputs["Result"], em.inputs["Color"])
        outn = next(n for n in nodes if n.type == "OUTPUT_MATERIAL")
        links.new(em.outputs[0], outn.inputs["Surface"])
        t = nodes.new("ShaderNodeTexImage"); t.image = img_a; t.name = "BAKE_TARGET"
        nodes.active = t
    sc.cycles.samples = 1
    sc.render.bake.margin = 6
    bpy.ops.object.bake(type="EMIT", margin=6)

    # AO pass with a ground plane so the base gets a soft contact shadow
    bpy.ops.mesh.primitive_plane_add(size=max(40, height * 20), location=(0, 0, -0.0005))
    ground = bpy.context.object
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    for m in mats:
        t = m.node_tree.nodes["BAKE_TARGET"]; t.image = img_o; m.node_tree.nodes.active = t
    if sc.world is None:
        sc.world = bpy.data.worlds.new("w")
    sc.world.light_settings.distance = max(0.02, height * ao_frac)
    sc.cycles.samples = SAMPLES
    bpy.ops.object.bake(type="AO", margin=6)
    bpy.data.objects.remove(ground, do_unlink=True)

    a = np.array(img_a.pixels[:], dtype=np.float32).reshape(tex, tex, 4)
    o = np.array(img_o.pixels[:], dtype=np.float32).reshape(tex, tex, 4)[..., :1]
    lin = np.where(a[..., :3] <= 0.04045, a[..., :3] / 12.92, ((a[..., :3] + 0.055) / 1.055) ** 2.4)
    ao = 0.42 + 0.58 * np.clip(o, 0, 1) ** 0.8  # crevices keep ~45% of their colour, never black
    lin = lin * ao
    out = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(np.clip(lin, 0, None), 1 / 2.4) - 0.055)
    final = bpy.data.images.new(name, tex, tex, alpha=False)
    px = np.concatenate([np.clip(out, 0, 1), np.ones((tex, tex, 1), np.float32)], axis=2)
    final.pixels[:] = px.ravel()
    final.file_format = "PNG"
    final.filepath_raw = f"{TEXDIR}/{name}.png"
    os.makedirs(TEXDIR, exist_ok=True)
    final.save()
    return final


def finish_material(ob, img, name, double):
    # drop source UVs, keep the bake UV as the only map
    for uv in list(ob.data.uv_layers):
        if uv.name != "bake":
            ob.data.uv_layers.remove(uv)
    ob.data.uv_layers[0].name = "UVMap"
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.use_backface_culling = not double
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    b.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.25
    ob.data.materials.clear()
    ob.data.materials.append(m)


# ------------------------------------------------------------------ main


def build(name, spec, report):
    kit, source, fit, tex, opt = spec
    reset()
    kmn, kmx = kenney_box(kit, name[:-4] if name.endswith("_far") else name)
    ksize = kmx - kmn
    if source.startswith("proc:"):
        key, *args = source[5:].split(":")
        if key == "pine":
            objs = proc_pine(int(args[0]), *map(float, args[1:4]), int(args[4]))
        elif key == "pebbles":
            objs = proc_pebbles(int(args[0]))
        else:
            objs = PROC[key]()
        src_label = source
    else:
        objs = import_gltf(source)
        src_label = os.path.basename(source)
    ob = join_meshes(objs, name)
    if opt.get("rotz"):
        ob.data.transform(Matrix.Rotation(math.radians(opt["rotz"]), 4, "Z"))
    if opt.get("zs"):
        ob.scale.z = opt["zs"]
        bpy.ops.object.transform_apply(scale=True)
    if opt.get("decimate") and tris(ob) > opt["decimate"]:
        d = ob.modifiers.new("dec", "DECIMATE"); d.ratio = opt["decimate"] / tris(ob)
        bpy.ops.object.modifier_apply(modifier="dec")
        # decimation leaves the source custom normals twisted (dark slivers): rebuild smooth normals
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
        bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.shade_smooth()
    mn, mx = bbox(ob)
    size = mx - mn
    kw, nw = max(ksize.x, ksize.y), max(size.x, size.y)
    hr, wr = ksize.z / size.z, kw / nw
    s = {"height": hr, "inside": min(hr, wr), "mean": math.sqrt(hr * wr),
         "length": (ksize.x / size.x) if ksize.x >= ksize.y else (ksize.y / size.y)}[fit]
    if opt.get("maxw"):
        s = min(s, opt["maxw"] * wr)
    sxy = min(s, opt["sqz"] * wr) if opt.get("sqz") else s
    ob.scale = (sxy, sxy, s)
    bpy.ops.object.transform_apply(scale=True)
    mn, mx = bbox(ob)
    if opt.get("pivot") == "match":
        kc = (kmn + kmx) / 2; nc = (mn + mx) / 2
        ob.location = (kc.x - nc.x, kc.y - nc.y, -0.003 - mn.z)  # Kenney sinks 0.05 below 0; we sit on the ground
        bpy.ops.object.transform_apply(location=True)
    mn, mx = bbox(ob)
    height = mx.z - max(mn.z, 0)
    img = bake_model(ob, tex, opt.get("tint", (1, 1, 1)), opt.get("grad", 0.8), opt.get("ao", 0.3), height, name)
    finish_material(ob, img, name, opt.get("double", False))
    # clean everything but the model, pack the texture into the GLB
    for o in list(bpy.data.objects):
        if o != ob:
            bpy.data.objects.remove(o, do_unlink=True)
    os.makedirs(f"{OUT}/{kit}", exist_ok=True)
    path = f"{OUT}/{kit}/{name}.glb"
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
                              export_image_format="AUTO", export_yup=True)
    full_tris = tris(ob)
    far = None
    mn, mx = bbox(ob)
    report[name] = dict(far_tris=far, kit=kit, source=src_label, tris=full_tris, tex=tex,
                        size=[round(v, 3) for v in (mx - mn)], kenney_size=[round(v, 3) for v in ksize],
                        min=[round(v, 3) for v in mn], kenney_min=[round(v, 3) for v in kmn],
                        bytes=os.path.getsize(path))
    print("BUILT", name, report[name])


# Far/border variants: decimated BEFORE unwrapping and baked on their own (decimating a baked mesh tears the UVs).
for _n, (_k, _src, _fit, _tex, _opt) in list(PLAN.items()):
    if _opt.get("far"):
        _o = dict(_opt); _o["decimate"] = _o.pop("far")
        # Tree_3's flat disc canopy folds when collapsed to 170 tris; its border stand-in is the round Tree_1 blob
        _src = _src.replace("Tree_3_A", "Tree_1_B").replace("Tree_3_B", "Tree_1_A")
        PLAN[_n + "_far"] = (_k, _src, _fit, 256, _o)


def main():
    only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    rep_path = f"{REPO}/tools/lookdev/build_report.json"
    report = json.load(open(rep_path)) if os.path.exists(rep_path) else {}
    for name, spec in PLAN.items():
        if only and name not in only:
            continue
        build(name, spec, report)
        json.dump(report, open(rep_path, "w"), indent=1)


main()
