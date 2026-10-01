"""Maple Highlands (GDD milestone M2) models -> assets/models_v3/maple/ (+ items in assets/models_v3/items/).
Same bake as every models_v3 asset. Placement + paste-ready dicts: assets/models_v3/ASSETS_M2.md.

Usage (headless, Cycles on the RTX 3060 when available):
  /home/mm/.local/bin/blender -b --python tools/lookdev/build_m2.py -- [only_name ...]
Report: tools/lookdev/build_m2_report.json. Everything here is own work (CC0).

Region accent: highland teal #2a9d8f (machines, roofs, ironwork). Build sites export ONE GLB with one child node per
stage ("stage1".."stageN", shared material and texture) so BuildSite can raise them one by one.
"""
import os

_lo = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_leftover.py")).read()
exec(compile(_lo.replace("    run_plan(PLAN,", "    pass  # run_plan(PLAN,"), "build_leftover.py", "exec"))

# ------------------------------------------------------------------ Maple Highlands palette (sRGB, docs/DESIGN.md section 13)
TEAL = (0.165, 0.616, 0.561)         # #2a9d8f region accent
TEAL_D = (0.11, 0.42, 0.39)
MAPLE_RED = (0.85, 0.31, 0.18)       # #d94f2e
MAPLE_ORANGE = (0.93, 0.54, 0.17)    # #ed8a2b
MAPLE_GOLD = (0.94, 0.71, 0.23)      # #f0b53a
MAPLE_BARK = (0.54, 0.51, 0.47)      # grey bark (GDD 7.3 "log, grey bark")
MAPLE_CUT = (0.96, 0.85, 0.66)       # pale maple wood
MAPLE_BOARD = (0.93, 0.78, 0.55)
TAG_RED = (0.86, 0.2, 0.18)
STONE = (0.60, 0.555, 0.50)
SLATE_R = (0.40, 0.38, 0.38)


# ------------------------------------------------------------------ helpers

def groof(w, d, y_eave, pitch, over, mat, thick=0.16, cx=0.0, cz=0.0):
    """Gable roof, ridge along X, centred on (cx, cz). Returns (parts, ridge_y)."""
    t = math.tan(math.radians(pitch))
    half = d / 2 + over
    panel = half / math.cos(math.radians(pitch))
    p = []
    for s in (-1, 1):
        y = y_eave + (d / 2 - half / 2) * t + thick / 2
        p.append(gb((w + 2 * over, thick, panel), (cx, y, cz + s * half / 2), mat, bev=0.05, rot=(s * pitch, 0, 0)))
    return p, y_eave + d / 2 * t


def gables(w, d, y_eave, pitch, mat, cx=0.0, cz=0.0, thick=0.12):
    rise = d / 2 * math.tan(math.radians(pitch))
    out = []
    for s in (-1, 1):
        x0, x1 = cx - w / 2 + 0.02, cx + w / 2 - 0.02
        pts = [(x0, y_eave, cz + s * (d / 2 - 0.02)), (x0, y_eave + rise - 0.05, cz), (x0, y_eave, cz - s * (d / 2 - 0.02))]
        # triangle on the side walls (ridge along X -> gables face +/-X)
        pts = [(cx + s * (w / 2 - 0.04), y_eave, cz - d / 2 + 0.04), (cx + s * (w / 2 - 0.04), y_eave, cz + d / 2 - 0.04),
               (cx + s * (w / 2 - 0.04), y_eave + rise - 0.04, cz)]
        out.append(gpoly(pts if s > 0 else list(reversed(pts)), thick, mat))
    return out


def window(x, y, z, w, h, frame, glass, face="z"):
    """Window on a wall facing +Z (face='z') or +X (face='x')."""
    if face == "z":
        return [gb((w + 0.12, h + 0.12, 0.07), (x, y, z), frame, bev=0.02), gb((w, h, 0.05), (x, y, z + 0.02), glass, bev=0.0),
                gb((0.05, h, 0.04), (x, y, z + 0.045), frame, bev=0.0)]
    return [gb((0.07, h + 0.12, w + 0.12), (x, y, z), frame, bev=0.02), gb((0.05, h, w), (x + 0.02, y, z), glass, bev=0.0),
            gb((0.04, h, 0.05), (x + 0.045, y, z), frame, bev=0.0)]


def mmats():
    m = wood_mats()
    m.update(teal=M("teal", TEAL), teal_d=M("teald", TEAL_D), stone=M("stone", STONE),
             cut=M("cut", MAPLE_CUT, "planks"), board=M("board", MAPLE_BOARD, "planks"),
             mbark=M("mbark", MAPLE_BARK, "bark"), mring=M("mring", (0.95, 0.84, 0.64), "rings"),
             white=M("white", (0.97, 0.95, 0.9)), wglass=M("wglass", (0.55, 0.72, 0.82)), tag=M("tag", TAG_RED))
    return m


# ------------------------------------------------------------------ trees (kenney units)

def maple_tree(variant, far=False):
    """Maple: short sturdy grey trunk, broad round autumn crown (red / orange / gold lumps)."""
    rnd = random.Random({"A": 5, "B": 17, "C": 29}[variant])
    bark = M("mbark", MAPLE_BARK, "bark")
    cols = {"A": (MAPLE_RED, MAPLE_ORANGE), "B": (MAPLE_ORANGE, MAPLE_GOLD), "C": (MAPLE_GOLD, MAPLE_RED)}[variant]
    la, lb = M("leafA", cols[0]), M("leafB", cols[1])
    if variant == "A":
        cz, rx, ry, rz, th = 1.12, 0.35, 0.33, 0.44, 0.78
    elif variant == "B":
        cz, rx, ry, rz, th = 1.28, 0.3, 0.29, 0.52, 0.92
    else:
        cz, rx, ry, rz, th = 1.0, 0.36, 0.34, 0.38, 0.66
    p = []
    sides = 5 if far else 7
    n = 1 if far else 3
    pts = [Vector((0, 0, -0.04 + (th + 0.1) * i / n)) for i in range(n + 1)]
    p.append(tube(pts, [0.07 - 0.03 * i / n for i in range(n + 1)], sides, bark))
    if not far:
        for k, az in enumerate((0.6, 2.7, 4.6)):
            a = Vector((0, 0, th * 0.75))
            b = a + Vector((math.cos(az) * rx * 0.55, math.sin(az) * ry * 0.55, rz * 0.6))
            p.append(tube([a, (a + b) / 2 + Vector((0, 0, 0.03)), b], [0.03, 0.022, 0.014], 5, bark))
    if far:
        p.append(blob(1.0, (0, 0, cz), (rx * 0.98, ry * 0.98, rz * 0.92), la, 1, ico=2, amp=0.1))
        p.append(blob(1.0, (-rx * 0.3, ry * 0.2, cz + rz * 0.35), (rx * 0.62, ry * 0.62, rz * 0.5), lb, 2, ico=2, amp=0.1))
        return p
    p.append(blob(1.0, (0, 0, cz), (rx * 0.84, ry * 0.84, rz * 0.82), la, 0.7, seg=9, rings=6, amp=0.08))
    az0 = rnd.uniform(0, 6.28)
    for i in range(5):
        az = az0 + i * 2 * math.pi / 5 + rnd.uniform(-0.25, 0.25)
        el = [-0.3, 0.2, 0.5, -0.05, 0.35][i]
        q = (rx * 0.52 * math.cos(az) * math.cos(el), ry * 0.52 * math.sin(az) * math.cos(el), cz + rz * 0.7 * math.sin(el))
        r = rx * rnd.uniform(0.54, 0.63)
        p.append(blob(1.0, q, (r, r, r * 1.05), la if i % 2 else lb, i + 2.1, seg=8, rings=6, amp=0.11))
    p.append(blob(1.0, (0.0, 0.02, cz + rz * 0.74), (rx * 0.48, rx * 0.48, rx * 0.5), lb, 9.3, seg=8, rings=6, amp=0.1))
    return p


