"""Frost Peaks (GDD milestone M4, valley 5) models -> assets/models_v3/frost/ (+ items in assets/models_v3/items/).
Same bake as every models_v3 asset. Placement + paste-ready dicts: assets/models_v3/ASSETS_M4.md.

Usage (headless, Cycles on the RTX 3060 when available):
  /home/mm/.local/bin/blender -b --python tools/lookdev/build_m4.py -- [only_name ...]
Report: tools/lookdev/build_m4_report.json. Everything here is own work (CC0).

Region accent: alpine red #c8283a (machines, roofs, cable car, train, ironwork). Snow #f2f6fc on every roof and cap.
Kiln glow is a separate emissive GLB (kiln_glow.glb) so the game can ramp it 0 -> 1 over the bake.
"""
import os

exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "m345_lib.py")).read(), "m345_lib.py", "exec"))

# ------------------------------------------------------------------ Frost Peaks palette (sRGB, docs/DESIGN.md section 15)
ALP = (0.784, 0.157, 0.227)         # #c8283a region accent, alpine red
ALP_D = (0.55, 0.11, 0.16)          # #8c1c29 frames, trims
SNOW = (0.95, 0.965, 0.99)          # #f2f6fc snow caps
FIR = (0.18, 0.37, 0.31)            # #2f5e4f blue-green fir
FIR2 = (0.25, 0.46, 0.38)           # #407561 lighter tier
FIR_BARK = (0.43, 0.31, 0.25)
FROST_END = (0.93, 0.80, 0.62)
DRY = (0.91, 0.62, 0.32)            # #e89e52 kiln-dried lumber, warm orange
DRY_END = (0.80, 0.50, 0.26)
SPRUCE_TOP = (0.96, 0.82, 0.52)     # guitar top
ROSE = (0.36, 0.20, 0.13)           # fingerboard, bridge
GUITAR_SIDE = (0.70, 0.40, 0.20)
STONE_K = (0.70, 0.67, 0.63)        # kiln stone (warm light grey)
LOGWALL = (0.62, 0.42, 0.27)
GLOW = (1.0, 0.48, 0.12)


def fmats():
    m = mmats()
    m.update(alp=M("alp", ALP), alp_d=M("alpd", ALP_D), snow=M("snow", SNOW), wht=M("wht", WHITE),
             fbark=M("fbark", FIR_BARK, "bark"), fend=M("fend", FROST_END, "rings"), dry=M("dry", DRY, "planks"),
             blk=M("blk", (0.22, 0.22, 0.24)), lamp=M("lamp", (1.0, 0.9, 0.6)), gold=M("gold", (1.0, 0.8, 0.25)),
             kstone=M("kstone", STONE_K), logw=M("logw", LOGWALL, "bark"), char=M("char", CHARCOAL),
             cream2=M("cream2", (0.97, 0.93, 0.84)))
    return m


def snow_cap(size, pos, rot=(0, 0, 0)):
    """Soft snow slab sitting on a roof or ledge (Godot size and position)."""
    return gb(size, pos, M("snow", SNOW), bev=min(0.06, size[1] * 0.45), seg=2, rot=rot)


def snow_roof(W, D, ye, pitch, over, roof_thick=0.16):
    """Snow layer on a groof() gable roof with the same arguments: same panels, raised onto the roof, a bit narrower."""
    lift = (roof_thick / 2 + 0.045) / math.cos(math.radians(pitch))
    parts, _ = groof(W - 0.12, D, ye + lift, pitch, over - 0.5, M("snow", SNOW), thick=0.09)   # red eave band stays visible
    return parts


def cut_below(ob, y_godot):
    """Flatten every vertex below world height y (Godot) onto it (keeps the upper part of a cylinder/sphere)."""
    bpy.context.view_layer.update()   # location/rotation were just set: refresh matrix_world first
    mw = ob.matrix_world.copy(); inv = mw.inverted()
    for v in ob.data.vertices:
        w = mw @ v.co
        if w.z < y_godot:
            w.z = y_godot
            v.co = inv @ w
    return ob


# ------------------------------------------------------------------ trees (kenney units; game scale x1.15 on top)

def _taper(ob, hz, k0=1.12, k1=0.95):
    for v in ob.data.vertices:
        t = min(max((v.co.z + hz) / (2 * hz), 0.0), 1.0)
        k = k0 - k1 * t
        v.co.x *= k; v.co.y *= k
    return ob


def frost_fir(variant, far=False):
    """Frost fir: short trunk, stacked blue-green cone tiers with a white snow collar on each, snow tip.
    Kenney units; the game scales firs 1.15x more, so the widest stays <= 0.69 (0.79 after 1.15x)."""
    rnd = random.Random({"A": 7, "B": 19, "C": 41, "D": 53}[variant])
    bark = M("fbark", FIR_BARK, "bark")
    la, lb, sn = M("fir", FIR), M("fir2", FIR2), M("snow", SNOW)
    H, R, n = {"A": (1.62, 0.31, 4), "B": (1.85, 0.27, 4), "C": (1.42, 0.335, 3), "D": (1.7, 0.33, 4)}[variant]
    p = []
    tr = tube([Vector((0, 0, -0.04)), Vector((0, 0, 0.18)), Vector((0, 0, 0.42))], [0.055, 0.045, 0.035], 5 if far else 7, bark)
    p.append(tr)
    if far:
        hz = (H - 0.15) / 2
        c = blob(1.0, (0, 0, 0.15 + hz), (R * 0.98, R * 0.98, hz), la, 1, ico=2, amp=0.1)
        p.append(_taper(c, hz, 1.15, 1.0))
        hs = hz * 0.55
        s = blob(1.0, (0, 0, 0.15 + hz + hz * 0.45), (R * 0.62, R * 0.62, hs), sn, 2, ico=2, amp=0.12)
        p.append(_taper(s, hs, 1.1, 0.95))
        return p
    z0 = 0.16
    th = (H - z0) / n * 1.4
    for i in range(n):
        f = i / max(n - 1, 1)
        zb = z0 + i * (H - z0 - th * 0.55) / max(n - 1, 1)
        r = R * (1.0 - 0.58 * f) * rnd.uniform(0.95, 1.03)
        hz = th * 0.55
        c = blob(1.0, (rnd.uniform(-0.01, 0.01), rnd.uniform(-0.01, 0.01), zb + hz * 0.8), (r, r, hz), la if i % 2 == 0 else lb,
                 i * 1.9 + 0.3, seg=10, rings=6, amp=0.09)
        p.append(_taper(c, hz, 1.12, 0.92))
        snow_r = r * (0.66 if variant != "D" else 0.74)
        sh = th * 0.16
        s = blob(1.0, (0.01, -0.01, zb + hz * 0.8 + hz * 0.32), (snow_r, snow_r, sh), sn, i * 2.3 + 1.1, seg=8, rings=4, amp=0.16)
        p.append(s)
    p.append(blob(1.0, (0, 0, H - 0.02), (0.05, 0.05, 0.09), sn, 9.7, seg=6, rings=4, amp=0.08))
    return p


def frost_stump():
    side, end = M("fbark", FIR_BARK, "bark"), M("fend", FROST_END, "rings")
    p = [_log(0.15, 0.2, (0, 0, 0.1), (0, 0, 0), side, end, verts=12)]
    p.append(blob(1.0, (0.02, 0.0, 0.205), (0.12, 0.11, 0.03), M("snow", SNOW), 1.0, seg=8, rings=4, amp=0.15))
    p.append(blob(1.0, (0.0, 0.0, -0.005), (0.32, 0.3, 0.045), M("snow", SNOW), 2.0, seg=10, rings=4, amp=0.12))
    return p


def frost_log_stack():
    side, end = M("fbark", FIR_BARK, "bark"), M("fend", FROST_END, "rings")
    p, r = [], 0.075
    for count, row in [(4, 0.0), (3, 1.0), (2, 2.0)]:
        for i in range(count):
            x = (i - (count - 1) / 2) * 2 * r * 1.02
            p.append(_log(r, 0.66, (x, 0, r + row * r * 1.75), (math.pi / 2, 0, 0), side, end, verts=9, seg=1))
    p.append(blob(1.0, (0, 0, r * 2 * 1.75 + r * 1.75), (0.16, 0.32, 0.035), M("snow", SNOW), 3.0, seg=9, rings=4, amp=0.12))
    return p


