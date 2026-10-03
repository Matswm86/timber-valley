"""Redwood Coast (GDD milestone M3, valley 4) models -> assets/models_v3/redwood/ (+ items in assets/models_v3/items/).
Same bake as every models_v3 asset. Placement + paste-ready dicts: assets/models_v3/ASSETS_M3.md.

Usage (headless, Cycles on the RTX 3060 when available):
  /home/mm/.local/bin/blender -b --python tools/lookdev/build_m3.py -- [only_name ...]
Report: tools/lookdev/build_m3_report.json. Everything here is own work (CC0).

Region accent: harbour navy #1e3a64 (machines, roofs, hulls, ironwork), with signal red #cc3333 as the 10% pop
(lighthouse stripes, buoys, boot-top). Build sites export ONE GLB with child nodes stage1..stageN.
"""
import os

exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "m345_lib.py")).read(), "m345_lib.py", "exec"))

# ------------------------------------------------------------------ Redwood Coast palette (sRGB, docs/DESIGN.md section 14)
NAVY = (0.118, 0.227, 0.392)        # #1e3a64 region accent
NAVY_D = (0.075, 0.145, 0.255)      # #13253f frames, straps
SIG_RED = (0.80, 0.20, 0.20)        # #cc3333 lighthouse stripes, buoys, boot-top (10%)
RW_BARK = (0.56, 0.27, 0.17)        # #8f452b fibrous red-brown bark
RW_CUT = (0.86, 0.50, 0.38)         # #db8061 redwood heartwood (timber)
RW_RING = (0.91, 0.64, 0.50)
RW_LEAF = (0.15, 0.36, 0.22)        # #265c38 deep canopy
RW_LEAF2 = (0.21, 0.45, 0.27)       # #357345 lighter canopy lumps
DECK = (0.47, 0.30, 0.21)           # #784d36 dark deckboard
SPAR = (0.89, 0.71, 0.46)           # #e3b575 varnished mast
SAND = (0.90, 0.81, 0.62)
SAIL = (0.96, 0.93, 0.84)
ROCK = (0.58, 0.54, 0.49)           # warm grey (never blue-grey, DESIGN.md 10)


def rmats():
    m = mmats()
    m.update(navy=M("navy", NAVY), navy_d=M("navyd", NAVY_D), sred=M("sred", SIG_RED), wht=M("wht", WHITE),
             rbark=M("rbark", RW_BARK, "bark"), rring=M("rring", RW_RING, "rings"), rcut=M("rcut", RW_CUT, "planks"),
             deck=M("deck", DECK, "planks"), spar=M("spar", SPAR, "planks"), sail=M("sail", SAIL), rock=M("rock", ROCK),
             blk=M("blk", (0.22, 0.22, 0.24)), lamp=M("lamp", (1.0, 0.9, 0.6)), gold=M("gold", (1.0, 0.8, 0.25)))
    return m


# ------------------------------------------------------------------ trees (kenney units; game scale x1.6 on top)

def redwood_tree(variant, far=False):
    """Redwood: tall straight red-brown trunk with a buttressed base, narrow dark-green crown of stacked flat clumps.
    Kenney units; the game scales redwoods 1.6x more than other trees, so the crown stays <= 0.49 wide (0.79 after 1.6x)."""
    rnd = random.Random({"A": 3, "B": 13, "C": 31}[variant])
    bark = M("rbark", RW_BARK, "bark")
    la, lb = M("rleaf", RW_LEAF), M("rleaf2", RW_LEAF2)
    H = {"A": 1.72, "B": 1.9, "C": 1.62}[variant]
    W = {"A": 0.235, "B": 0.2, "C": 0.24}[variant]
    p = []
    n = 1 if far else 4
    pts = [Vector((0, 0, -0.04 + (H * 0.94) * i / n)) for i in range(n + 1)]
    rad = [0.072 - 0.04 * (i / n) for i in range(n + 1)]
    tr = tube(pts, rad, 5 if far else 8, bark)
    if not far:
        lobe_base(tr, 0.14, 0.45, lobes=4)
    p.append(tr)
    z0 = H * 0.38
    if far:   # one tapered column (a cone that keeps the lumpy edge) + the tip
        zc = z0 + (H - z0) * 0.45
        hz = (H - z0) * 0.52
        c = blob(1.0, (0, 0, zc), (W * 0.98, W * 0.98, hz), la, 1, ico=2, amp=0.12)
        for v in c.data.vertices:
            t = min(max((v.co.z + hz) / (2 * hz), 0.0), 1.0)
            k = 1.15 - 0.75 * t
            v.co.x *= k; v.co.y *= k
        p.append(c)
        p.append(blob(1.0, (0.01, 0.0, H * 0.93), (W * 0.32, W * 0.32, H * 0.1), lb, 2, ico=2, amp=0.1))
        return p
    k = 6 if variant != "C" else 5
    tiers = []
    for i in range(k):
        f = i / (k - 1)
        z = z0 + 0.08 + (H - z0 - 0.2) * f
        r = W * (1.0 - 0.62 * f ** 1.2) * rnd.uniform(0.92, 1.04)
        if variant == "C" and i == 0:
            r *= 1.04
        tiers.append((z, r))
    p += conifer_tiers(tiers, [la, lb], rnd, offset=0.035, seg=8, rings=6, amp=0.16, flat=0.7)
    # core column so no sky shows between clumps
    p.append(blob(1.0, (0, 0, z0 + (H - z0) * 0.45), (W * 0.55, W * 0.55, (H - z0) * 0.5), la, 5.5, seg=7, rings=5, amp=0.08))
    if variant == "C":   # broken double top
        p.append(blob(1.0, (0.06, 0.02, H - 0.04), (0.06, 0.06, 0.11), lb, 8.1, seg=6, rings=4, amp=0.1))
        p.append(blob(1.0, (-0.07, -0.02, H - 0.1), (0.05, 0.05, 0.09), la, 8.7, seg=6, rings=4, amp=0.1))
    else:
        p.append(blob(1.0, (0, 0, H - 0.02), (0.055, 0.055, 0.14), lb, 9.1, seg=6, rings=4, amp=0.08))
    return p


def redwood_stump():
    side, end = M("rbark", RW_BARK, "bark"), M("rring", RW_RING, "rings")
    lg = _log(0.2, 0.24, (0, 0, 0.12), (0, 0, 0), side, end, verts=14)
    lobe_base(lg, 0.2, 0.5, lobes=5)
    p = [lg]
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.3
        rt = _add("primitive_uv_sphere_add", segments=7, ring_count=4, radius=0.08, location=(0.2 * math.cos(a), 0.2 * math.sin(a), 0.02))
        rt.scale = (1.5, 0.7, 0.55); rt.rotation_euler = (0, 0, a); _assign(rt, side); _smooth(rt); p.append(rt)
    return p


def redwood_log_stack():
    side, end = M("rbark", RW_BARK, "bark"), M("rring", RW_RING, "rings")
    p, r = [], 0.1
    for count, row in [(3, 0.0), (2, 1.0)]:
        for i in range(count):
            x = (i - (count - 1) / 2) * 2 * r * 1.02
            p.append(_log(r * (0.95 + 0.05 * (i % 2)), 0.8, (x, 0, r + row * r * 1.72), (math.pi / 2, 0, 0), side, end, verts=10, seg=1))
    return p


def dune_grass():
    """Tall pale marram tufts on a sand mound (deco scatter, kenney units)."""
    p = [blob(1.0, (0, 0, -0.01), (0.2, 0.17, 0.05), M("sand", SAND), 2.0, seg=9, rings=4, amp=0.1)]
    rnd = random.Random(4)
    g1, g2 = M("dg1", (0.62, 0.66, 0.36)), M("dg2", (0.78, 0.74, 0.46))
    for i in range(11):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.0, 0.12)
        b = Vector((d * math.cos(a), d * math.sin(a), 0.0))
        tip = b + Vector((math.cos(a) * 0.09, math.sin(a) * 0.09, rnd.uniform(0.22, 0.34)))
        p.append(tube([b, (b + tip) / 2 + Vector((0, 0, 0.02)), tip], [0.016, 0.011, 0.002], 3, g1 if i % 2 else g2, cap_top=False))
    return p


def driftwood():
    """Bleached driftwood log with a branch stub (deco, kenney units)."""
    w = M("drift", (0.80, 0.75, 0.66), "bark")
    p = [tube([Vector((-0.3, 0, 0.04)), Vector((-0.05, 0.02, 0.05)), Vector((0.2, -0.02, 0.045)), Vector((0.32, 0.0, 0.035))],
              [0.04, 0.045, 0.038, 0.02], 6, w)]
    p.append(tube([Vector((0.05, 0.02, 0.06)), Vector((0.12, 0.12, 0.1)), Vector((0.16, 0.2, 0.11))], [0.02, 0.014, 0.006], 5, w))
    return p