def maple_stump():
    side = M("mbark", MAPLE_BARK, "bark")
    end = M("rings", (0.95, 0.84, 0.64), "rings")
    p = [_log(0.17, 0.2, (0, 0, 0.1), (0, 0, 0), side, end, verts=14)]
    for i in range(4):
        a = i * math.pi / 2 + 0.7
        rt = _add("primitive_uv_sphere_add", segments=8, ring_count=4, radius=0.075, location=(0.16 * math.cos(a), 0.16 * math.sin(a), 0.02))
        rt.scale = (1.4, 0.7, 0.6); rt.rotation_euler = (0, 0, a); _assign(rt, side); _smooth(rt); p.append(rt)
    for i in range(3):   # a few fallen leaves
        a = i * 2.1 + 0.3
        lf = _add("primitive_uv_sphere_add", segments=6, ring_count=3, radius=0.05, location=(0.3 * math.cos(a), 0.3 * math.sin(a), 0.006))
        lf.scale = (1.0, 0.7, 0.12); _assign(lf, M("lf%d" % i, (MAPLE_RED, MAPLE_ORANGE, MAPLE_GOLD)[i])); p.append(lf)
    return p


def maple_log_stack():
    side = M("mbark", MAPLE_BARK, "bark")
    end = M("rings", (0.95, 0.84, 0.64), "rings")
    p = []
    r = 0.075
    for count, row in [(4, 0.0), (3, 1.0), (2, 2.0)]:
        for i in range(count):
            x = (i - (count - 1) / 2) * 2 * r * 1.02
            p.append(_log(r * (0.96 + 0.04 * ((i * 7) % 3)), 0.66, (x, 0, r + row * r * 1.75), (math.pi / 2, 0, 0), side, end, verts=9, seg=1))
    return p


def leaf_pile():
    """Low mound of fallen maple leaves (deco scatter, kenney units ~ scale 2.2-3)."""
    p = [blob(1.0, (0, 0, 0.0), (0.26, 0.22, 0.07), M("pile", MAPLE_ORANGE), 3.0, seg=10, rings=5, amp=0.15)]
    rnd = random.Random(8)
    for i in range(9):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.05, 0.3)
        lf = _add("primitive_uv_sphere_add", segments=6, ring_count=3, radius=0.035, location=(d * math.cos(a), d * math.sin(a), 0.02 + 0.04 * (d < 0.18)))
        lf.scale = (1.0, 0.7, 0.15); lf.rotation_euler = (0, 0, a)
        _assign(lf, M("lf%d" % (i % 3), (MAPLE_RED, MAPLE_GOLD, (0.75, 0.35, 0.16))[i % 3])); p.append(lf)
    return p


def bush_autumn():
    """Round autumn bush, same footprint as nature/plant_bush (kenney units)."""
    return [blob(1.0, (0, 0, 0.13), (0.2, 0.19, 0.16), M("b1", MAPLE_RED), 1.0, seg=9, rings=6, amp=0.12),
            blob(1.0, (0.14, 0.06, 0.1), (0.14, 0.13, 0.12), M("b2", MAPLE_ORANGE), 2.0, seg=8, rings=5, amp=0.12),
            blob(1.0, (-0.12, -0.08, 0.09), (0.13, 0.12, 0.11), M("b3", MAPLE_GOLD), 3.0, seg=8, rings=5, amp=0.12)]


# ------------------------------------------------------------------ items (world metres, scale 1)

def item_maple_log():
    return [_log_along_x(0.16, 0.95, M("mbark", MAPLE_BARK, "bark"), M("rings", (0.95, 0.84, 0.64), "rings"))]


def item_beam():
    """Square maple beam 1.15 x 0.27 x 0.27 along X, ring ends."""
    side, end = M("beam", MAPLE_CUT, "planks"), M("rings", (0.93, 0.76, 0.52), "rings")
    ob = rbox(1.15, 0.27, 0.27, (0, 0, 0.135), side, bev=0.035, seg=2)
    ob.data.materials.append(end)
    for f in ob.data.polygons:
        f.material_index = 1 if abs(f.normal.x) > 0.7 else 0
    return [ob]


def item_floorboard():
    """Tongue-and-groove board 0.95 x 0.06 x 0.22 (Godot z), tongue on the +Z edge, groove line on -Z."""
    m = mmats()
    p = [gb((0.95, 0.06, 0.2), (0, 0.03, 0), m["board"], bev=0.012)]
    p.append(gb((0.95, 0.022, 0.03), (0, 0.03, 0.11), m["board"], bev=0.006))
    p.append(gb((0.96, 0.018, 0.02), (0, 0.03, -0.097), M("groove", (0.45, 0.32, 0.2)), bev=0.0))
    return p


def item_cabin_kit():
    """Strapped bundle of short beams and floorboards on skids, red tag (export only). 0.9 x 0.56 x 0.9."""
    m = mmats()
    strap = M("strap", TEAL_D)
    p = []
    for z in (-0.3, 0.3):
        p.append(gb((0.86, 0.08, 0.12), (0, 0.04, z), m["dark"], bev=0.02))
    for i in range(4):
        b = gb((0.88, 0.19, 0.2), (0, 0.18, -0.33 + i * 0.22), m["cut"], bev=0.03)
        p.append(b)
    for i in range(4):
        p.append(gb((0.2, 0.06, 0.88), (-0.33 + i * 0.22, 0.31, 0), m["board"], bev=0.012))
    for i in range(3):
        p.append(gb((0.88, 0.17, 0.27), (0, 0.43, -0.3 + i * 0.3), m["cut"], bev=0.03))
    for x in (-0.25, 0.25):
        p.append(gb((0.06, 0.56, 0.92), (x, 0.28, 0), strap, bev=0.01))
    p.append(gb((0.16, 0.12, 0.02), (0.36, 0.42, 0.465), m["tag"], bev=0.01))
    p.append(gc(0.012, 0.06, (0.3, 0.46, 0.465), m["steel_d"], axis="x", verts=6))
    return p


# ------------------------------------------------------------------ machines (world metres; Machine piles at x -2.7 / +2.7)

def beam_saw():
    """Beam Saw (r3_beamsaw): roller bed along X, big circular blade (beam_saw_blade.glb at (0, 0.95, 0.05)) under a hood."""
    m = mmats()
    p = [gb((3.8, 0.45, 1.2), (0, 0.38, 0), m["teal"], bev=0.1)]
    for x in (-1.6, 1.6):
        for z in (-0.45, 0.45):
            p.append(gb((0.16, 0.18, 0.16), (x, 0.09, z), m["steel_d"], bev=0.03))
    for z in (-0.55, 0.55):
        p.append(gb((3.9, 0.12, 0.1), (0, 0.66, z), m["yellow"], bev=0.03))
    for i in range(8):
        x = -1.7 + i * 0.48
        if abs(x) < 0.4:
            continue
        p.append(gc(0.06, 1.0, (x, 0.62, 0), m["steel"], axis="z", verts=8))
    p.append(gb((0.3, 0.9, 1.4), (0, 1.12, -0.3), m["teal_d"], bev=0.08))        # blade column behind
    hood = gc(0.66, 0.3, (0, 1.0, 0.05), m["cream"], axis="z", verts=16)
    p.append(hood)
    p.append(gb((1.4, 0.7, 0.32), (0, 0.65, 0.05), m["teal"], bev=0.05))        # lower blade housing (below the bed)
    p.append(gb((0.8, 0.6, 0.6), (0.2, 0.75, -0.95), m["yellow"], bev=0.1))     # motor
    p.append(gc(0.14, 0.2, (0.2, 1.12, -0.95), m["steel"], verts=10))
    p.append(gb((0.35, 0.5, 0.3), (1.5, 0.95, -0.75), m["yellow"], bev=0.07))
    p.append(gb((0.22, 0.16, 0.05), (1.5, 1.05, -0.58), m["green_btn"], bev=0.02))
    for k in range(2):                                                          # beams on the outfeed
        bm = item_beam()
        gmove(bm, 1.25, 0.72 + k * 0.27, -0.1 + k * 0.04)
        p += bm
    return p


def beam_saw_blade():
    """Big blade for the beam saw, r 0.55, disc normal along Godot Z, pivot at its centre."""
    st, mark = M("steel", (0.80, 0.82, 0.85)), M("mark", TEAL)
    p = [gc(0.5, 0.035, (0, 0, 0), st, axis="z", verts=28)]
    for i in range(22):
        a = 2 * math.pi * i / 22
        p.append(gb((0.09, 0.07, 0.035), (0.52 * math.cos(a), 0.52 * math.sin(a), 0), st, bev=0.0, rot=(0, 0, math.degrees(a) + 30)))
    for i in range(4):
        a = 2 * math.pi * i / 4 + 0.4
        p.append(gb((0.2, 0.06, 0.04), (0.28 * math.cos(a), 0.28 * math.sin(a), 0), mark, bev=0.0, rot=(0, 0, math.degrees(a))))
    p.append(gc(0.08, 0.06, (0, 0, 0), M("hub", (0.35, 0.35, 0.36)), axis="z", verts=12))
    return p


