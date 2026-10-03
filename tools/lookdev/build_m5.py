"""Grand Timber Station (GDD milestone M5, the finale, section 7.7) models -> assets/models_v3/station/.
Same bake as every models_v3 asset. Placement + paste-ready dicts: assets/models_v3/ASSETS_M5.md.

Usage (headless, Cycles on the RTX 3060 when available):
  /home/mm/.local/bin/blender -b --python tools/lookdev/build_m5.py -- [only_name ...]
Report: tools/lookdev/build_m5_report.json. Everything here is own work (CC0).

Accent: station brass #c99a2e (clock, trims, finials, loco bands) on cream sandstone, with station maroon #6e2430 roofs
and rolling stock. The five platform slots each wear their own valley's accent so the player knows where each one belongs.
"""
import os

exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "m345_lib.py")).read(), "m345_lib.py", "exec"))

# ------------------------------------------------------------------ station palette (sRGB, docs/DESIGN.md section 16)
BRASS = (0.788, 0.604, 0.18)        # #c99a2e accent
BRASS_L = (0.95, 0.80, 0.40)
MAROON = (0.43, 0.14, 0.19)         # #6e2430 roofs, loco, coaches
MAROON_D = (0.30, 0.09, 0.12)
SAND = (0.90, 0.84, 0.72)           # #e6d6b8 cream sandstone
SAND_D = (0.72, 0.64, 0.52)         # #b8a385 plinths, pilasters
LIME = (0.42, 0.64, 0.28)
LIME2 = (0.36, 0.56, 0.24)
VALLEY = {1: ((1.0, 0.45, 0.12), (0.75, 0.33, 0.09)),    # Home orange
          2: ((0.25, 0.54, 0.76), (0.17, 0.38, 0.55)),   # Birch Bend river blue
          3: ((0.165, 0.616, 0.561), (0.11, 0.42, 0.39)),  # Maple Highlands teal
          4: ((0.118, 0.227, 0.392), (0.075, 0.145, 0.255)),  # Redwood navy
          5: ((0.784, 0.157, 0.227), (0.55, 0.11, 0.16))}     # Frost alpine red
TRACK_Z = 1.0     # station-local track centre (world z -51 with the station at (0, -52))


def smats():
    m = mmats()
    m.update(brass=M("brass", BRASS), brass_l=M("brassl", BRASS_L), mar=M("mar", MAROON), mar_d=M("mard", MAROON_D),
             sand=M("sand", SAND), sand_d=M("sandd", SAND_D), blk=M("blk", (0.2, 0.2, 0.22)), wht=M("wht", WHITE),
             lamp=M("lamp", (1.0, 0.9, 0.6)), glass=M("glass2", (0.66, 0.80, 0.86)))
    return m


def cut_below(ob, y_godot):
    bpy.context.view_layer.update()   # location/rotation were just set: refresh matrix_world first
    mw = ob.matrix_world.copy(); inv = mw.inverted()
    for v in ob.data.vertices:
        w = mw @ v.co
        if w.z < y_godot:
            w.z = y_godot
            v.co = inv @ w
    return ob


def arch_window(x, y, z, w, h, frame, glass, face="z"):
    """Tall window with a round top (rectangle + half-disc), on a wall facing +Z or +X."""
    if face == "z":
        return [gb((w + 0.14, h + 0.1, 0.06), (x, y, z), frame, bev=0.0), gb((w, h, 0.05), (x, y, z + 0.02), glass, bev=0.0),
                cut_below(gc(w / 2 + 0.07, 0.06, (x, y + h / 2, z), frame, axis="z", verts=10), y + h / 2),
                cut_below(gc(w / 2, 0.05, (x, y + h / 2, z + 0.02), glass, axis="z", verts=10), y + h / 2)]
    return [gb((0.06, h + 0.1, w + 0.14), (x, y, z), frame, bev=0.0), gb((0.05, h, w), (x + 0.02, y, z), glass, bev=0.0),
            gc(w / 2 + 0.07, 0.06, (x, y + h / 2, z), frame, axis="x", verts=12), gc(w / 2, 0.05, (x + 0.02, y + h / 2, z), glass, axis="x", verts=12)]


# ------------------------------------------------------------------ the capstone

