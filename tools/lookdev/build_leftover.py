"""Replace the last Kenney models and prototype code-built shapes in Home Valley and Birch Bend with v3 GLBs
(same bake as build_v3.py / build_m1.py: albedo x height gradient x AO with a ground plane, one material,
one embedded texture). Placement for every file: assets/models_v3/ASSETS_LEFTOVER.md.

Usage (headless, Cycles on the RTX 3060 when available):
  /home/mm/.local/bin/blender -b --python tools/lookdev/build_leftover.py -- [only_name ...]
Report: tools/lookdev/build_leftover_report.json. Everything here is own work (CC0).

All builders below take Godot coordinates (x right, y up, +z toward the camera) through gb()/gc()/gl();
the conversion to Blender (x, -z, y) happens in one place.
"""
import os

exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "m2_lib.py")).read(), "m2_lib.py", "exec"))

OUT_ROOT = f"{REPO}/assets/models_v3"

# ------------------------------------------------------------------ V1 palette (matches World.gd / Shapes.gd colours)
ORANGE = (1.0, 0.45, 0.12)        # sawmill 1 frame, V1 machine accent
V1_GREEN = (0.3, 0.75, 0.3)       # sawmill 2 frame
BED_BLUE = (0.2, 0.5, 0.86)       # V1 saw beds (kept so the sawmills read the same as before)
MEGA_RED = (0.9, 0.28, 0.2)
ROOF_GREEN = (0.3, 0.55, 0.35)
ROOF_GREEN2 = (0.35, 0.55, 0.3)
LODGE_RED = (0.62, 0.24, 0.18)
LOG_SIDE = (0.62, 0.40, 0.24)
LOG_END = (0.93, 0.76, 0.52)
TYRE = (0.24, 0.23, 0.22)
STEEL_D = (0.45, 0.46, 0.47)
AWNING_RED = (0.86, 0.33, 0.26)
AWNING_CREAM = (0.98, 0.93, 0.82)
CONCRETE = (0.70, 0.67, 0.62)
BRICK = (0.66, 0.42, 0.33)


def wood_mats():
    return dict(plank=M("plank", PLANK, "planks"), dark=M("dark", DARK_WOOD, "bark"),
                bark=M("bark", LOG_SIDE, "bark"), end=M("rings", LOG_END, "rings"),
                yellow=M("yellow", YELLOW), steel=M("steel", STEEL), steel_d=M("steeld", STEEL_D),
                cream=M("cream", CREAM), grey=M("grey", WARM_GREY), tyre=M("tyre", TYRE),
                green_btn=M("btn", GREEN_BTN), glass=M("glass", GLASS), furn=M("furn", FURN, "planks"),
                red=M("red", (0.93, 0.33, 0.30)), door=M("door", DOOR_DARK, "planks"))


# ------------------------------------------------------------------ shared: conveyor pieces

BELT_H = 0.55   # Conveyor.HEIGHT: belt top


def belt_rails():
    """1 m of conveyor frame along Godot Z, centred, FLAT ENDS: scale.z = segment length (+0.8 overlap)."""
    y = 0.5   # half length in Blender Y
    yel, grey = M("yellow", YELLOW), M("frame", (0.50, 0.50, 0.50))
    p = []
    for s in (-1, 1):
        p.append(prism(rrect(0.08, 0.22, 0.025, cx=s * 0.44, cz=0.44), -y, y, grey, smooth=True))
        p.append(prism(rrect(0.13, 0.085, 0.035, cx=s * 0.45, cz=0.6), -y, y, yel, smooth=True))
    p.append(prism(rrect(0.82, 0.08, 0.02, cz=0.38), -y, y, grey))
    return p


def belt_legs():
    """One leg station (two legs + cross brace + feet), placed where Conveyor puts its BoxMesh legs."""
    st = M("leg", (0.42, 0.43, 0.44))
    p = []
    for s in (-1, 1):
        p.append(gb((0.07, 0.4, 0.07), (s * 0.35, 0.2, 0), st, bev=0.02, seg=1))
        p.append(gb((0.16, 0.04, 0.16), (s * 0.35, 0.02, 0), st, bev=0.015, seg=1))
    p.append(gb((0.7, 0.05, 0.05), (0, 0.18, 0), st, bev=0.015, seg=1))
    return p


def belt_end():
    """End roller at the start/end of a belt run; drum axis along Godot X at belt height."""
    yel, dark = M("yellow", YELLOW), M("drum", (0.32, 0.32, 0.33))
    p = [gc(0.07, 0.84, (0, BELT_H - 0.07, 0), dark, axis="x", verts=12)]
    for s in (-1, 1):
        p.append(gc(0.13, 0.05, (s * 0.46, BELT_H - 0.06, 0), yel, axis="x", verts=14, bev=0.015))
        p.append(gb((0.07, 0.42, 0.07), (s * 0.4, 0.21, 0), M("leg", (0.42, 0.43, 0.44)), bev=0.02, seg=1))
    return p


def palisade_post():
    """One upright palisade log: base at y 0, height 1.0, pointed top. Scale y 0.95-1.3 like today."""
    side = M("bark", (0.55, 0.34, 0.2), "bark")
    top = M("rings", (0.98, 0.8, 0.52), "rings")
    c = gc(0.16, 0.86, (0, 0.43, 0), side, verts=8)
    t = gc(0.16, 0.14, (0, 0.93, 0), top, verts=8, r2=0.03)
    return [c, t]


def bridge_river():
    """River bridge at (RIVER_X, 0, BRIDGE_Z): spans x -4.3..4.3, walkway z -1.3..1.3, deck top y 0.10."""
    m = wood_mats()
    rail = M("rail", (0.70, 0.50, 0.32), "bark")
    p = []
    rnd = random.Random(4)
    n = 13
    for i in range(n):
        x = -4.2 + i * (8.4 / (n - 1))
        p.append(gb((0.52, 0.07, 2.7 + rnd.uniform(-0.06, 0.06)), (x, 0.065, rnd.uniform(-0.04, 0.04)), m["plank"], bev=0.02, seg=1,
                    rot=(0, rnd.uniform(-2.5, 2.5), 0)))
    for z in (-0.95, 0.95):
        p.append(gl(0.1, 8.9, (0, 0.0, z), m["bark"], m["end"], axis="x", verts=8))
    for x in (-4.2, -2.1, 0.0, 2.1, 4.2):
        for z in (-1.33, 1.33):
            p.append(gl(0.08, 1.05, (x, 0.42, z), m["dark"], m["end"], axis="y", verts=6))
    for z in (-1.33, 1.33):
        p.append(gl(0.06, 8.7, (0, 0.92, z), rail, m["end"], axis="x", verts=8))
    stone = M("stone", WARM_GREY)
    for x in (-4.45, 4.45):
        for z in (-1.45, 1.45):
            p.append(blob(1.0, gpos(x, 0.05, z), (0.32, 0.26, 0.18), stone, x + z, seg=7, rings=4, amp=0.15))
    return p