def planer_mill():
    """Planer Mill (r3_planer): infeed table, teal planer body, outfeed with floorboards, chip pipe to a cyclone at the back."""
    m = mmats()
    p = [gb((1.1, 0.08, 0.9), (-1.25, 0.86, 0), m["steel"], bev=0.03), gb((1.0, 0.08, 0.9), (1.3, 0.86, 0), m["steel"], bev=0.03)]
    for x in (-1.7, -0.8, 0.85, 1.75):
        for z in (-0.35, 0.35):
            p.append(gb((0.08, 0.82, 0.08), (x, 0.41, z), m["steel_d"], bev=0.02))
    p.append(gb((1.3, 1.0, 1.3), (0, 0.65, 0), m["teal"], bev=0.12))
    p.append(gb((1.36, 0.3, 1.36), (0, 1.3, 0), m["cream"], bev=0.1))
    p.append(gb((1.2, 0.12, 0.2), (0, 0.95, 0.6), m["yellow"], bev=0.03))
    p.append(gb((0.22, 0.16, 0.05), (0.45, 0.6, 0.67), m["green_btn"], bev=0.02))
    for k in range(3):
        fb = item_floorboard()
        gmove(fb, 1.3, 0.9 + k * 0.065, -0.2 + k * 0.03)
        p += fb
    # chip pipe up and back to the cyclone
    pipe = M("pipe", (0.75, 0.76, 0.75))
    p.append(gseg((0, 1.4, -0.3), (0, 2.45, -0.6), 0.1, pipe, verts=8))
    p.append(gseg((0, 2.45, -0.6), (0.9, 2.55, -1.1), 0.1, pipe, verts=8))
    p.append(gc(0.42, 0.6, (1.1, 2.5, -1.15), m["teal"], verts=16))
    p.append(gc(0.42, 0.9, (1.1, 1.75, -1.15), m["teal"], verts=16, r2=0.1))
    p.append(gc(0.3, 0.12, (1.1, 2.86, -1.15), m["teal_d"], verts=14))
    for a in (0.3, 2.4, 4.5):
        p.append(gseg((1.1 + 0.4 * math.cos(a), 2.2, -1.15 + 0.4 * math.sin(a)), (1.1 + 0.6 * math.cos(a), 0.0, -1.15 + 0.6 * math.sin(a)), 0.035, m["steel_d"]))
    p.append(gb((0.36, 0.3, 0.36), (1.1, 0.15, -1.15), m["cut"], bev=0.05))     # chip bin
    return p


def planer_roller():
    """Fluted feed roller at the planer mouth (spinner), axis along Godot Z, pivot at its centre. Place at (-0.66, 1.0, 0)."""
    st = M("steel", (0.62, 0.64, 0.66))
    p = [gc(0.11, 1.0, (0, 0, 0), st, axis="z", verts=12)]
    for i in range(6):
        a = 2 * math.pi * i / 6
        p.append(gb((0.04, 0.04, 1.0), (0.11 * math.cos(a), 0.11 * math.sin(a), 0), M("flute", YELLOW), bev=0.0, rot=(0, 0, math.degrees(a))))
    return p


def kit_factory():
    """Cabin Kit Factory (r3_kitfactory, ASSEMBLER). Beam intake at (-3.0, 0, -1.45), floorboard intake at (-3.0, 0, 1.45),
    output at (3.0, 0, 0). Strapping portal over the assembly table; the press head is kit_factory_press.glb."""
    m = mmats()
    roof = M("roof", TEAL, "boards", bands=12.0, dir="X")
    walls = M("walls", CREAM, "boards", bands=16.0, dir="X")
    p = [gb((4.6, 0.2, 4.0), (0, 0.1, 0), m["grey"], bev=0.07)]
    p.append(gb((4.4, 2.8, 0.16), (0, 1.6, -1.9), walls, bev=0.04))
    for s in (-1, 1):
        p.append(gb((0.2, 2.9, 0.2), (s * 2.2, 1.45, -1.9), m["dark"], bev=0.05))
        p.append(gb((0.2, 2.6, 0.2), (s * 2.2, 1.3, -0.5), m["dark"], bev=0.05))
    p.append(gb((4.6, 0.18, 0.2), (0, 2.62, -0.5), m["dark"], bev=0.05))
    p.append(gb((5.0, 0.16, 1.9), (0, 3.0, -1.2), roof, bev=0.05, rot=(12, 0, 0)))
    # intake roller tables (both from the -X side) and the assembly table
    for z in (-1.2, 1.2):
        p.append(gb((1.4, 0.1, 0.8), (-1.5, 0.78, z), m["steel"], bev=0.03))
        for i in range(4):
            p.append(gc(0.035, 0.76, (-2.05 + i * 0.36, 0.85, z), m["steel_d"], axis="z", verts=8))
        for x in (-2.1, -0.9):
            p.append(gb((0.07, 0.7, 0.07), (x, 0.45, z - 0.3), m["steel_d"], bev=0.02))
            p.append(gb((0.07, 0.7, 0.07), (x, 0.45, z + 0.3), m["steel_d"], bev=0.02))
        p.append(gb((0.12, 0.08, 0.84), (-2.25, 0.86, z), m["yellow"], bev=0.02))
    p.append(gb((1.9, 0.75, 1.8), (0.1, 0.48, 0), m["teal"], bev=0.1))
    p.append(gb((1.95, 0.08, 1.85), (0.1, 0.89, 0), m["steel"], bev=0.03))
    for z in (-1.0, 1.0):
        p.append(gb((0.26, 2.0, 0.26), (0.1, 1.9, z), m["teal_d"], bev=0.07))
    p.append(gb((0.36, 0.34, 2.4), (0.1, 2.95, 0), m["teal_d"], bev=0.09))
    p.append(gb((0.4, 0.08, 2.45), (0.1, 3.14, 0), m["yellow"], bev=0.03))
    p.append(gc(0.13, 0.3, (0.1, 2.65, 0), m["steel"], verts=10))
    # output roller to +X with a finished kit
    p.append(gb((1.3, 0.1, 0.9), (1.75, 0.78, 0), m["steel"], bev=0.03))
    for i in range(4):
        p.append(gc(0.035, 0.86, (1.25 + i * 0.34, 0.85, 0), m["steel_d"], axis="z", verts=8))
    for x in (1.2, 2.3):
        for z in (-0.35, 0.35):
            p.append(gb((0.07, 0.7, 0.07), (x, 0.45, z), m["steel_d"], bev=0.02))
    kit = item_cabin_kit()
    gmove(kit, 1.75, 0.83, 0)
    p += kit
    p.append(gb((0.4, 0.55, 0.3), (-1.0, 0.48, -1.75), m["yellow"], bev=0.07))
    p.append(gb((0.24, 0.16, 0.05), (-1.0, 0.6, -1.58), m["green_btn"], bev=0.02))
    return p


def kit_factory_press():
    """Strapping press head (Machine.plates): pivot = top of the plate; tween y 1.75 (up) to 1.0 (on the kit)."""
    m = mmats()
    return [gb((1.1, 0.14, 1.1), (0, -0.07, 0), m["steel"], bev=0.04), gc(0.08, 0.9, (0, 0.45, 0), m["steel"], verts=10),
            gb((1.12, 0.05, 0.12), (0, -0.12, 0), m["yellow"], bev=0.0)]


# ------------------------------------------------------------------ workers, rail, train