def snow_drift():
    """Soft wind-blown snow mound (deco scatter, kenney units)."""
    return [blob(1.0, (0, 0, -0.02), (0.3, 0.2, 0.09), M("snow", SNOW), 1.3, seg=10, rings=5, amp=0.15),
            blob(1.0, (0.18, 0.05, -0.01), (0.14, 0.12, 0.06), M("snow", SNOW), 2.7, seg=8, rings=4, amp=0.15)]


def snow_rock():
    """Warm-grey boulder with a snow cap (deco, kenney units)."""
    r = M("rock", (0.56, 0.53, 0.5))
    p = [blob(1.0, (0, 0, 0.07), (0.2, 0.17, 0.14), r, 1.7, ico=2, amp=0.22)]
    cap = blob(1.0, (0.0, 0.0, 0.17), (0.16, 0.14, 0.05), M("snow", SNOW), 2.2, ico=2, amp=0.2)
    p.append(cap)
    return p


def snow_bush():
    """Low juniper bush under snow (deco, kenney units)."""
    return [blob(1.0, (0, 0, 0.1), (0.2, 0.18, 0.12), M("fir", FIR), 1.0, seg=9, rings=5, amp=0.14),
            blob(1.0, (0.02, 0.0, 0.17), (0.15, 0.13, 0.06), M("snow", SNOW), 2.0, seg=8, rings=4, amp=0.18)]


# ------------------------------------------------------------------ items (world metres, scale 1)

def item_frost_log():
    """Fir log with a strip of snow on top (cell 1.05 x 0.4, layer 0.33)."""
    p = [_log_along_x(0.15, 0.95, M("fbark", FIR_BARK, "bark"), M("fend", FROST_END, "rings"))]
    s = blob(1.0, gpos(0.02, 0.29, 0.0), (0.4, 0.09, 0.035), M("snow", SNOW), 1.2, seg=10, rings=4, amp=0.15)
    p.append(s)
    return p


def item_dry_lumber():
    """Kiln-dried plank: warm orange, toasted ends, red kiln stamp. 0.95 x 0.1 x 0.36 (cell 1.0 x 0.4, layer 0.11)."""
    side, end = M("dry", DRY, "planks"), M("dryend", DRY_END, "rings")
    ob = rbox(0.95, 0.36, 0.1, (0, 0, 0.05), side, bev=0.02, seg=2)
    ob.data.materials.append(end)
    for f in ob.data.polygons:
        f.material_index = 1 if abs(f.normal.x) > 0.7 else 0
    return [ob, gb((0.12, 0.004, 0.12), (-0.28, 0.101, 0.06), M("stamp", ALP), bev=0.0),
            gb((0.06, 0.004, 0.06), (-0.28, 0.102, 0.06), M("stamp2", DRY), bev=0.0)]


def item_skis():
    """Pair of wooden skis, long along Z (cell 0.4 x 1.6, layer 0.12): upturned tips at -Z, red top stripe, black bindings."""
    wood, red, blk = M("skiw", (0.88, 0.62, 0.36), "planks"), M("red", ALP), M("blk", (0.18, 0.18, 0.2))
    p = []
    for x in (-0.07, 0.07):
        p.append(gb((0.1, 0.03, 1.3), (x, 0.015, 0.12), wood, bev=0.008, seg=1))
        p.append(gb((0.1, 0.03, 0.26), (x, 0.06, -0.62), wood, bev=0.0, rot=(22, 0, 0)))
        p.append(gb((0.035, 0.006, 1.2), (x, 0.033, 0.1), red, bev=0.0))
        p.append(gb((0.11, 0.05, 0.12), (x, 0.055, 0.15), blk, bev=0.0))
    return p


def item_sled():
    """Wooden toboggan, long along Z (cell 0.8 x 1.3, layer 0.5): red bent runners curled up at -Z, slatted seat, rope
    at the front. 0.68 x 0.43 x 1.3."""
    wood, red, rope = M("sledw", (0.86, 0.6, 0.34), "planks"), M("red", ALP), M("rope", (0.86, 0.78, 0.6))
    p = []
    for x in (-0.28, 0.28):
        pts = [(x, 0.03, 0.6), (x, 0.03, -0.4), (x, 0.13, -0.6), (x, 0.33, -0.6), (x, 0.38, -0.5)]
        p.append(gtube(pts, 0.03, red, sides=4))
        for z in (-0.25, 0.45):
            p.append(gb((0.05, 0.27, 0.05), (x, 0.17, z), red, bev=0.0))
    for i in range(4):
        p.append(gb((0.68, 0.035, 0.2), (0, 0.32, -0.28 + i * 0.25), wood, bev=0.0))
    p.append(gtube([(-0.28, 0.36, -0.55), (0.0, 0.42, -0.72), (0.28, 0.36, -0.55)], 0.012, rope, sides=3, cap=False))
    return p


def item_guitar():
    """Acoustic guitar lying face up, long along Z (cell 0.5 x 1.2, layer 0.2): body at +Z, neck and headstock at -Z.
    0.38 x 0.12 x 1.19."""
    top, side, rose, blk = M("top", SPRUCE_TOP, "planks"), M("side", GUITAR_SIDE), M("rose", ROSE), M("hole", (0.08, 0.06, 0.05))
    p = []
    for (z, r) in ((0.28, 0.19), (0.02, 0.15)):
        p.append(gc(r, 0.1, (0, 0.05, z), side, verts=14))
        p.append(gc(r - 0.008, 0.012, (0, 0.104, z), top, verts=14))
    p.append(gb((0.26, 0.012, 0.2), (0, 0.104, 0.15), top, bev=0.0))
    p.append(gc(0.05, 0.006, (0, 0.111, 0.07), blk, verts=10))
    p.append(gb((0.13, 0.014, 0.035), (0, 0.112, 0.31), rose, bev=0.0))
    p.append(gb((0.055, 0.04, 0.45), (0, 0.08, -0.35), side, bev=0.0))           # neck
    p.append(gb((0.05, 0.008, 0.45), (0, 0.104, -0.35), rose, bev=0.0))           # fingerboard
    p.append(gb((0.085, 0.03, 0.15), (0, 0.075, -0.64), rose, bev=0.0, rot=(10, 0, 0)))     # headstock
    p.append(gb((0.14, 0.02, 0.1), (0, 0.08, -0.64), M("peg", (0.9, 0.85, 0.7)), bev=0.0, rot=(10, 0, 0)))
    p.append(gb((0.03, 0.003, 0.88), (0, 0.112, -0.14), M("str", (0.85, 0.83, 0.78)), bev=0.0))
    return p


# ------------------------------------------------------------------ machines (world metres; Machine piles at x -2.7 / +2.7)