def grand_station():
    """Grand Timber Station (cap_station), 6 BuildSite stages. Origin = pad (0, -52). A through-station over the z -51 rail:
    the track runs along X through the hall at local z +1.0 (lay maple/rail_straight_4m there, rot 90); the north-south
    passage (the V1 -> V3 gate path) runs straight through arches at x -1.4..1.4 in both long walls.
    Footprint x -7.6..7.6, z -2.8..5.0. stage1 platforms + crossing planks, stage2 lower walls + corner piers, stage3 upper
    walls + clerestory, stage4 arched train-shed roof, stage5 clock tower over the entrance, stage6 spire, sign, flags."""
    m = smats()
    S = {}
    L = 15.0
    zn, zs = -2.65, 4.65             # north / south wall lines
    s1 = []
    for x0, x1 in ((-7.5, -1.4), (1.4, 7.5)):
        cx, w = (x0 + x1) / 2, x1 - x0
        s1.append(gb((w, 0.4, 2.2), (cx, 0.2, -1.35), m["sand_d"], bev=0.04))     # north platform z -2.45..-0.25
        s1.append(gb((w, 0.4, 2.2), (cx, 0.2, 3.35), m["sand_d"], bev=0.04))      # south platform z 2.25..4.45
        for z in (-0.3, 2.3):
            s1.append(gb((w, 0.02, 0.12), (cx, 0.41, z), m["yellow"], bev=0.0))
    s1.append(gb((2.8, 0.06, 2.5), (0, 0.15, TRACK_Z), m["plank"], bev=0.0))          # level crossing planks (flush with rail top)
    s1.append(gb((2.8, 0.03, 7.4), (0, 0.015, 1.0), M("pave", (0.80, 0.72, 0.60)), bev=0.0))   # passage paving
    S["stage1"] = s1
    s2 = []
    for z in (zn, zs):
        for x0, x1 in ((-7.6, -1.4), (1.4, 7.6)):
            s2.append(gb((x1 - x0, 3.0, 0.3), ((x0 + x1) / 2, 1.5, z), m["sand"], bev=0.03))
        s2.append(gb((2.8, 0.45, 0.3), (0, 2.78, z), m["sand"], bev=0.0))         # lintel over the passage arch
        s2.append(cut_below(gc(1.4, 0.32, (0, 2.55, z), m["sand"], axis="z", verts=16), 2.55))    # arch head (half disc)
        s2.append(cut_below(gc(1.2, 0.34, (0, 2.55, z), M("archin", (0.38, 0.30, 0.25)), axis="z", verts=16), 2.55))
        for x in (-1.55, 1.55):
            s2.append(gb((0.3, 3.0, 0.42), (x, 1.5, z), m["sand_d"], bev=0.0))
        s2.append(gb((L + 0.3, 0.3, 0.42), (0, 0.15, z), m["sand_d"], bev=0.0))    # plinth band
    for x in (-5.4, -3.4, 3.4, 5.4):                                                # arched windows on the camera side
        s2 += arch_window(x, 1.55, zs + 0.16, 0.8, 1.4, m["brass"], m["glass"])
    for sx in (-1, 1):                                                              # corner piers
        for z in (zn, zs):
            s2.append(gb((0.9, 4.8, 0.9), (sx * 7.6, 2.4, z), m["sand_d"], bev=0.0))
            s2.append(gb((1.0, 0.18, 1.0), (sx * 7.6, 4.85, z), m["brass"], bev=0.0))
    S["stage2"] = s2
    s3 = []
    for z in (zn, zs):
        s3.append(gb((L, 1.4, 0.28), (0, 3.7, z), m["sand"], bev=0.0))
        s3.append(gb((L + 0.1, 0.12, 0.36), (0, 3.03, z), m["brass"], bev=0.0))
        s3.append(gb((L + 0.1, 0.16, 0.38), (0, 4.42, z), m["sand_d"], bev=0.0))
    for x in (-6.0, -4.4, -2.8, 2.8, 4.4, 6.0):                                     # clerestory windows (flat, 2 boxes each)
        s3.append(gb((0.82, 0.82, 0.04), (x, 3.7, zs + 0.15), m["brass"], bev=0.0))
        s3.append(gb((0.7, 0.7, 0.04), (x, 3.7, zs + 0.17), m["glass"], bev=0.0))
    S["stage3"] = s3
    s4 = []
    ry = 2.0                                                                        # segmental vault: rise 2.0 over the 7.3 m span
    vault = gc(3.75, L + 0.2, (0, 4.5, TRACK_Z), M("roof", MAROON, "boards", bands=26.0, dir="X"), axis="x", verts=24)
    vault.scale = (1, 1, 1)
    s4.append(cut_below(vault, 4.5))
    for v in vault.data.vertices:                                                   # flatten the half-cylinder to the rise
        w = vault.matrix_world @ v.co
        w.z = 4.5 + (w.z - 4.5) * ry / 3.75
        v.co = vault.matrix_world.inverted() @ w
    glazing = gb((L + 0.25, 0.08, 1.6), (0, 4.5 + ry + 0.02, TRACK_Z), m["glass"], bev=0.0)
    s4.append(glazing)
    for x in (-7.5, -3.75, 0.0, 3.75, 7.5):                                         # brass ribs
        pts = [(x, 4.5 + ry * math.sin(t) + 0.04, TRACK_Z + 3.78 * math.cos(t)) for t in [math.pi * k / 6 for k in range(7)]]
        s4.append(gtube(pts, 0.07, m["brass"], sides=4))
    for sx in (-1, 1):                                                              # fan windows in the end gables
        fan = gc(3.4, 0.12, (sx * 7.6, 4.5, TRACK_Z), m["glass"], axis="x", verts=16)
        s4.append(cut_below(fan, 4.5))
        for v in fan.data.vertices:
            w = fan.matrix_world @ v.co; w.z = 4.5 + (w.z - 4.5) * ry / 3.4; v.co = fan.matrix_world.inverted() @ w
        for k in range(1, 4):
            a = math.pi * k / 4
            s4.append(gseg((sx * 7.62, 4.5, TRACK_Z), (sx * 7.62, 4.5 + ry * math.sin(a) * 0.98, TRACK_Z + 3.35 * math.cos(a)), 0.04, m["brass"], verts=4))
    S["stage4"] = s4
    s5 = [gb((2.6, 5.0, 1.6), (0, 5.4, 4.2), m["sand"], bev=0.05)]                  # clock tower on the entrance
    for sx in (-1, 1):
        s5.append(gb((0.22, 5.0, 0.22), (sx * 1.3, 5.4, 5.0), m["brass"], bev=0.02))
    s5.append(gb((2.8, 0.2, 1.8), (0, 7.95, 4.2), m["sand_d"], bev=0.03))
    for (pos, axis) in (((0, 6.9, 5.02), "z"), ((1.32, 6.9, 4.2), "x"), ((-1.32, 6.9, 4.2), "x")):
        s5.append(gc(0.72, 0.06, pos, m["brass"], axis=axis, verts=14))
        s5.append(gc(0.62, 0.08, pos, M("face", (0.98, 0.95, 0.86)), axis=axis, verts=14))
    s5.append(gb((0.06, 0.5, 0.03), (0, 7.1, 5.08), m["blk"], bev=0.0))
    s5.append(gb((0.36, 0.06, 0.03), (0.15, 6.9, 5.08), m["blk"], bev=0.0))
    s5.append(gb((3.2, 0.14, 1.0), (0, 3.15, 5.0), m["mar"], bev=0.04))             # entrance canopy
    for x in (-1.45, 1.45):
        s5.append(gc(0.08, 3.0, (x, 1.5, 4.95), m["brass"], verts=8))
    S["stage5"] = s5
    s6 = [gc(1.95, 2.2, (0, 9.15, 4.2), m["mar"], verts=4, r2=0.05)]
    s6[-1].rotation_euler.z = math.pi / 4
    s6.append(gc(0.05, 1.0, (0, 10.6, 4.2), m["brass"], verts=6))
    s6.append(blob(1.0, gpos(0, 10.35, 4.2), (0.14, 0.14, 0.14), m["brass_l"], 1.0, seg=8, rings=5, amp=0.0))
    s6.append(gb((0.55, 0.2, 0.03), (0.15, 10.95, 4.2), m["brass"], bev=0.0))
    s6.append(gb((2.5, 0.75, 0.1), (0, 4.25, 5.06), M("signbd", (0.97, 0.92, 0.80)), bev=0.03))   # 'GRAND TIMBER STATION'
    s6.append(gb((2.6, 0.08, 0.12), (0, 4.65, 5.06), m["brass"], bev=0.0))
    s6.append(gb((2.6, 0.08, 0.12), (0, 3.85, 5.06), m["brass"], bev=0.0))
    for i, k in enumerate((1, 2, 3, 4, 5)):                                          # one pennant per valley along the ridge
        x = -5.0 + i * 2.5
        y0 = 4.5 + ry + 0.05
        s6.append(gc(0.035, 1.3, (x, y0 + 0.65, TRACK_Z), m["brass"], verts=6))
        s6.append(gpoly([(x, y0 + 1.25, TRACK_Z), (x + 0.75, y0 + 1.08, TRACK_Z), (x, y0 + 0.9, TRACK_Z)], 0.03, M(f"flag{k}", VALLEY[k][0])))
    S["stage6"] = s6
    return S