def forklift():
    """Forklift hauler (r3_forklift1). Forks to +Z (Walker turns the model's +Z to the walk direction).
    Carry anchor = ItemStack at (0, 0.2, 1.05)."""
    m = mmats()
    blk = M("blk", (0.22, 0.22, 0.24))
    p = [gb((1.1, 0.55, 1.5), (0, 0.55, -0.2), m["teal"], bev=0.14)]
    p.append(gb((1.12, 0.5, 0.45), (0, 0.6, -0.85), m["teal_d"], bev=0.16))          # counterweight
    p.append(gb((0.5, 0.12, 0.45), (0, 0.9, -0.35), blk, bev=0.05))                  # seat
    p.append(gb((0.5, 0.45, 0.1), (0, 1.12, -0.58), blk, bev=0.04))
    p.append(gc(0.03, 0.4, (0, 1.05, 0.2), blk, verts=6))
    p.append(gc(0.16, 0.03, (0, 1.25, 0.2), blk, verts=10))
    for x in (-0.48, 0.48):
        for z in (-0.7, 0.3):
            p.append(gc(0.07 if z < 0 else 0.06, 1.25, (x, 1.48, z), blk, verts=6))
        p.append(gc(0.26, 0.24, (x, 0.26, 0.4), m["tyre"], axis="x", verts=12))
        p.append(gc(0.22, 0.22, (x, 0.22, -0.72), m["tyre"], axis="x", verts=12))
    p.append(gb((1.1, 0.07, 1.15), (0, 2.12, -0.2), blk, bev=0.03))
    for x in (-0.36, 0.36):
        p.append(gb((0.1, 2.1, 0.12), (x, 1.05, 0.66), m["yellow"], bev=0.03))
        p.append(gb((0.1, 0.05, 0.85), (x * 0.6, 0.1, 1.15), m["steel_d"], bev=0.01))
        p.append(gb((0.1, 0.5, 0.05), (x * 0.6, 0.33, 0.73), m["steel_d"], bev=0.01))
    p.append(gb((0.85, 0.12, 0.08), (0, 0.55, 0.74), m["steel_d"], bev=0.02))
    p.append(gb((0.85, 0.1, 0.08), (0, 2.05, 0.66), m["yellow"], bev=0.02))
    p.append(gb((0.16, 0.1, 0.1), (0.4, 2.2, -0.65), M("beacon", (1.0, 0.6, 0.15)), bev=0.03))
    return p


RAIL_TOP = 0.18
GAUGE = 1.0


def rail_straight_4m():
    """4 m of track along Godot Z, centred, gauge 1.0, rail top y 0.18, FLAT rail ends: tile every 4.0 m."""
    sleeper, steel = M("sleeper", (0.48, 0.34, 0.24), "planks"), M("rail", (0.62, 0.6, 0.58))
    p = []
    for i in range(5):
        p.append(gb((1.6, 0.08, 0.24), (0, 0.04, -1.6 + i * 0.8), sleeper, bev=0.02))
    for s in (-1, 1):
        p.append(prism([(s * GAUGE / 2 - 0.045, 0.08), (s * GAUGE / 2 + 0.045, 0.08), (s * GAUGE / 2 + 0.02, 0.15),
                        (s * GAUGE / 2 + 0.035, 0.15), (s * GAUGE / 2 + 0.035, RAIL_TOP), (s * GAUGE / 2 - 0.035, RAIL_TOP),
                        (s * GAUGE / 2 - 0.035, 0.15), (s * GAUGE / 2 - 0.02, 0.15)], -2.0, 2.0, steel))
    return p


def rail_bumper():
    """Buffer stop at the end of a track (track along Z, the stop faces +Z); place at the last rail end."""
    m = mmats()
    p = [gb((1.6, 0.08, 0.24), (0, 0.04, 0), M("sleeper", (0.48, 0.34, 0.24), "planks"), bev=0.02)]
    for x in (-0.55, 0.55):
        p.append(gb((0.14, 0.75, 0.14), (x, 0.45, 0), m["dark"], bev=0.04))
        p.append(gseg((x, 0.1, -0.6), (x, 0.7, 0.0), 0.05, m["dark"]))
    p.append(gb((1.5, 0.28, 0.18), (0, 0.72, 0.05), M("bumper", TAG_RED), bev=0.06))
    for x in (-0.4, 0.0, 0.4):
        p.append(gb((0.16, 0.29, 0.19), (x, 0.72, 0.05), m["white"], bev=0.02))
    return p


def handcar():
    """Pump handcar for the handcar stops (decor). On rails of gauge 1.0 (wheels on the rail top at y 0.18); along Z."""
    m = mmats()
    red = M("red", (0.74, 0.25, 0.18))
    p = [gb((1.3, 0.1, 1.6), (0, 0.55, 0), m["plank"], bev=0.03)]
    p.append(gb((1.1, 0.14, 1.4), (0, 0.44, 0), m["teal_d"], bev=0.04))
    for x in (-0.5, 0.5):
        for z in (-0.5, 0.5):
            p.append(gc(0.22, 0.07, (x, RAIL_TOP + 0.22, z), red, axis="x", verts=12))
    p.append(gb((0.16, 0.75, 0.16), (0, 0.97, 0), m["teal"], bev=0.04))
    p.append(gc(0.08, 0.22, (0, 1.35, 0), m["teal_d"], axis="x", verts=10))
    p.append(gb((0.08, 0.08, 1.5), (0, 1.38, 0), m["teal"], bev=0.03, rot=(10, 0, 0)))
    for z in (-0.74, 0.74):
        p.append(gc(0.035, 0.7, (0, 1.38 - z * 0.17, z), m["dark"], axis="x", verts=8))
    return p


def handcar_tile():
    """One destination tile (GDD 7.6 E): 1.6 x 1.6, top y 0.06, plank floor with a yellow rim. Label3D on top."""
    m = mmats()
    p = [gb((1.6, 0.05, 1.6), (0, 0.025, 0), m["yellow"], bev=0.02)]
    for i in range(5):
        p.append(gb((1.4, 0.03, 0.26), (0, 0.06, -0.56 + i * 0.28), m["plank"], bev=0.01))
    return p


def handcar_stop():
    """Handcar stop sign + bench + lamp (hub decor). Sign board face at z +0.07, centre (0, 2.0, 0): Label3D 'HANDCAR'."""
    m = mmats()
    p = []
    for x in (-0.75, 0.75):
        p.append(gb((0.12, 2.5, 0.12), (x, 1.25, 0), m["teal"], bev=0.03))
    p.append(gb((1.8, 0.6, 0.1), (0, 2.0, 0), m["cream"], bev=0.04))
    p.append(gb((1.9, 0.08, 0.16), (0, 2.34, 0), m["teal_d"], bev=0.03))
    p.append(gc(0.08, 0.18, (0, 2.48, 0), m["teal_d"], verts=10))
    bx = 1.7
    p.append(gb((1.2, 0.07, 0.4), (bx, 0.48, 0.2), m["plank"], bev=0.02))
    p.append(gb((1.2, 0.3, 0.06), (bx, 0.72, 0.0), m["plank"], bev=0.02))
    for sx in (-1, 1):
        p.append(gb((0.06, 0.48, 0.4), (bx + sx * 0.52, 0.24, 0.2), m["teal_d"], bev=0.02))
    p += lantern_post_parts(-1.7, 0.2, m)
    return p


def lantern_post_parts(x, z, m):
    return [gb((0.3, 0.12, 0.3), (x, 0.06, z), m["teal_d"], bev=0.03), gc(0.05, 2.0, (x, 1.1, z), m["teal"], verts=8),
            gb((0.26, 0.3, 0.26), (x, 2.25, z), M("lamp", (1.0, 0.88, 0.55)), bev=0.04),
            gc(0.2, 0.15, (x, 2.47, z), m["teal_d"], verts=8, r2=0.03)]


def lantern_post():
    """Village street lantern (decor)."""
    return lantern_post_parts(0, 0, mmats())