def beach_rock():
    """Warm-grey coastal boulder pair (deco, kenney units)."""
    r = M("rock", ROCK)
    return [blob(1.0, (0, 0, 0.06), (0.2, 0.16, 0.13), r, 1.2, ico=2, amp=0.22),
            blob(1.0, (0.18, -0.08, 0.03), (0.09, 0.08, 0.07), r, 2.6, ico=1, amp=0.2)]


# ------------------------------------------------------------------ items (world metres, scale 1)

def item_red_log():
    """Thick redwood log, 1.2 long, d 0.42 (cell 1.3 x 0.5, layer 0.42)."""
    return [_log_along_x(0.205, 1.2, M("rbark", RW_BARK, "bark"), M("rring", RW_RING, "rings"))]


def item_timber():
    """Big square redwood timber 1.24 x 0.38 (h) x 0.42 (d), ring ends, navy mill stamp on top."""
    side, end = M("rcut", RW_CUT, "planks"), M("rring", (0.92, 0.62, 0.47), "rings")
    ob = rbox(1.24, 0.42, 0.38, (0, 0, 0.19), side, bev=0.04, seg=2)
    ob.data.materials.append(end)
    for f in ob.data.polygons:
        f.material_index = 1 if abs(f.normal.x) > 0.7 else 0
    return [ob, gb((0.18, 0.006, 0.14), (0.32, 0.381, 0.0), M("stamp", NAVY), bev=0.0)]


def item_deckboard():
    """Dark deck board 1.05 x 0.08 x 0.32 with three anti-slip grooves on top."""
    d = M("deck", DECK, "planks")
    p = [gb((1.05, 0.08, 0.32), (0, 0.04, 0), d, bev=0.014)]
    for z in (-0.08, 0.0, 0.08):
        p.append(gb((1.03, 0.006, 0.018), (0, 0.081, z), M("groove", (0.3, 0.19, 0.13)), bev=0.0))
    return p


def item_mast():
    """Ship mast, long along Z (cell 0.4 x 2.4, layer 0.4): tapered varnished spar d 0.36 -> 0.22, iron bands, navy tip."""
    spar, iron, navy = M("spar", SPAR, "planks"), M("iron", (0.3, 0.3, 0.32)), M("navy", NAVY)
    L = 2.3
    ob = gc(0.18, L, (0, 0.18, 0), spar, axis="z", verts=12, r2=0.11)
    ob.location = gpos(0, 0.18, 0)
    p = [ob]
    # cone axis: Blender Z rotated onto Godot Z; r1 (0.18) ends up at Godot -Z, the thin end at +Z
    for z, r in ((-0.85, 0.172), (-0.1, 0.152), (0.65, 0.132)):
        p.append(gc(r + 0.012, 0.06, (0, 0.18, z), iron, axis="z", verts=12))
    p.append(gc(0.118, 0.16, (0, 0.18, 1.08), navy, axis="z", verts=12))
    p.append(gb((0.4, 0.05, 0.07), (0, 0.18, 0.86), M("tree", (0.55, 0.36, 0.22), "planks"), bev=0.012))   # crosstrees: reads as a mast
    p.append(gb((0.07, 0.05, 0.3), (0.0, 0.18, 0.86), M("tree", (0.55, 0.36, 0.22), "planks"), bev=0.012))
    return p


# ------------------------------------------------------------------ machines (world metres; Machine piles at x -2.7 / +2.7)

def redwood_mill():
    """Redwood Mill (r4_redmill): big twin-arbor headrig. Carriage bed along X; the main blade (redwood_mill_blade.glb,
    r 0.75) spins at (0, 0.8, 0.15) and the same GLB at scale 0.56 is the top saw at (0.22, 1.72, 0.15)."""
    m = rmats()
    p = [gb((4.6, 0.24, 1.9), (0, 0.12, 0.0), m["grey"], bev=0.06)]
    p.append(gb((4.4, 0.42, 1.0), (0, 0.45, 0.15), m["navy"], bev=0.1))
    for z in (-0.3, 0.6):
        p.append(gb((4.5, 0.1, 0.1), (0, 0.71, z), m["yellow"], bev=0.03))
    # carriage with log dogs and a redwood log on the infeed
    p.append(gb((1.7, 0.16, 0.8), (-1.25, 0.82, 0.15), m["yellow"], bev=0.05))
    for x in (-1.9, -0.6):
        p.append(gb((0.12, 0.5, 0.14), (x, 1.05, -0.24), m["steel_d"], bev=0.03))
    p.append(gl(0.3, 1.5, (-1.4, 1.2, 0.15), m["rbark"], m["rring"], verts=12))
    # arbor housings behind the blades, columns, top beam
    p.append(gb((0.9, 1.0, 0.6), (0.0, 0.62, -0.5), m["navy_d"], bev=0.08))
    p.append(gb((0.7, 0.62, 0.55), (0.22, 1.72, -0.48), m["navy_d"], bev=0.08))
    for x in (-0.62, 0.78):
        p.append(gb((0.28, 2.6, 0.32), (x, 1.3, -0.62), m["navy"], bev=0.07))
    p.append(gb((1.75, 0.32, 0.4), (0.08, 2.6, -0.62), m["navy"], bev=0.08))
    p.append(gb((1.85, 0.08, 0.45), (0.08, 2.78, -0.62), m["yellow"], bev=0.03))
    p.append(gc(0.12, 0.3, (0.08, 2.95, -0.62), m["sred"], verts=10))                      # warning beacon
    # operator booth at the back right
    p.append(gb((1.0, 1.6, 0.95), (1.55, 1.05, -0.7), m["navy"], bev=0.07))
    p.append(gb((0.8, 0.5, 0.06), (1.55, 1.45, -0.21), m["wglass"], bev=0.02))
    p.append(gb((1.15, 0.1, 1.1), (1.55, 1.9, -0.7), m["cream"], bev=0.04))
    # sawdust chute and pile on the front left
    p.append(blob(1.0, gpos(0.35, 0.18, 0.85), (0.45, 0.3, 0.16), M("dust", (0.93, 0.68, 0.52)), 1.0, seg=8, rings=5, amp=0.1))
    # outfeed rollers + two timbers
    for i in range(4):
        p.append(gc(0.06, 0.95, (0.85 + i * 0.42, 0.78, 0.15), m["steel"], axis="z", verts=8))
    for k in range(2):
        t = item_timber()
        gmove(t, 1.45, 0.82 + k * 0.4, 0.15)
        p += t
    return p


def redwood_mill_blade():
    """Main headrig blade r 0.75, disc normal along Godot Z, pivot at its centre (Machine.spinners)."""
    st, mark = M("steel", (0.80, 0.82, 0.85)), M("mark", NAVY)
    p = [gc(0.69, 0.04, (0, 0, 0), st, axis="z", verts=32)]
    for i in range(26):
        a = 2 * math.pi * i / 26
        p.append(gb((0.12, 0.08, 0.04), (0.71 * math.cos(a), 0.71 * math.sin(a), 0), st, bev=0.0, rot=(0, 0, math.degrees(a) + 30)))
    for i in range(3):
        a = 2 * math.pi * i / 3 + 0.4
        p.append(gb((0.3, 0.07, 0.05), (0.36 * math.cos(a), 0.36 * math.sin(a), 0), mark, bev=0.0, rot=(0, 0, math.degrees(a))))
    p.append(gc(0.12, 0.07, (0, 0, 0), M("hub", (0.35, 0.35, 0.36)), axis="z", verts=12))
    return p


def deck_saw():
    """Deck Saw (r4_decksaw): gang resaw table. The 3-blade arbor (deck_saw_gang.glb) spins at (0, 0.92, 0)."""
    m = rmats()
    p = [gb((3.3, 0.75, 1.1), (0, 0.42, 0), m["navy"], bev=0.1)]
    for x in (-1.45, 1.45):
        for z in (-0.4, 0.4):
            p.append(gb((0.16, 0.14, 0.16), (x, 0.07, z), m["steel_d"], bev=0.03))
    p.append(gb((3.4, 0.08, 1.15), (0, 0.83, 0), m["steel"], bev=0.03))
    for z in (-0.6, 0.6):
        p.append(gb((3.4, 0.1, 0.08), (0, 0.9, z), m["yellow"], bev=0.02))
    # hood over the back half of the gang, feed rollers either side
    p.append(gb((1.1, 0.55, 0.55), (0, 1.27, -0.38), m["navy_d"], bev=0.1))
    p.append(gb((1.15, 0.08, 0.6), (0, 1.56, -0.36), m["yellow"], bev=0.03))
    for x in (-0.75, 0.75):
        p.append(gc(0.08, 0.95, (x, 1.34, 0), m["steel"], axis="z", verts=10))
        p.append(gb((0.12, 0.6, 0.1), (x, 1.15, -0.5), m["navy_d"], bev=0.03))
    p.append(gb((0.6, 0.6, 0.5), (1.2, 1.15, -0.75), m["yellow"], bev=0.1))       # motor
    p.append(gb((0.22, 0.16, 0.05), (1.2, 1.28, -0.49), m["green_btn"], bev=0.02))
    t = item_timber()
    gmove(t, -1.15, 0.87, 0)
    p += t
    for k in range(3):
        d = item_deckboard()
        gmove(d, 1.1, 0.87 + k * 0.085, -0.1 + k * 0.05)
        p += d
    return p