def station_plot():
    """Empty capstone site before / while cap_station builds: survey stakes, rope around the footprint, stone pile, a
    'COMING SOON' board facing +Z at (3.5, 1.3, 5.2). Origin = station origin. Hide it when stage1 rises."""
    m = smats()
    rope = M("rope", (0.86, 0.78, 0.6))
    c = [(-7.6, -2.8), (7.6, -2.8), (7.6, 5.0), (-7.6, 5.0)]
    p = []
    for (x, z) in c + [(-1.6, 5.0), (1.6, 5.0), (-1.6, -2.8), (1.6, -2.8)]:
        p.append(gb((0.1, 0.8, 0.1), (x, 0.4, z), m["plank"], bev=0.0))
        p.append(gb((0.24, 0.14, 0.02), (x + 0.12, 0.7, z), m["brass"], bev=0.0))
    for a, b in (((-7.6, -2.8), (-1.6, -2.8)), ((1.6, -2.8), (7.6, -2.8)), ((7.6, -2.8), (7.6, 5.0)), ((7.6, 5.0), (1.6, 5.0)),
                 ((-1.6, 5.0), (-7.6, 5.0)), ((-7.6, 5.0), (-7.6, -2.8))):
        p.append(gseg((a[0], 0.55, a[1]), (b[0], 0.55, b[1]), 0.015, rope, verts=3))
    for i, (x, z) in enumerate(((-5.0, -1.6), (-4.5, -1.9), (-4.8, -1.2), (5.2, 3.5))):
        p.append(blob(1.0, gpos(x, 0.12, z), (0.4, 0.32, 0.22), m["sand_d"], i, seg=7, rings=4, amp=0.15))
    for k in range(3):
        p.append(gb((1.6, 0.25, 0.3), (-4.8, 0.13 + k * 0.25, 2.6 + (k % 2) * 0.05), m["sand"], bev=0.02))
    for x in (2.6, 4.4):
        p.append(gb((0.1, 1.6, 0.1), (x, 0.8, 5.2), m["dark"], bev=0.0))
    p.append(gb((2.0, 0.8, 0.08), (3.5, 1.3, 5.2), M("board", (0.97, 0.92, 0.8)), bev=0.03))
    p.append(gb((2.1, 0.1, 0.12), (3.5, 1.74, 5.2), m["mar"], bev=0.02))
    return p