def drying_kiln():
    """Drying Kiln (r5_kiln, r5_kiln2, r5_kiln3; BATCH). Stone kiln house with a snowy barrel roof and a red steel door at
    +Z. Door = kiln_door.glb, hinge at (-0.72, 0.2, 1.26). Glow = kiln_glow.glb at the origin (chimney mouth + two vents).
    Input pile/DROP at (-2.7, 0, 0.3), output at (2.7, 0, 0.3)."""
    m = fmats()
    W, D, H = 3.0, 2.4, 1.9
    p = [gb((W + 0.3, 0.25, D + 0.3), (0, 0.12, 0), m["grey"], bev=0.06)]
    p.append(gb((W, H, D), (0, 0.25 + H / 2, 0), m["kstone"], bev=0.08))
    for sx in (-1, 1):                                                          # red steel corner frames
        for sz in (-1, 1):
            p.append(gb((0.16, H + 0.05, 0.16), (sx * W / 2, 0.25 + H / 2, sz * D / 2), m["alp_d"], bev=0.03))
    vault = gc(D / 2 + 0.05, W + 0.1, (0, 0.25 + H, 0), m["alp"], axis="x", verts=16)
    p.append(cut_below(vault, 0.25 + H))                                        # keep the upper half: barrel roof
    sn = blob(1.0, gpos(0, 0.25 + H + D / 2 - 0.05, 0), (W / 2 + 0.05, D * 0.32, 0.12), m["snow"], 2.0, seg=12, rings=5, amp=0.06)
    p.append(sn)
    p.append(gb((1.7, 1.55, 0.12), (0, 0.25 + 0.8, D / 2 + 0.02), m["char"], bev=0.03))   # door opening (dark)
    p.append(gb((1.9, 0.18, 0.2), (0, 0.25 + 1.62, D / 2 + 0.05), m["alp_d"], bev=0.04))  # lintel
    p.append(gc(0.17, 0.05, (1.12, 1.55, D / 2 + 0.03), m["gold"], axis="z", verts=14))  # thermometer dial
    p.append(gc(0.13, 0.06, (1.12, 1.55, D / 2 + 0.04), m["cream2"], axis="z", verts=14))
    p.append(gb((0.02, 0.1, 0.02), (1.14, 1.58, D / 2 + 0.075), m["alp"], bev=0.0, rot=(0, 0, -40)))
    p.append(gb((0.6, 2.6, 0.6), (0.9, 2.5, -0.75), m["kstone"], bev=0.06))                # chimney
    p.append(gb((0.7, 0.14, 0.7), (0.9, 3.85, -0.75), m["alp_d"], bev=0.04))
    p.append(snow_cap((0.62, 0.06, 0.62), (0.9, 3.95, -0.75)))
    p.append(gb((0.3, 0.12, 0.3), (0.9, 3.93, -0.75), m["char"], bev=0.0))
    for x in (-0.55, 0.55):                                                     # vents above the door
        p.append(gb((0.36, 0.14, 0.06), (x, 2.0, D / 2 + 0.01), m["char"], bev=0.01))
    p.append(gb((0.7, 0.5, 0.5), (-1.45, 0.5, D / 2 + 0.05), m["dark"], bev=0.04))        # firewood box
    for i in range(3):
        p.append(gl(0.07, 0.62, (-1.45, 0.82, D / 2 - 0.12 + i * 0.15), m["fbark"], m["fend"], verts=7))
    return p


def kiln_door():
    """Kiln door, hinge = origin (place at (-0.72, 0.2, 1.26) on drying_kiln). Spans +X 1.44 m, 1.5 tall.
    Closed = rotation 0; open = rotation.y -1.75 rad (swings out toward the camera). Red steel, rivets, handle."""
    m = fmats()
    p = [gb((1.44, 1.5, 0.08), (0.72, 0.78, 0), m["alp"], bev=0.03)]
    for y in (0.25, 1.3):
        p.append(gb((1.46, 0.1, 0.1), (0.72, y, 0.0), m["alp_d"], bev=0.02))
    for x in (0.15, 0.55, 0.95, 1.3):
        for y in (0.25, 1.3):
            p.append(gc(0.022, 0.03, (x, y, 0.06), m["steel"], axis="z", verts=6))
    p.append(gb((0.08, 0.35, 0.08), (1.25, 0.78, 0.08), m["steel"], bev=0.02))
    p.append(gc(0.03, 0.28, (0.0, 0.5, 0), m["steel_d"], verts=8))
    p.append(gc(0.03, 0.28, (0.0, 1.1, 0), m["steel_d"], verts=8))
    return p


def kiln_glow():
    """Emissive parts of the kiln (one material, no texture): chimney mouth disc and the two vent slits. Origin = kiln origin.
    Ramp the material's emission_energy_multiplier 0 -> 3 over the bake (GDD 7.6 D) and back to 0 when the door opens."""
    g = M("glow", GLOW)
    return [gb((0.26, 0.02, 0.26), (0.9, 4.0, -0.75), g, bev=0.0), gb((0.3, 0.09, 0.02), (-0.55, 2.0, 1.235), g, bev=0.0),
            gb((0.3, 0.09, 0.02), (0.55, 2.0, 1.235), g, bev=0.0)]


def _open_shed(w, d, h, m, roof_mat):
    """Open workshop: plank floor, four red posts, lean-to snowy roof over the back half only (camera sees the work)."""
    p = [gb((w, 0.18, d), (0, 0.09, 0), m["plank"], bev=0.05)]
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(gb((0.18, h, 0.18), (sx * (w / 2 - 0.15), h / 2, sz * (d / 2 - 0.15)), m["alp_d"], bev=0.04))
    for z in (-d / 2 + 0.15, d / 2 - 0.15):
        p.append(gb((w + 0.1, 0.18, 0.2), (0, h, z), m["alp_d"], bev=0.04))
    depth = d * 0.55
    p.append(gb((w + 0.6, 0.16, depth / math.cos(math.radians(16))), (0, h + 0.28, -d / 2 + depth / 2 - 0.25), roof_mat, bev=0.05, rot=(16, 0, 0)))
    p.append(snow_cap((w + 0.4, 0.1, depth * 0.62), (0, h + 0.4 + 0.19 * depth * 0.29, -d / 2 + depth / 2 - 0.25 - 0.19 * depth), rot=(16, 0, 0)))
    p.append(gb((w - 0.3, 1.0, 0.1), (0, 0.7, -d / 2 + 0.12), m["logw"], bev=0.03))
    return p


def ski_workshop():
    """Ski Workshop (r5_skiworks): open shed, steam box at the back, bending press in the middle. The press head is
    ski_press.glb (Machine.plates): pivot = top of the plate, plate_up 1.55, plate_down 1.08. Piles x -2.7 / +2.7."""
    m = fmats()
    roof = M("roof", ALP, "boards", bands=12.0, dir="X")
    p = _open_shed(3.6, 2.8, 2.3, m, roof)
    p.append(gb((1.6, 0.75, 1.0), (0, 0.55, 0.2), m["alp"], bev=0.08))             # press base
    p.append(gb((1.65, 0.08, 1.05), (0, 0.95, 0.2), m["steel"], bev=0.02))
    for x in (-0.7, 0.7):                                                           # press columns + top beam
        p.append(gb((0.14, 1.4, 0.14), (x, 1.3, -0.25), m["alp_d"], bev=0.03))
    p.append(gb((1.6, 0.2, 0.25), (0, 2.0, -0.25), m["alp_d"], bev=0.04))
    p.append(gc(0.07, 0.4, (0, 1.75, -0.25), m["steel"], verts=8))
    sk = item_skis()
    gmove(sk, 0, 0.99, 0.2, rot_y_deg=90)
    p += sk
    p.append(gb((1.3, 0.6, 0.5), (-0.6, 0.55, -1.0), m["steel_d"], bev=0.06))      # steam box
    p.append(gc(0.06, 0.8, (-1.05, 1.1, -1.0), m["steel"], verts=8))
    p.append(gb((0.35, 0.45, 0.3), (1.25, 0.6, -0.95), m["yellow"], bev=0.06))
    p.append(gb((0.2, 0.14, 0.04), (1.25, 0.7, -0.79), m["green_btn"], bev=0.02))
    for i in range(3):                                                              # lumber on the infeed
        d = item_dry_lumber()
        gmove(d, -1.25, 0.19 + i * 0.1, 0.65)
        p += d
    return p


def ski_press():
    """Ski bending press head (Machine.plates): pivot = top of the plate; plate_up 1.55, plate_down 1.08."""
    m = fmats()
    p = [gb((1.4, 0.12, 0.5), (0, -0.06, 0), m["steel"], bev=0.03), gc(0.06, 0.6, (0, 0.3, 0), m["steel"], verts=8)]
    p.append(gb((1.42, 0.05, 0.1), (0, -0.1, 0.2), m["alp"], bev=0.0))
    return p