def train_loco():
    """Highland Railway locomotive (r3_rail). Front at -Z (it drives toward -Z with rotation 0, like the barge).
    Gauge 1.0, rail top 0.18. Origin = track centre at ground."""
    m = mmats()
    red = M("red", (0.74, 0.25, 0.18))
    blk = M("blk", (0.22, 0.22, 0.24))
    gold = M("gold", (1.0, 0.8, 0.25))
    p = [gb((1.5, 0.3, 4.0), (0, 0.62, 0), blk, bev=0.06)]
    for z in (-1.25, 0.0, 1.25):
        for x in (-0.55, 0.55):
            p.append(gc(0.32, 0.12, (x, RAIL_TOP + 0.32, z), red, axis="x", verts=14))
    for x in (-0.6, 0.6):
        p.append(gb((0.06, 0.06, 2.6), (x, RAIL_TOP + 0.32, 0), m["steel"], bev=0.0))
    p.append(gc(0.55, 2.4, (0, 1.33, -0.75), m["teal"], axis="z", verts=16))
    p.append(gc(0.58, 0.1, (0, 1.33, -1.9), m["teal_d"], axis="z", verts=16))
    for z in (-1.3, -0.3):
        p.append(gc(0.57, 0.08, (0, 1.33, z), gold, axis="z", verts=16))
    p.append(gc(0.14, 0.55, (0, 2.05, -1.45), blk, verts=10))
    p.append(gc(0.26, 0.22, (0, 2.38, -1.45), blk, verts=12, r2=0.17))
    p.append(gc(0.17, 0.3, (0, 1.95, -0.6), gold, verts=12))
    p.append(gb((1.6, 1.3, 1.3), (0, 1.55, 1.15), m["teal"], bev=0.08))
    p.append(gb((1.8, 0.12, 1.55), (0, 2.27, 1.15), m["cream"], bev=0.05))
    for x in (-0.81, 0.81):
        p.append(gb((0.05, 0.5, 0.6), (x, 1.75, 1.05), m["wglass"], bev=0.02))
    p.append(gpoly([(-0.75, 0.3, -2.0), (0.75, 0.3, -2.0), (0, 0.3, -2.55)], 0.35, red))   # cow catcher
    p.append(gc(0.13, 0.12, (0, 1.6, -2.0), M("lamp", (1.0, 0.92, 0.6)), axis="z", verts=10))
    for x in (-0.55, 0.55):
        p.append(gc(0.09, 0.2, (x, 0.65, 2.05), red, axis="z", verts=8))
    return p


def train_wagon():
    """Flat wagon with stakes (r3_rail, 3 wagons x 4 kits, 5 with r3_rail2). Deck top y 0.92, deck 1.8 x 3.2:
    ItemStack (cols 2, rows 2) at (0, 0.92, 0). Couple wagons 3.6 m apart along +Z behind the loco (loco centre to first wagon 3.8)."""
    m = mmats()
    red = M("red", (0.74, 0.25, 0.18))
    blk = M("blk", (0.22, 0.22, 0.24))
    p = [gb((1.4, 0.3, 3.2), (0, 0.6, 0), blk, bev=0.06), gb((1.8, 0.14, 3.2), (0, 0.85, 0), m["plank"], bev=0.04)]
    for z in (-1.0, 1.0):
        for x in (-0.55, 0.55):
            p.append(gc(0.3, 0.12, (x, RAIL_TOP + 0.3, z), red, axis="x", verts=12))
    for x in (-0.86, 0.86):
        for z in (-1.5, 0.0, 1.5):
            p.append(gb((0.08, 0.45, 0.08), (x, 1.1, z), m["teal"], bev=0.02))
    for z in (-1.7, 1.7):
        p.append(gc(0.08, 0.2, (0, 0.62, z), m["steel_d"], axis="z", verts=8))
    return p


def rail_platform():
    """Railway loading platform (the train's TruckDock). Origin = dock origin; deck top y 0.40 over x -1.6..2.4, z -3..3;
    export pile at (0.6, 0.4, 0); track centre line at x +3.5 (lay rail_straight_4m there)."""
    m = mmats()
    roof = M("roof", TEAL, "boards", bands=10.0, dir="X")
    p = [gb((4.0, 0.4, 6.0), (0.4, 0.2, 0), m["stone"], bev=0.06), gb((4.0, 0.06, 6.0), (0.4, 0.4, 0), m["plank"], bev=0.02)]
    p.append(gb((0.12, 0.012, 6.0), (2.25, 0.435, 0), m["yellow"], bev=0.0))
    # shelter at the back-left with a bench, bell post at the front
    for x in (-1.4, 0.2):
        for z in (-2.8, -1.8):
            p.append(gb((0.12, 2.1, 0.12), (x, 1.45, z), m["dark"], bev=0.03))
    p.append(gb((2.1, 0.12, 1.5), (-0.6, 2.55, -2.3), roof, bev=0.04, rot=(10, 0, 0)))
    p.append(gb((1.5, 0.9, 0.08), (-0.6, 0.9, -2.85), m["plank"], bev=0.02))
    p.append(gb((1.2, 0.07, 0.36), (-0.6, 0.85, -2.55), m["furn"], bev=0.02))
    p.append(gb((0.1, 1.5, 0.1), (1.9, 1.15, 2.6), m["teal"], bev=0.03))
    p.append(gb((0.5, 0.08, 0.08), (1.75, 1.9, 2.6), m["teal"], bev=0.02))
    p.append(gc(0.12, 0.2, (1.6, 1.75, 2.6), M("gold", (1.0, 0.8, 0.25)), verts=10, r2=0.06))
    p += lantern_post_parts(1.9, -2.6, m)
    return p


# ------------------------------------------------------------------ buildings

def highland_office():
    """Highland Office (r3_office): stone base, cream boards, teal roof. Door + porch at +Z; sign board face at
    (0, 2.1, 1.55): Label3D 'OFFICE' at z 1.62. Footprint 3.8 x 3.2, blocker (3.8, 3.0, 3.2)."""
    m = mmats()
    walls = M("walls", CREAM, "boards", bands=16.0, dir="Z")
    roof = M("roof", TEAL, "boards", bands=12.0, dir="X")
    W, D = 3.6, 3.0
    p = [gb((W + 0.2, 0.7, D + 0.2), (0, 0.35, 0), m["stone"], bev=0.08)]
    p.append(gb((W, 1.8, D), (0, 1.6, 0), walls, bev=0.04))
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(gb((0.16, 1.85, 0.16), (sx * W / 2, 1.62, sz * D / 2), m["teal_d"], bev=0.03))
    rp, ridge = groof(W, D, 2.5, 34, 0.35, roof)
    p += rp
    p += gables(W, D, 2.5, 34, walls)
    p.append(gb((0.85, 1.55, 0.08), (-0.75, 1.48, D / 2 + 0.02), m["door"], bev=0.03))
    p.append(gc(0.04, 0.05, (-0.5, 1.4, D / 2 + 0.08), m["yellow"], axis="z", verts=8))
    p += window(0.8, 1.7, D / 2 + 0.01, 0.8, 0.6, m["white"], m["wglass"])
    p += window(W / 2 + 0.01, 1.7, 0.0, 0.8, 0.6, m["white"], m["wglass"], face="x")
    p.append(gb((1.6, 0.14, 1.0), (-0.4, 0.07, D / 2 + 0.6), m["plank"], bev=0.03))
    p.append(gb((1.4, 0.5, 0.1), (0.0, 2.1, D / 2 + 0.05), m["yellow"], bev=0.04))
    p.append(gb((0.5, 1.2, 0.5), (1.0, ridge + 0.1, -0.6), m["stone"], bev=0.06))
    return p


def market_canopy_teal():
    return _canopy(TEAL, AWNING_CREAM)