def deck_saw_gang():
    """Gang arbor: 3 blades r 0.33 on one axle along Godot Z (spacing 0.17), pivot at the axle centre."""
    st = M("steel", (0.80, 0.82, 0.85))
    p = [gc(0.05, 0.6, (0, 0, 0), M("hub", (0.35, 0.35, 0.36)), axis="z", verts=10)]
    for z in (-0.17, 0.0, 0.17):
        p.append(gc(0.3, 0.025, (0, 0, z), st, axis="z", verts=24))
        for i in range(10):
            a = 2 * math.pi * i / 10 + z * 3
            p.append(gb((0.07, 0.05, 0.025), (0.31 * math.cos(a), 0.31 * math.sin(a), z), st, bev=0.0, rot=(0, 0, math.degrees(a) + 30)))
        p.append(gb((0.18, 0.05, 0.03), (0.15, 0.0, z), M("mark", NAVY), bev=0.0, rot=(0, 0, 40 + z * 300)))
    return p


def mast_lathe():
    """Mast Lathe (r4_mastlathe): long bed along X, navy headstock (-X) and tailstock (+X), yellow tool carriage.
    The spinning log (mast_lathe_log.glb, built along Z) goes at (0, 1.12, 0) with rot_y 90 so it lies along X."""
    m = rmats()
    p = [gb((4.2, 0.22, 0.75), (0, 0.78, -0.05), m["navy"], bev=0.06)]
    for x in (-1.6, 0.0, 1.6):
        p.append(gb((0.4, 0.7, 0.6), (x, 0.35, -0.05), m["navy_d"], bev=0.06))
    for z in (-0.3, 0.2):
        p.append(gb((4.2, 0.06, 0.08), (0, 0.92, z), m["steel"], bev=0.02))
    p.append(gb((0.75, 1.15, 0.9), (-2.05, 1.0, -0.05), m["navy"], bev=0.1))           # headstock
    p.append(gb((0.78, 0.08, 0.93), (-2.05, 1.6, -0.05), m["yellow"], bev=0.03))
    p.append(gc(0.22, 0.12, (-1.66, 1.12, 0), m["steel"], axis="x", verts=12))          # chuck
    p.append(gb((0.55, 0.75, 0.7), (1.95, 1.1, -0.05), m["navy"], bev=0.09))            # tailstock
    p.append(gc(0.07, 0.3, (1.62, 1.12, 0), m["steel"], axis="x", verts=8, r2=0.02))
    p.append(gb((0.5, 0.25, 0.55), (0.3, 1.05, 0.5), m["yellow"], bev=0.05))            # carriage
    p.append(gb((0.12, 0.2, 0.3), (0.3, 1.2, 0.36), m["steel_d"], bev=0.02))
    p.append(gb((0.3, 0.45, 0.25), (-1.2, 0.95, -0.7), m["yellow"], bev=0.06))          # control box
    p.append(gb((0.2, 0.14, 0.04), (-1.2, 1.05, -0.56), m["green_btn"], bev=0.02))
    p.append(blob(1.0, gpos(0.3, 0.05, 0.55), (0.6, 0.35, 0.12), M("chips", (0.93, 0.66, 0.5)), 2.0, seg=8, rings=4, amp=0.15))
    # finished mast on a rack behind
    for x in (-1.4, 1.4):
        p.append(gb((0.12, 1.2, 0.12), (x, 0.6, -0.95), m["dark"], bev=0.03))
        p.append(gb((0.12, 0.08, 0.4), (x, 1.2, -0.95), m["dark"], bev=0.02))
    mast = item_mast()
    for o in mast:
        o.matrix_world = Matrix.Translation(gpos(0, 1.08, -0.95)) @ Matrix.Rotation(math.pi / 2, 4, "Z") @ o.matrix_world
    p += mast
    return p


def mast_lathe_log():
    """Spinning workpiece: built along Godot Z (spins about local Z like every spinner), 3.2 long. The -Z half is bark,
    the +Z half is already turned (pale, smooth). Add it with rot_y 90 so it lies along the lathe bed (X)."""
    bark, spar, end = M("rbark", RW_BARK, "bark"), M("spar", SPAR, "planks"), M("rring", RW_RING, "rings")
    p = [gc(0.2, 1.6, (0, 0, -0.8), bark, axis="z", verts=12)]
    p.append(gc(0.135, 1.5, (0, 0, 0.75), spar, axis="z", verts=12))
    p.append(gc(0.2, 0.12, (0, 0, 0.04), spar, axis="z", verts=12, r2=0.135))
    p.append(gc(0.205, 0.02, (0, 0, -1.6), end, axis="z", verts=12))
    p.append(gc(0.14, 0.02, (0, 0, 1.5), end, axis="z", verts=12))
    return p


# ------------------------------------------------------------------ vehicles

def sheer_line(st, y_of, r, mat, out=0.02):
    """One continuous tube per hull side through the stations (x, hw, yd, yk, f) at y = y_of(station)."""
    return [gtube([(a[0], y_of(a), sgn * (a[1] + out)) for a in st], r, mat, sides=6) for sgn in (-1, 1)]


def log_skidder():
    """Log Skidder (r4_skidder*): articulated forestry tractor, cab + blade at +Z (Walker turns +Z to the walk direction),
    log bunk at the back: carried ItemStack at (0, 1.0, -1.2), logs lie across (along X) like every pile."""
    m = rmats()
    tyre, hub = M("tyre", (0.2, 0.2, 0.21)), M("hub", YELLOW)
    p = [gb((1.25, 0.55, 1.55), (0, 0.85, 0.75), m["navy"], bev=0.14)]              # front frame + engine
    p.append(gb((1.3, 0.45, 0.6), (0, 1.05, 1.35), m["navy_d"], bev=0.14))
    p.append(gb((0.2, 0.25, 0.4), (0.35, 1.45, 1.3), m["blk"], bev=0.04))             # exhaust stack base
    p.append(gc(0.05, 0.5, (0.35, 1.75, 1.3), m["blk"], verts=8))
    p.append(gb((1.1, 0.95, 0.95), (0, 1.55, 0.35), m["navy"], bev=0.1))              # cab
    p.append(gb((1.0, 0.55, 0.05), (0, 1.62, 0.84), m["wglass"], bev=0.02))
    for x in (-0.56, 0.56):
        p.append(gb((0.05, 0.5, 0.65), (x, 1.62, 0.35), m["wglass"], bev=0.02))
    p.append(gb((1.2, 0.08, 1.05), (0, 2.06, 0.35), m["cream"], bev=0.04))
    p.append(gb((0.18, 0.1, 0.1), (0.4, 2.15, 0.1), M("beacon", (1.0, 0.6, 0.15)), bev=0.03))
    p.append(gb((1.6, 0.45, 0.12), (0, 0.4, 1.95), m["yellow"], bev=0.05, rot=(-10, 0, 0)))   # dozer blade
    p.append(gb((0.6, 0.4, 0.5), (0, 0.85, -0.2), m["navy_d"], bev=0.08))             # articulation joint
    p.append(gb((1.2, 0.4, 1.2), (0, 0.75, -1.1), m["navy"], bev=0.1))               # rear frame
    p.append(gb((1.6, 0.12, 0.7), (0, 0.98, -1.2), m["steel_d"], bev=0.03))          # log bunk
    for x in (-0.78, 0.78):
        p.append(gb((0.1, 0.55, 0.12), (x, 1.3, -1.2), m["yellow"], bev=0.03))
    for x in (-0.55, 0.55):                                                            # arch + winch at the back
        p.append(gb((0.14, 1.25, 0.14), (x, 1.25, -1.72), m["yellow"], bev=0.04))
    p.append(gb((1.25, 0.18, 0.2), (0, 1.9, -1.72), m["yellow"], bev=0.05))
    p.append(gc(0.16, 0.6, (0, 1.75, -1.72), m["steel_d"], axis="x", verts=10))
    for x in (-0.72, 0.72):
        for z in (0.95, -1.1):
            p.append(gc(0.5, 0.38, (x, 0.5, z), tyre, axis="x", verts=14, bev=0.04))
            p.append(gc(0.24, 0.4, (x, 0.5, z), hub, axis="x", verts=8))
    return p