def _platform_slot(k):
    """Valley platform slot (GDD 7.7): stone slab, a pallet bay for the goods pile, a sign post in the valley's accent with a
    brass rim (board face z -0.82 + 0.06, centre (1.1, 1.9, *)), a brass station lamp. Origin = slab centre."""
    m = smats()
    a, ad = (M(f"acc{k}", VALLEY[k][0]), M(f"accd{k}", VALLEY[k][1]))
    p = [gb((3.4, 0.2, 2.6), (0, 0.1, 0), m["sand_d"], bev=0.04), gb((3.42, 0.03, 0.14), (0, 0.205, 1.24), m["yellow"], bev=0.0)]
    p.append(gb((1.8, 0.08, 1.8), (-0.55, 0.24, 0.1), m["plank"], bev=0.01))           # pallet bay (pile at (-0.55, 0.28, 0.1))
    for x in (-1.3, 0.2):
        p.append(gb((0.08, 0.1, 1.8), (x, 0.25, 0.1), m["dark"], bev=0.0))
    for x in (0.55, 1.65):
        p.append(gb((0.1, 2.3, 0.1), (x, 1.25, -0.85), ad, bev=0.02))
    p.append(gb((1.4, 0.7, 0.08), (1.1, 1.9, -0.82), a, bev=0.03))
    p.append(gb((1.5, 0.06, 0.12), (1.1, 2.28, -0.82), m["brass"], bev=0.0))
    p.append(gb((1.5, 0.06, 0.12), (1.1, 1.52, -0.82), m["brass"], bev=0.0))
    p.append(gc(0.13, 0.04, (1.1, 2.48, -0.82), m["brass"], axis="z", verts=12))      # brass station emblem
    p.append(gc(0.05, 2.4, (-1.5, 1.3, -1.05), m["mar"], verts=8))                    # lamp
    p.append(gb((0.6, 0.06, 0.06), (-1.3, 2.45, -1.05), m["mar"], bev=0.0))
    for x in (-1.75, -1.25):
        p.append(blob(1.0, gpos(x, 2.33, -1.05), (0.11, 0.11, 0.11), m["lamp"], 1.0, seg=8, rings=5, amp=0.0))
    return p


# ------------------------------------------------------------------ rail line pieces (along Z like maple/rail_straight_4m)