def sled_workshop():
    """Sled Workshop (r5_sledshop, ASSEMBLER): dry lumber in from -X at z -1.2, skis in from -X at z +1.2, sled out at +X.
    Put the piles at (-3.2, 0, -1.45) lumber, (-3.2, 0, 1.45) skis, (3.2, 0, 0) sleds. The swinging drill arm is
    sled_workshop_arm.glb at (0.9, 0, -1.2) (Machine.arms: rotation.y swings +-0.9 rad)."""
    m = fmats()
    roof = M("roof", ALP, "boards", bands=12.0, dir="X")
    p = [gb((4.6, 0.18, 4.0), (0, 0.09, 0), m["plank"], bev=0.05)]
    p.append(gb((4.4, 2.6, 0.16), (0, 1.48, -1.9), m["logw"], bev=0.04))
    for s in (-1, 1):
        p.append(gb((0.2, 2.8, 0.2), (s * 2.2, 1.4, -1.9), m["alp_d"], bev=0.05))
        p.append(gb((0.2, 2.5, 0.2), (s * 2.2, 1.25, -0.6), m["alp_d"], bev=0.05))
    p.append(gb((4.6, 0.18, 0.2), (0, 2.5, -0.6), m["alp_d"], bev=0.05))
    p.append(gb((5.0, 0.16, 1.8), (0, 2.85, -1.25), roof, bev=0.05, rot=(12, 0, 0)))
    p.append(snow_cap((4.8, 0.1, 1.05), (0, 3.03, -1.52), rot=(12, 0, 0)))
    for z in (-1.2, 1.2):                                                           # intake tables
        p.append(gb((1.4, 0.1, 0.8), (-1.5, 0.78, z), m["steel"], bev=0.03))
        for x in (-2.1, -0.9):
            for dz in (-0.3, 0.3):
                p.append(gb((0.07, 0.7, 0.07), (x, 0.45, z + dz), m["steel_d"], bev=0.02))
        p.append(gb((0.12, 0.08, 0.84), (-2.25, 0.86, z), m["yellow"], bev=0.02))
    d = item_dry_lumber()
    gmove(d, -1.5, 0.83, -1.2)
    p += d
    sk = item_skis()
    gmove(sk, -1.5, 0.83, 1.2, rot_y_deg=90)
    p += sk
    p.append(gb((1.8, 0.75, 1.6), (0.3, 0.48, 0), m["alp"], bev=0.1))             # assembly table
    p.append(gb((1.85, 0.08, 1.65), (0.3, 0.89, 0), m["plank"], bev=0.03))
    sl = item_sled()
    gmove(sl, 0.3, 0.93, 0, rot_y_deg=90)
    p += sl
    p.append(gb((1.3, 0.1, 0.9), (1.85, 0.78, 0), m["steel"], bev=0.03))           # outfeed
    for x in (1.3, 2.4):
        for z in (-0.35, 0.35):
            p.append(gb((0.07, 0.7, 0.07), (x, 0.45, z), m["steel_d"], bev=0.02))
    p.append(gb((0.3, 0.12, 0.3), (0.9, 0.24, -1.2), m["steel_d"], bev=0.03))        # arm post base
    p.append(gc(0.08, 2.0, (0.9, 1.2, -1.2), m["alp_d"], verts=10))
    p.append(gb((0.4, 0.55, 0.3), (-0.9, 0.48, -1.72), m["yellow"], bev=0.07))
    p.append(gb((0.24, 0.16, 0.05), (-0.9, 0.6, -1.55), m["green_btn"], bev=0.02))
    return p


def sled_workshop_arm():
    """Swinging drill arm, pivot = the post axis (place at (0.9, 0, -1.2) on sled_workshop). Reaches +Z over the table."""
    m = fmats()
    return [gc(0.12, 0.25, (0, 2.1, 0), m["alp"], verts=12), gb((0.18, 0.16, 1.3), (0, 2.1, 0.65), m["alp"], bev=0.04),
            gb((0.26, 0.4, 0.26), (0, 1.85, 1.2), m["yellow"], bev=0.05), gc(0.03, 0.4, (0, 1.45, 1.2), m["steel"], verts=6, r2=0.005)]


def luthier_workshop():
    """Luthier Workshop (r5_luthier): open log workshop, guitars hanging on the back wall, workbench with a guitar body,
    sanding disc (luthier_sander.glb) at (1.15, 1.15, 0.35). Piles x -2.7 / +2.7 (output 12 guitars)."""
    m = fmats()
    roof = M("roof", ALP, "boards", bands=12.0, dir="X")
    p = _open_shed(3.8, 3.0, 2.4, m, roof)
    p.append(gb((3.5, 1.4, 0.1), (0, 1.25, -1.33), m["logw"], bev=0.03))             # back wall (taller)
    for i, x in enumerate((-1.0, -0.4, 0.2)):                                         # guitars on the wall
        g = item_guitar()
        for o in g:
            o.matrix_world = Matrix.Translation(gpos(x, 1.25, -1.2)) @ Matrix.Rotation(math.radians(90), 4, "X") @ o.matrix_world
        p += g
    p.append(gb((2.0, 0.08, 0.9), (-0.4, 0.92, 0.2), m["furn"], bev=0.03))            # workbench
    for x in (-1.3, 0.5):
        for z in (-0.15, 0.55):
            p.append(gb((0.08, 0.84, 0.08), (x, 0.46, z), m["dark"], bev=0.02))
    g = item_guitar()
    gmove(g, -0.5, 0.96, 0.2, rot_y_deg=90)
    p += g
    p.append(gb((0.5, 0.9, 0.5), (1.15, 0.55, 0.3), m["alp"], bev=0.06))             # sander stand
    p.append(gb((0.6, 0.06, 0.4), (1.15, 1.02, 0.35), m["steel"], bev=0.02))
    p.append(gc(0.05, 0.08, (-1.1, 1.0, 0.45), m["gold"], verts=8))                   # glue pot, clamps
    for x in (-0.2, 0.1):
        p.append(gb((0.04, 0.22, 0.2), (x, 1.05, 0.55), m["steel_d"], bev=0.01))
    p.append(gc(0.22, 0.05, (-1.4, 0.18, -0.6), m["dry"], verts=12))                    # wood shavings
    return p


def luthier_sander():
    """Sanding disc (spinner), r 0.28, disc normal along Godot Z, pivot at the centre: add at (1.15, 1.32, 0.56)."""
    m = fmats()
    return [gc(0.28, 0.04, (0, 0, 0), M("paper", (0.86, 0.74, 0.52)), axis="z", verts=20),
            gc(0.06, 0.06, (0, 0, -0.02), m["steel_d"], axis="z", verts=10),
            gb((0.3, 0.05, 0.045), (0.1, 0.0, 0.0), m["alp"], bev=0.0)]


# ------------------------------------------------------------------ vehicles

def snowcat():
    """Snowcat hauler (r5_snowcat): red cab on two wide tracks, plow blade at +Z (front), cargo bed at the back:
    carried ItemStack at (0, 1.05, -0.95)."""
    m = fmats()
    trk = M("track", (0.2, 0.2, 0.21))
    p = []
    for x in (-0.68, 0.68):
        p.append(gb((0.5, 0.55, 2.7), (x, 0.32, 0), trk, bev=0.24, seg=3))
        for z in (-1.0, 0.0, 1.0):
            p.append(gc(0.2, 0.52, (x, 0.32, z), m["steel_d"], axis="x", verts=10))
        for i in range(9):
            p.append(gb((0.52, 0.04, 0.1), (x, 0.61, -1.2 + i * 0.3), m["blk"], bev=0.0))
    p.append(gb((1.25, 0.35, 2.4), (0, 0.75, 0), m["alp_d"], bev=0.08))
    p.append(gb((1.3, 1.0, 1.15), (0, 1.4, 0.55), m["alp"], bev=0.14))               # cab
    p.append(gb((1.2, 0.5, 0.05), (0, 1.55, 1.13), m["wglass"], bev=0.02))
    for x in (-0.66, 0.66):
        p.append(gb((0.05, 0.45, 0.85), (x, 1.55, 0.55), m["wglass"], bev=0.02))
    p.append(gb((1.35, 0.08, 1.2), (0, 1.94, 0.55), m["cream2"], bev=0.04))
    p.append(gb((0.9, 0.12, 0.12), (0, 2.03, 0.4), m["blk"], bev=0.03))             # light bar
    for x in (-0.3, 0.3):
        p.append(gc(0.07, 0.05, (x, 2.03, 0.47), m["lamp"], axis="z", verts=8))
    p.append(gb((0.18, 0.12, 0.12), (0.45, 2.05, 0.3), M("beacon", (1.0, 0.6, 0.15)), bev=0.03))
    p.append(gb((1.8, 0.55, 0.12), (0, 0.45, 1.6), m["yellow"], bev=0.05, rot=(-15, 0, 0)))  # plow
    p.append(gb((1.35, 0.1, 1.15), (0, 0.97, -0.75), m["plank"], bev=0.03))          # cargo bed
    for x in (-0.66, 0.66):
        p.append(gb((0.06, 0.4, 1.1), (x, 1.15, -0.75), m["alp"], bev=0.02))
    p.append(gb((1.3, 0.4, 0.06), (0, 1.15, -1.32), m["alp"], bev=0.02))
    return p