def cargo_ship():
    """Cargo freighter for the Order Board (r4_orders). Bow at -Z (sails toward -Z at rotation 0, like the barge).
    Origin = waterline under the hull centre; deck top y 1.25; hold deck (crates) top y 1.55 at z -0.8..1.6."""
    m = rmats()
    hullc, red, deckm = M("hull", NAVY), M("boot", SIG_RED), M("deck", (0.62, 0.6, 0.56))
    L, Bm = 11.0, 1.75

    def hm(cy, is_deck):
        if is_deck:
            return deckm
        return red if cy < 0.25 else hullc
    st = []
    for i in range(10):
        f = i / 9.0                                # 0 = stern (+Z after the turn), 1 = bow
        x = -L / 2 + L * f
        hw = Bm * (1.0 if f < 0.7 else (1 - ((f - 0.7) / 0.3) ** 1.8) * 0.96 + 0.04) * (0.92 if f < 0.06 else 1.0)
        yd = 1.25 + (0.35 * ((f - 0.75) / 0.25) ** 2 if f > 0.75 else 0)
        yk = -0.7 + (0.55 * ((f - 0.85) / 0.15) if f > 0.85 else 0) + (0.3 if f < 0.06 else 0)
        st.append((x, hw, yd, yk, 2.2 if 0.1 < f < 0.8 else 1.5))
    hull = hull_loft(st, hm, K=6)
    p = [hull]
    p += sheer_line(st[1:], lambda s_: 0.8, 0.07, m["wht"], out=0.03)          # white line along the hull
    for s in (-1, 1):                                                                # bulwarks
        p.append(gb((L * 0.6, 0.35, 0.08), (-1.0, 1.42, s * (Bm - 0.06)), hullc, bev=0.02))
    # superstructure aft (stern = -X here, turned to +Z below)
    p.append(gb((2.2, 1.2, 3.0), (-3.9, 1.85, 0), m["wht"], bev=0.08))
    p.append(gb((1.5, 0.85, 2.6), (-3.8, 2.85, 0), m["wht"], bev=0.08))
    p.append(gb((0.06, 0.4, 2.2), (-3.04, 2.95, 0), m["wglass"], bev=0.02))
    for s in (-1, 1):
        p.append(gb((1.0, 0.35, 0.06), (-3.8, 2.95, s * 1.31), m["wglass"], bev=0.02))
        for k in range(3):
            p.append(gc(0.12, 0.06, (-4.6 + k * 0.55, 1.95, s * 1.51), m["wglass"], axis="z", verts=10))
    p.append(gb((1.7, 0.1, 2.9), (-3.8, 3.32, 0), m["navy_d"], bev=0.04))
    p.append(gc(0.42, 1.3, (-4.4, 3.9, 0), m["wht"], verts=14))                         # funnel
    p.append(gc(0.44, 0.35, (-4.4, 4.0, 0), red, verts=14))
    p.append(gc(0.43, 0.25, (-4.4, 4.62, 0), m["blk"], verts=14))
    p.append(gc(0.08, 0.3, (-4.0, 4.1, 0.25), m["gold"], verts=8, r2=0.14))           # horn
    p.append(gc(0.04, 1.6, (-3.6, 4.0, 0), m["blk"], verts=6))                         # radar mast
    p.append(gb((0.7, 0.08, 0.12), (-3.6, 4.6, 0), m["blk"], bev=0.02))
    # cargo hold: crates of timber and deckboards, two yellow derricks
    p.append(gb((5.0, 0.3, 2.6), (0.2, 1.4, 0), m["navy_d"], bev=0.05))
    for i, (x, z, h) in enumerate(((-1.5, -0.6, 0.6), (-1.5, 0.6, 0.6), (-0.3, -0.6, 0.9), (-0.3, 0.6, 0.6), (0.9, -0.6, 0.6),
                                   (0.9, 0.6, 0.9), (2.1, 0.0, 0.6))):
        p.append(gb((1.1, h, 1.1), (x, 1.55 + h / 2, z), m["plank"] if i % 2 else M("crate", RW_CUT, "planks"), bev=0.04))
    for x in (-2.35, 2.85):
        p.append(gc(0.1, 2.6, (x, 2.55, 0), m["yellow"], verts=8))
        p.append(gseg((x, 2.0, 0), (x + (1.4 if x < 0 else -1.4), 3.4, 0), 0.06, m["yellow"]))
    # foredeck: mast, bollards, anchor
    p.append(gc(0.06, 2.0, (4.3, 2.4, 0), m["blk"], verts=6))
    for s in (-1, 1):
        p.append(gc(0.1, 0.25, (4.0, 1.45, s * 0.7), m["blk"], verts=8))
        p.append(gc(0.12, 0.08, (5.0, 1.3, s * 0.5), m["blk"], axis="z", verts=8))
    gmove(p, rot_y_deg=90)   # bow from +X to -Z
    return p


def fishing_boat():
    """Shopper boat for the Fishing Pier (r4_harbor). Bow at -Z. Origin = waterline; benches top y 0.75 at z 0.2 and 1.0."""
    m = rmats()
    hullc, red, inner = M("hull", WHITE), M("boot", SIG_RED), M("inner", (0.9, 0.78, 0.6), "planks")

    def hm(cy, is_deck):
        if is_deck:
            return inner
        return red if cy < 0.05 else (M("stripe", NAVY) if cy > 0.62 else hullc)
    L, Bm = 4.6, 0.85
    st = []
    for i in range(8):
        f = i / 7.0
        x = -L / 2 + L * f
        hw = Bm * (1.0 if f < 0.55 else (1 - ((f - 0.55) / 0.45) ** 1.6) * 0.95 + 0.05) * (0.9 if f < 0.08 else 1.0)
        yd = 0.75 + (0.18 * ((f - 0.6) / 0.4) ** 2 if f > 0.6 else 0)
        yk = -0.35 + (0.4 * ((f - 0.8) / 0.2) if f > 0.8 else 0)
        st.append((x, hw, yd, yk, 1.6))
    p = [hull_loft(st, hm, K=6)]
    p.append(gb((1.1, 1.0, 1.15), (-1.3, 1.25, 0), m["wht"], bev=0.06))               # wheelhouse at the stern
    p.append(gb((1.25, 0.08, 1.3), (-1.3, 1.78, 0), m["navy"], bev=0.04))
    p.append(gb((0.05, 0.35, 0.9), (-0.74, 1.38, 0), m["wglass"], bev=0.02))
    p.append(gc(0.03, 0.9, (-1.5, 2.2, 0), m["blk"], verts=6))
    p.append(gb((0.1, 0.25, 0.4), (-1.5, 2.5, 0.15), m["sred"], bev=0.01))            # pennant
    for x in (0.2, 1.0):
        p.append(gb((0.28, 0.06, 1.4), (x, 0.72, 0), m["plank"], bev=0.02))
    for s in (-1, 1):
        t = _add("primitive_torus_add", major_radius=0.14, minor_radius=0.05, major_segments=10, minor_segments=5,
                 location=gpos(0.6, 0.55, s * 0.88), rotation=(math.pi / 2, 0, 0))
        _assign(t, m["tyre"]); _smooth(t); p.append(t)
    gmove(p, rot_y_deg=90)
    return p


# ------------------------------------------------------------------ harbour

PIER_TOP = 0.3


def pier_straight_4m():
    """4 m of pier along Godot X, 3.0 wide, deck top y 0.3, FLAT ends (tile every 4.0 m; rot 90 for a north-south pier).
    Piles reach y -1.6 so they stand in the sea."""
    m = rmats()
    p = []
    for i in range(10):
        p.append(gb((0.38, 0.08, 3.0), (-1.8 + i * 0.4, PIER_TOP - 0.04, 0), m["plank"] if i % 3 else M("pl2", (0.86, 0.68, 0.45), "planks"), bev=0.012))
    for z in (-1.42, 1.42):
        p.append(gb((4.0, 0.22, 0.16), (0, PIER_TOP - 0.19, z), m["dark"], bev=0.03))
        for x in (-1.6, 1.6):
            p.append(gl(0.13, 2.0, (x, PIER_TOP - 1.0, z), m["dark"], m["end"], axis="y", verts=8))
    return p