def rail_bridge_8m():
    """8 m rail bridge for the river at x -27 (river 6.4 wide): two maroon lattice trusses, sleepers, rails at y 0.18
    (same gauge/top as maple/rail_straight_4m), stone abutments at both ends. Along Z: rot 90 for the east-west line."""
    m = smats()
    sleeper, steel = M("sleeper", (0.48, 0.34, 0.24), "planks"), M("rail", (0.62, 0.6, 0.58))
    p = [gb((1.9, 0.1, 8.0), (0, 0.05, 0), m["mar_d"], bev=0.02)]
    for i in range(10):
        p.append(gb((1.6, 0.06, 0.24), (0, 0.11, -3.6 + i * 0.8), sleeper, bev=0.0))
    for s in (-1, 1):
        p.append(gb((0.07, 0.07, 8.0), (s * 0.5, 0.165, 0), steel, bev=0.0))
        x = s * 1.0
        p.append(gb((0.12, 0.14, 8.0), (x, 0.17, 0), m["mar"], bev=0.02))
        p.append(gb((0.12, 0.12, 7.2), (x, 1.5, 0), m["mar"], bev=0.02))
        for k in range(7):
            z = -3.6 + k * 1.2
            p.append(gb((0.08, 1.3, 0.08), (x, 0.85, z), m["mar"], bev=0.0))
            if k < 6:
                p.append(gseg((x, 0.25, z), (x, 1.45, z + 1.2), 0.03, m["mar"], verts=4))
        p.append(gb((0.16, 0.06, 7.3), (x, 1.58, 0), m["brass"], bev=0.0))
    for z in (-4.2, 4.2):
        p.append(gb((2.4, 0.9, 0.8), (0, -0.35, z), m["sand_d"], bev=0.05))
    return p


def rail_road_crossing_4m():
    """4 m of track for the line crossing the road at x 17: plank road surface flush with the rail top between and beside
    the rails, white stop bars. Along Z (rot 90 for the east-west line), same rails as maple/rail_straight_4m."""
    m = smats()
    steel = M("rail", (0.62, 0.6, 0.58))
    p = []
    for i in range(12):
        p.append(gb((1.9, 0.12, 0.32), (0, 0.06, -1.76 + i * 0.32), m["plank"] if i % 2 else M("pl2", (0.86, 0.68, 0.45), "planks"), bev=0.0))
    for s in (-1, 1):
        p.append(gb((0.07, 0.06, 4.0), (s * 0.5, 0.15, 0), steel, bev=0.0))
        p.append(gb((0.3, 0.02, 4.0), (s * 1.3, 0.01, 0), m["wht"], bev=0.0))
    return p


# ------------------------------------------------------------------ Timber Express

def express_loco():
    """Timber Express steam loco (cutscene loop, GDD 7.7). Maroon with brass bands, red wheels, front at -Z. Gauge 1.0,
    wheels on rail top y 0.18; origin = track centre at ground. Tender = express_tender.glb 3.4 m behind (+Z)."""
    m = smats()
    red = M("red", (0.74, 0.2, 0.16))
    p = [gb((1.4, 0.3, 4.4), (0, 0.6, 0.1), m["blk"], bev=0.05)]
    for z in (-0.3, 0.75, 1.8):
        for x in (-0.55, 0.55):
            p.append(gc(0.42, 0.1, (x, 0.18 + 0.42, z), red, axis="x", verts=16))
            p.append(gc(0.12, 0.12, (x, 0.6, z), m["brass"], axis="x", verts=8))
    for x in (-0.6, 0.6):
        p.append(gc(0.22, 0.1, (x, 0.4, -1.5), red, axis="x", verts=10))
        p.append(gb((0.05, 0.06, 2.2), (x * 1.02, 0.6, 0.75), m["steel"], bev=0.0))
    p.append(gc(0.58, 3.0, (0, 1.42, -0.4), m["mar"], axis="z", verts=18))            # boiler
    p.append(gc(0.6, 0.7, (0, 1.42, -1.95), m["blk"], axis="z", verts=18))            # smokebox
    p.append(gc(0.42, 0.06, (0, 1.42, -2.32), m["blk"], axis="z", verts=14))
    for z in (-1.5, -0.4, 0.7):
        p.append(gc(0.6, 0.08, (0, 1.42, z), m["brass"], axis="z", verts=18))
    p.append(gc(0.15, 0.6, (0, 2.2, -1.95), m["blk"], verts=10, r2=0.2))             # chimney
    p.append(gc(0.22, 0.06, (0, 2.52, -1.95), m["brass"], verts=10))
    p.append(gc(0.2, 0.32, (0, 2.06, -0.3), m["brass"], verts=12))                     # dome
    p.append(blob(1.0, gpos(0, 2.22, -0.3), (0.2, 0.2, 0.1), m["brass_l"], 0.0, seg=10, rings=5, amp=0.0))
    p.append(gb((1.7, 1.5, 1.4), (0, 1.75, 1.75), m["mar"], bev=0.08))               # cab
    p.append(gb((1.9, 0.12, 1.65), (0, 2.55, 1.75), m["mar_d"], bev=0.04))
    for x in (-0.86, 0.86):
        p.append(gb((0.05, 0.5, 0.55), (x, 2.0, 1.6), m["glass"], bev=0.02))
        p.append(gb((0.05, 0.08, 1.4), (x, 1.2, 1.75), m["brass"], bev=0.0))
    p.append(gpoly([(-0.75, 0.32, -2.3), (0.75, 0.32, -2.3), (0, 0.32, -2.85)], 0.3, m["brass"]))   # cow catcher
    p.append(gc(0.14, 0.12, (0, 1.85, -2.35), m["lamp"], axis="z", verts=10))
    p.append(gb((1.0, 0.24, 0.05), (0, 1.0, -2.36), m["mar"], bev=0.02))              # buffer beam
    return p