def _house(kind):
    m = mmats()
    S = {}
    if kind == "cottage":
        W, D, H, pitch = 4.4, 3.6, 2.3, 40
        wall = M("walls", (0.97, 0.93, 0.84), "boards", bands=14.0, dir="Z")
        roofm = M("roof", (0.74, 0.27, 0.2), "boards", bands=12.0, dir="X")
    elif kind == "farmhouse":
        W, D, H, pitch = 5.2, 4.0, 2.5, 36
        wall = M("walls", (0.93, 0.76, 0.43), "boards", bands=14.0, dir="Z")
        roofm = M("roof", SLATE_R, "boards", bands=12.0, dir="X")
    elif kind == "school":
        W, D, H, pitch = 5.4, 4.0, 2.7, 34
        wall = M("walls", (0.97, 0.95, 0.9), "boards", bands=16.0, dir="Z")
        roofm = M("roof", TEAL, "boards", bands=12.0, dir="X")
    else:  # inn (two storeys)
        W, D, H, pitch = 5.4, 4.4, 4.6, 38
        wall = M("walls", (0.97, 0.92, 0.8), "boards", bands=14.0, dir="Z")
        roofm = M("roof", TEAL, "boards", bands=12.0, dir="X")
    b = 0.35   # plinth height
    # stage 1: stone plinth + steps
    S["stage1"] = [gb((W + 0.3, b, D + 0.3), (0, b / 2, 0), m["stone"], bev=0.08),
                   gb((1.4, 0.18, 0.5), (0 if kind != "farmhouse" else -1.2, 0.09, D / 2 + 0.38), m["stone"], bev=0.04)]
    # stage 2: timber frame (corner posts, mid posts, top ring)
    s2 = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            s2.append(gb((0.18, H, 0.18), (sx * W / 2, b + H / 2, sz * D / 2), m["dark"], bev=0.04))
        s2.append(gb((0.15, H, 0.15), (sx * W / 4, b + H / 2, D / 2), m["dark"], bev=0.03))
    for sz in (-1, 1):
        s2.append(gb((W + 0.1, 0.16, 0.16), (0, b + H, sz * D / 2), m["dark"], bev=0.04))
    for sx in (-1, 1):
        s2.append(gb((0.16, 0.16, D + 0.1), (sx * W / 2, b + H, 0), m["dark"], bev=0.04))
    if kind == "inn":
        for sz in (-1, 1):
            s2.append(gb((W + 0.1, 0.14, 0.14), (0, b + 2.1, sz * D / 2 + sz * 0.02), m["dark"], bev=0.03))
    S["stage2"] = s2
    # stage 3: walls, door, windows
    s3 = []
    if kind == "inn":
        s3.append(gb((W - 0.06, 2.1, D - 0.06), (0, b + 1.05, 0), m["stone"], bev=0.04))
        s3.append(gb((W - 0.06, H - 2.1, D - 0.06), (0, b + 2.1 + (H - 2.1) / 2, 0), wall, bev=0.04))
        for x in (-1.6, 1.6):   # half-timbering on the upper floor
            s3.append(gb((0.1, H - 2.1, 0.06), (x, b + 2.1 + (H - 2.1) / 2, D / 2 + 0.01), m["dark"], bev=0.0))
            s3.append(gseg((x - 0.55, b + 2.2, D / 2 + 0.02), (x + 0.55, b + H - 0.1, D / 2 + 0.02), 0.04, m["dark"]))
    else:
        s3.append(gb((W - 0.06, H, D - 0.06), (0, b + H / 2, 0), wall, bev=0.04))
    door_x = -1.2 if kind == "farmhouse" else 0.0
    s3.append(gb((0.9, 1.7, 0.08), (door_x, b + 0.85, D / 2 + 0.01), m["door"], bev=0.03))
    s3.append(gc(0.04, 0.05, (door_x + 0.28, b + 0.85, D / 2 + 0.07), m["yellow"], axis="z", verts=8))
    wy = b + 1.35
    wins = {"cottage": [-1.4, 1.4], "farmhouse": [0.5, 1.7], "school": [-1.7, -0.75, 0.75, 1.7], "inn": [-1.7, 1.7]}[kind]
    for x in wins:
        s3 += window(x, wy, D / 2 + 0.0, 0.75 if kind != "school" else 0.55, 0.7, m["white"], m["wglass"])
    s3 += window(W / 2, wy, 0.0, 0.75, 0.65, m["white"], m["wglass"], face="x")
    if kind == "inn":
        for x in (-1.6, 0.0, 1.6):
            s3 += window(x, b + 3.2, D / 2 + 0.0, 0.7, 0.65, m["white"], m["wglass"])
    S["stage3"] = s3
    # stage 4: roof and details
    s4, ridge = groof(W, D, b + H, pitch, 0.35, roofm)
    s4 += gables(W, D, b + H, pitch, wall)
    if kind in ("cottage", "inn", "farmhouse"):
        cx = 1.3 if kind != "farmhouse" else -1.6
        s4.append(gb((0.55, 1.3, 0.55), (cx, ridge - 0.2, -0.5), m["stone"], bev=0.06))
        s4.append(gb((0.65, 0.12, 0.65), (cx, ridge + 0.5, -0.5), M("cap", (0.45, 0.42, 0.4)), bev=0.03))
    if kind == "cottage":
        s4.append(gb((1.0, 0.18, 0.24), (-1.4, wy - 0.5, D / 2 + 0.14), m["plank"], bev=0.03))
        for k in range(3):
            s4.append(blob(1.0, gpos(-1.72 + k * 0.32, wy - 0.36, D / 2 + 0.14), (0.14, 0.1, 0.09), M("fl%d" % (k % 2), (0.93, 0.33, 0.3) if k % 2 == 0 else (0.98, 0.84, 0.25)), k, seg=6, rings=4, amp=0.1))
    if kind == "farmhouse":   # porch roof over the door + dormer
        s4.append(gb((2.0, 0.1, 1.1), (-1.2, b + 2.1, D / 2 + 0.5), roofm, bev=0.03, rot=(14, 0, 0)))
        for x in (-2.0, -0.4):
            s4.append(gb((0.1, 2.0, 0.1), (x, b + 1.0, D / 2 + 0.95), m["dark"], bev=0.02))
        s4.append(gb((1.0, 0.8, 0.9), (0.9, ridge - 0.9, 0.85), wall, bev=0.03))
        s4 += window(0.9, ridge - 0.9, 1.31, 0.5, 0.45, m["white"], m["wglass"])
        s4.append(gb((1.2, 0.1, 1.15), (0.9, ridge - 0.42, 0.85), roofm, bev=0.03, rot=(10, 0, 0)))
    if kind == "school":      # bell tower on the ridge
        s4.append(gb((0.9, 0.8, 0.9), (0, ridge + 0.2, 0), M("white2", (0.97, 0.95, 0.9)), bev=0.04))
        for sx in (-1, 1):
            for sz in (-1, 1):
                s4.append(gb((0.1, 0.7, 0.1), (sx * 0.38, ridge + 0.95, sz * 0.38), m["white"], bev=0.02))
        s4.append(gc(0.17, 0.3, (0, ridge + 0.95, 0), M("bell", (1.0, 0.8, 0.25)), verts=10, r2=0.08))
        s4.append(gc(0.72, 0.9, (0, ridge + 1.75, 0), m["teal"], verts=4, r2=0.02))
        s4.append(gb((1.0, 0.35, 0.06), (0, b + H - 0.25, D / 2 + 0.05), m["yellow"], bev=0.03))
    if kind == "inn":         # hanging sign on a bracket
        s4.append(gb((0.08, 0.08, 0.8), (W / 2 - 0.4, b + 2.5, D / 2 + 0.4), m["dark"], bev=0.02))
        s4.append(gb((0.7, 0.5, 0.06), (W / 2 - 0.4, b + 2.1, D / 2 + 0.72), m["yellow"], bev=0.03))
        s4.append(gb((0.06, 0.25, 0.25), (W / 2 - 0.4, b + 2.1, D / 2 + 0.76), M("mug", (0.85, 0.5, 0.2)), bev=0.02))
    S["stage4"] = s4
    return S


def house_cottage():
    return _house("cottage")


def house_farmhouse():
    return _house("farmhouse")


def house_school():
    return _house("school")


def house_inn():
    return _house("inn")