def pier_end():
    """Pier head (4 m along X, same section as pier_straight_4m) with bollards, a harbour lamp, a ladder, tyre fenders.
    The +X end is the sea end."""
    m = rmats()
    p = pier_straight_4m()
    p.append(gb((0.2, 0.2, 3.1), (2.0, PIER_TOP - 0.08, 0), m["dark"], bev=0.04))
    for z in (-1.1, 1.1):
        p.append(gc(0.13, 0.3, (1.6, PIER_TOP + 0.15, z), m["blk"], verts=10))
        p.append(gc(0.17, 0.06, (1.6, PIER_TOP + 0.32, z), m["blk"], verts=10))
    for z in (-0.6, 0.6):
        t = _add("primitive_torus_add", major_radius=0.2, minor_radius=0.07, major_segments=10, minor_segments=6,
                 location=gpos(2.12, PIER_TOP - 0.35, z), rotation=(0, math.pi / 2, 0))
        _assign(t, m["tyre"]); _smooth(t); p.append(t)
    for z in (-0.25, 0.25):
        p.append(gb((0.05, 1.3, 0.05), (2.08, PIER_TOP - 0.55, z), m["steel"], bev=0.0))
    for k in range(4):
        p.append(gb((0.05, 0.04, 0.55), (2.08, PIER_TOP - 1.1 + k * 0.3, 0), m["steel"], bev=0.0))
    p += harbor_lamp_parts(1.5, -1.3, m, y0=PIER_TOP)
    p.append(_add("primitive_torus_add", major_radius=0.2, minor_radius=0.05, major_segments=10, minor_segments=5,
                  location=gpos(0.8, PIER_TOP + 0.05, 1.0)))
    _assign(p[-1], M("rope", (0.86, 0.78, 0.6))); _smooth(p[-1])
    return p


def harbor_lamp_parts(x, z, m, y0=0.0):
    return [gb((0.3, 0.12, 0.3), (x, y0 + 0.06, z), m["navy_d"], bev=0.03), gc(0.055, 2.2, (x, y0 + 1.2, z), m["navy"], verts=8),
            gb((0.6, 0.06, 0.06), (x + 0.2, y0 + 2.25, z), m["navy"], bev=0.01),
            gc(0.14, 0.22, (x + 0.42, y0 + 2.08, z), m["lamp"], verts=8),
            gc(0.2, 0.12, (x + 0.42, y0 + 2.24, z), m["navy_d"], verts=8, r2=0.04)]


def harbor_lamp():
    """Harbour street lamp (decor)."""
    return harbor_lamp_parts(0, 0, rmats())


def order_board():
    """Cargo Order Board (r4_orders). Board face at z +0.07, centre (0, 1.75, 0): three manifest rows for Label3D +
    item icon at y 2.05, 1.72 and 1.39 (x -0.9 icon, x -0.55.. text). Navy header strip y 2.4 for 'CARGO ORDER'."""
    m = rmats()
    p = []
    for x in (-1.25, 1.25):
        p.append(gl(0.08, 2.8, (x, 1.4, 0), m["dark"], m["end"], axis="y", verts=8))
    p.append(gb((2.4, 1.45, 0.1), (0, 1.75, 0), M("board", (0.95, 0.89, 0.76), "planks"), bev=0.03))
    p.append(gb((2.5, 0.32, 0.12), (0, 2.42, 0.005), m["navy"], bev=0.03))
    for y in (1.88, 1.55):
        p.append(gb((2.2, 0.02, 0.02), (0, y, 0.06), M("line", (0.75, 0.66, 0.52)), bev=0.0))
    for x in (-1.05, 1.05):
        p.append(gc(0.03, 0.02, (x, 2.25, 0.07), m["gold"], axis="z", verts=8))
    p.append(gb((2.8, 0.1, 0.7), (0, 2.85, -0.05), m["navy_d"], bev=0.04, rot=(-12, 0, 0)))
    p.append(gseg((1.25, 2.3, 0.0), (1.65, 2.3, 0.0), 0.03, m["steel_d"]))            # ship's bell
    p.append(gc(0.16, 0.26, (1.65, 2.08, 0), m["gold"], verts=12, r2=0.08))
    p.append(gb((3.0, 0.12, 0.6), (0, 0.06, 0.4), m["plank"], bev=0.03))
    return p


def dock_crane():
    """Small harbour crane base (decor at the order dock). The turning cab + jib is dock_crane_jib.glb at (0, 1.4, 0);
    use it as a Machine arm (rotation.y swings) or tween it when an order ships."""
    m = rmats()
    return [gb((1.6, 0.25, 1.6), (0, 0.12, 0), m["grey"], bev=0.06), gc(0.42, 1.2, (0, 0.8, 0), m["navy"], verts=12),
            gc(0.55, 0.12, (0, 1.36, 0), m["yellow"], verts=14)]


def dock_crane_jib():
    """Crane cab + jib + hook, pivot at the turntable (place at (0, 1.4, 0) on dock_crane.glb). Jib points +X."""
    m = rmats()
    p = [gb((1.1, 1.0, 1.0), (-0.1, 0.55, 0), m["navy"], bev=0.08), gb((0.05, 0.45, 0.7), (0.46, 0.7, 0), m["wglass"], bev=0.02),
         gb((1.2, 0.08, 1.1), (-0.1, 1.08, 0), m["cream"], bev=0.03), gb((0.5, 0.5, 0.8), (-0.85, 0.4, 0), m["navy_d"], bev=0.05)]
    p.append(gseg((0.2, 0.9, 0), (3.3, 2.6, 0), 0.09, m["yellow"]))
    p.append(gseg((-0.4, 1.1, 0), (0.6, 2.4, 0), 0.06, m["yellow"]))
    p.append(gseg((0.6, 2.4, 0), (3.3, 2.6, 0), 0.03, m["steel_d"]))
    p.append(gseg((3.3, 2.6, 0), (3.3, 1.2, 0), 0.015, m["steel_d"], verts=4))
    p.append(gb((0.2, 0.25, 0.12), (3.3, 1.1, 0), m["yellow"], bev=0.03))
    p.append(gc(0.05, 0.2, (3.3, 0.9, 0), m["steel_d"], verts=6))
    return p


# ------------------------------------------------------------------ ship building

SHIP_L, SHIP_B = 9.0, 1.35
KEEL_Y = 0.62     # keel bottom on the keel blocks


def _ship_stations():
    st = []
    for i in range(9):
        f = i / 8.0                               # 0 = stern (-X), 1 = bow (+X, toward the sea)
        x = -SHIP_L / 2 + SHIP_L * f
        if f > 0.42:
            hw = SHIP_B * max(1 - ((f - 0.42) / 0.58) ** 2, 0.0) ** 0.7
        else:
            hw = SHIP_B * (1 - 0.25 * ((0.42 - f) / 0.42) ** 2)
        hw = max(hw, 0.05)
        yd = KEEL_Y + 1.9 + 0.35 * abs(f - 0.45) ** 2 * 3
        yk = KEEL_Y + (0.5 * ((f - 0.8) / 0.2) ** 1.5 if f > 0.8 else 0) + (0.25 * ((0.12 - f) / 0.12) if f < 0.12 else 0)
        st.append((x, hw, yd, yk, 1.35))
    return st