# ------------------------------------------------------------------ shared: market

def shop_counter():
    """Counter for one product (Shop.add_shelf). 1.2 x 2.0, top at y 0.62 = the ItemStack height. Symmetric in x."""
    m = wood_mats()
    boards = M("boards", (0.80, 0.56, 0.34), "boards", bands=10.0, dir="Y")
    top = M("top", (0.72, 0.5, 0.3), "planks")
    p = [gb((1.2, 0.5, 2.0), (0, 0.3, 0), boards, bev=0.04),
         gb((1.24, 0.06, 2.04), (0, 0.03, 0), m["dark"], bev=0.02, seg=1),
         gb((1.32, 0.07, 2.12), (0, 0.585, 0), top, bev=0.03)]
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(gb((0.09, 0.56, 0.09), (sx * 0.58, 0.28, sz * 0.98), m["dark"], bev=0.025, seg=1))
    return p


def shop_till():
    """Till counter (Shop._build_till) with a cash chest instead of the Kenney chest. Top at y 0.96."""
    m = wood_mats()
    boards = M("boards", (0.80, 0.56, 0.34), "boards", bands=10.0, dir="Y")
    top = M("top", (0.72, 0.5, 0.3), "planks")
    gold = M("gold", (1.0, 0.80, 0.25))
    p = [gb((1.3, 0.86, 1.6), (0, 0.45, 0), boards, bev=0.05),
         gb((1.34, 0.06, 1.64), (0, 0.03, 0), m["dark"], bev=0.02, seg=1),
         gb((1.46, 0.08, 1.76), (0, 0.92, 0), top, bev=0.03)]
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(gb((0.1, 0.9, 0.1), (sx * 0.62, 0.45, sz * 0.77), m["dark"], bev=0.03, seg=1))
    # cash chest at the old chest spot (0, 0.96, 0.3)
    p.append(gb((0.5, 0.3, 0.62), (0, 1.11, 0.3), M("chest", (0.55, 0.33, 0.2), "planks"), bev=0.05))
    lid = gc(0.25, 0.62, (0, 1.26, 0.3), M("lid", (0.62, 0.38, 0.22), "planks"), axis="z", verts=14)
    p.append(lid)
    for z in (0.05, 0.55):
        p.append(gb((0.53, 0.33, 0.05), (0, 1.12, z), gold, bev=0.015, seg=1))
    p.append(gb((0.08, 0.1, 0.06), (0, 1.2, 0.3 - 0.33), gold, bev=0.02, seg=1))
    for i, (x, z) in enumerate(((0.0, -0.35), (0.12, -0.42), (-0.1, -0.45))):
        p.append(gc(0.08, 0.05 + 0.03 * i, (x, 0.985 + 0.015 * i, z), gold, verts=12))
    return p


def _canopy(stripe_a, stripe_b):
    """Market awning, origin = Shop x 0 and the canopy's z centre. 12 stripes, 10.1 m long, posts at x 0.55."""
    m = wood_mats()
    A, B = M("awA", stripe_a), M("awB", stripe_b)
    p = []
    L, n = 10.1, 12
    w = L / n
    for i in range(n):
        z = L / 2 - w * (i + 0.5)
        mat = A if i % 2 == 0 else B
        p.append(gb((1.0, 0.05, w + 0.004), (0.95, 2.35, z), mat, bev=0.02, seg=1, rot=(0, 0, -14)))
        p.append(gb((0.04, 0.2, w - 0.03), (1.45, 2.16, z), mat, bev=0.015, seg=1))
    for z in (L / 2, 0.0, -L / 2):
        p.append(gl(0.06, 2.45, (0.55, 1.225, z), m["dark"], m["end"], axis="y", verts=8))
    p.append(gl(0.055, L + 0.2, (0.5, 2.44, 0), m["dark"], m["end"], axis="z", verts=8))
    return p


def market_canopy():
    return _canopy(AWNING_RED, AWNING_CREAM)


# ------------------------------------------------------------------ shared: export truck + dock

def truck_flatbed():
    """V1 export truck at scale 1.0 (replaces car/truck-flat x 1.7). Cab at +Z, flatbed top y 1.25 over z -2.35..0.5."""
    m = wood_mats()
    cab = M("cab", (0.95, 0.45, 0.15))
    chassis = M("chassis", (0.30, 0.29, 0.29))
    hub = M("hub", CREAM)
    p = [gb((1.4, 0.3, 4.5), (0, 0.62, -0.05), chassis, bev=0.06)]
    for x in (-0.98, 0.98):
        for z in (-1.55, 1.45):
            p.append(gc(0.42, 0.3, (x, 0.42, z), m["tyre"], axis="x", verts=12, bev=0.03))
            p.append(gc(0.2, 0.32, (x, 0.42, z), hub, axis="x", verts=8))
            p.append(gb((0.36, 0.12, 1.0), (x, 0.92, z), chassis, bev=0.05, seg=1))
    p.append(gb((2.2, 0.13, 2.9), (0, 1.185, -0.92), m["plank"], bev=0.03))
    for x in (-1.05, 1.05):
        for z in (-2.3, -0.9, 0.45):
            p.append(gb((0.09, 0.38, 0.09), (x, 1.43, z), m["dark"], bev=0.025, seg=1))
    p.append(gb((2.2, 0.55, 0.12), (0, 1.5, 0.55), cab, bev=0.04))           # headboard behind the cab
    p.append(gb((2.1, 0.75, 1.65), (0, 1.22, 1.45), cab, bev=0.14, seg=2))    # lower cab + hood
    p.append(gb((2.0, 0.75, 1.1), (0, 1.9, 1.15), cab, bev=0.16, seg=2))      # cabin
    p.append(gb((1.9, 0.1, 1.15), (0, 2.3, 1.15), m["cream"], bev=0.05))      # roof cap
    p.append(gb((1.7, 0.48, 0.06), (0, 1.92, 1.72), m["glass"], bev=0.03, rot=(-12, 0, 0)))
    for x in (-1.01, 1.01):
        p.append(gb((0.05, 0.42, 0.7), (x, 1.95, 1.1), m["glass"], bev=0.02))
    p.append(gb((2.15, 0.22, 0.16), (0, 0.78, 2.3), m["steel"], bev=0.06))     # bumper
    for x in (-0.75, 0.75):
        p.append(gc(0.1, 0.06, (x, 1.12, 2.28), M("lamp", (1.0, 0.92, 0.6)), axis="z", verts=10))
    p.append(gb((0.9, 0.35, 0.05), (0, 1.15, 2.28), M("grille", (0.35, 0.33, 0.32)), bev=0.03))
    return p