def express_tender():
    """Tender loaded with logs (the timber line). Couple 3.4 m behind the loco centre; deck top y 1.0."""
    m = smats()
    p = [gb((1.4, 0.3, 2.6), (0, 0.6, 0), m["blk"], bev=0.05), gb((1.75, 0.9, 2.5), (0, 1.25, 0), m["mar"], bev=0.08)]
    p.append(gb((1.8, 0.08, 2.55), (0, 1.72, 0), m["brass"], bev=0.0))
    for z in (-0.75, 0.75):
        for x in (-0.55, 0.55):
            p.append(gc(0.3, 0.1, (x, 0.48, z), M("red", (0.74, 0.2, 0.16)), axis="x", verts=12))
    for i, (x, y) in enumerate(((-0.4, 1.85), (0.0, 1.85), (0.4, 1.85), (-0.2, 2.18), (0.2, 2.18))):
        p.append(gl(0.17, 2.1, (x, y, 0), M("bark", (0.62, 0.40, 0.24), "bark"), M("rings", (0.93, 0.76, 0.52), "rings"), axis="z", verts=8))
    return p


def express_coach():
    """Passenger coach: maroon lower body, cream upper with windows, grey roof, brass lining. Couple 4.6 m apart along +Z;
    tender centre to first coach centre 3.8. Gauge 1.0."""
    m = smats()
    p = [gb((1.4, 0.3, 4.0), (0, 0.6, 0), m["blk"], bev=0.05)]
    for z in (-1.4, 1.4):
        for x in (-0.55, 0.55):
            p.append(gc(0.28, 0.1, (x, 0.46, z), m["steel_d"], axis="x", verts=12))
    p.append(gb((1.8, 0.8, 4.3), (0, 1.15, 0), m["mar"], bev=0.06))
    p.append(gb((1.8, 0.7, 4.3), (0, 1.9, 0), m["sand"], bev=0.04))
    p.append(gb((1.84, 0.06, 4.32), (0, 1.56, 0), m["brass"], bev=0.0))
    for x in (-0.91, 0.91):
        for i in range(5):
            p.append(gb((0.04, 0.42, 0.55), (x, 1.92, -1.6 + i * 0.8), m["glass"], bev=0.01))
    roof = gc(1.0, 4.4, (0, 2.1, 0), M("roofc", (0.42, 0.40, 0.38)), axis="z", verts=12)
    p.append(cut_below(roof, 2.25))
    for z in (-2.2, 2.2):
        p.append(gb((1.0, 0.24, 0.1), (0, 0.85, z), m["mar_d"], bev=0.02))
    return p


# ------------------------------------------------------------------ ornamental trees (kenney units)