def ship_hull():
    """Repeatable slipway ship (r4_slipway, r4_slipway2): a three-masted schooner, 4 BuildSite stages, long along X with
    the bow at +X (the sea). Origin = slipway origin on the ground; keel bottom y 0.62 on the slipway's keel blocks.
    stage1 keel + ribs, stage2 planked hull, stage3 deck + rails + navy sheer strake + cabin, stage4 three masts, furled
    sails, bowsprit, flag. Launch = slide the whole node +X 8 m and down 1.2 m (GDD 7.6 B, 4 s)."""
    m = rmats()
    st = _ship_stations()
    S = {}
    s1 = [gb((SHIP_L * 0.98, 0.22, 0.24), (0, KEEL_Y + 0.11, 0), m["dark"], bev=0.04)]
    s1.append(gseg((SHIP_L / 2 - 0.4, KEEL_Y + 0.15, 0), (SHIP_L / 2 + 0.25, KEEL_Y + 2.5, 0), 0.12, m["dark"]))   # stem
    s1.append(gseg((-SHIP_L / 2 + 0.2, KEEL_Y + 0.15, 0), (-SHIP_L / 2 + 0.05, KEEL_Y + 2.3, 0), 0.12, m["dark"]))  # sternpost
    for (x, hw, yd, yk, full) in st[1:-1]:
        pts = []
        for k in range(7):
            t = math.pi * k / 6
            c, s = math.cos(t), math.sin(t)
            lat = hw * (abs(c) ** (1 / full)) * (1 if c >= 0 else -1)
            pts.append((x, yd - (yd - yk) * (s ** (1 / full)), lat))
        s1.append(gtube(pts, 0.08, M("rib", (0.84, 0.62, 0.42)), sides=5))
    rib = M("rib", (0.84, 0.62, 0.42))
    s1 += sheer_line(st, lambda s_: s_[2] - 0.08, 0.07, rib, out=0.0)                         # clamp along the deck line
    s1 += sheer_line(st[1:-1], lambda s_: s_[3] + (s_[2] - s_[3]) * 0.45, 0.06, rib, out=-0.12)   # bilge stringer
    S["stage1"] = s1
    hullwood, boot = M("hullw", (0.70, 0.46, 0.30), "planks"), M("boot", SIG_RED)

    def hm(cy, is_deck):
        if is_deck:
            return m["deck"]
        return boot if cy < KEEL_Y + 0.55 else hullwood
    S["stage2"] = [hull_open(st, 0.09, lambda cy: boot if cy < KEEL_Y + 0.55 else hullwood,
                             M("hold", (0.55, 0.38, 0.26), "planks"), m["dark"], K=6)]
    s3 = [deck_strip(st, 0.06, -0.12, 0.08, m["deck"])]                               # deck goes in with stage 3
    s3 += sheer_line(st, lambda s_: s_[2] - 0.12, 0.1, m["navy"], out=0.02)          # navy sheer strake
    for sgn in (-1, 1):
        s3.append(gtube([(a[0], a[2] + 0.38, sgn * a[1] * 0.97) for a in st[1:-1]], 0.035, m["wht"], sides=4))
    for (x, hw, yd, yk, f) in st[1:-1:2]:
        for sgn in (-1, 1):
            s3.append(gb((0.06, 0.4, 0.06), (x, yd + 0.18, sgn * hw * 0.97), m["wht"], bev=0.0))
    s3.append(gb((1.6, 0.75, 1.3), (-2.9, KEEL_Y + 2.45, 0), m["wht"], bev=0.06))    # deckhouse aft
    s3.append(gb((1.75, 0.1, 1.45), (-2.9, KEEL_Y + 2.86, 0), m["navy"], bev=0.03))
    for z in (-0.66, 0.66):
        s3.append(gc(0.1, 0.05, (-2.6, KEEL_Y + 2.5, z), m["wglass"], axis="z", verts=8))
    s3.append(gc(0.35, 0.1, (-4.0, KEEL_Y + 2.7, 0), m["dark"], axis="x", verts=10))  # ship's wheel
    S["stage3"] = s3
    s4 = []
    for x, h in ((-1.9, 6.4), (0.6, 7.2), (2.9, 6.0)):
        yb = KEEL_Y + 2.1
        s4.append(gc(0.13, h, (x, yb + h / 2, 0), m["spar"], verts=8, r2=0.08))
        s4.append(gc(0.135, 0.12, (x, yb + h - 0.2, 0), m["navy"], verts=8))
        s4.append(gseg((x - 0.2, yb + 0.9, 0), (x - 2.0, yb + 1.4, 0), 0.05, m["spar"], verts=6))     # boom
        sail = blob(1.0, gpos(x - 1.1, yb + 1.25, 0), (1.0, 0.13, 0.16), m["sail"], x, seg=8, rings=4, amp=0.1)
        sail.rotation_euler.y = math.radians(-15); s4.append(sail)
        s4.append(gseg((x, yb + 1.4, 0), (x, yb + h * 0.85, 0), 0.02, m["sail"], verts=4))
        s4.append(gb((1.0, 0.1, 0.1), (x - 0.5, yb + h * 0.62, 0), m["spar"], bev=0.02, rot=(0, 0, 8)))  # gaff
    s4.append(gseg((SHIP_L / 2 + 0.1, KEEL_Y + 2.3, 0), (SHIP_L / 2 + 2.0, KEEL_Y + 2.9, 0), 0.07, m["spar"], verts=6))   # bowsprit
    s4.append(gtube([(SHIP_L / 2 + 2.0, KEEL_Y + 2.9, 0), (2.9, KEEL_Y + 7.8, 0), (0.6, KEEL_Y + 9.1, 0), (-1.9, KEEL_Y + 8.3, 0),
                     (-SHIP_L / 2 + 0.2, KEEL_Y + 2.8, 0)], 0.016, m["dark"], sides=3))
    s4.append(gpoly([(0.6, KEEL_Y + 9.2, 0.0), (1.4, KEEL_Y + 9.0, 0.0), (0.6, KEEL_Y + 8.8, 0.0)], 0.03, m["sred"]))   # pennant
    S["stage4"] = s4
    return S


def slipway():
    """Shipyard slipway (r4_slipway, r4_slipway2). Ways along X: land part x -6..4 at the keel-block top y 0.62, then a
    ramp down to y -1.4 at x 12 (the sea, +X). Origin = where ship_hull.glb goes. Scaffold + winch hut at the back (-Z),
    sign board face at (-5.2, 2.2, -2.35) for Label3D 'SLIPWAY' / 'Next ship in 0:12'. Collision: keep the ways walkable."""
    m = rmats()
    p = []
    for z in (-0.55, 0.55):                              # sliding ways
        p.append(gb((10.0, 0.25, 0.4), (-1.0, 0.125, z), m["dark"], bev=0.04))
        p.append(gb((8.4, 0.25, 0.4), (8.0, -0.6, z), m["dark"], bev=0.04, rot=(0, 0, -13.5)))
        for x in (5.5, 8.0, 10.5):
            p.append(gl(0.1, 2.0, (x, -1.0, z), m["dark"], m["end"], axis="y", verts=6))
    for x in (-3.8, -2.4, -1.0, 0.4, 1.8, 3.2):            # keel blocks
        p.append(gb((0.5, 0.37, 0.7), (x, 0.435, 0), M("blocks", (0.82, 0.62, 0.42), "planks"), bev=0.03))
    p.append(gb((11.0, 0.08, 3.0), (-0.5, 0.04, 0), M("gravel", (0.78, 0.72, 0.62)), bev=0.02))
    # scaffold tower along the back
    for x in (-4.0, -1.0, 2.0):
        for z in (-2.2, -1.7):
            p.append(gb((0.1, 3.4, 0.1), (x, 1.7, z), m["plank"], bev=0.02))
    for y in (1.3, 2.5):
        p.append(gb((6.4, 0.06, 0.6), (-1.0, y, -1.95), m["plank"], bev=0.02))
        p.append(gb((6.3, 0.05, 0.05), (-1.0, y + 0.5, -1.65), m["plank"], bev=0.0))
    for x in (-2.5, 0.5):
        p.append(gseg((x - 1.4, 0.0, -2.2), (x + 1.4, 2.5, -2.2), 0.04, m["plank"], verts=4))
    # winch hut + sign
    p.append(gb((1.6, 1.6, 1.4), (-5.3, 0.8, -2.0), M("walls", WHITE, "boards", bands=14.0, dir="Z"), bev=0.05))
    p.append(gb((1.9, 0.12, 1.7), (-5.3, 1.7, -2.0), m["navy"], bev=0.04, rot=(8, 0, 0)))
    p.append(gc(0.3, 0.7, (-4.3, 0.55, -1.6), m["navy_d"], axis="x", verts=10))
    p.append(gb((1.5, 0.5, 0.08), (-5.3, 2.2, -1.25), m["yellow"], bev=0.03))
    for x in (-5.95, -4.65):
        p.append(gb((0.06, 0.6, 0.06), (x, 1.95, -1.25), m["dark"], bev=0.0))
    return p


# ------------------------------------------------------------------ buildings

def harbor_office():
    """Harbor Office (r4_office): white weatherboards, navy roof, round porthole windows, life ring. Door + porch at +Z;
    yellow sign board face (0, 2.1, 1.55): Label3D 'OFFICE' at z 1.62. Blocker (3.8, 3.0, 3.2); upgrade zone +Z 3.4."""
    m = rmats()
    walls = M("walls", WHITE, "boards", bands=16.0, dir="Z")
    roof = M("roof", NAVY, "boards", bands=12.0, dir="X")
    W, D = 3.6, 3.0
    p = [gb((W + 0.2, 0.45, D + 0.2), (0, 0.22, 0), m["rock"], bev=0.08)]
    p.append(gb((W, 2.05, D), (0, 1.47, 0), walls, bev=0.04))
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(gb((0.16, 2.1, 0.16), (sx * W / 2, 1.5, sz * D / 2), m["navy_d"], bev=0.03))
    rp, ridge = groof(W, D, 2.5, 34, 0.35, roof)
    p += rp
    p += gables(W, D, 2.5, 34, walls)
    p.append(gb((0.85, 1.55, 0.08), (-0.75, 1.23, D / 2 + 0.02), m["navy"], bev=0.03))
    p.append(gc(0.04, 0.05, (-0.5, 1.2, D / 2 + 0.08), m["gold"], axis="z", verts=8))
    for x in (0.55, 1.2):
        p.append(gc(0.24, 0.07, (x, 1.45, D / 2 + 0.02), m["gold"], axis="z", verts=14))
        p.append(gc(0.19, 0.08, (x, 1.45, D / 2 + 0.03), m["wglass"], axis="z", verts=14))
    p.append(gc(0.26, 0.07, (W / 2 + 0.02, 1.45, 0), m["gold"], axis="x", verts=14))
    p.append(gc(0.21, 0.08, (W / 2 + 0.03, 1.45, 0), m["wglass"], axis="x", verts=14))
    ring = _add("primitive_torus_add", major_radius=0.22, minor_radius=0.06, major_segments=12, minor_segments=6,
                location=gpos(-1.55, 1.25, D / 2 + 0.1), rotation=(math.pi / 2, 0, 0))
    _assign(ring, m["sred"]); _smooth(ring); p.append(ring)
    p.append(gb((1.6, 0.14, 1.0), (-0.4, 0.07, D / 2 + 0.6), m["plank"], bev=0.03))
    p.append(gb((1.4, 0.5, 0.1), (0.0, 2.1, D / 2 + 0.05), m["yellow"], bev=0.04))
    p.append(gb((0.5, 1.1, 0.5), (1.0, ridge + 0.05, -0.6), m["rock"], bev=0.06))
    return p