def truck_dock():
    """TruckDock slab + posts, origin = dock origin (the slab sits at x +0.6 like today; top y 0.18)."""
    m = wood_mats()
    con = M("concrete", CONCRETE)
    p = [gb((4.2, 0.18, 5.0), (0.6, 0.09, 0), con, bev=0.06)]
    p.append(gb((0.22, 0.24, 5.0), (2.62, 0.2, 0), m["dark"], bev=0.05))
    for i in range(5):
        p.append(gb((0.06, 0.012, 0.5), (2.35, 0.186, -2.0 + i * 1.0), m["yellow"], bev=0.0))
    for z in (-2.3, 2.3):
        p.append(gb((0.22, 1.7, 0.22), (2.25, 0.85, z), m["yellow"], bev=0.06))
        p.append(gb((0.3, 0.08, 0.3), (2.25, 1.74, z), m["steel_d"], bev=0.03))
        p.append(gb((0.26, 0.24, 0.26), (2.25, 1.9, z), M("lamp", (1.0, 0.93, 0.62)), bev=0.06))
        p.append(gb((0.34, 0.06, 0.34), (2.25, 2.05, z), m["steel_d"], bev=0.03))
        p.append(gb((0.36, 0.1, 0.36), (2.25, 0.05, z), m["steel_d"], bev=0.03))
    return p


# ------------------------------------------------------------------ Home Valley machines + buildings

def _sawmill(frame_rgb):
    """_dress_sawmill without the code belt and ChainSaw: same coordinates, origin = Machine.body."""
    m = wood_mats()
    bed, fr = M("bed", BED_BLUE), M("frame", frame_rgb)
    p = [gb((4.4, 0.38, 1.15), (0, 0.31, 0.2), bed, bev=0.1, seg=2)]
    for x in (-1.8, 1.8):
        for z in (-0.25, 0.65):
            p.append(gb((0.18, 0.14, 0.18), (x, 0.07, z), m["steel_d"], bev=0.04, seg=1))
    for z in (-0.42, 0.82):
        p.append(gb((4.5, 0.14, 0.12), (0, 0.56, z), m["yellow"], bev=0.04))
    for x in (-0.75, 0.75):
        p.append(gb((0.26, 2.7, 0.32), (x, 1.35, -0.45), fr, bev=0.08))
        p.append(gb((0.42, 0.12, 0.5), (x, 0.06, -0.45), fr, bev=0.04))
    p.append(gb((1.8, 0.3, 0.36), (0, 2.7, -0.45), fr, bev=0.09))
    p.append(gb((1.9, 0.08, 0.42), (0, 2.88, -0.45), m["yellow"], bev=0.03))
    for s in (-1, 1):   # corner gussets
        p.append(gb((0.36, 0.08, 0.1), (s * 0.52, 2.45, -0.45), fr, bev=0.03, rot=(0, 0, s * 45)))
    p.append(gb((0.1, 0.58, 0.1), (1.4, 0.29, -0.75), m["steel_d"], bev=0.03, seg=1))
    p.append(gb((0.35, 0.5, 0.3), (1.4, 0.8, -0.75), m["yellow"], bev=0.08))
    p.append(gb((0.22, 0.16, 0.05), (1.4, 0.92, -0.58), m["green_btn"], bev=0.02))
    p.append(gc(0.035, 0.04, (1.4, 0.72, -0.585), m["red"], axis="z", verts=10))
    for k in range(3):
        p.append(gl(0.17, 1.3, (-1.2, 0.17, -1.25 + k * 0.36 - 0.36), m["bark"], m["end"]))
    for z in (-0.18, 0.18):
        p.append(gl(0.17, 1.3, (-1.2, 0.47, -1.25 + z), m["bark"], m["end"]))
    return p


def sawmill_body_orange():
    return _sawmill(ORANGE)


def sawmill_body_green():
    return _sawmill(V1_GREEN)


def _shed_frame(w, d, h, roof_rgb, m):
    """Open shed like World._shed: floor, four log posts, beams, lean-to roof over the back (-Z) 62%."""
    roof = M("roof", roof_rgb, "boards", bands=12.0, dir="X")
    p = [gb((w, 0.2, d), (0, 0.1, 0), m["plank"], bev=0.05)]
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(gl(0.13, h, (sx * (w / 2 - 0.2), h / 2, sz * (d / 2 - 0.2)), m["bark"], m["end"], axis="y", verts=9))
    for z in (-d / 2 + 0.2, d / 2 - 0.2):
        p.append(gb((w + 0.2, 0.2, 0.24), (0, h, z), m["dark"], bev=0.05))
    slope = math.radians(18)
    depth = d * 0.5 + 0.35
    panel = depth / math.cos(slope)
    rise = depth * math.tan(slope)
    zc = -d / 2 - 0.4 + depth / 2
    p.append(gb((w + 0.7, 0.16, panel), (0, h + rise / 2 + 0.1, zc), roof, bev=0.05, rot=(18, 0, 0)))
    p.append(gb((w + 0.8, 0.2, 0.22), (0, h + 0.1, zc + depth / 2), M("trim", tuple(c * 0.75 for c in roof_rgb)), bev=0.05))
    p.append(gb((w + 0.2, rise + 0.2, 0.18), (0, h + rise / 2, -d / 2 + 0.2), m["dark"], bev=0.04))
    return p


