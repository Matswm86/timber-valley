"""Build assets/models_v3/chars: KayKit Adventurers (CC0) characters, rounder replacements for the
Kenney blocky characters. Same 12 file names as assets/models/chars/.

Per character: drop weapons, hats, helmets and capes; recolour the KayKit gradient atlas per variant
(workwear colours); join the body into ONE skinned mesh, decimate to <= BODY_TRIS; bake albedo x soft
height gradient x ambient occlusion from the full-res source (selected-to-active) into one 512 px
texture; add the KayKit 1H axe (and a golden "upgraded" copy) as meshes parented to bone handslot.r;
author a one-frame "Carry_Pose" (arms forward) for the carry overlay; keep only the animations the
game needs; scale the rig so the character is Kenney height; export GLB.

Usage: /home/mm/.local/bin/blender -b --python tools/lookdev/build_chars.py -- [only_name ...]
Source: $LOOKDEV_SRC/KayKit-Character-Pack-Adventures-1.0 (git clone of
https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0).
"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.environ.get("LOOKDEV_SRC", "/home/mm/MWM/data/lookdev_src")
KK = f"{SRC}/KayKit-Character-Pack-Adventures-1.0/addons/kaykit_character_pack_adventures"
OUT = f"{REPO}/assets/models_v3/chars"
TEXDIR = f"{REPO}/tools/lookdev/tex/chars"
SAMPLES = int(os.environ.get("LOOKDEV_SAMPLES", "64"))
TEX = 512
BODY_TRIS = 2700
AXE_TRIS = 150
AXE_SCALE = 0.75     # KayKit's 1H axe is oversized next to a lumber-game prop; scaled about the grip
TARGET_H = 0.80      # rest height in file units (Kenney: 0.676, but boxier; 0.80 gives the same on-screen presence)
KEEP_PARTS = ("_Body", "_Head", "_Arm", "_Leg")
ANIMS = ["Idle", "Walking_A", "Running_A", "1H_Melee_Attack_Chop", "1H_Melee_Attack_Slice_Horizontal",
         "PickUp", "Interact", "Use_Item", "Cheer"]

# sRGB hex workwear palette (bright against the grass, no greens)
RED, RED_D = "#d4483b", "#a8342c"
MUSTARD, MUSTARD_D = "#e3a93b", "#c98f2c"
BLUE, SKY = "#3f78b8", "#6aa6dc"
ORANGE, ORANGE_D = "#e27a33", "#c0602a"
TAN, CREAM, PINK, TEAL = "#c79a62", "#efe4cf", "#e27d8c", "#2f8f86"
DENIM, BROWN, DKBROWN, SLATE = "#46628f", "#6b4a33", "#4a3326", "#3a3f4a"
GINGER, BLOND, BLACKH = "#c56a2f", "#e6c27a", "#2e2622"

# name: (base model, {(row, col) atlas cell: colour}, role note)
PLAN = {
    # player (2026-10-01): was the bald ginger Barbarian; now the friendliest candidate (= character-player-alt-2 spec)
    "character-male-e":   ("Knight", {(0, 1): BROWN, (0, 7): DKBROWN, (1, 7): DENIM, (0, 3): DKBROWN, (0, 6): BROWN},
                           "player", dict(face=True, beanie="#e8a33a", plaid=dict(cells=[(0, 3)], z_min=0.48, colours=("#c8342b", "#26201f")))),
    "character-male-a":   ("Barbarian", {(1, 0): MUSTARD, (1, 1): MUSTARD_D, (0, 1): DKBROWN, (2, 3): BROWN}, "lumberjack"),
    "character-male-b":   ("Knight", {(0, 3): TAN, (0, 7): BROWN, (1, 7): DKBROWN, (0, 1): BROWN}, "hauler"),
    "character-male-c":   ("Knight", {(0, 3): BLUE, (0, 7): DENIM, (1, 7): SLATE}, "lumberjack"),
    "character-male-d":   ("Mage", {(1, 0): ORANGE, (1, 7): DKBROWN}, "lumberjack"),
    "character-male-f":   ("Mage", {(1, 0): TEAL, (1, 7): SLATE, (0, 1): BROWN}, "customer"),
    "character-female-a": ("Rogue", {(1, 0): TEAL, (1, 1): CREAM}, "lumberjack"),   # was red: only the player wears red now
    "character-female-b": ("Rogue", {(1, 0): "#c0606e", (1, 1): PINK, (0, 1): BLOND}, "hauler"),
    "character-female-c": ("Rogue_Hooded", {(1, 0): ORANGE_D, (1, 1): ORANGE}, "hauler"),
    "character-female-d": ("Rogue", {(1, 0): BLUE, (1, 1): SKY, (0, 1): DKBROWN}, "hauler"),
    "character-female-e": ("Rogue", {(1, 0): BROWN, (1, 1): CREAM, (0, 1): BLACKH}, "cashier"),
    "character-female-f": ("Rogue_Hooded", {(1, 0): DENIM, (1, 1): CREAM}, "customer"),   # hood was mustard: too close to the player cap
}
# Player candidates (2026-10-01, Mats: the bald ginger Barbarian reads "grumpy"). 4th element = options:
#   face: friendlier brows (inner ends raised, thinner) + a dark smile;  plaid: procedural red/black check on the
#   listed shirt cells above z_min (rest pose);  beanie: knit cap (colour) modelled on the head bone.
PLAID_RED = ("#c8342b", "#26201f")
PLAYER_ALTS = {
    "character-player-alt-1": ("Knight", {(0, 1): DKBROWN, (0, 7): DKBROWN, (1, 7): DENIM, (0, 3): DKBROWN, (0, 6): BROWN},
                               "player", dict(face=True, plaid=dict(cells=[(0, 3)], z_min=0.48, colours=PLAID_RED))),
    # alt-2 shipped as character-male-e (see PLAN); kept here so all candidates rebuild
    "character-player-alt-2": ("Knight", {(0, 1): BROWN, (0, 7): DKBROWN, (1, 7): DENIM, (0, 3): DKBROWN, (0, 6): BROWN},
                               "player", dict(face=True, beanie="#e8a33a", plaid=dict(cells=[(0, 3)], z_min=0.48, colours=PLAID_RED))),
    "character-player-alt-3": ("Mage", {(0, 1): "#3b2a22", (1, 7): DENIM, (2, 3): DKBROWN, (0, 3): BROWN, (0, 5): DKBROWN},
                               "player", dict(face=True, plaid=dict(cells=[(1, 0)], z_min=0.5, colours=PLAID_RED))),
    "character-player-alt-4": ("Barbarian", {(0, 1): DKBROWN, (2, 3): DENIM, (1, 7): DENIM},
                               "player", dict(face=True, beanie="#c8342b", plaid=dict(cells=[(1, 0), (1, 1)], z_min=0.5, colours=("#e9b23f", "#3a2a22")))),
}
AXE_GOLD = {(1, 3): "#f2c14e", (1, 5): "#8a4b2a"}  # upgraded axe: gold head, dark handle


def hex_rgb(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


def recolour(img, cells, name):
    """Copy of a KayKit 8x4 gradient atlas with some cells re-tinted, keeping each cell's luminance ramp."""
    w, h = img.size
    px = np.array(img.pixels[:], np.float32).reshape(h, w, 4)[::-1].copy()  # top row first
    cw, ch = w // 8, h // 4
    for (r, c), col in cells.items():
        cell = px[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw, :3]
        lum = cell @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        ref = float(np.median(lum[ch // 3: 2 * ch // 3, cw // 8: cw // 2]))
        px[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw, :3] = np.clip(hex_rgb(col) * (lum / max(ref, 1e-3))[..., None], 0, 1)
    new = bpy.data.images.new(name, w, h, alpha=True)
    new.colorspace_settings.name = img.colorspace_settings.name  # before pixels: changing it regenerates the buffer
    new.pixels[:] = px[::-1].ravel()
    if os.environ.get("LOOKDEV_DEBUG"):
        os.makedirs(TEXDIR, exist_ok=True)
        new.file_format = "PNG"; new.filepath_raw = f"{TEXDIR}/_{name}.png"; new.save()
    return new


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def select_only(objs, active=None):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]


def _m(nodes, links, op, a, b=None, val=None):
    n = nodes.new("ShaderNodeMath"); n.operation = op
    for i, x in enumerate((a, b)):
        if x is None:
            continue
        if isinstance(x, (int, float)):
            n.inputs[i].default_value = x
        else:
            links.new(x, n.inputs[i])
    return n.outputs[0]


def plaid_socket(nodes, links, colour_in, plaid):
    """Mix a red/black check (rest-pose world X/Z, period 1/freq) over the given atlas cells above z_min."""
    uvn = nodes.new("ShaderNodeUVMap"); sep = nodes.new("ShaderNodeSeparateXYZ"); links.new(uvn.outputs[0], sep.inputs[0])
    col = _m(nodes, links, "FLOOR", _m(nodes, links, "MULTIPLY", sep.outputs["X"], 8.0))
    row = _m(nodes, links, "FLOOR", _m(nodes, links, "MULTIPLY", _m(nodes, links, "SUBTRACT", 1.0, sep.outputs["Y"]), 4.0))
    mask = None
    for (r, c) in plaid["cells"]:
        mc = _m(nodes, links, "LESS_THAN", _m(nodes, links, "ABSOLUTE", _m(nodes, links, "SUBTRACT", col, float(c))), 0.5)
        mr = _m(nodes, links, "LESS_THAN", _m(nodes, links, "ABSOLUTE", _m(nodes, links, "SUBTRACT", row, float(r))), 0.5)
        mm = _m(nodes, links, "MULTIPLY", mc, mr)
        mask = mm if mask is None else _m(nodes, links, "MAXIMUM", mask, mm)
    geo = nodes.new("ShaderNodeNewGeometry"); gs = nodes.new("ShaderNodeSeparateXYZ"); links.new(geo.outputs["Position"], gs.inputs[0])
    mask = _m(nodes, links, "MULTIPLY", mask, _m(nodes, links, "GREATER_THAN", gs.outputs["Z"], plaid["z_min"]))
    f = plaid.get("freq", 5.0) * 6.2832
    s1 = _m(nodes, links, "GREATER_THAN", _m(nodes, links, "SINE", _m(nodes, links, "MULTIPLY", _m(nodes, links, "ADD", gs.outputs["X"], gs.outputs["Y"]), f)), 0.0)
    s2 = _m(nodes, links, "GREATER_THAN", _m(nodes, links, "SINE", _m(nodes, links, "MULTIPLY", gs.outputs["Z"], f)), 0.0)
    k = _m(nodes, links, "MULTIPLY", _m(nodes, links, "ADD", s1, s2), 0.5)
    ramp = nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
    a, b = (hex_rgb(h) for h in plaid["colours"])
    lin = lambda c: [float(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c]
    e0, e1 = ramp.color_ramp.elements
    e0.position = 0.0; e0.color = (*lin(a), 1)
    e1.position = 0.4; e1.color = (*lin(a * 0.55), 1)
    e2 = ramp.color_ramp.elements.new(0.9); e2.color = (*lin(b), 1)
    links.new(k, ramp.inputs["Fac"])
    mix = nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    links.new(mask, mix.inputs["Factor"]); links.new(colour_in, mix.inputs["A"]); links.new(ramp.outputs["Color"], mix.inputs["B"])
    return mix.outputs["Result"]


def emission_setup(mat, img, grad_lo, height, plaid=None):
    """High-poly material -> emission of atlas(img) x height gradient (world Z in rest pose)."""
    nt = mat.node_tree; nodes, links = nt.nodes, nt.links
    tex = next(n for n in nodes if n.type == "TEX_IMAGE")
    tex.image = img
    geo = nodes.new("ShaderNodeNewGeometry"); sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(geo.outputs["Position"], sep.inputs[0])
    mr = nodes.new("ShaderNodeMapRange"); mr.clamp = True
    mr.inputs["From Max"].default_value = height
    mr.inputs["To Min"].default_value = grad_lo
    links.new(sep.outputs["Z"], mr.inputs["Value"])
    mul = nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs["Factor"].default_value = 1
    links.new(plaid_socket(nodes, links, tex.outputs["Color"], plaid) if plaid else tex.outputs["Color"], mul.inputs["A"])
    cmb = nodes.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        links.new(mr.outputs["Result"], cmb.inputs[k])
    links.new(cmb.outputs[0], mul.inputs["B"])
    em = nodes.new("ShaderNodeEmission"); links.new(mul.outputs["Result"], em.inputs["Color"])
    out = next(n for n in nodes if n.type == "OUTPUT_MATERIAL")
    links.new(em.outputs[0], out.inputs["Surface"])


def decimate(ob, target):
    if tris(ob) <= target:
        return
    select_only([ob])
    d = ob.modifiers.new("dec", "DECIMATE"); d.ratio = target / tris(ob); d.use_collapse_triangulate = True
    while ob.modifiers[0].name != "dec":
        bpy.ops.object.modifier_move_up(modifier="dec")
    bpy.ops.object.modifier_apply(modifier="dec")


def pose_carry(rig):
    """One-frame pose: both arms forward and bent, hands in front of the chest (like carrying planks)."""
    act = bpy.data.actions.new("Carry_Pose")
    rig.animation_data.action = act
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    # The glTF importer re-orients bone axes, so aim each limb by its joint-to-joint vector, not bone.vector.
    for sb in ("l", "r"):
        up, lo, wr = (rig.pose.bones[f"{b}.{sb}"] for b in ("upperarm", "lowerarm", "wrist"))
        side = 1.0 if up.head.x > 0 else -1.0
        for pb, child, d in ((up, lo, Vector((side * 0.3, -0.5, -0.8))), (lo, wr, Vector((-side * 0.5, -0.85, 0.15)))):
            bpy.context.view_layer.update()
            q = (child.head - pb.head).normalized().rotation_difference(d.normalized())
            h = pb.head.copy()
            pb.matrix = Matrix.Translation(h) @ q.to_matrix().to_4x4() @ Matrix.Translation(-h) @ pb.matrix
            bpy.context.view_layer.update()
    for n in ("upperarm.l", "lowerarm.l", "upperarm.r", "lowerarm.r"):
        pb = rig.pose.bones[n]
        pb.rotation_mode = "QUATERNION"
        pb.keyframe_insert("rotation_quaternion", frame=1)
        pb.keyframe_insert("location", frame=1)
    return act


def bake(low, highs, height, name):
    sc = bpy.context.scene
    low.data.uv_layers.new(name="UVMap")
    select_only([low])
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(55), island_margin=0.02, area_weight=0.0)
    bpy.ops.object.mode_set(mode="OBJECT")
    img_a = bpy.data.images.new(name + "_alb", TEX, TEX, alpha=False)
    img_o = bpy.data.images.new(name + "_ao", TEX, TEX, alpha=False); img_o.colorspace_settings.name = "Non-Color"
    tgt = bpy.data.materials.new(name + "_tgt"); tgt.use_nodes = True
    tn = tgt.node_tree.nodes.new("ShaderNodeTexImage"); tn.image = img_a; tgt.node_tree.nodes.active = tn
    low.data.materials.clear(); low.data.materials.append(tgt)
    # 1) albedo x gradient from the full-res source
    for h in highs:
        h.hide_render = False
    select_only(highs + [low], active=low)
    sc.render.bake.use_selected_to_active = True
    sc.render.bake.cage_extrusion = 0.03
    sc.render.bake.max_ray_distance = 0.1
    sc.cycles.samples = 1
    bpy.ops.object.bake(type="EMIT", margin=4)
    # 2) AO on the low mesh alone (rest pose; no ground: characters move and get the real-time shadow)
    for h in highs:
        h.hide_render = True
    sc.render.bake.use_selected_to_active = False
    tn.image = img_o
    select_only([low])
    sc.world.light_settings.distance = height * 0.08
    sc.cycles.samples = SAMPLES
    bpy.ops.object.bake(type="AO", margin=4)
    a = np.array(img_a.pixels[:], np.float32).reshape(TEX, TEX, 4)
    o = np.array(img_o.pixels[:], np.float32).reshape(TEX, TEX, 4)[..., :1]
    lin = np.where(a[..., :3] <= 0.04045, a[..., :3] / 12.92, ((a[..., :3] + 0.055) / 1.055) ** 2.4)
    lin = lin * (0.5 + 0.5 * np.clip(o, 0, 1) ** 0.8)  # creases keep about half their colour, never black
    out = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(np.clip(lin, 0, None), 1 / 2.4) - 0.055)
    final = bpy.data.images.new(name, TEX, TEX, alpha=False)
    final.pixels[:] = np.concatenate([np.clip(out, 0, 1), np.ones((TEX, TEX, 1), np.float32)], axis=2).ravel()
    os.makedirs(TEXDIR, exist_ok=True)
    final.file_format = "PNG"; final.filepath_raw = f"{TEXDIR}/{name}.png"; final.save()
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    t = m.node_tree.nodes.new("ShaderNodeTexImage"); t.image = final
    m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.3
    return m


def _islands(bm):
    seen, out = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, comp = [v], []
        seen.add(v.index)
        while stack:
            a = stack.pop(); comp.append(a)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen:
                    seen.add(b.index); stack.append(b)
        out.append(comp)
    return out


def friendly_face(head):
    """Rest-pose edit of the KayKit head template: brows thinner, raised 2.5 cm, inner ends higher than outer
    (KayKit's slope down toward the nose reads angry); the skin-coloured mouth strip becomes a dark smile."""
    import bmesh
    M = head.matrix_world; Mi = M.inverted()
    bm = bmesh.new(); bm.from_mesh(head.data); bm.verts.ensure_lookup_table()
    uv = bm.loops.layers.uv.active
    eye_uv = None
    brows, mouths = {-1: [], 1: []}, []
    for comp in _islands(bm):
        ws = [M @ v.co for v in comp]
        c = sum(ws, Vector()) / len(ws)
        us = [l[uv].uv.copy() for v in comp for l in v.link_loops]
        mu = sum((Vector((u.x, u.y)) for u in us), Vector((0, 0))) / len(us)
        cell = (int((1 - mu.y) * 4), int(mu.x * 8))
        if cell == (0, 2) and eye_uv is None:
            eye_uv = mu.copy()
        if cell == (0, 1) and c.y < -0.3 and 0.05 < abs(c.x) < 0.4 and 1.64 < c.z < 1.86 and len(comp) < 80:
            brows[1 if c.x > 0 else -1].append((comp, ws))
        if cell == (0, 0) and c.y < -0.38 and abs(c.x) < 0.01 and 1.36 < c.z < 1.43 and len(comp) <= 10:
            mouths.append((comp, ws))
    for side, isl in brows.items():
        pts = [w for _, ws in isl for w in ws]
        if not pts:
            continue
        ax = [abs(p.x) for p in pts]; zs = [p.z for p in pts]
        mx, mz = sum(ax) / len(ax), sum(zs) / len(zs)
        slope = sum((a - mx) * (z - mz) for a, z in zip(ax, zs)) / max(sum((a - mx) ** 2 for a in ax), 1e-6)
        for comp, ws in isl:
            for v, w in zip(comp, ws):
                a = abs(w.x)
                fit = mz + slope * (a - mx)
                nz = mz + 0.025 + (w.z - fit) * 0.6 - 0.14 * (a - mx)
                v.co = Mi @ Vector((w.x, w.y, nz))
    for comp, ws in mouths:
        zc = sum(w.z for w in ws) / len(ws)
        for v, w in zip(comp, ws):
            x = w.x * 0.45
            v.co = Mi @ Vector((x, w.y - 0.006, zc - 0.035 + (w.z - zc) * 0.4 + 5.0 * x * x))
            for l in v.link_loops:
                l[uv].uv = eye_uv
    bm.to_mesh(head.data); bm.free()
    return len(brows[1]) + len(brows[-1]), len(mouths)


def add_beanie(rig, head, colour, name):
    """Knit cap on the head bone: dome with vertical ribs (texture), rolled brim, pompom. Own work (CC0)."""
    import bmesh
    # tuck the hair under the cap: hair above the brim line moves inward and down, so the bake cannot pick it up
    M = head.matrix_world; Mi = M.inverted()
    uvl = head.data.uv_layers.active.data
    hair = set()
    for p in head.data.polygons:
        u = sum(uvl[i].uv.x for i in p.loop_indices) / p.loop_total; v = sum(uvl[i].uv.y for i in p.loop_indices) / p.loop_total
        if (int((1 - v) * 4), int(u * 8)) == (0, 1):
            hair.update(p.vertices)
    for i in hair:
        w = M @ head.data.vertices[i].co
        if w.z > 1.86:
            k = min((w.z - 1.86) / 0.3, 1.0)
            head.data.vertices[i].co = Mi @ Vector((w.x * (1 - 0.12 * k), w.y * (1 - 0.12 * k), 1.86 + (w.z - 1.86) * 0.55))
    zs = [(head.matrix_world @ v.co).z for v in head.data.vertices]
    top = max(zs)
    parts = []
    dome = bpy.data.meshes.new("beanie")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=1.0, calc_uvs=True)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.05], context="VERTS")
    for v in bm.verts:
        v.co = Vector((v.co.x * 0.545, v.co.y * 0.545, 1.84 + max(v.co.z, 0.0) * max(top + 0.1 - 1.84, 0.38)))
    bm.to_mesh(dome); bm.free()
    for d, n in ((dome, "BeanieDome"),):
        ob = bpy.data.objects.new(n, d); bpy.context.collection.objects.link(ob); parts.append(ob)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.54, minor_radius=0.075, major_segments=14, minor_segments=5, location=(0, 0, 1.88))
    brim = bpy.context.object; brim.scale = (1.0, 1.0, 1.15); bpy.ops.object.transform_apply(scale=True); parts.append(brim)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=5, radius=0.13, location=(0, 0, 1.84 + max(top + 0.1 - 1.84, 0.38) + 0.07))
    parts.append(bpy.context.object)
    w, h = 64, 8
    img = bpy.data.images.new(name + "_beanie", w, h, alpha=True)
    c = hex_rgb(colour)
    px = np.zeros((h, w, 4), np.float32); px[..., 3] = 1
    for x in range(w):
        px[:, x, :3] = c
    img.pixels[:] = px.ravel()
    mat = bpy.data.materials.new(name + "_beanie"); mat.use_nodes = True
    tn = mat.node_tree.nodes.new("ShaderNodeTexImage"); tn.image = img
    mat.node_tree.links.new(tn.outputs["Color"], next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"])
    for ob in parts:
        if not ob.data.uv_layers:
            ob.data.uv_layers.new(name="UVMap")
        ob.data.materials.clear(); ob.data.materials.append(mat)
        for p in ob.data.polygons:
            p.use_smooth = True
        vg = ob.vertex_groups.new(name="head"); vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
        ob.parent = rig
        am = ob.modifiers.new("Armature", "ARMATURE"); am.object = rig
    select_only(parts)
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active; ob.name = "Beanie_Head"
    return ob, mat, img


def build(name, spec, report):
    base, cells, role = spec[:3]
    opts = spec[3] if len(spec) > 3 else {}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"
    sc.world = bpy.data.worlds.new("w")
    # the 1H axe comes from the Barbarian file (only it has one); read its pose relative to handslot.r
    objs = import_glb(f"{KK}/Characters/gltf/Barbarian.glb")
    brig = next(o for o in objs if o.type == "ARMATURE")
    brig.data.pose_position = "REST"; bpy.context.view_layer.update()
    axe_src = next(o for o in objs if o.name.startswith("1H_Axe") and "Offhand" not in o.name)
    axe_local = brig.data.bones["handslot.r"].matrix_local.inverted() @ (brig.matrix_world.inverted() @ axe_src.matrix_world)
    axe_me = axe_src.data.copy(); axe_me.name = "axe_src"
    barb_img = axe_src.material_slots[0].material.node_tree.nodes[next(
        n.name for n in axe_src.material_slots[0].material.node_tree.nodes if n.type == "TEX_IMAGE")].image
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)

    objs = import_glb(f"{KK}/Characters/gltf/{base}.glb")
    rig = next(o for o in objs if o.type == "ARMATURE")
    rig.name = "Rig"
    parts = [o for o in objs if o.type == "MESH" and any(k in o.name for k in KEEP_PARTS) and o.parent == rig]
    for o in objs:
        if o.type == "MESH" and o not in parts:
            bpy.data.objects.remove(o, do_unlink=True)
    rig.data.pose_position = "REST"
    bpy.context.view_layer.update()
    dg0 = bpy.context.evaluated_depsgraph_get()
    ref_height = max((p.matrix_world @ v.co).z for p in parts for v in p.evaluated_get(dg0).to_mesh().vertices)  # before head edits
    mat = parts[0].material_slots[0].material
    src_img = next(n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE").image
    atlas = recolour(src_img, cells, name + "_atlas")
    face_info = None
    if opts.get("face"):
        face_info = friendly_face(next(p for p in parts if "_Head" in p.name))
    beanie = None
    if opts.get("beanie"):
        beanie = add_beanie(rig, next(p for p in parts if "_Head" in p.name), opts["beanie"], name)
        parts.append(beanie[0])
    # height of the rest pose
    dg = bpy.context.evaluated_depsgraph_get()
    zs = [(p.matrix_world @ v.co).z for p in parts if not p.name.startswith("Beanie") for v in p.evaluated_get(dg).to_mesh().vertices]
    height = ref_height  # same rig scale as the unedited base (the cap and the hair tuck do not change body size)

    # low body = joined copy of the parts, decimated (vertex weights are interpolated by the collapse)
    # the head carries the silhouette: it keeps 90% of its triangles, the rest of the body shares what is left
    lows = []
    head_t = sum(tris(p) for p in parts if "_Head" in p.name)
    rest_t = sum(tris(p) for p in parts) - head_t
    rest_ratio = min(1.0, (BODY_TRIS - 0.9 * head_t) / rest_t)
    for p in parts:
        c = p.copy(); c.data = p.data.copy(); bpy.context.collection.objects.link(c); lows.append(c)
        decimate(c, int(tris(c) * (0.9 if "_Head" in p.name else rest_ratio)))
    select_only(lows)
    bpy.ops.object.join()
    low = bpy.context.view_layer.objects.active; low.name = "Body"; low.data.name = "Body"
    for uv in list(low.data.uv_layers):
        low.data.uv_layers.remove(uv)
    select_only([low])
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(65))
    body_tris = tris(low)

    # axes: high (source detail) and low (decimated), plain + gold, gold offset during the bake
    hand = rig.matrix_world @ rig.data.bones["handslot.r"].matrix_local
    highs = list(parts)
    axe_lows = {}
    for tag, off, img in (("Axe", 0.0, barb_img), ("AxeUpgraded", 3.0, recolour(barb_img, AXE_GOLD, name + "_gold"))):
        hm = bpy.data.materials.new(tag + "_hi"); hm.use_nodes = True
        hn = hm.node_tree.nodes.new("ShaderNodeTexImage"); hn.image = img
        hi = bpy.data.objects.new(tag + "_hi", axe_me.copy()); bpy.context.collection.objects.link(hi)
        hi.data.materials.clear(); hi.data.materials.append(hm)
        hi.matrix_world = Matrix.Translation((off, 0, 0)) @ hand @ Matrix.Scale(AXE_SCALE, 4) @ axe_local
        emission_setup(hm, img, 0.85, height)
        highs.append(hi)
        lo = bpy.data.objects.new(tag, axe_me.copy()); bpy.context.collection.objects.link(lo)
        lo.matrix_world = hi.matrix_world.copy()
        decimate(lo, AXE_TRIS)
        select_only([lo]); bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
        axe_lows[tag] = lo
    emission_setup(mat, atlas, 0.85, height, plaid=opts.get("plaid"))
    if beanie:
        emission_setup(beanie[1], beanie[2], 0.85, height)

    # bake body + both axes into one texture: join temporarily, split by vertex group afterwards
    for tag, lo in axe_lows.items():
        vg = lo.vertex_groups.new(name="__" + tag)
        vg.add(list(range(len(lo.data.vertices))), 1.0, "REPLACE")
        for uv in list(lo.data.uv_layers):
            lo.data.uv_layers.remove(uv)
    world_body = low.matrix_world.copy()
    select_only([low] + list(axe_lows.values()), active=low)
    bpy.ops.object.join()
    low = bpy.context.view_layer.objects.active
    final_mat = bake(low, highs, height, name)
    low.data.materials.clear(); low.data.materials.append(final_mat)
    # split the axes back out
    for tag in axe_lows:
        select_only([low])
        bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="DESELECT")
        low.vertex_groups.active_index = low.vertex_groups["__" + tag].index
        bpy.ops.object.vertex_group_select(); bpy.ops.mesh.separate(type="SELECTED")
        bpy.ops.object.mode_set(mode="OBJECT")
        ax = next(o for o in bpy.context.selected_objects if o != low)
        ax.name = tag; ax.data.name = tag
        ax.vertex_groups.clear()
        for mod in list(ax.modifiers):
            ax.modifiers.remove(mod)
        if tag == "AxeUpgraded":
            ax.data.transform(Matrix.Translation((-3.0, 0, 0)))
        mw = ax.matrix_world.copy()
        ax.parent = rig; ax.parent_type = "BONE"; ax.parent_bone = "handslot.r"
        bpy.context.view_layer.update()
        ax.matrix_world = mw
        ax.hide_render = False
        axe_lows[tag] = ax
        report_axe = tris(ax)
    for vg in [v for v in low.vertex_groups if v.name.startswith("__")]:
        low.vertex_groups.remove(vg)
    for h in highs:
        bpy.data.objects.remove(h, do_unlink=True)
    low.hide_render = False

    # animations: keep what the game needs, plus the authored carry pose
    keep = set(ANIMS)
    for a in list(bpy.data.actions):
        if a.name not in keep:
            bpy.data.actions.remove(a)
    missing = [n for n in ANIMS if n not in bpy.data.actions]
    rig.data.pose_position = "POSE"
    if rig.animation_data is None:
        rig.animation_data_create()
    pose_carry(rig)
    rig.animation_data.action = bpy.data.actions["Idle"]
    for a in bpy.data.actions:
        a.use_fake_user = True

    s = TARGET_H / height
    rig.scale = (s, s, s)
    os.makedirs(OUT, exist_ok=True)
    path = f"{OUT}/{name}.glb"
    select_only([rig, low] + list(axe_lows.values()), active=rig)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=False,
                              export_animations=True, export_animation_mode="ACTIONS", export_skins=True,
                              export_yup=True, export_image_format="AUTO")
    report[name] = dict(base=base, role=role, body_tris=body_tris, axe_tris=report_axe, tex=TEX,
                        rest_height=round(height * s, 3), rig_scale=round(s, 4), missing_anims=missing,
                        anims=sorted(a.name for a in bpy.data.actions), bytes=os.path.getsize(path),
                        options={k: v for k, v in opts.items() if k != "plaid"} | ({"plaid": True} if opts.get("plaid") else {}),
                        face_edit=face_info)
    print("BUILT", name, report[name])


def main():
    only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    rep_path = f"{REPO}/tools/lookdev/build_chars_report.json"
    report = json.load(open(rep_path)) if os.path.exists(rep_path) else {}
    for name, spec in {**PLAN, **PLAYER_ALTS}.items():
        if only and name not in only:
            continue
        build(name, spec, report)
        json.dump(report, open(rep_path, "w"), indent=1)


main()