def mountain_loco():
    """Mountain railway loco (r5_express_r5): boxy alpine electric loco, red with a cream band, pantograph. Front at -Z.
    Gauge 1.0, wheels on the rail top y 0.18; origin = track centre at ground. Use the M2 rail and buffer stop."""
    m = fmats()
    p = [gb((1.45, 0.3, 3.6), (0, 0.6, 0), m["blk"], bev=0.06)]
    for z in (-1.1, -0.4, 0.4, 1.1):
        for x in (-0.55, 0.55):
            p.append(gc(0.26, 0.1, (x, 0.18 + 0.26, z), m["steel_d"], axis="x", verts=12))
    p.append(gb((1.6, 1.45, 3.4), (0, 1.5, 0), m["alp"], bev=0.18, seg=2))
    p.append(gb((1.62, 0.22, 3.42), (0, 1.25, 0), m["cream2"], bev=0.04))
    for z in (-1.71, 1.71):
        p.append(gb((1.2, 0.5, 0.05), (0, 1.75, z), m["wglass"], bev=0.02))
        p.append(gc(0.09, 0.05, (0.5, 1.05, z), m["lamp"], axis="z", verts=8))
        p.append(gc(0.09, 0.05, (-0.5, 1.05, z), m["lamp"], axis="z", verts=8))
    for x in (-0.81, 0.81):
        for z in (-0.9, 0.0, 0.9):
            p.append(gb((0.05, 0.4, 0.5), (x, 1.75, z), m["wglass"], bev=0.02))
    p.append(gb((1.5, 0.1, 3.2), (0, 2.27, 0), m["alp_d"], bev=0.04))
    p.append(snow_cap((1.3, 0.08, 2.6), (0, 2.34, 0)))
    for z in (-0.5, 0.5):
        p.append(gb((0.08, 0.06, 0.08), (0, 2.42, z), m["blk"], bev=0.0))
    p.append(gseg((0, 2.45, -0.5), (0, 2.95, 0.0), 0.025, m["blk"], verts=4))      # pantograph
    p.append(gseg((0, 2.45, 0.5), (0, 2.95, 0.0), 0.025, m["blk"], verts=4))
    p.append(gb((0.9, 0.04, 0.1), (0, 2.97, 0.0), m["blk"], bev=0.0))
    return p


def mountain_wagon():
    """Guitar wagon (3 behind the loco): low-sided red box wagon, deck top y 0.92, deck 1.8 x 3.2: ItemStack
    (cols 2, rows 2) at (0, 0.92, 0). Couple 3.6 m apart along +Z; loco centre to first wagon centre 3.6."""
    m = fmats()
    p = [gb((1.4, 0.3, 3.2), (0, 0.6, 0), m["blk"], bev=0.06), gb((1.8, 0.14, 3.2), (0, 0.85, 0), m["plank"], bev=0.04)]
    for z in (-1.0, 1.0):
        for x in (-0.55, 0.55):
            p.append(gc(0.3, 0.12, (x, 0.18 + 0.3, z), m["steel_d"], axis="x", verts=12))
    for x in (-0.86, 0.86):
        p.append(gb((0.08, 0.35, 3.2), (x, 1.1, 0), m["alp"], bev=0.02))
    for z in (-1.56, 1.56):
        p.append(gb((1.8, 0.35, 0.08), (0, 1.1, z), m["alp"], bev=0.02))
        p.append(gc(0.08, 0.2, (0, 0.62, z + (0.14 if z > 0 else -0.14)), m["steel_d"], axis="z", verts=8))
    return p


def rail_platform_alpine():
    """V5 platform for the mountain train: same layout as maple/rail_platform.glb (deck top y 0.40 over x -1.6..2.4,
    z -3..3; export pile at (0.6, 0.4, 0); track centre at dock-local x +3.5), red roof under snow."""
    parts = accent(rail_platform, ALP, ALP_D)()
    parts.append(snow_cap((1.9, 0.08, 0.9), (-0.6, 2.7, -2.52), rot=(10, 0, 0)))
    return parts


# ------------------------------------------------------------------ cable car (gateway)

CABLE_Y = 4.2


def _cc_station(snowy):
    m = fmats()
    p = [gb((4.0, 0.4, 4.0), (0, 0.2, 0), m["kstone"], bev=0.06)]
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(gb((0.22, 4.4, 0.22), (sx * 1.7, 2.6, sz * 1.7), m["alp_d"], bev=0.05))
    roof = M("roof", ALP, "boards", bands=10.0, dir="X")
    rp, ridge = groof(3.8, 3.8, 4.8, 28, 0.3, roof)
    p += rp
    if snowy:
        p += snow_roof(3.8, 3.8, 4.8, 28, 0.3)
    p.append(gb((3.6, 0.3, 3.6), (0, 4.7, 0), m["alp_d"], bev=0.05))
    p.append(gb((0.5, 0.4, 0.5), (0, 4.45, 0), m["steel_d"], bev=0.05))             # wheel hanger
    p.append(gb((3.4, 0.08, 1.4), (0, 0.44, 0.9), m["plank"], bev=0.02))            # boarding deck
    p.append(gb((1.6, 0.45, 0.08), (0, 3.3, 1.75), m["yellow"], bev=0.03))          # sign board
    p.append(gb((0.18, 1.0, 0.18), (1.5, 0.9, 1.5), m["alp"], bev=0.03))           # ticket post
    p.append(gb((0.4, 0.3, 0.1), (1.5, 1.45, 1.56), m["cream2"], bev=0.02))
    return p


def cablecar_station_bottom():
    """Cable car bottom station (r5_cablecar pad at (50, -47), V4 side). Cable leaves along -Z at y 4.2 from the bull-wheel
    (cablecar_bullwheel.glb at (0, 4.2, 0)); sign board face (0, 3.3, 1.79): Label3D 'CABLE CAR'. Boarding deck at +Z."""
    return _cc_station(False)


def cablecar_station_top():
    """Cable car top station at (50, -58) (V5 side), same layout as the bottom station with snow on the roof."""
    return _cc_station(True)


def cablecar_bullwheel():
    """Horizontal bull-wheel (moving part), axis = Godot Y, r 1.3, pivot at its centre; spin rotation.y while a car rides."""
    m = fmats()
    p = [gc(1.3, 0.1, (0, 0, 0), m["steel"], verts=20), gc(1.15, 0.12, (0, 0, 0), m["steel_d"], verts=20)]
    for i in range(4):
        p.append(gb((2.3, 0.06, 0.1), (0, 0.04, 0), m["alp"], bev=0.0, rot=(0, i * 45, 0)))
    p.append(gc(0.18, 0.2, (0, 0, 0), m["alp_d"], verts=10))
    return p