def house_barn():
    """Barn (r3_house3): red walls, grey gambrel roof, big white-trim doors at +Z, hayloft door, hay bales."""
    m = mmats()
    red = M("walls", (0.74, 0.22, 0.17), "boards", bands=18.0, dir="X")
    red_s = M("walls2", (0.74, 0.22, 0.17), "boards", bands=18.0, dir="Z")
    roofm = M("roof", (0.45, 0.43, 0.42), "boards", bands=12.0, dir="Z")
    hay = M("hay", (0.93, 0.8, 0.42), "planks")
    W, D, H, b = 4.8, 5.4, 2.6, 0.3   # gable faces +Z (the camera) like the Boathouse
    S = {"stage1": [gb((W + 0.3, b, D + 0.3), (0, b / 2, 0), m["stone"], bev=0.08)]}
    s2 = []
    for sx in (-1, 1):
        for sz in (-1, 0, 1):
            s2.append(gb((0.18, H, 0.18), (sx * W / 2, b + H / 2, sz * D / 2), m["dark"], bev=0.04))
        s2.append(gb((0.16, 0.16, D + 0.1), (sx * W / 2, b + H, 0), m["dark"], bev=0.04))
    for sz in (-1, 1):
        s2.append(gb((W + 0.1, 0.16, 0.16), (0, b + H, sz * D / 2), m["dark"], bev=0.04))
    S["stage2"] = s2
    body = gb((W - 0.06, H, D - 0.06), (0, b + H / 2, 0), red_s, bev=0.04)
    body.data.materials.append(red)
    for f in body.data.polygons:
        f.material_index = 1 if abs(f.normal.y) > 0.5 else 0
    s3 = [body]
    fz = D / 2
    s3.append(gb((2.0, 2.0, 0.08), (0, b + 1.0, fz + 0.01), M("inside", DOOR_DARK), bev=0.02))
    for x in (-0.5, 0.5):   # two door leaves with white X braces
        s3.append(gb((0.95, 1.95, 0.08), (x, b + 0.98, fz + 0.04), red, bev=0.02))
        s3.append(gseg((x - 0.42, b + 0.1, fz + 0.09), (x + 0.42, b + 1.85, fz + 0.09), 0.04, m["white"]))
        s3.append(gseg((x + 0.42, b + 0.1, fz + 0.09), (x - 0.42, b + 1.85, fz + 0.09), 0.04, m["white"]))
    s3.append(gb((2.2, 0.12, 0.1), (0, b + 2.02, fz + 0.06), m["white"], bev=0.02))
    for x in (-1.05, 1.05):
        s3.append(gb((0.1, 2.05, 0.1), (x, b + 1.0, fz + 0.06), m["white"], bev=0.02))
    S["stage3"] = s3
    # gambrel: steep lower slopes + shallow upper slopes, ridge along Z
    s4 = []
    y0 = b + H
    for s in (-1, 1):
        s4.append(gb((1.25, 0.15, D + 0.5), (s * (W / 2 - 0.35), y0 + 0.75, 0), roofm, bev=0.04, rot=(0, 0, -s * 62)))
        s4.append(gb((1.85, 0.15, D + 0.5), (s * 0.82, y0 + 1.73, 0), roofm, bev=0.04, rot=(0, 0, -s * 22)))
    for z in (fz - 0.02, -fz + 0.12):
        s4.append(gpoly([(-W / 2 + 0.05, y0, z), (W / 2 - 0.05, y0, z), (W / 2 - 0.65, y0 + 1.4, z), (0, y0 + 2.0, z),
                         (-W / 2 + 0.65, y0 + 1.4, z)], 0.1, red))
    s4.append(gb((1.0, 0.9, 0.08), (0, y0 + 0.9, fz + 0.05), m["white"], bev=0.02))
    s4.append(gb((0.84, 0.74, 0.08), (0, y0 + 0.9, fz + 0.08), M("loft", DOOR_DARK), bev=0.0))
    for (x, z, y) in ((W / 2 + 0.6, 1.2, 0.3), (W / 2 + 0.6, 0.3, 0.3), (W / 2 + 0.6, 0.75, 0.85)):
        s4.append(gb((0.6, 0.55, 0.85), (x, y, z), hay, bev=0.1))
    S["stage4"] = s4
    return S


def clock_tower():
    """Clock Tower landmark (r3_clocktower): 6 stages, 11.6 m. Front (+Z) door and clock face. Footprint 4 x 4."""
    m = mmats()
    stone2 = M("stone2", (0.68, 0.63, 0.57))
    roofm = M("roof", TEAL, "boards", bands=10.0, dir="Z")
    gold = M("gold", (1.0, 0.8, 0.25))
    S = {"stage1": [gb((4.0, 0.5, 4.0), (0, 0.25, 0), m["stone"], bev=0.08), gb((1.6, 0.25, 0.6), (0, 0.12, 2.25), m["stone"], bev=0.05)]}
    s2 = [gb((3.0, 3.0, 3.0), (0, 2.0, 0), stone2, bev=0.08)]
    s2.append(gb((1.0, 1.7, 0.08), (0, 1.35, 1.51), m["door"], bev=0.03))
    s2.append(gc(0.5, 0.08, (0, 2.2, 1.5), m["door"], axis="z", verts=12))
    for sx in (-1, 1):
        for sz in (-1, 1):
            s2.append(gb((0.3, 3.0, 0.3), (sx * 1.45, 2.0, sz * 1.45), m["stone"], bev=0.05))
    s2.append(gb((3.2, 0.2, 3.2), (0, 3.5, 0), m["stone"], bev=0.05))
    S["stage2"] = s2
    s3 = [gb((2.6, 2.5, 2.6), (0, 4.85, 0), M("walls", CREAM, "boards", bands=14.0, dir="Z"), bev=0.05)]
    for sx in (-1, 1):
        for sz in (-1, 1):
            s3.append(gb((0.18, 2.5, 0.18), (sx * 1.3, 4.85, sz * 1.3), m["teal_d"], bev=0.03))
    s3 += window(0, 4.8, 1.3, 0.5, 0.9, m["white"], m["wglass"])
    s3 += window(1.3, 4.8, 0, 0.5, 0.9, m["white"], m["wglass"], face="x")
    s3.append(gb((2.9, 0.2, 2.9), (0, 6.15, 0), m["teal_d"], bev=0.05))
    S["stage3"] = s3
    s4 = [gb((2.8, 1.8, 2.8), (0, 7.15, 0), m["teal"], bev=0.08)]
    for (pos, axis) in (((0, 7.15, 1.41), "z"), ((1.41, 7.15, 0), "x"), ((-1.41, 7.15, 0), "x")):
        s4.append(gc(0.72, 0.06, pos, gold, axis=axis, verts=20))
        s4.append(gc(0.64, 0.08, pos, M("face", (0.98, 0.95, 0.86)), axis=axis, verts=20))
    s4.append(gb((0.06, 0.5, 0.03), (0, 7.36, 1.47), M("hands", (0.15, 0.13, 0.12)), bev=0.0))
    s4.append(gb((0.36, 0.06, 0.03), (0.15, 7.15, 1.47), M("hands", (0.15, 0.13, 0.12)), bev=0.0))
    s4.append(gb((3.0, 0.16, 3.0), (0, 8.1, 0), m["teal_d"], bev=0.05))
    S["stage4"] = s4
    s5 = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            s5.append(gb((0.3, 1.4, 0.3), (sx * 1.2, 8.88, sz * 1.2), stone2, bev=0.05))
    s5.append(gc(0.42, 0.65, (0, 8.9, 0), gold, verts=14, r2=0.18))
    s5.append(gc(0.07, 0.4, (0, 9.4, 0), m["dark"], verts=8))
    s5.append(gb((2.8, 0.14, 2.8), (0, 9.63, 0), m["stone"], bev=0.05))
    S["stage5"] = s5
    s6 = [gc(2.15, 1.9, (0, 10.65, 0), roofm, verts=4, r2=0.05)]
    s6[-1].rotation_euler.z = math.pi / 4
    s6.append(gc(0.04, 0.7, (0, 11.9, 0), gold, verts=6))
    s6.append(blob(1.0, gpos(0, 11.65, 0), (0.12, 0.12, 0.12), gold, 1.0, seg=8, rings=5, amp=0.0))
    s6.append(gb((0.5, 0.18, 0.03), (0.12, 12.1, 0), gold, bev=0.0))
    S["stage6"] = s6
    return S


def highland_gate():
    """Highland Gate (r3_gate) in the north palisade: two log towers, crossbeam, teal roof. Passage along Z, 2.7 m clear
    (x -1.35..1.35). Sign board face at (0, 2.95, 1.13): Label3D 'MAPLE HIGHLANDS' at z 1.16."""
    m = mmats()
    roofm = M("roof", TEAL, "boards", bands=10.0, dir="X")
    p = []
    for s in (-1, 1):
        x = s * 1.9
        p.append(gb((1.2, 0.5, 1.2), (x, 0.25, 0), m["stone"], bev=0.08))
        for (dx, dz) in ((-0.38, -0.38), (0.38, -0.38), (-0.38, 0.38), (0.38, 0.38)):
            p.append(gll(0.17, 3.2, (x + dx, 2.1, dz), m["bark"], m["end"], axis="y", verts=8))
        p.append(gc(0.17, 0.25, (x - 0.38, 3.8, 0.38), m["end"], verts=8, r2=0.04))
        p.append(gc(0.17, 0.25, (x + 0.38, 3.8, 0.38), m["end"], verts=8, r2=0.04))
    p.append(gll(0.2, 5.2, (0, 3.45, 0.3), m["bark"], m["end"], axis="x", verts=8))
    p.append(gll(0.2, 5.2, (0, 3.45, -0.3), m["bark"], m["end"], axis="x", verts=8))
    rp, ridge = groof(5.0, 1.4, 3.7, 32, 0.25, roofm)
    p += rp
    # sign hangs in front of the roof eave (z 0.95) so the 52 deg camera sees it
    p.append(gb((2.6, 0.6, 0.1), (0, 2.95, 1.08), M("sign", (0.93, 0.80, 0.58), "planks"), bev=0.03))
    p.append(gb((2.7, 0.06, 0.14), (0, 3.28, 1.08), m["teal_d"], bev=0.02))
    for x in (-1.0, 1.0):
        p.append(gc(0.02, 0.5, (x, 3.5, 1.08), m["dark"], verts=6))
    for s in (-1, 1):
        p.append(blob(1.0, gpos(s * 1.9, 0.45, 0.9), (0.3, 0.26, 0.24), M("bush", MAPLE_ORANGE), s, seg=8, rings=5, amp=0.12))
    return p