def station_tree(kind, far=False):
    """Clipped ornamental trees for the station square: 'lime' = round clipped crown on a straight stem, 'cone' = conical
    topiary. Kenney units, same scale range as the V1 trees."""
    bark = M("bark", (0.5, 0.36, 0.26), "bark")
    la, lb = M("lime", LIME), M("lime2", LIME2)
    p = [tube([Vector((0, 0, -0.04)), Vector((0, 0, 0.5)), Vector((0, 0, 1.0))], [0.04, 0.035, 0.03], 5 if far else 7, bark)]
    if kind == "lime":
        if far:
            p.append(blob(1.0, (0, 0, 1.12), (0.3, 0.3, 0.3), la, 1.0, ico=2, amp=0.04))
        else:
            p.append(blob(1.0, (0, 0, 1.12), (0.3, 0.3, 0.3), la, 1.0, seg=14, rings=9, amp=0.05))
            for i in range(5):
                a = i * 1.26
                p.append(blob(1.0, (0.18 * math.cos(a), 0.18 * math.sin(a), 1.12 + 0.12 * math.sin(a * 2)), (0.16, 0.16, 0.15),
                              lb if i % 2 else la, i + 2.0, seg=8, rings=5, amp=0.06))
    else:
        hz = 0.55
        c = blob(1.0, (0, 0, 0.35 + hz), (0.27, 0.27, hz), la, 3.0, ico=2 if far else 0, seg=14, rings=10, amp=0.04)
        for v in c.data.vertices:
            t = min(max((v.co.z + hz) / (2 * hz), 0.0), 1.0)
            k = 1.1 - 1.0 * t
            v.co.x *= k; v.co.y *= k
        p.append(c)
        if not far:
            p.append(blob(1.0, (0, 0, 0.35 + 2 * hz + 0.03), (0.05, 0.05, 0.05), lb, 4.0, seg=6, rings=4, amp=0.0))
    return p


# ------------------------------------------------------------------ props (world units)

def station_bench():
    """Maroon cast-iron bench with wooden slats (platforms, square)."""
    m = smats()
    p = []
    for x in (-0.75, 0.75):
        p.append(gb((0.08, 0.45, 0.5), (x, 0.23, 0.0), m["mar"], bev=0.02))
        p.append(gb((0.08, 0.5, 0.08), (x, 0.7, -0.24), m["mar"], bev=0.02))
    for i in range(3):
        p.append(gb((1.7, 0.05, 0.13), (0, 0.46, -0.16 + i * 0.16), m["plank"], bev=0.01))
    for y in (0.65, 0.85):
        p.append(gb((1.7, 0.12, 0.04), (0, y, -0.26), m["plank"], bev=0.01))
    return p


def clock_post():
    """Brass platform clock on a maroon post, two faces (+Z / -Z), 3.0 m."""
    m = smats()
    p = [gb((0.4, 0.15, 0.4), (0, 0.075, 0), m["mar_d"], bev=0.03), gc(0.07, 2.4, (0, 1.35, 0), m["mar"], verts=8)]
    p.append(gc(0.42, 0.24, (0, 2.75, 0), m["brass"], axis="z", verts=18))
    for z in (0.125, -0.125):
        p.append(gc(0.35, 0.02, (0, 2.75, z), M("face", (0.98, 0.95, 0.86)), axis="z", verts=18))
        p.append(gb((0.03, 0.26, 0.01), (0, 2.85, z * 1.12), m["blk"], bev=0.0))
        p.append(gb((0.18, 0.03, 0.01), (0.07, 2.75, z * 1.12), m["blk"], bev=0.0))
    p.append(blob(1.0, gpos(0, 3.02, 0), (0.07, 0.07, 0.07), m["brass_l"], 0.0, seg=8, rings=5, amp=0.0))
    return p


def flower_planter():
    """Sandstone planter with red and yellow flowers and a clipped box hedge (square decor)."""
    m = smats()
    p = [gb((1.2, 0.5, 0.6), (0, 0.25, 0), m["sand_d"], bev=0.04), gb((1.26, 0.06, 0.66), (0, 0.5, 0), m["sand"], bev=0.02)]
    p.append(gb((1.0, 0.18, 0.45), (0, 0.6, 0), M("hedge", LIME2), bev=0.06))
    for i in range(7):
        x = -0.42 + i * 0.14
        p.append(blob(1.0, gpos(x, 0.75, 0.08 * (-1) ** i), (0.07, 0.07, 0.06), M(f"fl{i % 2}", (0.9, 0.24, 0.2) if i % 2 else (0.98, 0.82, 0.22)), i, seg=6, rings=4, amp=0.1))
    return p