def market_canopy_navy():
    return _canopy(NAVY, AWNING_CREAM)


# ------------------------------------------------------------------ Level Crossing (gateway)

def crossing_post():
    """Level-crossing post (r4_crossing): base, navy post, mechanism box, white crossbuck with red rim, twin red lamps.
    The boom (crossing_arm.glb) hangs at (0.12, 1.05, 0) pointing +X; put one post on each road edge, the east one rot 180."""
    m = rmats()
    p = [gb((0.7, 0.2, 0.7), (0, 0.1, 0), m["grey"], bev=0.05), gb((0.5, 0.9, 0.45), (0, 0.65, 0), m["navy"], bev=0.06)]
    p.append(gb((0.55, 0.08, 0.5), (0, 1.12, 0), m["yellow"], bev=0.02))
    p.append(gc(0.07, 2.6, (-0.12, 1.3, -0.1), m["wht"], verts=8))
    for k in range(4):
        p.append(gc(0.075, 0.18, (-0.12, 0.45 + k * 0.55, -0.1), m["sred"], verts=8))
    for a in (35, -35):
        p.append(gb((1.3, 0.2, 0.05), (-0.12, 2.35, -0.02), m["sred"], bev=0.02, rot=(0, 0, a)))
        p.append(gb((1.2, 0.13, 0.06), (-0.12, 2.35, -0.0), m["wht"], bev=0.01, rot=(0, 0, a)))
    p.append(gb((0.7, 0.24, 0.08), (-0.12, 1.78, 0.0), m["blk"], bev=0.03))
    for x in (-0.36, 0.12):
        p.append(gc(0.09, 0.05, (x, 1.78, 0.05), m["sred"], axis="z", verts=10))
    return p


def crossing_arm():
    """Barrier boom, pivot = origin (hinge). Points +X, 3.6 m, red/white stripes, red lamp near the tip, counterweight at
    -X. Lowered = rotation 0; raised = rotation.z 80 deg (tween 0.5 s)."""
    m = rmats()
    p = [gc(0.1, 0.2, (0, 0, 0), m["steel_d"], axis="z", verts=10), gb((0.5, 0.25, 0.22), (-0.35, 0, 0), m["blk"], bev=0.05)]
    for i in range(6):
        p.append(gb((0.6, 0.11, 0.08), (0.2 + i * 0.6, 0, 0), m["sred"] if i % 2 == 0 else m["wht"], bev=0.02))
    p.append(gc(0.06, 0.05, (3.1, 0.1, 0.0), m["sred"], verts=8))
    p.append(gb((0.06, 0.3, 0.06), (2.2, -0.2, 0), m["wht"], bev=0.0))
    return p


def crossing_closed():
    """Closed gap in the road fence before r4_crossing is bought: red/white plank barricade, 3.0 m along Z, two trestles.
    Shrink to 0.01 and free on unlock (like the Highland Gate doors)."""
    m = rmats()
    p = []
    for z in (-1.3, 1.3):
        for s in (-1, 1):
            p.append(gseg((s * 0.3, 0.0, z), (0, 1.0, z), 0.04, m["dark"], verts=4))
    for y in (0.55, 0.9):
        for i in range(6):
            p.append(gb((0.06, 0.18, 0.5), (0.05, y, -1.25 + i * 0.5), m["sred"] if i % 2 == 0 else m["wht"], bev=0.01))
    p.append(gb((0.08, 0.5, 0.9), (0.1, 1.35, 0), m["yellow"], bev=0.02))
    return p


# ------------------------------------------------------------------ landmark

def lighthouse():
    """Lighthouse (r4_lighthouse), 6 stages, 14.2 m. Door faces +Z. Footprint 5 x 5; collision cylinder r 1.6, h 10.
    stage1 rock base + plinth, stage2 white lower tower + door, stage3 red middle band + windows, stage4 white upper tower,
    stage5 navy gallery + rail + glass lantern, stage6 red dome + vent ball + vane."""
    m = rmats()
    S = {}
    S["stage1"] = [blob(1.0, gpos(x, 0.15, z), (r, r * 0.9, r * 0.45), m["rock"], k + 0.5, ico=2, amp=0.2)
                   for k, (x, z, r) in enumerate(((-1.4, -1.0, 1.0), (1.3, -0.8, 1.1), (0.0, 1.3, 0.9), (-1.6, 1.0, 0.7), (1.5, 1.2, 0.6)))]
    S["stage1"] += [gc(2.0, 0.6, (0, 0.5, 0), m["stone"], verts=20), gb((1.4, 0.3, 0.8), (0, 0.15, 2.2), m["stone"], bev=0.05)]
    S["stage2"] = [gc(1.55, 3.6, (0, 2.6, 0), m["wht"], verts=20, r2=1.4), gb((0.9, 1.7, 0.1), (0, 1.65, 1.5), m["navy"], bev=0.03),
                   gb((1.1, 0.14, 0.3), (0, 2.55, 1.52), m["navy_d"], bev=0.03)]
    S["stage2"] += window(0.0, 3.6, 1.42, 0.35, 0.55, m["navy_d"], m["wglass"])
    S["stage3"] = [gc(1.4, 3.0, (0, 5.9, 0), m["sred"], verts=20, r2=1.22)]
    S["stage3"] += window(0.0, 5.9, 1.33, 0.32, 0.55, m["wht"], m["wglass"])
    S["stage3"] += window(1.32, 6.6, 0.0, 0.32, 0.5, m["wht"], m["wglass"], face="x")
    S["stage4"] = [gc(1.22, 2.4, (0, 8.6, 0), m["wht"], verts=20, r2=1.08), gc(1.25, 0.25, (0, 7.5, 0), m["sred"], verts=20)]
    s5 = [gc(1.55, 0.2, (0, 9.9, 0), m["navy"], verts=20), gc(0.85, 0.3, (0, 10.15, 0), m["navy_d"], verts=16)]
    for i in range(16):
        a = 2 * math.pi * i / 16
        s5.append(gb((0.05, 0.6, 0.05), (1.45 * math.cos(a), 10.3, 1.45 * math.sin(a)), m["navy_d"], bev=0.0))
    rail = _add("primitive_torus_add", major_radius=1.45, minor_radius=0.04, major_segments=20, minor_segments=4, location=gpos(0, 10.6, 0))
    _assign(rail, m["navy_d"]); s5.append(rail)
    s5.append(gc(0.78, 1.2, (0, 10.9, 0), M("lantern", (1.0, 0.92, 0.62)), verts=12))
    for i in range(6):
        a = 2 * math.pi * i / 6
        s5.append(gb((0.06, 1.2, 0.06), (0.8 * math.cos(a), 10.9, 0.8 * math.sin(a)), m["navy_d"], bev=0.0))
    S["stage5"] = s5
    s6 = [gc(0.95, 0.15, (0, 11.55, 0), m["navy_d"], verts=16)]
    dome = blob(1.0, gpos(0, 11.6, 0), (0.92, 0.92, 0.75), m["sred"], 0.0, seg=14, rings=6, amp=0.0)
    for v in dome.data.vertices:
        if v.co.z < 0:
            v.co.z = 0.0
    s6.append(dome)
    s6.append(blob(1.0, gpos(0, 12.55, 0), (0.18, 0.18, 0.18), m["navy_d"], 0.0, seg=8, rings=5, amp=0.0))
    s6.append(gc(0.03, 1.1, (0, 13.2, 0), m["navy_d"], verts=6))
    s6.append(gpoly([(0.0, 13.55, 0.0), (0.55, 13.45, 0.0), (0.0, 13.3, 0.0)], 0.03, m["gold"]))
    S["stage6"] = s6
    return S


# ------------------------------------------------------------------ props (world units)

def buoy():
    """Red/white channel buoy (decor on the water or the quay)."""
    m = rmats()
    return [gc(0.45, 0.5, (0, 0.25, 0), m["sred"], verts=14, r2=0.42), gc(0.42, 0.12, (0, 0.56, 0), m["wht"], verts=14),
            gc(0.34, 0.5, (0, 0.85, 0), m["sred"], verts=12, r2=0.2), gc(0.05, 0.5, (0, 1.3, 0), m["blk"], verts=6),
            gc(0.1, 0.18, (0, 1.6, 0), m["lamp"], verts=8)]