def cablecar_gondola():
    """Gondola (moving part). Origin = the grip on the cable (y 0); the red cabin hangs below (floor y -3.75), doors at +Z.
    Ride: tween position along the cable 4 s (GDD 9.1); at a station the floor sits at deck height 0.45."""
    m = fmats()
    p = [gc(0.12, 0.25, (0, -0.05, 0), m["steel_d"], axis="z", verts=8), gb((0.12, 1.6, 0.12), (0, -0.85, 0), m["steel_d"], bev=0.03)]
    p.append(gseg((0, -1.6, 0), (0.0, -1.9, 0.0), 0.06, m["steel_d"]))
    p.append(gb((1.4, 0.14, 1.4), (0, -1.95, 0), m["alp_d"], bev=0.05))
    p.append(gb((1.5, 1.7, 1.5), (0, -2.9, 0), m["alp"], bev=0.18, seg=2))
    for (x, z, w, d) in ((0, 0.76, 1.1, 0.04), (0, -0.76, 1.1, 0.04), (0.76, 0, 0.04, 1.1), (-0.76, 0, 0.04, 1.1)):
        p.append(gb((w, 0.6, d), (x, -2.65, z), m["wglass"], bev=0.01))
    p.append(gb((1.52, 0.14, 1.52), (0, -3.38, 0), m["cream2"], bev=0.04))
    p.append(gb((0.05, 1.3, 0.06), (0, -2.95, 0.77), m["alp_d"], bev=0.0))
    p.append(snow_cap((1.2, 0.07, 1.2), (0, -2.02, 0)))
    return p


def cablecar_cable_1m():
    """1 m of haul rope along Godot Z, flat ends, r 0.035: scale.z = span length; place at y 4.2 between the stations."""
    return [gc(0.035, 1.0, (0, 0, 0), M("rope", (0.25, 0.25, 0.27)), axis="z", verts=6)]


def cablecar_chain():
    """Closed chain across the bottom station's boarding deck before r5_cablecar (shrink to 0.01 on unlock).
    3.2 m along X at z 1.6, two posts, 'CLOSED' plate face at (0, 0.75, 1.65)."""
    m = fmats()
    p = []
    for x in (-1.6, 1.6):
        p.append(gb((0.12, 1.0, 0.12), (x, 0.5 + 0.44, 1.6), m["alp"], bev=0.03))
    pts = [(-1.6 + 3.2 * i / 8, 1.2 + 0.25 * ((i / 8 - 0.5) ** 2 * 4 - 1), 1.6) for i in range(9)]
    p.append(gtube(pts, 0.03, m["steel_d"], sides=4))
    p.append(gb((0.9, 0.35, 0.04), (0, 0.75 + 0.44, 1.62), m["alp"], bev=0.02))
    return p


# ------------------------------------------------------------------ buildings

def mountain_office():
    """Mountain Office (r5_office): log walls on a stone base, red roof under snow, window boxes. Same anchors as the
    Highland Office: door at +Z, yellow sign face (0, 2.1, 1.55) for Label3D 'OFFICE' at z 1.62, blocker (3.8, 3.0, 3.2)."""
    m = fmats()
    roof = M("roof", ALP, "boards", bands=12.0, dir="X")
    W, D = 3.6, 3.0
    p = [gb((W + 0.2, 0.6, D + 0.2), (0, 0.3, 0), m["kstone"], bev=0.08)]
    for i in range(7):                                                          # stacked log walls (front/back + sides)
        y = 0.7 + i * 0.27
        for sz in (-1, 1):
            p.append(gll(0.14, W + 0.3, (0, y, sz * D / 2), m["logw"], m["fend"], axis="x", verts=7))
        for sx in (-1, 1):
            p.append(gll(0.14, D + 0.3, (sx * W / 2, y + 0.135, 0), m["logw"], m["fend"], axis="z", verts=7))
    p.append(gb((W - 0.1, 1.9, D - 0.1), (0, 1.55, 0), m["logw"], bev=0.02))
    rp, ridge = groof(W, D, 2.55, 30, 0.45, roof)
    p += rp
    p += snow_roof(W, D, 2.55, 30, 0.45)
    p += gables(W, D, 2.55, 30, m["logw"])
    p.append(gb((0.85, 1.55, 0.1), (-0.75, 1.38, D / 2 + 0.12), m["alp"], bev=0.03))
    p.append(gc(0.04, 0.05, (-0.5, 1.35, D / 2 + 0.19), m["gold"], axis="z", verts=8))
    p += window(0.8, 1.6, D / 2 + 0.1, 0.8, 0.6, m["cream2"], m["wglass"])
    p.append(gb((0.95, 0.15, 0.2), (0.8, 1.2, D / 2 + 0.2), m["alp"], bev=0.03))
    p.append(gb((1.6, 0.14, 1.0), (-0.4, 0.07, D / 2 + 0.7), m["plank"], bev=0.03))
    p.append(gb((1.4, 0.5, 0.1), (0.0, 2.1, D / 2 + 0.12), m["yellow"], bev=0.04))
    p.append(gb((0.5, 1.1, 0.5), (1.0, ridge + 0.05, -0.6), m["kstone"], bev=0.06))
    p.append(snow_cap((0.56, 0.07, 0.56), (1.0, ridge + 0.62, -0.6)))
    return p


def market_canopy_alpine():
    return _canopy(ALP, AWNING_CREAM)


def ski_lodge():
    """Ski Lodge chalet (backdrop behind the r5_skilodge market at (60, -62)): two storeys, wide snowy eaves, red balcony.
    Front (+Z) faces the market counters. Footprint 6 x 4.6; blocker (6.0, 4.0, 4.6)."""
    m = fmats()
    roof = M("roof", ALP, "boards", bands=12.0, dir="X")
    W, D = 6.0, 4.6
    p = [gb((W + 0.2, 1.4, D + 0.2), (0, 0.7, 0), m["kstone"], bev=0.08)]
    p.append(gb((W, 2.4, D), (0, 2.6, 0), M("walls", LOGWALL, "boards", bands=22.0, dir="Y"), bev=0.04))
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(gb((0.22, 3.8, 0.22), (sx * W / 2, 1.9, sz * D / 2), m["alp_d"], bev=0.04))
    rp, ridge = groof(W, D, 3.8, 32, 0.8, roof, thick=0.2)
    p += rp
    p += snow_roof(W, D, 3.8, 32, 0.8, roof_thick=0.2)
    p += gables(W, D, 3.8, 32, M("walls2", LOGWALL, "boards", bands=22.0, dir="Y"))
    p.append(gb((1.2, 1.2, 0.1), (0, 0.65, D / 2 + 0.06), m["alp"], bev=0.03))        # door
    for x in (-2.0, 2.0):
        p += window(x, 0.85, D / 2 + 0.06, 0.9, 0.7, m["cream2"], m["wglass"])
    for x in (-1.8, 0.0, 1.8):
        p += window(x, 2.7, D / 2 + 0.02, 0.8, 0.8, m["cream2"], m["wglass"])
    p.append(gb((W - 0.4, 0.12, 0.9), (0, 1.95, D / 2 + 0.45), m["plank"], bev=0.03))   # balcony
    p.append(gb((W - 0.4, 0.1, 0.08), (0, 2.6, D / 2 + 0.86), m["alp"], bev=0.02))
    for i in range(12):
        p.append(gb((0.06, 0.6, 0.06), (-W / 2 + 0.35 + i * (W - 0.7) / 11, 2.3, D / 2 + 0.86), m["alp"], bev=0.0))
    for x in (-2.6, 2.6):
        p.append(gseg((x, 1.4, D / 2 + 0.02), (x, 1.9, D / 2 + 0.85), 0.06, m["alp_d"]))
    p.append(gb((2.6, 0.45, 0.08), (0, 2.38, D / 2 + 0.92), m["yellow"], bev=0.03))   # sign 'SKI LODGE' on the balcony rail
    p.append(gb((0.6, 1.4, 0.6), (1.8, ridge + 0.2, -0.8), m["kstone"], bev=0.06))
    p.append(snow_cap((0.66, 0.08, 0.66), (1.8, ridge + 0.94, -0.8)))
    return p