def luggage_cart():
    """Platform luggage cart with trunks and suitcases (decor)."""
    m = smats()
    p = [gb((0.9, 0.08, 1.5), (0, 0.4, 0), m["plank"], bev=0.02)]
    for z in (-0.5, 0.5):
        for x in (-0.48, 0.48):
            p.append(gc(0.18, 0.06, (x, 0.2, z), m["mar_d"], axis="x", verts=10))
    p.append(gb((0.05, 0.6, 0.05), (-0.4, 0.75, -0.78), m["mar"], bev=0.0))
    p.append(gb((0.05, 0.6, 0.05), (0.4, 0.75, -0.78), m["mar"], bev=0.0))
    p.append(gb((0.85, 0.05, 0.05), (0, 1.05, -0.78), m["mar"], bev=0.0))
    for (s, pos, c) in (((0.8, 0.45, 0.5), (0, 0.67, 0.3), (0.55, 0.33, 0.2)), ((0.6, 0.3, 0.45), (-0.05, 0.6, -0.3), (0.3, 0.45, 0.3)),
                        ((0.5, 0.25, 0.35), (0.05, 1.02, 0.3), (0.85, 0.66, 0.4))):
        p.append(gb(s, pos, M("case", c), bev=0.04))
    p.append(gb((0.82, 0.05, 0.08), (0, 0.9, 0.3), m["brass"], bev=0.0))
    return p


def station_lamp():
    """Double-globe station lamp, maroon post, brass collar (platforms, square, rail line)."""
    m = smats()
    p = [gb((0.32, 0.14, 0.32), (0, 0.07, 0), m["mar_d"], bev=0.03), gc(0.06, 2.6, (0, 1.4, 0), m["mar"], verts=8),
         gc(0.09, 0.1, (0, 2.4, 0), m["brass"], verts=8), gb((0.9, 0.06, 0.06), (0, 2.6, 0), m["mar"], bev=0.0)]
    for x in (-0.42, 0.42):
        p.append(gc(0.03, 0.15, (x, 2.53, 0), m["brass"], verts=6))
        p.append(blob(1.0, gpos(x, 2.32, 0), (0.13, 0.13, 0.15), m["lamp"], 1.0, seg=10, rings=6, amp=0.0))
    return p


def handcar_stop_station():
    return accent(handcar_stop, MAROON, MAROON_D)()


# ------------------------------------------------------------------ plan
K, W = "kenney", "world"
T = dict(ao=0.22, grad=0.86)
PLAN = {
    "grand_station":         ("station", grand_station, 512, W, dict(ao=0.06, grad=0.85)),
    "station_plot":          ("station", station_plot, 256, W, dict(ao=0.3, grad=0.9)),
    "platform_slot_v1":      ("station", lambda: _platform_slot(1), 256, W, dict(ao=0.25, grad=0.85)),
    "platform_slot_v2":      ("station", lambda: _platform_slot(2), 256, W, dict(ao=0.25, grad=0.85)),
    "platform_slot_v3":      ("station", lambda: _platform_slot(3), 256, W, dict(ao=0.25, grad=0.85)),
    "platform_slot_v4":      ("station", lambda: _platform_slot(4), 256, W, dict(ao=0.25, grad=0.85)),
    "platform_slot_v5":      ("station", lambda: _platform_slot(5), 256, W, dict(ao=0.25, grad=0.85)),
    "rail_bridge_8m":        ("station", rail_bridge_8m, 256, W, dict(ao=0.3, grad=0.85)),
    "rail_road_crossing_4m": ("station", rail_road_crossing_4m, 256, W, dict(ao=0.5, grad=0.9)),
    "express_loco":          ("station", express_loco, 512, W, dict(ao=0.22, grad=0.8)),
    "express_tender":        ("station", express_tender, 256, W, dict(ao=0.3, grad=0.8)),
    "express_coach":         ("station", express_coach, 256, W, dict(ao=0.25, grad=0.8)),
    "tree_station_lime":     ("station", lambda: station_tree("lime"), 512, K, T),
    "tree_station_cone":     ("station", lambda: station_tree("cone"), 512, K, T),
    "tree_station_lime_far": ("station", lambda: station_tree("lime", far=True), 256, K, T),
    "tree_station_cone_far": ("station", lambda: station_tree("cone", far=True), 256, K, T),
    "station_bench":         ("station", station_bench, 128, W, dict(ao=0.35, grad=0.85)),
    "clock_post":            ("station", clock_post, 128, W, dict(ao=0.25, grad=0.85)),
    "flower_planter":        ("station", flower_planter, 128, W, dict(ao=0.35, grad=0.85)),
    "luggage_cart":          ("station", luggage_cart, 128, W, dict(ao=0.35, grad=0.85)),
    "station_lamp":          ("station", station_lamp, 128, W, dict(ao=0.2, grad=0.85)),
    "handcar_stop_station":  ("station", handcar_stop_station, 256, W, dict(ao=0.22, grad=0.85)),
}

if __name__ == "__main__" and os.environ.get("M345_NO_RUN") != "1":
    run_plan(PLAN, f"{REPO}/tools/lookdev/build_m5_report.json", OUT_ROOT)