def fish_crates():
    """Stack of four wooden harbour crates with navy stencils (decor)."""
    m = rmats()
    p = []
    for (x, y, z, r) in ((0, 0, 0, 0), (0.62, 0, 0.1, 8), (0.3, 0.42, 0.04, -6), (-0.1, 0, 0.6, 15)):
        p.append(gb((0.58, 0.4, 0.42), (x, y + 0.2, z), M("crate", (0.84, 0.66, 0.44), "planks"), bev=0.03, rot=(0, r, 0)))
        p.append(gb((0.2, 0.12, 0.01), (x, y + 0.22, z + 0.215), m["navy"], bev=0.0, rot=(0, r, 0)))
    return p


def anchor_prop():
    """Old iron anchor leaning on a rock (decor), 1.6 m."""
    m = rmats()
    iron = M("iron", (0.3, 0.3, 0.32))
    p = [blob(1.0, gpos(0.3, 0.15, -0.3), (0.5, 0.4, 0.3), m["rock"], 1.3, ico=2, amp=0.2)]
    p.append(gseg((0, 0.15, 0), (0.25, 1.5, -0.2), 0.07, iron))
    p.append(gseg((0.17, 1.15, -0.13), (0.4, 1.12, 0.3), 0.04, iron))
    p.append(gseg((0.17, 1.15, -0.13), (-0.06, 1.18, -0.56), 0.04, iron))
    p.append(gseg((-0.55, 0.45, 0.0), (0, 0.12, 0), 0.06, iron))
    p.append(gseg((0.55, 0.45, 0.0), (0, 0.12, 0), 0.06, iron))
    for x in (-0.6, 0.6):
        p.append(gpoly([(x, 0.4, 0.0), (x * 0.75, 0.6, 0.0), (x * 1.15, 0.65, 0.0)] if x < 0 else
                       [(x, 0.4, 0.0), (x * 1.15, 0.65, 0.0), (x * 0.75, 0.6, 0.0)], 0.06, iron))
    t = _add("primitive_torus_add", major_radius=0.13, minor_radius=0.03, major_segments=10, minor_segments=4,
             location=gpos(0.26, 1.62, -0.2), rotation=(math.pi / 2, 0, 0))
    _assign(t, iron); p.append(t)
    return p


def bollard():
    """Iron mooring bollard with a rope loop (decor on quays)."""
    m = rmats()
    p = [gc(0.18, 0.08, (0, 0.04, 0), m["blk"], verts=10), gc(0.13, 0.45, (0, 0.3, 0), m["blk"], verts=10),
         gc(0.18, 0.08, (0, 0.55, 0), m["blk"], verts=10)]
    t = _add("primitive_torus_add", major_radius=0.17, minor_radius=0.035, major_segments=10, minor_segments=4, location=gpos(0, 0.35, 0))
    _assign(t, M("rope", (0.86, 0.78, 0.6))); p.append(t)
    return p


def handcar_stop_navy():
    return accent(handcar_stop, NAVY, NAVY_D)()


def handcar_navy():
    return accent(handcar, NAVY, NAVY_D)()


def forklift_navy():
    return accent(forklift, NAVY, NAVY_D)()


# ------------------------------------------------------------------ plan
K, W = "kenney", "world"
T = dict(ao=0.22, grad=0.86)
PLAN = {
    "tree_redwoodA":      ("redwood", lambda: redwood_tree("A"), 512, K, T),
    "tree_redwoodB":      ("redwood", lambda: redwood_tree("B"), 512, K, T),
    "tree_redwoodC":      ("redwood", lambda: redwood_tree("C"), 512, K, T),
    "tree_redwoodA_far":  ("redwood", lambda: redwood_tree("A", far=True), 256, K, T),
    "tree_redwoodB_far":  ("redwood", lambda: redwood_tree("B", far=True), 256, K, T),
    "tree_redwoodC_far":  ("redwood", lambda: redwood_tree("C", far=True), 256, K, T),
    "stump_redwood":      ("redwood", redwood_stump, 256, K, dict(ao=0.45, grad=0.8)),
    "log_stack_redwood":  ("redwood", redwood_log_stack, 256, K, dict(ao=0.4, grad=0.82)),
    "dune_grass":         ("redwood", dune_grass, 128, K, dict(ao=0.4, grad=0.8)),
    "driftwood":          ("redwood", driftwood, 128, K, dict(ao=0.5, grad=0.85)),
    "beach_rock":         ("redwood", beach_rock, 256, K, dict(ao=0.4, grad=0.8)),
    "item_red_log":       ("items", item_red_log, 256, W, dict(ao=0.5, grad=0.85)),
    "item_timber":        ("items", item_timber, 256, W, dict(ao=0.5, grad=0.85)),
    "item_deckboard":     ("items", item_deckboard, 128, W, dict(ao=0.8, grad=0.88)),
    "item_mast":          ("items", item_mast, 256, W, dict(ao=0.4, grad=0.88)),
    "redwood_mill":       ("redwood", redwood_mill, 512, W, dict(ao=0.2, grad=0.82)),
    "redwood_mill_blade": ("redwood", redwood_mill_blade, 128, W, dict(ao=0.3, grad=0.95, no_ground=True)),
    "deck_saw":           ("redwood", deck_saw, 512, W, dict(ao=0.22, grad=0.82)),
    "deck_saw_gang":      ("redwood", deck_saw_gang, 128, W, dict(ao=0.3, grad=0.95, no_ground=True)),
    "mast_lathe":         ("redwood", mast_lathe, 512, W, dict(ao=0.22, grad=0.82)),
    "mast_lathe_log":     ("redwood", mast_lathe_log, 256, W, dict(ao=0.3, grad=0.95, no_ground=True)),
    "log_skidder":        ("redwood", log_skidder, 256, W, dict(ao=0.25, grad=0.82)),
    "forklift_navy":      ("redwood", forklift_navy, 256, W, dict(ao=0.25, grad=0.82)),
    "handcar_navy":       ("redwood", handcar_navy, 256, W, dict(ao=0.3, grad=0.82)),
    "cargo_ship":         ("redwood", cargo_ship, 512, W, dict(ao=0.15, grad=0.85)),
    "fishing_boat":       ("redwood", fishing_boat, 256, W, dict(ao=0.25, grad=0.85)),
    "pier_straight_4m":   ("redwood", pier_straight_4m, 256, W, dict(ao=0.4, grad=0.85)),
    "pier_end":           ("redwood", pier_end, 256, W, dict(ao=0.35, grad=0.85)),
    "order_board":        ("redwood", order_board, 256, W, dict(ao=0.25, grad=0.85)),
    "dock_crane":         ("redwood", dock_crane, 128, W, dict(ao=0.3, grad=0.85)),
    "dock_crane_jib":     ("redwood", dock_crane_jib, 256, W, dict(ao=0.3, grad=0.9, no_ground=True)),
    "slipway":            ("redwood", slipway, 512, W, dict(ao=0.1, grad=0.85)),
    "ship_hull":          ("redwood", ship_hull, 512, W, dict(ao=0.08, grad=0.85)),
    "harbor_office":      ("redwood", harbor_office, 512, W, dict(ao=0.18, grad=0.82)),
    "market_canopy_navy": ("redwood", market_canopy_navy, 256, W, dict(ao=0.18, grad=0.85)),
    "crossing_post":      ("redwood", crossing_post, 256, W, dict(ao=0.25, grad=0.85)),
    "crossing_arm":       ("redwood", crossing_arm, 128, W, dict(ao=0.3, grad=0.95, no_ground=True)),
    "crossing_closed":    ("redwood", crossing_closed, 128, W, dict(ao=0.35, grad=0.85)),
    "handcar_stop_navy":  ("redwood", handcar_stop_navy, 256, W, dict(ao=0.22, grad=0.85)),
    "lighthouse":         ("redwood", lighthouse, 512, W, dict(ao=0.06, grad=0.85)),
    "buoy":               ("redwood", buoy, 128, W, dict(ao=0.3, grad=0.85)),
    "fish_crates":        ("redwood", fish_crates, 128, W, dict(ao=0.35, grad=0.85)),
    "anchor_prop":        ("redwood", anchor_prop, 128, W, dict(ao=0.35, grad=0.85)),
    "bollard":            ("redwood", bollard, 128, W, dict(ao=0.35, grad=0.85)),
    "harbor_lamp":        ("redwood", harbor_lamp, 128, W, dict(ao=0.2, grad=0.85)),
}

if __name__ == "__main__" and os.environ.get("M345_NO_RUN") != "1":
    run_plan(PLAN, f"{REPO}/tools/lookdev/build_m3_report.json", OUT_ROOT)