def handcar_stop_alpine():
    parts = accent(handcar_stop, ALP, ALP_D)()
    parts.append(snow_cap((1.85, 0.06, 0.2), (0, 2.42, 0)))
    return parts


def handcar_alpine():
    return accent(handcar, ALP, ALP_D)()


# ------------------------------------------------------------------ landmark

def summit_observatory():
    """Summit Observatory (r5_observatory), 6 stages, 11.6 m. Door faces +Z. Footprint 6 x 6; collision cylinder r 2.4, h 8.
    stage1 rocky outcrop + stone plinth + steps, stage2 stone drum with door, stage3 timber upper floor with windows,
    stage4 red balcony ring + dome base, stage5 white dome with its slit, stage6 telescope + mast + red flag."""
    m = fmats()
    S = {}
    rocks = [blob(1.0, gpos(x, 0.2, z), (r, r * 0.9, r * 0.55), M("rock", (0.56, 0.53, 0.5)), k + 0.3, ico=2, amp=0.2)
             for k, (x, z, r) in enumerate(((-2.0, -1.4, 1.2), (1.9, -1.2, 1.3), (-2.2, 1.2, 0.9), (2.1, 1.5, 0.8), (0.0, -2.2, 1.1)))]
    S["stage1"] = rocks + [gc(2.6, 0.7, (0, 0.55, 0), m["kstone"], verts=20), gb((1.6, 0.25, 0.9), (0, 0.12, 2.8), m["kstone"], bev=0.05),
                           gb((1.6, 0.25, 0.6), (0, 0.37, 2.6), m["kstone"], bev=0.05),
                           blob(1.0, gpos(-1.6, 0.92, -1.2), (0.9, 0.7, 0.12), m["snow"], 1.0, seg=10, rings=4, amp=0.12)]
    S["stage2"] = [gc(2.1, 2.6, (0, 2.2, 0), m["kstone"], verts=20), gb((1.0, 1.8, 0.12), (0, 1.8, 2.08), m["alp"], bev=0.03),
                   gb((1.25, 0.2, 0.25), (0, 2.8, 2.1), m["alp_d"], bev=0.04)]
    S["stage2"] += window(1.45, 2.4, 1.48, 0.4, 0.55, m["cream2"], m["wglass"])
    S["stage2"] += window(-1.45, 2.4, 1.48, 0.4, 0.55, m["cream2"], m["wglass"])
    S["stage3"] = [gc(1.95, 2.0, (0, 4.5, 0), M("walls", LOGWALL, "boards", bands=24.0, dir="Y"), verts=20)]
    for i in range(8):
        a = 2 * math.pi * i / 8
        S["stage3"].append(gb((0.18, 2.0, 0.18), (1.93 * math.cos(a), 4.5, 1.93 * math.sin(a)), m["alp_d"], bev=0.03))
    S["stage3"] += window(0, 4.6, 1.93, 0.6, 0.8, m["cream2"], m["wglass"])
    S["stage3"] += window(1.93, 4.6, 0, 0.6, 0.8, m["cream2"], m["wglass"], face="x")
    S["stage3"] += window(-1.93, 4.6, 0, 0.6, 0.8, m["cream2"], m["wglass"], face="x")
    s4 = [gc(2.5, 0.18, (0, 5.6, 0), m["alp_d"], verts=20)]
    rail = _add("primitive_torus_add", major_radius=2.4, minor_radius=0.05, major_segments=24, minor_segments=4, location=gpos(0, 6.3, 0))
    _assign(rail, m["alp"]); s4.append(rail)
    for i in range(16):
        a = 2 * math.pi * i / 16
        s4.append(gb((0.06, 0.65, 0.06), (2.4 * math.cos(a), 5.98, 2.4 * math.sin(a)), m["alp"], bev=0.0))
    s4.append(gc(1.9, 0.5, (0, 5.95, 0), m["kstone"], verts=20))
    s4.append(blob(1.0, gpos(1.6, 5.75, 1.0), (0.6, 0.45, 0.08), m["snow"], 3.0, seg=8, rings=4, amp=0.15))
    S["stage4"] = s4
    dome = blob(1.0, gpos(0, 6.2, 0), (1.85, 1.85, 1.7), m["wht"], 0.0, seg=16, rings=8, amp=0.0)
    for v in dome.data.vertices:
        if v.co.z < 0:
            v.co.z = 0.0
    s5 = [dome]
    for i in range(6):                                                               # red dome ribs
        a = math.radians(30 + i * 60)
        pts = [(1.86 * math.cos(t) * math.cos(a), 6.2 + 1.71 * math.sin(t), 1.86 * math.cos(t) * math.sin(a)) for t in (0.0, 0.4, 0.8, 1.2, 1.5)]
        s5.append(gtube(pts, 0.05, m["alp"], sides=4))
    s5.append(gb((0.5, 1.6, 0.3), (0, 7.2, 1.5), m["char"], bev=0.04, rot=(-38, 0, 0)))   # telescope slit
    S["stage5"] = s5
    s6 = [gc(0.22, 2.2, (0, 7.8, 1.1), m["steel"], verts=12, r2=0.17)]
    s6[-1].rotation_euler.x = math.radians(48)
    s6[-1].location = gpos(0, 7.7, 1.45)
    s6.append(gc(0.24, 0.3, (0, 8.42, 2.2), m["gold"], verts=12))
    s6[-1].rotation_euler.x = math.radians(48); s6[-1].location = gpos(0, 8.38, 2.2)
    s6.append(gc(0.03, 2.0, (-0.9, 8.6, -0.6), m["steel_d"], verts=6))
    s6.append(gpoly([(-0.9, 9.5, -0.6), (-0.1, 9.35, -0.6), (-0.9, 9.15, -0.6)], 0.03, m["alp"]))
    s6.append(gc(0.12, 0.18, (0.9, 7.85, -0.7), m["steel"], verts=10))                  # weather station cups
    for a in (0, 120, 240):
        s6.append(gseg((0.9, 7.95, -0.7), (0.9 + 0.3 * math.cos(math.radians(a)), 7.95, -0.7 + 0.3 * math.sin(math.radians(a))), 0.015, m["steel_d"], verts=4))
    S["stage6"] = s6
    return S


# ------------------------------------------------------------------ props (world units)

def ski_rack():
    """Rack with three pairs of skis leaning on it (lodge decor)."""
    m = fmats()
    p = []
    for x in (-0.8, 0.8):
        p.append(gb((0.1, 1.3, 0.1), (x, 0.65, 0), m["alp_d"], bev=0.02))
    p.append(gb((1.8, 0.1, 0.12), (0, 1.25, 0), m["alp_d"], bev=0.02))
    for i, x in enumerate((-0.5, 0.0, 0.5)):
        sk = item_skis()
        for o in sk:
            o.matrix_world = Matrix.Translation(gpos(x, 0.75, 0.3)) @ Matrix.Rotation(math.radians(-75), 4, "X") @ o.matrix_world
        p += sk
    p.append(snow_cap((1.8, 0.05, 0.14), (0, 1.33, 0)))
    return p


def snowman():
    """Snowman with a red scarf and a carrot nose (decor), 1.3 m."""
    m = fmats()
    s = m["snow"]
    p = [blob(1.0, gpos(0, 0.32, 0), (0.42, 0.42, 0.36), s, 1.0, seg=12, rings=7, amp=0.04),
         blob(1.0, gpos(0, 0.82, 0), (0.3, 0.3, 0.27), s, 2.0, seg=12, rings=7, amp=0.04),
         blob(1.0, gpos(0, 1.18, 0), (0.21, 0.21, 0.2), s, 3.0, seg=10, rings=6, amp=0.03)]
    p.append(gc(0.24, 0.08, (0, 1.0, 0), m["alp"], verts=14))
    p.append(gb((0.1, 0.32, 0.04), (0.12, 0.85, 0.24), m["alp"], bev=0.02, rot=(0, 0, 8)))
    p.append(gc(0.035, 0.18, (0, 1.18, 0.27), M("carrot", (0.95, 0.5, 0.15)), axis="z", verts=6, r2=0.005))
    for x in (-0.07, 0.07):
        p.append(gc(0.022, 0.02, (x, 1.25, 0.19), m["blk"], axis="z", verts=6))
    for y in (0.75, 0.88):
        p.append(gc(0.03, 0.02, (0, y, 0.29), m["blk"], axis="z", verts=6))
    p.append(gseg((0.25, 0.85, 0), (0.6, 1.15, 0.05), 0.025, m["dark"], verts=4))
    p.append(gseg((-0.25, 0.85, 0), (-0.58, 1.1, -0.05), 0.025, m["dark"], verts=4))
    return p