def office_hut():
    """Upgrade Office (World._build_office), origin = office root. 3.2 x 2.4 open shed, desk, cash chest, notice board."""
    m = wood_mats()
    p = _shed_frame(3.2, 2.4, 2.1, ROOF_GREEN, m)
    p.append(gb((2.8, 0.9, 0.1), (0, 0.65, -1.0), M("wall", (0.84, 0.6, 0.37), "boards", bands=14.0, dir="X"), bev=0.03))
    # desk (old workbench spot)
    p.append(gb((1.15, 0.07, 0.62), (-0.6, 0.93, -0.3), m["furn"], bev=0.025))
    for sx in (-1, 1):
        p.append(gb((0.08, 0.7, 0.55), (-0.6 + sx * 0.5, 0.55, -0.3), m["furn"], bev=0.02, seg=1))
    p.append(gb((0.42, 0.012, 0.3), (-0.75, 0.97, -0.25), M("paper", (0.98, 0.96, 0.9)), bev=0.0, rot=(0, 12, 0)))
    p.append(gb((0.3, 0.05, 0.22), (-0.3, 0.99, -0.35), M("ledger", (0.25, 0.45, 0.32)), bev=0.01, rot=(0, -8, 0)))
    p.append(gc(0.04, 0.07, (-0.95, 1.0, -0.45), M("ink", (0.2, 0.22, 0.3)), verts=8))
    p.append(gc(0.17, 0.05, (-0.6, 0.62, 0.3), m["furn"], verts=12))                 # stool
    for a in range(3):
        aa = a * 2.094
        p.append(gb((0.04, 0.42, 0.04), (-0.6 + 0.11 * math.cos(aa), 0.4, 0.3 + 0.11 * math.sin(aa)), m["dark"], bev=0.01, seg=1))
    # cash chest (old chest spot)
    gold = M("gold", (1.0, 0.8, 0.25))
    p.append(gb((0.66, 0.4, 0.48), (0.8, 0.4, -0.4), M("chest", (0.55, 0.33, 0.2), "planks"), bev=0.05))
    p.append(gb((0.68, 0.08, 0.5), (0.8, 0.64, -0.62), M("lid", (0.62, 0.38, 0.22), "planks"), bev=0.03, rot=(-55, 0, 0)))
    for x in (0.55, 1.05):
        p.append(gb((0.05, 0.42, 0.5), (x, 0.41, -0.4), gold, bev=0.015, seg=1))
    for i in range(4):
        p.append(gc(0.07, 0.04, (0.66 + i * 0.09, 0.62 + 0.02 * (i % 2), -0.38), gold, verts=10))
    # notice board with a painted up-arrow (old signpost spot)
    p.append(gl(0.06, 1.5, (1.9, 0.75, 1.3), m["dark"], m["end"], axis="y", verts=8))
    p.append(gb((0.8, 0.6, 0.07), (1.9, 1.35, 1.34), M("board", (0.93, 0.80, 0.58), "planks"), bev=0.03))
    arrow = M("arrow", (0.25, 0.68, 0.32))
    p.append(gb((0.13, 0.26, 0.03), (1.9, 1.27, 1.385), arrow, bev=0.0))
    p.append(gpoly([(1.73, 1.4, 1.40), (2.07, 1.4, 1.40), (1.9, 1.58, 1.40)], 0.03, arrow))
    return p


def saw_blade():
    """Spinning saw disc (Machine.add_saw_blade), r 0.3, disc normal along Godot Z, pivot at its centre."""
    st, mark = M("steel", (0.80, 0.82, 0.85)), M("mark", (0.9, 0.35, 0.15))
    p = [gc(0.27, 0.03, (0, 0, 0), st, axis="z", verts=24)]
    for i in range(16):
        a = 2 * math.pi * i / 16
        t = gb((0.06, 0.05, 0.03), (0.285 * math.cos(a), 0.285 * math.sin(a), 0), st, bev=0.0, rot=(0, 0, math.degrees(a) + 30))
        p.append(t)
    for i in range(4):
        a = 2 * math.pi * i / 4 + 0.4
        p.append(gb((0.12, 0.04, 0.036), (0.16 * math.cos(a), 0.16 * math.sin(a), 0), mark, bev=0.01, seg=1, rot=(0, 0, math.degrees(a))))
    p.append(gc(0.05, 0.05, (0, 0, 0), M("hub", (0.35, 0.35, 0.36)), axis="z", verts=10))
    return p


def carpentry_shed():
    """Carpentry (World._build_carpentry), origin = Machine.body. Workbench left, saw bench right (the blade is saw_blade.glb)."""
    m = wood_mats()
    p = _shed_frame(3.6, 2.6, 2.3, ROOF_GREEN2, m)
    p.append(gb((3.2, 1.0, 0.1), (0, 0.7, -1.1), M("wall", (0.84, 0.6, 0.37), "boards", bands=14.0, dir="X"), bev=0.03))
    for x, rz in ((-1.1, 0), (-0.75, 0), (0.2, 15)):   # tools on the back wall
        p.append(gb((0.05, 0.42, 0.03), (x, 1.45, -1.03), m["dark"], bev=0.01, seg=1, rot=(0, 0, rz)))
    p.append(gb((0.36, 0.14, 0.02), (-1.1, 1.62, -1.02), m["steel"], bev=0.0))
    p.append(gb((0.12, 0.1, 0.05), (-0.75, 1.7, -1.02), m["steel_d"], bev=0.02, seg=1))
    # workbench with a vise and planks (old workbench spot, x -0.7)
    p.append(gb((1.15, 0.09, 0.66), (-0.7, 0.92, 0.1), m["furn"], bev=0.03))
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(gb((0.08, 0.7, 0.08), (-0.7 + sx * 0.5, 0.55, 0.1 + sz * 0.26), m["dark"], bev=0.02, seg=1))
    p.append(gb((1.0, 0.05, 0.05), (-0.7, 0.4, 0.1), m["dark"], bev=0.015, seg=1))
    p.append(gb((0.16, 0.12, 0.12), (-1.25, 1.0, 0.38), m["steel_d"], bev=0.03))
    p.append(gb((0.9, 0.06, 0.24), (-0.65, 1.0, 0.0), m["plank"], bev=0.015, rot=(0, 6, 0)))
    p.append(gb((0.85, 0.06, 0.24), (-0.7, 1.06, 0.02), m["plank"], bev=0.015, rot=(0, -4, 0)))
    # saw bench under the blade (old grinder spot, x 0.8): top 0.95, blade at (0.8, 1.05, 0.35)
    p.append(gb((0.9, 0.1, 0.9), (0.8, 0.9, 0.3), M("sawtop", (0.66, 0.66, 0.64)), bev=0.03))
    p.append(gb((0.8, 0.65, 0.8), (0.8, 0.52, 0.3), M("sawbox", ORANGE), bev=0.06))
    p.append(gb((0.06, 0.04, 0.7), (0.8, 0.96, 0.3), M("slot", (0.2, 0.2, 0.21)), bev=0.0))
    p.append(gb((0.2, 0.18, 0.05), (0.8, 0.6, 0.72), m["yellow"], bev=0.02))
    # chair in progress (old chair spot, rot 30)
    ch = item_chair()
    gmove(ch, 0.9, 0.2, -0.95, rot_y_deg=30)
    p += ch
    return p