def highland_gate_doors():
    """Closed double door between the gate towers (remove/shrink it when r3_gate is bought, like the Birch gate fence)."""
    m = mmats()
    p = []
    for s in (-1, 1):
        x = s * 0.68
        p.append(gb((1.3, 2.5, 0.12), (x, 1.3, 0), M("door", (0.62, 0.42, 0.26), "planks"), bev=0.03))
        for y in (0.5, 2.1):
            p.append(gb((1.3, 0.14, 0.16), (x, y, 0.02), m["dark"], bev=0.03))
        p.append(gseg((x - 0.55, 0.55, 0.11), (x + 0.55, 2.05, 0.11), 0.05, m["dark"]))
        p.append(gb((0.06, 0.4, 0.05), (s * 0.08, 1.3, 0.1), m["steel_d"], bev=0.01))
    return p


def build_plot():
    """Empty village plot before stage 1: four stakes with red flags, rope, a stone pile. 5 x 5, origin = plot centre."""
    m = mmats()
    rope = M("rope", (0.86, 0.78, 0.6))
    p = []
    c = [(-2.4, -2.4), (2.4, -2.4), (2.4, 2.4), (-2.4, 2.4)]
    for (x, z) in c:
        p.append(gb((0.1, 0.7, 0.1), (x, 0.35, z), m["plank"], bev=0.02))
        p.append(gb((0.22, 0.14, 0.02), (x + 0.12, 0.62, z), m["tag"], bev=0.0))
    for a, b_ in zip(c, c[1:] + c[:1]):
        p.append(gseg((a[0], 0.5, a[1]), (b_[0], 0.5, b_[1]), 0.015, rope, verts=4))
    for i, (x, z) in enumerate(((-1.7, -1.7), (-1.35, -1.85), (-1.55, -1.4))):
        p.append(blob(1.0, gpos(x, 0.08, z), (0.24, 0.2, 0.15), m["stone"], i, seg=7, rings=4, amp=0.15))
    return p


def beam_cart():
    """Two-wheeled hand cart with beams (Builders' Yard decor)."""
    m = mmats()
    p = [gb((0.9, 0.08, 1.4), (0, 0.55, 0), m["plank"], bev=0.02)]
    for x in (-0.5, 0.5):
        p.append(gc(0.35, 0.07, (x, 0.35, 0.15), m["dark"], axis="x", verts=12))
        p.append(gb((0.06, 0.2, 1.4), (x * 0.9, 0.68, 0), m["plank"], bev=0.01))
    for x in (-0.3, 0.3):
        p.append(gb((0.05, 0.05, 0.8), (x, 0.55, -1.05), m["dark"], bev=0.01, rot=(-12, 0, 0)))
    for k, (x, y) in enumerate(((-0.2, 0.73), (0.15, 0.73), (0.0, 0.98))):
        bm = item_beam()
        for o in bm:
            o.matrix_world = Matrix.Translation(gpos(x, y - 0.13, 0)) @ Matrix.Rotation(math.pi / 2, 4, "Z") @ o.matrix_world
        p += bm
    return p


# ------------------------------------------------------------------ plan
K, W = "kenney", "world"
T = dict(ao=0.22, grad=0.86)
PLAN = {
    "tree_mapleA":        ("maple", lambda: maple_tree("A"), 512, K, T),
    "tree_mapleB":        ("maple", lambda: maple_tree("B"), 512, K, T),
    "tree_mapleC":        ("maple", lambda: maple_tree("C"), 512, K, T),
    "tree_mapleA_far":    ("maple", lambda: maple_tree("A", far=True), 256, K, T),
    "tree_mapleB_far":    ("maple", lambda: maple_tree("B", far=True), 256, K, T),
    "tree_mapleC_far":    ("maple", lambda: maple_tree("C", far=True), 256, K, T),
    "stump_maple":        ("maple", maple_stump, 256, K, dict(ao=0.45, grad=0.8)),
    "log_stack_maple":    ("maple", maple_log_stack, 256, K, dict(ao=0.4, grad=0.82)),
    "leaf_pile":          ("maple", leaf_pile, 128, K, dict(ao=0.6, grad=0.85)),
    "bush_autumn":        ("maple", bush_autumn, 256, K, dict(ao=0.4, grad=0.8)),
    "item_maple_log":     ("items", item_maple_log, 256, W, dict(ao=0.5, grad=0.85)),
    "item_beam":          ("items", item_beam, 256, W, dict(ao=0.5, grad=0.85)),
    "item_floorboard":    ("items", item_floorboard, 128, W, dict(ao=0.8, grad=0.88)),
    "item_cabin_kit":     ("items", item_cabin_kit, 256, W, dict(ao=0.3, grad=0.85)),
    "beam_saw":           ("maple", beam_saw, 512, W, dict(ao=0.22, grad=0.82)),
    "beam_saw_blade":     ("maple", beam_saw_blade, 128, W, dict(ao=0.3, grad=0.95, no_ground=True)),
    "planer_mill":        ("maple", planer_mill, 512, W, dict(ao=0.2, grad=0.82)),
    "planer_roller":      ("maple", planer_roller, 128, W, dict(ao=0.3, grad=0.95, no_ground=True)),
    "kit_factory":        ("maple", kit_factory, 512, W, dict(ao=0.16, grad=0.82)),
    "kit_factory_press":  ("maple", kit_factory_press, 128, W, dict(ao=0.3, grad=0.9, no_ground=True)),
    "forklift":           ("maple", forklift, 256, W, dict(ao=0.25, grad=0.82)),
    "rail_straight_4m":   ("maple", rail_straight_4m, 256, W, dict(ao=0.5, grad=0.85)),
    "rail_bumper":        ("maple", rail_bumper, 128, W, dict(ao=0.35, grad=0.85)),
    "handcar":            ("maple", handcar, 256, W, dict(ao=0.3, grad=0.82)),
    "handcar_tile":       ("maple", handcar_tile, 128, W, dict(ao=0.8, grad=0.9)),
    "handcar_stop":       ("maple", handcar_stop, 256, W, dict(ao=0.22, grad=0.85)),
    "lantern_post":       ("maple", lantern_post, 128, W, dict(ao=0.2, grad=0.85)),
    "train_loco":         ("maple", train_loco, 512, W, dict(ao=0.22, grad=0.8)),
    "train_wagon":        ("maple", train_wagon, 256, W, dict(ao=0.3, grad=0.8)),
    "rail_platform":      ("maple", rail_platform, 512, W, dict(ao=0.25, grad=0.85)),
    "highland_office":    ("maple", highland_office, 512, W, dict(ao=0.18, grad=0.82)),
    "market_canopy_teal": ("maple", market_canopy_teal, 256, W, dict(ao=0.18, grad=0.85)),
    "house_cottage":      ("maple", house_cottage, 512, W, dict(ao=0.15, grad=0.82)),
    "house_farmhouse":    ("maple", house_farmhouse, 512, W, dict(ao=0.15, grad=0.82)),
    "house_barn":         ("maple", house_barn, 512, W, dict(ao=0.15, grad=0.82)),
    "house_school":       ("maple", house_school, 512, W, dict(ao=0.15, grad=0.82)),
    "house_inn":          ("maple", house_inn, 512, W, dict(ao=0.13, grad=0.82)),
    "clock_tower":        ("maple", clock_tower, 512, W, dict(ao=0.08, grad=0.82)),
    "highland_gate":      ("maple", highland_gate, 512, W, dict(ao=0.2, grad=0.82)),
    "highland_gate_doors": ("maple", highland_gate_doors, 256, W, dict(ao=0.3, grad=0.85)),
    "build_plot":         ("maple", build_plot, 128, W, dict(ao=0.4, grad=0.9)),
    "beam_cart":          ("maple", beam_cart, 256, W, dict(ao=0.3, grad=0.85)),
}

run_plan(PLAN, f"{REPO}/tools/lookdev/build_m2_report.json", OUT_ROOT)