def alpine_lamp():
    """Red street lantern with a snow cap (streets, lodge, station)."""
    m = fmats()
    return [gb((0.3, 0.12, 0.3), (0, 0.06, 0), m["alp_d"], bev=0.03), gc(0.05, 2.0, (0, 1.1, 0), m["alp"], verts=8),
            gb((0.26, 0.3, 0.26), (0, 2.25, 0), m["lamp"], bev=0.04), gc(0.22, 0.15, (0, 2.47, 0), m["alp_d"], verts=8, r2=0.03),
            blob(1.0, gpos(0, 2.55, 0), (0.17, 0.17, 0.05), m["snow"], 1.0, seg=8, rings=4, amp=0.1)]


def firewood_snow():
    """Firewood stack under a little snow roof (lodge, office decor)."""
    m = fmats()
    p = [gb((1.4, 0.1, 0.6), (0, 0.05, 0), m["dark"], bev=0.02)]
    for row in range(3):
        for i in range(5 - row % 2):
            p.append(gll(0.08, 0.55, (-0.55 + i * 0.27 + (row % 2) * 0.135, 0.18 + row * 0.15, 0), m["fbark"], m["fend"], axis="z", verts=7))
    for x in (-0.68, 0.68):
        p.append(gb((0.08, 1.0, 0.08), (x, 0.5, -0.25), m["dark"], bev=0.02))
    p.append(gb((1.6, 0.06, 0.8), (0, 1.02, 0.0), m["plank"], bev=0.02, rot=(-10, 0, 0)))
    p.append(snow_cap((1.55, 0.07, 0.75), (0, 1.08, 0.0), rot=(-10, 0, 0)))
    return p


# ------------------------------------------------------------------ plan
K, W = "kenney", "world"
T = dict(ao=0.22, grad=0.86)
PLAN = {
    "tree_frostfirA":       ("frost", lambda: frost_fir("A"), 512, K, T),
    "tree_frostfirB":       ("frost", lambda: frost_fir("B"), 512, K, T),
    "tree_frostfirC":       ("frost", lambda: frost_fir("C"), 512, K, T),
    "tree_frostfirD":       ("frost", lambda: frost_fir("D"), 512, K, T),
    "tree_frostfirA_far":   ("frost", lambda: frost_fir("A", far=True), 256, K, T),
    "tree_frostfirB_far":   ("frost", lambda: frost_fir("B", far=True), 256, K, T),
    "tree_frostfirC_far":   ("frost", lambda: frost_fir("C", far=True), 256, K, T),
    "tree_frostfirD_far":   ("frost", lambda: frost_fir("D", far=True), 256, K, T),
    "stump_frost":          ("frost", frost_stump, 256, K, dict(ao=0.45, grad=0.8)),
    "log_stack_frost":      ("frost", frost_log_stack, 256, K, dict(ao=0.4, grad=0.82)),
    "snow_drift":           ("frost", snow_drift, 128, K, dict(ao=0.5, grad=0.9)),
    "snow_rock":            ("frost", snow_rock, 256, K, dict(ao=0.4, grad=0.8)),
    "snow_bush":            ("frost", snow_bush, 128, K, dict(ao=0.4, grad=0.82)),
    "item_frost_log":       ("items", item_frost_log, 256, W, dict(ao=0.5, grad=0.85)),
    "item_dry_lumber":      ("items", item_dry_lumber, 128, W, dict(ao=0.7, grad=0.88)),
    "item_skis":            ("items", item_skis, 256, W, dict(ao=0.6, grad=0.88)),
    "item_sled":            ("items", item_sled, 256, W, dict(ao=0.35, grad=0.85)),
    "item_guitar":          ("items", item_guitar, 256, W, dict(ao=0.5, grad=0.88)),
    "drying_kiln":          ("frost", drying_kiln, 512, W, dict(ao=0.18, grad=0.82)),
    "kiln_door":            ("frost", kiln_door, 128, W, dict(ao=0.3, grad=0.92, no_ground=True)),
    "kiln_glow":            ("frost", kiln_glow, 0, W, dict(emissive=(1.0, 0.48, 0.12, 1.0))),
    "ski_workshop":         ("frost", ski_workshop, 512, W, dict(ao=0.2, grad=0.82)),
    "ski_press":            ("frost", ski_press, 128, W, dict(ao=0.3, grad=0.92, no_ground=True)),
    "sled_workshop":        ("frost", sled_workshop, 512, W, dict(ao=0.16, grad=0.82)),
    "sled_workshop_arm":    ("frost", sled_workshop_arm, 128, W, dict(ao=0.3, grad=0.9, no_ground=True)),
    "luthier_workshop":     ("frost", luthier_workshop, 512, W, dict(ao=0.18, grad=0.82)),
    "luthier_sander":       ("frost", luthier_sander, 128, W, dict(ao=0.3, grad=0.95, no_ground=True)),
    "snowcat":              ("frost", snowcat, 256, W, dict(ao=0.25, grad=0.82)),
    "mountain_loco":        ("frost", mountain_loco, 512, W, dict(ao=0.22, grad=0.8)),
    "mountain_wagon":       ("frost", mountain_wagon, 256, W, dict(ao=0.3, grad=0.8)),
    "rail_platform_alpine": ("frost", rail_platform_alpine, 512, W, dict(ao=0.25, grad=0.85)),
    "cablecar_station_bottom": ("frost", cablecar_station_bottom, 512, W, dict(ao=0.18, grad=0.84)),
    "cablecar_station_top": ("frost", cablecar_station_top, 512, W, dict(ao=0.18, grad=0.84)),
    "cablecar_bullwheel":   ("frost", cablecar_bullwheel, 128, W, dict(ao=0.3, grad=0.95, no_ground=True)),
    "cablecar_gondola":     ("frost", cablecar_gondola, 256, W, dict(ao=0.25, grad=0.85, no_ground=True)),
    "cablecar_cable_1m":    ("frost", cablecar_cable_1m, 64, W, dict(ao=0.3, grad=1.0, no_ground=True)),
    "cablecar_chain":       ("frost", cablecar_chain, 128, W, dict(ao=0.35, grad=0.85)),
    "mountain_office":      ("frost", mountain_office, 512, W, dict(ao=0.18, grad=0.82)),
    "market_canopy_alpine": ("frost", market_canopy_alpine, 256, W, dict(ao=0.18, grad=0.85)),
    "ski_lodge":            ("frost", ski_lodge, 512, W, dict(ao=0.14, grad=0.82)),
    "handcar_stop_alpine":  ("frost", handcar_stop_alpine, 256, W, dict(ao=0.22, grad=0.85)),
    "handcar_alpine":       ("frost", handcar_alpine, 256, W, dict(ao=0.3, grad=0.82)),
    "summit_observatory":   ("frost", summit_observatory, 512, W, dict(ao=0.08, grad=0.85)),
    "ski_rack":             ("frost", ski_rack, 256, W, dict(ao=0.3, grad=0.85)),
    "snowman":              ("frost", snowman, 128, W, dict(ao=0.3, grad=0.9)),
    "alpine_lamp":          ("frost", alpine_lamp, 128, W, dict(ao=0.2, grad=0.85)),
    "firewood_snow":        ("frost", firewood_snow, 256, W, dict(ao=0.3, grad=0.85)),
}

if __name__ == "__main__" and os.environ.get("M345_NO_RUN") != "1":
    run_plan(PLAN, f"{REPO}/tools/lookdev/build_m4_report.json", OUT_ROOT)