def cnc_router():
    """CNC router (World._build_cnc), origin = Machine.body. Table at y 0.93, gantry, spindle; cog = cnc_cog.glb at (0, 2.45, 0)."""
    m = wood_mats()
    green, body = M("green", V1_GREEN), M("body", CREAM)
    p = [gb((3.8, 0.2, 2.8), (0, 0.1, 0), m["grey"], bev=0.06)]
    p.append(gb((2.6, 0.7, 1.5), (0, 0.55, 0), body, bev=0.1, seg=3))
    p.append(gb((2.64, 0.18, 1.54), (0, 0.32, 0), green, bev=0.06))
    p.append(gb((2.5, 0.06, 1.4), (0, 0.93, 0), m["steel"], bev=0.02))
    p.append(gb((1.4, 0.06, 0.5), (0, 0.99, 0.15), m["plank"], bev=0.015))
    for s in (-1, 1):
        p.append(gb((0.26, 1.2, 0.42), (s * 1.27, 1.45, -0.2), green, bev=0.08))
    p.append(gb((2.8, 0.34, 0.42), (0, 2.05, -0.2), green, bev=0.1, seg=3))
    p.append(gb((2.85, 0.06, 0.12), (0, 2.08, 0.03), m["yellow"], bev=0.02))
    p.append(gb((0.46, 0.6, 0.42), (0.25, 1.75, 0.12), M("head", ORANGE), bev=0.1, seg=3))
    p.append(gc(0.07, 0.4, (0.25, 1.28, 0.12), m["steel"], verts=10))
    p.append(gc(0.03, 0.12, (0.25, 1.03, 0.12), m["steel_d"], verts=8, r2=0.005))
    p.append(gc(0.06, 0.9, (-0.2, 2.25, -0.3), M("hose", (0.3, 0.3, 0.32)), axis="x", verts=8))
    # control screen on a stand (old screen spot) and a lever box (old lever spot)
    p.append(gb((0.08, 1.0, 0.08), (-1.2, 0.7, -1.0), m["steel_d"], bev=0.02, seg=1))
    p.append(gb((0.65, 0.5, 0.1), (-1.2, 1.35, -0.98), body, bev=0.05, rot=(-15, 0, 0)))
    p.append(gb((0.52, 0.36, 0.03), (-1.2, 1.36, -0.92), M("screen", (0.45, 0.85, 0.95)), bev=0.01, rot=(-15, 0, 0)))
    p.append(gb((0.4, 0.45, 0.3), (1.3, 0.42, -0.9), m["yellow"], bev=0.07))
    p.append(gc(0.025, 0.35, (1.3, 0.8, -0.9), m["steel_d"], verts=8))
    p.append(blob(1.0, gpos(1.3, 0.99, -0.9), (0.06, 0.06, 0.06), m["red"], 1.0, seg=8, rings=5, amp=0.0))
    return p


def cnc_cog():
    """Cog on top of the CNC (spinner). Disc normal along Godot Z, pivot at its centre, r 0.45."""
    yel, dark = M("yellow", YELLOW), M("hub", (0.35, 0.35, 0.36))
    p = [gc(0.36, 0.1, (0, 0, 0), yel, axis="z", verts=16)]
    for i in range(12):
        a = 2 * math.pi * i / 12
        p.append(gb((0.12, 0.1, 0.1), (0.4 * math.cos(a), 0.4 * math.sin(a), 0), yel, bev=0.0, rot=(0, 0, math.degrees(a))))
    p.append(gc(0.1, 0.14, (0, 0, 0), dark, axis="z", verts=12))
    for i in range(4):
        a = 2 * math.pi * i / 4 + 0.785
        p.append(gc(0.06, 0.12, (0.2 * math.cos(a), 0.2 * math.sin(a), 0), dark, axis="z", verts=8))
    return p


def bookcase_factory():
    """Bookcase Factory (World._build_factory), origin = Machine.body. Open-front hall, chimney (smoke at (-1.9, 3.6, -1.5)),
    hopper at mouth_in (-2.2, 1.4, -0.4), saw unit + press inside; arms = factory_arm.glb at (-2.3, 0.22, 1.2) and (2.4, 0.22, 1.2)."""
    m = wood_mats()
    walls = M("walls", CREAM, "boards", bands=16.0, dir="X")
    walls_s = M("walls2", CREAM, "boards", bands=16.0, dir="Y")
    roof = M("roof", (0.74, 0.33, 0.22), "boards", bands=12.0, dir="X")
    orange, green = M("orange", ORANGE), M("green", V1_GREEN)
    p = [gb((5.4, 0.22, 3.6), (0, 0.11, 0), m["grey"], bev=0.07)]
    p.append(gb((5.2, 3.0, 0.16), (0, 1.72, -1.72), walls, bev=0.04))
    for s in (-1, 1):
        pts = [(s * 2.62, 0.22, -1.78), (s * 2.62, 0.22, -0.18), (s * 2.62, 2.72, -0.18), (s * 2.62, 3.2, -1.78)]
        p.append(gpoly(pts if s > 0 else list(reversed(pts)), 0.14, walls_s))
        p.append(gb((0.2, 2.6, 0.2), (s * 2.62, 1.52, -0.18), m["dark"], bev=0.05))
    p.append(gb((5.5, 0.2, 0.2), (0, 2.75, -0.18), m["dark"], bev=0.05))
    slope = 14
    p.append(gb((5.9, 0.16, 2.1), (0, 3.02, -1.05), roof, bev=0.05, rot=(slope, 0, 0)))
    # chimney (brick) through the roof
    p.append(gb((0.6, 3.4, 0.6), (-1.9, 1.92, -1.5), M("brick", BRICK), bev=0.06))
    p.append(gb((0.74, 0.16, 0.74), (-1.9, 3.62, -1.5), m["grey"], bev=0.05))
    # hopper (intake) at the left
    hop = M("hopper", ORANGE)
    top, bot, zt, z0 = 0.55, 0.22, 1.45, 0.85
    cx, cz = -2.25, -0.55
    for w in (((cx - top, cz - top), (cx + top, cz - top), (cx + bot, cz - bot), (cx - bot, cz - bot)),
              ((cx + top, cz + top), (cx - top, cz + top), (cx - bot, cz + bot), (cx + bot, cz + bot)),
              ((cx - top, cz + top), (cx - top, cz - top), (cx - bot, cz - bot), (cx - bot, cz + bot)),
              ((cx + top, cz - top), (cx + top, cz + top), (cx + bot, cz + bot), (cx + bot, cz - bot))):
        a, b, c, d = w
        p.append(trapezoid_wall(Vector(gpos(a[0], zt, a[1])), Vector(gpos(b[0], zt, b[1])), Vector(gpos(c[0], z0, c[1])),
                                Vector(gpos(d[0], z0, d[1])), 0.05, hop))
    p.append(gb((0.5, 0.65, 0.5), (cx, 0.54, cz), m["steel_d"], bev=0.06))
    p.append(gb((1.2, 0.08, 1.2), (cx, 1.47, cz), m["yellow"], bev=0.03))
    # panel saw unit (old machine-fortified spot) and assembly press (old machine spot)
    p.append(gb((1.4, 1.1, 1.2), (-0.9, 0.77, -0.6), orange, bev=0.12, seg=3))
    p.append(gb((1.2, 0.3, 0.9), (-0.9, 1.45, -0.7), m["cream"], bev=0.08))
    p.append(gb((0.16, 0.16, 0.05), (-0.5, 1.0, 0.02), m["green_btn"], bev=0.02))
    p.append(gb((1.2, 1.3, 1.1), (1.3, 0.87, -0.65), green, bev=0.12, seg=3))
    p.append(gb((1.3, 0.22, 1.2), (1.3, 1.62, -0.65), m["cream"], bev=0.07))
    p.append(gc(0.12, 0.5, (1.3, 1.95, -0.65), m["steel"], verts=10))
    # roller table to the output and a half-built bookcase on it
    p.append(gb((2.3, 0.1, 0.7), (1.1, 0.82, 0.35), m["steel"], bev=0.03))
    for x in (0.1, 2.1):
        for z in (0.1, 0.6):
            p.append(gb((0.07, 0.6, 0.07), (x, 0.52, z), m["steel_d"], bev=0.02, seg=1))
    for i in range(6):
        p.append(gc(0.035, 0.66, (0.15 + i * 0.38, 0.89, 0.35), m["steel_d"], axis="z", verts=8))
    bc = item_bookcase()
    for o in bc:
        o.matrix_world = Matrix.Translation(gpos(1.6, 0.87, 0.35)) @ Matrix.Diagonal((0.8, 0.8, 0.8, 1)) @ o.matrix_world
    p += bc
    return p


def factory_arm():
    """Robot arm (Machine.arms rotate it about Y), pivot at the base; reaches toward -Z (into the factory). 1.9 m tall."""
    orange, dark = M("orange", ORANGE), M("joint", (0.3, 0.3, 0.32))
    p = [gc(0.3, 0.22, (0, 0.11, 0), dark, verts=16, bev=0.03),
         gc(0.22, 0.3, (0, 0.37, 0), orange, verts=14, bev=0.03)]
    lo = gb((0.2, 1.05, 0.2), (0, 0.95, -0.2), orange, bev=0.07, rot=(-22, 0, 0))
    p.append(lo)
    p.append(gc(0.13, 0.28, (0, 1.42, -0.4), dark, axis="x", verts=12))
    p.append(gb((0.16, 0.85, 0.16), (0, 1.47, -0.82), orange, bev=0.06, rot=(-75, 0, 0)))
    p.append(gc(0.1, 0.22, (0, 1.36, -1.22), dark, axis="x", verts=10))
    for s in (-1, 1):
        p.append(gb((0.04, 0.22, 0.06), (s * 0.06, 1.18, -1.26), M("steel", STEEL), bev=0.015, seg=1))
    return p


def grand_lodge():
    """Grand Lodge (World._build_lodge), origin = lodge root. 7 x 5 log cabin, red roof, porch + bench + rocking chair.
    Window glass is dark warm; lodge_windows.glb (emissive) sits in front of it."""
    m = wood_mats()
    log_m = M("log", (0.62, 0.40, 0.24), "bark")
    end_m = M("logend", (0.86, 0.68, 0.45), "rings")
    roof = M("roof", LODGE_RED, "boards", bands=14.0, dir="X")
    w, d, h, r = 7.0, 5.0, 3.2, 0.27
    rows = int(h / (r * 1.8))
    p = []
    for i in range(rows):
        y = r + i * r * 1.8
        for s in (-1, 1):
            p.append(gll(r, w + 0.5, (0, y, s * d / 2), log_m, end_m, axis="x", verts=8))
            p.append(gll(r, d + 0.5, (s * w / 2, y + r * 0.9, 0), log_m, end_m, axis="z", verts=8))
    slope = math.radians(32)
    half_d = d / 2 + 0.7
    panel = half_d / math.cos(slope)
    rise = half_d * math.tan(slope)
    for s in (-1, 1):
        p.append(gb((w + 1.2, 0.25, panel), (0, h + rise / 2 + 0.1, s * half_d / 2), roof, bev=0.07, rot=(s * 32, 0, 0)))
    p.append(gl(0.16, w + 1.3, (0, h + rise + 0.2, 0), M("ridge", (0.5, 0.2, 0.15)), end_m, axis="x", verts=8))
    g_rise = d / 2 * math.tan(slope)
    for z in (d / 2 - 0.1, -d / 2 - 0.1):
        p.append(_gable_fill(w - 0.3, h + 0.1, g_rise + 0.1, -z - 0.1, M("gable", (0.66, 0.44, 0.27), "boards", bands=16.0, dir="X"), thick=0.2))
    p.append(gb((0.9, 2.6, 0.9), (2.2, h + rise * 0.8, -0.8), M("stone", WARM_GREY), bev=0.1, seg=2))
    p.append(gb((1.05, 0.15, 1.05), (2.2, h + rise * 0.8 + 1.35, -0.8), M("stone2", (0.5, 0.47, 0.43)), bev=0.05))
    fz = d / 2 + r
    p.append(gb((1.1, 2.0, 0.12), (0, 1.0, fz + 0.01), m["door"], bev=0.04))
    p.append(gb((1.35, 0.14, 0.16), (0, 2.08, fz + 0.03), m["dark"], bev=0.04))
    p.append(gc(0.05, 0.06, (0.35, 1.0, fz + 0.09), M("knob", (1.0, 0.8, 0.25)), axis="z", verts=8))
    frame, glass = M("frame", (0.97, 0.95, 0.9)), M("glassw", (0.55, 0.42, 0.26))
    for x in (-2.4, 2.4):
        p.append(gb((1.16, 1.06, 0.08), (x, 1.7, fz - 0.02), frame, bev=0.03))
        p.append(gb((0.96, 0.86, 0.06), (x, 1.7, fz + 0.01), glass, bev=0.0))
        p.append(gb((0.06, 0.86, 0.04), (x, 1.7, fz + 0.04), frame, bev=0.0))
        p.append(gb((1.1, 0.2, 0.26), (x, 1.12, fz + 0.14), M("box", (0.55, 0.36, 0.22), "planks"), bev=0.04))
        for k in range(3):
            p.append(blob(1.0, gpos(x - 0.33 + k * 0.33, 1.27, fz + 0.14), (0.15, 0.11, 0.1),
                          M("fl%d" % (k % 2), (0.93, 0.33, 0.30) if k % 2 == 0 else (0.98, 0.84, 0.25)), k, seg=6, rings=4, amp=0.12))
    # porch
    p.append(gb((w + 1.6, 0.25, 1.8), (0, 0.125, d / 2 + 1.1), m["plank"], bev=0.05))
    for x in (-(w + 1.6) / 2 + 0.12, (w + 1.6) / 2 - 0.12):
        p.append(gl(0.07, 0.75, (x, 0.6, d / 2 + 1.85), m["dark"], m["end"], axis="y", verts=8))
        p.append(gb((0.08, 0.08, 1.7), (x, 0.92, d / 2 + 1.1), m["dark"], bev=0.025, seg=1))
    # bench (old bench spot) and rocking chair (old lounge chair spot)
    bx, bz = -2.6, d / 2 + 1.25
    p.append(gb((1.3, 0.07, 0.4), (bx, 0.68, bz), m["furn"], bev=0.025))
    p.append(gb((1.3, 0.35, 0.06), (bx, 0.95, bz - 0.2), m["furn"], bev=0.02))
    for sx in (-1, 1):
        p.append(gb((0.07, 0.42, 0.36), (bx + sx * 0.55, 0.46, bz), m["dark"], bev=0.02, seg=1))
    cx, cz = 2.0, d / 2 + 1.0
    p.append(gb((0.55, 0.07, 0.5), (cx, 0.72, cz), m["furn"], bev=0.025))
    p.append(gb((0.55, 0.6, 0.06), (cx, 1.05, cz - 0.26), m["furn"], bev=0.02, rot=(-10, 0, 0)))
    for sx in (-1, 1):
        p.append(gb((0.06, 0.06, 0.8), (cx + sx * 0.26, 0.3, cz), m["dark"], bev=0.0, rot=(8, 0, 0)))
        for dz in (0.2, -0.2):
            p.append(gb((0.06, 0.45, 0.06), (cx + sx * 0.26, 0.5, cz + dz), m["dark"], bev=0.0))
    return p


def lodge_windows():
    """Two warm emissive panes for the lodge (no bake). Front faces +Z, at the window centres of grand_lodge."""
    p = []
    for x in (-2.4, 2.4):
        for dx in (-0.25, 0.25):
            pl = _add("primitive_plane_add", size=1.0, location=(0, 0, 0))
            pl.scale = (0.44, 0.8, 1); bpy.ops.object.transform_apply(scale=True)
            pl.rotation_euler = (math.pi / 2, 0, 0)
            pl.location = gpos(x + dx, 1.7, 2.5 + 0.27 + 0.045)   # just in front of the glass (front face z 2.81), behind the mullion
            p.append(pl)
    return p


def megasaw_body():
    """Mega Saw (MegaSaw.gd) without the code belt, ChainSaw and log. Origin = MegaSaw.body."""
    m = wood_mats()
    bed, red = M("bed", (0.2, 0.5, 0.88)), M("red", MEGA_RED)
    sx = 1.6
    p = [gb((8.4, 0.7, 2.6), (-0.6, 0.45, 0), bed, bev=0.14, seg=3)]
    for x in (-4.3, -1.6, 1.1, 3.2):
        for z in (-1.0, 1.0):
            p.append(gb((0.3, 0.12, 0.3), (x, 0.06, z), m["steel_d"], bev=0.04, seg=1))
    for z in (-1.25, 1.25):
        p.append(gb((8.5, 0.2, 0.2), (-0.6, 0.85, z), m["yellow"], bev=0.06))
    p.append(gb((0.6, 4.8, 0.6), (sx, 2.4, -1.8), red, bev=0.14, seg=3))
    p.append(gb((1.1, 0.16, 1.1), (sx, 0.08, -1.8), m["steel_d"], bev=0.05))
    p.append(gb((0.7, 0.6, 2.4), (sx, 4.5, -0.7), red, bev=0.14, seg=3))
    p.append(gb((0.8, 0.12, 2.5), (sx, 4.86, -0.7), m["yellow"], bev=0.05))
    p.append(gb((0.3, 1.3, 0.3), (sx, 3.75, -1.15), red, bev=0.08, rot=(-40, 0, 0)))
    for k in range(4):   # warning stripes on the pillar
        p.append(gb((0.62, 0.1, 0.62), (sx, 0.5 + k * 0.25, -1.8), m["yellow"] if k % 2 == 0 else M("blk", (0.2, 0.2, 0.2)), bev=0.03, seg=1))
    p.append(blob(1.0, gpos(sx + 0.9, 0.0, 1.9), (1.32, 0.88, 0.54), M("dust", (0.98, 0.84, 0.58)), 2.0, seg=12, rings=6, amp=0.1))
    p.append(gb((0.5, 0.7, 0.4), (3.0, 0.5, -1.7), m["yellow"], bev=0.08))
    p.append(gb((0.3, 0.2, 0.05), (3.0, 0.65, -1.48), m["green_btn"], bev=0.02))
    return p


def megasaw_crane():
    """Tower crane for the Mega Saw. Origin = mast base; jib along +X at y 6.0 (tip x 4.2). Place at (-4.2, 0, -2.2), rot_y -20."""
    m = wood_mats()
    yel, dark = M("yellow", YELLOW), M("dark", (0.3, 0.3, 0.32))
    p = [gb((1.4, 0.35, 1.4), (0, 0.175, 0), M("concrete", CONCRETE), bev=0.07)]
    p.append(gb((0.45, 5.4, 0.45), (0, 3.05, 0), yel, bev=0.08))
    for k in range(6):
        p.append(gb((0.47, 0.06, 0.47), (0, 0.9 + k * 0.85, 0), dark, bev=0.02, seg=1))
    p.append(gb((0.9, 0.75, 0.9), (0.1, 6.0, 0), m["cream"], bev=0.12, seg=3))
    p.append(gb((0.06, 0.4, 0.6), (0.56, 6.05, 0), m["glass"], bev=0.02))
    p.append(gb((4.6, 0.32, 0.36), (2.5, 6.25, 0), yel, bev=0.08))
    p.append(gb((1.9, 0.28, 0.32), (-1.2, 6.25, 0), yel, bev=0.08))
    p.append(gb((0.75, 0.6, 0.6), (-1.75, 5.9, 0), M("weight", CONCRETE), bev=0.08))
    p.append(gb((0.3, 1.3, 0.3), (0, 7.0, 0), yel, bev=0.06))
    for x1 in (4.4, -1.9):
        p.append(gseg((0, 7.6, 0), (x1, 6.4, 0), 0.025, dark))
    p.append(gb((0.4, 0.22, 0.42), (3.7, 5.98, 0), dark, bev=0.05))
    return p


def crane_hook():
    """Hook on its cable (MegaSaw._crane_hook): origin = hook bottom (sits on the log), cable up to y 3.0."""
    yel, dark = M("yellow", YELLOW), M("dark", (0.25, 0.25, 0.27))
    p = [gc(0.025, 2.7, (0, 1.65, 0), dark, verts=6)]
    p.append(gb((0.32, 0.26, 0.2), (0, 0.38, 0), yel, bev=0.06))
    p.append(gb((0.34, 0.06, 0.22), (0, 0.38, 0), dark, bev=0.02, seg=1))
    t = _add("primitive_torus_add", major_radius=0.1, minor_radius=0.03, major_segments=10, minor_segments=5,
             location=gpos(0, 0.13, 0), rotation=(math.pi / 2, 0, 0))
    _assign(t, M("steel", STEEL)); _smooth(t); p.append(t)
    return p


def road_sign():
    """TIMBER VALLEY road sign (roadsign pad), origin = sign root. Board face at z +0.07: Label3D at (0, 2.1, 0.09)."""
    m = wood_mats()
    p = []
    for x in (-0.9, 0.9):
        p.append(gl(0.12, 2.6, (x, 1.3, 0), m["bark"], m["end"], axis="y", verts=9))
        p.append(gc(0.12, 0.2, (x, 2.7, 0), m["end"], verts=9, r2=0.03))
    p.append(gb((2.4, 1.1, 0.14), (0, 2.1, 0), M("board", (0.9, 0.66, 0.4), "planks"), bev=0.04))
    fr = M("frame", (0.5, 0.32, 0.18))
    for y in (1.55, 2.65):
        p.append(gb((2.5, 0.08, 0.18), (0, y, 0), fr, bev=0.03, seg=1))
    for x in (-1.22, 1.22):
        p.append(gb((0.08, 1.18, 0.18), (x, 2.1, 0), fr, bev=0.03, seg=1))
    rf = M("roof", ROOF_GREEN, "boards", bands=10.0, dir="X")
    for s in (-1, 1):
        p.append(gb((2.9, 0.08, 0.42), (0, 2.88, s * 0.17), rf, bev=0.03, rot=(s * 30, 0, 0)))
    return p


# ------------------------------------------------------------------ plan
W = "world"
PLAN = {
    "belt_rails":          ("shared", belt_rails, 128, W, dict(ao=0.6, grad=0.8)),
    "belt_legs":           ("shared", belt_legs, 128, W, dict(ao=0.5, grad=0.8)),
    "belt_end":            ("shared", belt_end, 128, W, dict(ao=0.5, grad=0.8)),
    "palisade_post":       ("shared", palisade_post, 128, W, dict(ao=0.35, grad=0.75)),
    "bridge_river":        ("shared", bridge_river, 512, W, dict(ao=0.4, grad=0.8)),
    "shop_counter":        ("shared", shop_counter, 256, W, dict(ao=0.5, grad=0.8)),
    "shop_till":           ("shared", shop_till, 256, W, dict(ao=0.35, grad=0.8)),
    "market_canopy":       ("shared", market_canopy, 256, W, dict(ao=0.18, grad=0.85)),
    "truck_flatbed":       ("shared", truck_flatbed, 512, W, dict(ao=0.25, grad=0.8)),
    "truck_dock":          ("shared", truck_dock, 256, W, dict(ao=0.3, grad=0.85)),
    "sawmill_body_orange": ("home", sawmill_body_orange, 512, W, dict(ao=0.22, grad=0.8)),
    "sawmill_body_green":  ("home", sawmill_body_green, 512, W, dict(ao=0.22, grad=0.8)),
    "office_hut":          ("home", office_hut, 512, W, dict(ao=0.2, grad=0.82)),
    "carpentry_shed":      ("home", carpentry_shed, 512, W, dict(ao=0.2, grad=0.82)),
    "saw_blade":           ("home", saw_blade, 128, W, dict(ao=0.3, grad=0.95, no_ground=True)),
    "cnc_router":          ("home", cnc_router, 512, W, dict(ao=0.2, grad=0.82)),
    "cnc_cog":             ("home", cnc_cog, 128, W, dict(ao=0.3, grad=0.95, no_ground=True)),
    "bookcase_factory":    ("home", bookcase_factory, 512, W, dict(ao=0.16, grad=0.82)),
    "factory_arm":         ("home", factory_arm, 128, W, dict(ao=0.3, grad=0.8)),
    "grand_lodge":         ("home", grand_lodge, 512, W, dict(ao=0.12, grad=0.82)),
    "lodge_windows":       ("home", lodge_windows, 0, W, dict(emissive=(1.0, 0.82, 0.5, 1.6))),
    "megasaw_body":        ("home", megasaw_body, 512, W, dict(ao=0.16, grad=0.82)),
    "megasaw_crane":       ("home", megasaw_crane, 256, W, dict(ao=0.12, grad=0.85)),
    "crane_hook":          ("home", crane_hook, 128, W, dict(ao=0.3, grad=0.95, no_ground=True)),
    "road_sign":           ("home", road_sign, 256, W, dict(ao=0.25, grad=0.82)),
}

if __name__ == "__main__" or True:
    run_plan(PLAN, f"{REPO}/tools/lookdev/build_leftover_report.json", OUT_ROOT)
