"""Review sheets for M3 Redwood Coast, M4 Frost Peaks, M5 Grand Timber Station -> tools/lookdev/compare_m3.png /
compare_m4.png / compare_m5.png. Every model at the game pitch with the Godot sun (render_scenes.py), fitted together as
ASSETS_M3/M4/M5.md place them, plus the tree lineup vs earlier valleys, icons, ground tiles and the imposter atlas.
  python3 tools/lookdev/make_compare_m345.py m3|m4|m5
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
L = f"{REPO}/tools/lookdev"
V3 = f"{REPO}/assets/models_v3"
MP, RW, FR, ST = f"{V3}/maple", f"{V3}/redwood", f"{V3}/frost", f"{V3}/station"
IT = f"{V3}/items"
BLENDER = "/home/mm/.local/bin/blender"
REGION = sys.argv[1]
R = f"{L}/_render/{REGION}"
COAST, SEA, SNOW, V1G = (0.44, 0.6, 0.28), (0.25, 0.5, 0.62), (0.88, 0.91, 0.95), (0.45, 0.66, 0.25)


def P(path, pos=(0, 0, 0), rot_y=0, scale=1, keep=None):
    d = {"glb": path, "pos": list(pos), "rot_y": rot_y, "scale": scale}
    if keep:
        d["keep"] = keep
    return d


def track(z0, n, x=0.0, rot=0, along_x=False):
    if along_x:
        return [P(f"{MP}/rail_straight_4m.glb", (z0 + 4 * i, 0, x), 90) for i in range(n)]
    return [P(f"{MP}/rail_straight_4m.glb", (x, 0, z0 + 4 * i), rot) for i in range(n)]


def stages(path, n, step, axis=0):
    out = []
    for i in range(n):
        pos = [0, 0, 0]; pos[axis] = i * step
        out.append(P(path, tuple(pos), 0, 1, [f"stage{k}" for k in range(1, i + 2)]))
    return out


def box(size, pos, rgb):
    return {"size": list(size), "pos": list(pos), "rgb": list(rgb)}


# scene = (title, parts, pad, wide, ground, boxes)
def scenes_m3():
    trees = [(f"{V3}/nature/tree_default.glb", 2.5), (f"{MP}/tree_mapleA.glb", 2.75), (f"{RW}/tree_redwoodA.glb", 4.0),
             (f"{RW}/tree_redwoodB.glb", 4.0), (f"{RW}/tree_redwoodC.glb", 4.0), (f"{RW}/tree_redwoodA_far.glb", 4.0),
             (f"{RW}/stump_redwood.glb", 4.0), (f"{RW}/log_stack_redwood.glb", 2.4), (f"{RW}/dune_grass.glb", 2.5),
             (f"{RW}/driftwood.glb", 2.5), (f"{RW}/beach_rock.glb", 2.5)]
    road = [box((3.6, 0.02, 9), (0, 0.01, 0), (0.35, 0.34, 0.33))]
    return [
        ("Trees at game scale: V1 default 2.5, maple A 2.75, redwood A/B/C x1.6 (4.0), redwood A _far, stump, log stack, dune grass, driftwood, rock",
         [P(p, (i * 2.4, 0, 0), 0, s) for i, (p, s) in enumerate(trees)], 1.05, True, COAST, []),
        ("Redwood Mill + main blade + top blade (same GLB x0.56)", [P(f"{RW}/redwood_mill.glb"), P(f"{RW}/redwood_mill_blade.glb", (0, 0.8, 0.15)),
                                                                 P(f"{RW}/redwood_mill_blade.glb", (0.22, 1.72, 0.15), 0, 0.56)], 1.15, False, COAST, []),
        ("Deck Saw + 3-blade gang (spinner)", [P(f"{RW}/deck_saw.glb"), P(f"{RW}/deck_saw_gang.glb", (0, 0.92, 0))], 1.15, False, COAST, []),
        ("Mast Lathe + spinning log (rot_y 90)", [P(f"{RW}/mast_lathe.glb"), P(f"{RW}/mast_lathe_log.glb", (0, 1.12, 0), 90)], 1.15, False, COAST, []),
        ("Log Skidder carrying 2 red logs", [P(f"{RW}/log_skidder.glb"), P(f"{IT}/item_red_log.glb", (0, 1.04, -1.2)),
                                             P(f"{IT}/item_red_log.glb", (0, 1.46, -1.2))], 1.25, False, COAST, []),
        ("Harbour forklift (navy) with 2 timbers", [P(f"{RW}/forklift_navy.glb"), P(f"{IT}/item_timber.glb", (0, 0.2, 1.05)),
                                                   P(f"{IT}/item_timber.glb", (0, 0.6, 1.05))], 1.3, False, COAST, []),
        ("Fishing pier: 2 straights + pier end, shopper boat, buoy", [P(f"{RW}/pier_straight_4m.glb", (0, 0, 0)), P(f"{RW}/pier_straight_4m.glb", (4, 0, 0)),
                                                                     P(f"{RW}/pier_end.glb", (8, 0, 0)), P(f"{RW}/fishing_boat.glb", (8.5, 0, 3.2), 90),
                                                                     P(f"{RW}/buoy.glb", (12.5, 0, -2.5))], 1.08, False, SEA, []),
        ("Order dock: cargo ship, Order Board, dock crane + jib", [P(f"{RW}/cargo_ship.glb", (5.5, 0, 0)), P(f"{RW}/pier_straight_4m.glb", (1.5, 0, 0), 90),
                                                                  P(f"{RW}/pier_straight_4m.glb", (1.5, 0, 4), 90), P(f"{RW}/pier_straight_4m.glb", (1.5, 0, -4), 90),
                                                                  P(f"{RW}/order_board.glb", (-1.5, 0, -1.5)), P(f"{RW}/dock_crane.glb", (1.5, 0.3, 3.5)),
                                                                  P(f"{RW}/dock_crane_jib.glb", (1.5, 1.7, 3.5), -30)], 1.08, False, SEA, []),
        ("Slipways: ship_hull stages 1 / 2 / 3 / 4 (repeatable BuildSite), bow to the sea (+X)",
         [P(f"{RW}/slipway.glb", (0, 0, -i * 6)) for i in range(4)] +
         [P(f"{RW}/ship_hull.glb", (0, 0, -i * 6), 0, 1, [f"stage{k}" for k in range(1, i + 2)]) for i in range(4)], 1.03, True, COAST, []),
        ("Harbor Office", [P(f"{RW}/harbor_office.glb")], 1.15, False, COAST, []),
        ("Harbor Market: counters, till, navy canopy", [P(f"{V3}/shared/shop_counter.glb", (0, 0, z)) for z in (2.6, 0.0, -2.6)] +
         [P(f"{V3}/shared/shop_till.glb", (0, 0, -5.2)), P(f"{RW}/market_canopy_navy.glb", (0, 0, -1.15))], 1.1, False, COAST, []),
        ("Level Crossing: posts + arms (down) on the road | closed barricade", [P(f"{RW}/crossing_post.glb", (-2.3, 0, -1.6)),
                                                                              P(f"{RW}/crossing_arm.glb", (-2.18, 1.05, -1.6)),
                                                                              P(f"{RW}/crossing_post.glb", (2.3, 0, 1.6), 180),
                                                                              P(f"{RW}/crossing_arm.glb", (2.18, 1.05, 1.6), 180),
                                                                              P(f"{RW}/crossing_closed.glb", (5.5, 0, 0))], 1.1, False, COAST, road),
        ("Handcar stop (navy): track, handcar, sign, tiles", track(-4, 2, 0, 90) + [P(f"{RW}/handcar_navy.glb", (0, 0, 0), 90), P(f"{RW}/handcar_stop_navy.glb", (0, 0, -2.0)),
                                                         P(f"{MP}/handcar_tile.glb", (-1.7, 0, 2.2)), P(f"{MP}/handcar_tile.glb", (1.7, 0, 2.2))], 1.1, False, COAST, []),
        ("Lighthouse stages 1-6 (landmark)", stages(f"{RW}/lighthouse.glb", 6, 5.5), 1.04, True, COAST, []),
        ("Props: buoy, fish crates, anchor, bollard, harbour lamp, redwood log stack x2.4",
         [P(f"{RW}/buoy.glb"), P(f"{RW}/fish_crates.glb", (2.0, 0, 0)), P(f"{RW}/anchor_prop.glb", (4.2, 0, 0)), P(f"{RW}/bollard.glb", (5.8, 0, 0)),
          P(f"{RW}/harbor_lamp.glb", (7.2, 0, 0)), P(f"{RW}/log_stack_redwood.glb", (9.4, 0, 0), 0, 2.4)], 1.1, False, COAST, []),
    ]


def scenes_m4():
    trees = [(f"{V3}/nature/tree_default.glb", 2.5), (f"{FR}/tree_frostfirA.glb", 2.875), (f"{FR}/tree_frostfirB.glb", 2.875),
             (f"{FR}/tree_frostfirC.glb", 2.875), (f"{FR}/tree_frostfirD.glb", 2.875), (f"{FR}/tree_frostfirA_far.glb", 2.875),
             (f"{FR}/stump_frost.glb", 2.875), (f"{FR}/log_stack_frost.glb", 2.4), (f"{FR}/snow_drift.glb", 2.5),
             (f"{FR}/snow_rock.glb", 2.5), (f"{FR}/snow_bush.glb", 2.5)]
    kiln = [P(f"{FR}/drying_kiln.glb"), P(f"{FR}/kiln_glow.glb")]
    return [
        ("Trees at game scale: V1 default 2.5, frost fir A/B/C/D x1.15 (2.875), fir A _far, stump, log stack, snow drift, snow rock, snow bush",
         [P(p, (i * 2.3, 0, 0), 0, s) for i, (p, s) in enumerate(trees)], 1.05, True, SNOW, []),
        ("Drying Kiln (batch) baking: door closed, glow on", kiln + [P(f"{FR}/kiln_door.glb", (-0.72, 0.2, 1.26))], 1.15, False, SNOW, []),
        ("Drying Kiln done: door open (rot_y -100)", kiln + [P(f"{FR}/kiln_door.glb", (-0.72, 0.2, 1.26), -100)], 1.15, False, SNOW, []),
        ("Ski Workshop + bending press (plate)", [P(f"{FR}/ski_workshop.glb"), P(f"{FR}/ski_press.glb", (0, 1.55, 0.2))], 1.15, False, SNOW, []),
        ("Sled Workshop (assembler) + drill arm", [P(f"{FR}/sled_workshop.glb"), P(f"{FR}/sled_workshop_arm.glb", (0.9, 0, -1.2), 25)], 1.12, False, SNOW, []),
        ("Luthier Workshop + sanding disc", [P(f"{FR}/luthier_workshop.glb"), P(f"{FR}/luthier_sander.glb", (1.15, 1.32, 0.56))], 1.15, False, SNOW, []),
        ("Snowcat carrying 2 sleds", [P(f"{FR}/snowcat.glb"), P(f"{IT}/item_sled.glb", (0, 1.02, -0.75), 90), P(f"{IT}/item_sled.glb", (0, 1.45, -0.75), 90)], 1.3, False, SNOW, []),
        ("Mountain train: alpine platform, track, loco + 2 wagons with guitars, buffer stop",
         [P(f"{FR}/rail_platform_alpine.glb", (-3.5, 0, 2))] + track(-6, 5) + [P(f"{FR}/mountain_loco.glb", (0, 0, -2.5)),
          P(f"{FR}/mountain_wagon.glb", (0, 0, 1.1)), P(f"{FR}/mountain_wagon.glb", (0, 0, 4.7)), P(f"{MP}/rail_bumper.glb", (0, 0, 12.1), 180)] +
         [P(f"{IT}/item_guitar.glb", (dx, 0.92, z + dz)) for z in (1.1, 4.7) for dx in (-0.45, 0.45) for dz in (-0.7, 0.7)], 1.05, False, SNOW, []),
        ("Cable car: bottom station (V4) + bull-wheel, cable span, gondola, top station (V5, rot 180), closed chain",
         [P(f"{FR}/cablecar_station_bottom.glb", (0, 0, 0)), P(f"{FR}/cablecar_bullwheel.glb", (0, 4.2, 0)), P(f"{FR}/cablecar_chain.glb", (0, 0, 0)),
          P(f"{FR}/cablecar_cable_1m.glb", (0, 4.2, -5.5), 0, [1, 1, 11.0]), P(f"{FR}/cablecar_gondola.glb", (0, 4.2, -5.5)),
          P(f"{FR}/cablecar_station_top.glb", (0, 0, -11)), P(f"{FR}/cablecar_bullwheel.glb", (0, 4.2, -11))], 1.05, True, SNOW, []),
        ("Mountain Office", [P(f"{FR}/mountain_office.glb")], 1.15, False, SNOW, []),
        ("Ski Lodge: chalet, counters, till, alpine canopy", [P(f"{FR}/ski_lodge.glb", (-1.5, 0, -8.5))] +
         [P(f"{V3}/shared/shop_counter.glb", (0, 0, z)) for z in (2.6, 0.0, -2.6)] +
         [P(f"{V3}/shared/shop_till.glb", (0, 0, -5.2)), P(f"{FR}/market_canopy_alpine.glb", (0, 0, -1.15))], 1.08, False, SNOW, []),
        ("Handcar stop (alpine): track, handcar, sign, tiles", track(-4, 2, 0, 90) + [P(f"{FR}/handcar_alpine.glb", (0, 0, 0), 90),
          P(f"{FR}/handcar_stop_alpine.glb", (0, 0, -2.0)), P(f"{MP}/handcar_tile.glb", (-1.7, 0, 2.2)), P(f"{MP}/handcar_tile.glb", (1.7, 0, 2.2))], 1.1, False, SNOW, []),
        ("Summit Observatory stages 1-6 (landmark)", stages(f"{FR}/summit_observatory.glb", 6, 7.0), 1.04, True, SNOW, []),
        ("Props: ski rack, snowman, alpine lamp, firewood, frost log stack x2.4",
         [P(f"{FR}/ski_rack.glb"), P(f"{FR}/snowman.glb", (2.3, 0, 0)), P(f"{FR}/alpine_lamp.glb", (4.0, 0, 0)), P(f"{FR}/firewood_snow.glb", (5.8, 0, 0)),
          P(f"{FR}/log_stack_frost.glb", (8.0, 0, 0), 0, 2.4)], 1.1, False, SNOW, []),
    ]


def scenes_m5():
    PAVE = (0.82, 0.75, 0.63)
    tz = 1.0
    line = [P(f"{MP}/rail_straight_4m.glb", (x, 0, tz), 90) for x in range(-14, 16, 4)]
    trees = [(f"{V3}/nature/tree_default.glb", 2.5), (f"{ST}/tree_station_lime.glb", 2.5), (f"{ST}/tree_station_cone.glb", 2.5),
             (f"{ST}/tree_station_lime_far.glb", 2.5), (f"{ST}/tree_station_cone_far.glb", 2.5)]
    stg = []
    for i in range(6):
        ox, oz = (i % 3) * 19.0, (i // 3) * 13.0
        stg.append(P(f"{ST}/grand_station.glb", (ox, 0, oz), 0, 1, [f"stage{k}" for k in range(1, i + 2)]))
    return [
        ("Grand Timber Station stages 1-6 (capstone BuildSite; rows: 1 2 3 / 4 5 6)", stg, 1.03, True, PAVE, []),
        ("Finished station on the z -51 line with the Timber Express passing, square props and clipped trees",
         [P(f"{ST}/grand_station.glb")] + line +
         [P(f"{ST}/express_loco.glb", (10.5, 0, tz), 90), P(f"{ST}/express_tender.glb", (13.9, 0, tz), 90),
          P(f"{ST}/flower_planter.glb", (-3.2, 0, 6.6)), P(f"{ST}/flower_planter.glb", (3.2, 0, 6.6)),
          P(f"{ST}/station_lamp.glb", (-5.0, 0, 6.3)), P(f"{ST}/station_lamp.glb", (5.0, 0, 6.3)),
          P(f"{ST}/clock_post.glb", (-8.8, 0, 5.8)), P(f"{ST}/station_bench.glb", (6.8, 0, 6.6)), P(f"{ST}/luggage_cart.glb", (-6.8, 0, 6.8), 70),
          P(f"{ST}/tree_station_lime.glb", (-10.5, 0, 6.5), 0, 2.5), P(f"{ST}/tree_station_cone.glb", (10.5, 0, 6.5), 0, 2.5)], 1.03, True, PAVE, []),
        ("Station plot (before stage 1)", [P(f"{ST}/station_plot.glb")], 1.08, False, PAVE, []),
        ("Platform slots V1..V5 (each valley's accent)", [P(f"{ST}/platform_slot_v{k}.glb", ((k - 3) * 4.0, 0, 0)) for k in range(1, 6)], 1.08, False, V1G, []),
        ("Rail bridge 8 m over the river (6.4 m)", [P(f"{ST}/rail_bridge_8m.glb", (0, 0, 0), 90)] + [P(f"{MP}/rail_straight_4m.glb", (x, 0, 0), 90) for x in (-6, 6)],
         1.1, False, V1G, [box((6.4, 0.02, 4.0), (0, 0.06, 0), (0.25, 0.5, 0.62))]),
        ("Rail line crossing the road (x 17): crossing tile + M3 crossing posts", [P(f"{ST}/rail_road_crossing_4m.glb", (0, 0, 0), 90),
          P(f"{MP}/rail_straight_4m.glb", (-4, 0, 0), 90), P(f"{MP}/rail_straight_4m.glb", (4, 0, 0), 90),
          P(f"{RW}/crossing_post.glb", (-2.4, 0, -1.6)), P(f"{RW}/crossing_arm.glb", (-2.28, 1.05, -1.6))], 1.1, False, V1G,
         [box((3.6, 0.02, 9.0), (0, 0.005, 0), (0.35, 0.34, 0.33))]),
        ("Timber Express: loco, log tender, 2 coaches", track(-6, 5) + [P(f"{ST}/express_loco.glb", (0, 0, -3.5)), P(f"{ST}/express_tender.glb", (0, 0, -0.1)),
          P(f"{ST}/express_coach.glb", (0, 0, 3.7)), P(f"{ST}/express_coach.glb", (0, 0, 8.3))], 1.05, False, V1G, []),
        ("Clipped station trees x2.5: V1 default, lime, cone, lime _far, cone _far", [P(p, (i * 2.0, 0, 0), 0, s) for i, (p, s) in enumerate(trees)], 1.1, False, PAVE, []),
        ("Props: bench, clock post, planter, luggage cart, station lamp", [P(f"{ST}/station_bench.glb"), P(f"{ST}/clock_post.glb", (2.0, 0, 0)),
          P(f"{ST}/flower_planter.glb", (3.8, 0, 0)), P(f"{ST}/luggage_cart.glb", (5.8, 0, 0)), P(f"{ST}/station_lamp.glb", (7.8, 0, 0))], 1.1, False, PAVE, []),
        ("Handcar stop (station maroon) + tiles", track(-4, 2, 0, 90) + [P(f"{MP}/handcar.glb", (0, 0, 0), 90), P(f"{ST}/handcar_stop_station.glb", (0, 0, -2.0)),
          P(f"{MP}/handcar_tile.glb", (-1.7, 0, 2.2)), P(f"{MP}/handcar_tile.glb", (1.7, 0, 2.2))], 1.1, False, PAVE, []),
    ]


CFG = {
    "m3": dict(title="Redwood Coast (M3) v3 models, game pitch 52 deg + Godot sun. Accent: harbour navy #1e3a64, signal red #cc3333 as the 10%",
               scenes=scenes_m3, icons=["red_log", "timber", "deckboard", "mast"],
               grounds=[("grass_coast", "grass_coast 3x3"), ("sand_beach", "sand_beach 3x3")], atlas="border_trees_atlas_m3", atlas_bg=(112, 153, 71)),
    "m4": dict(title="Frost Peaks (M4) v3 models, game pitch 52 deg + Godot sun. Accent: alpine red #c8283a, snow #f2f6fc, kiln glow #ff7a1f",
               scenes=scenes_m4, icons=["frost_log", "dry_lumber", "skis", "sled", "guitar"],
               grounds=[("snow_frost", "snow_frost 3x3"), ("snow_packed", "snow_packed 3x3")], atlas="border_trees_atlas_m4", atlas_bg=(222, 230, 240)),
    "m5": dict(title="Grand Timber Station (M5) v3 models, game pitch 52 deg + Godot sun. Accent: station brass #c99a2e, maroon #6e2430, cream sandstone",
               scenes=scenes_m5, icons=[], grounds=[("station_paving", "station_paving 3x3")], atlas="border_trees_atlas_m5", atlas_bg=(84, 148, 39)),
}


def render(SC):
    jobs = [{"out": f"{R}/sc_{i:02d}.png", "parts": parts, "ground": g, "boxes": bx, "size": 900 if wide else 600, "pad": pad}
            for i, (_, parts, pad, wide, g, bx) in enumerate(SC)]
    os.makedirs(R, exist_ok=True)
    json.dump(jobs, open(f"{R}/scenes.json", "w"), indent=1)
    subprocess.run([BLENDER, "-b", "--python", f"{L}/render_scenes.py", "--", f"{R}/scenes.json"], check=True, capture_output=True)


def crop_rows(im):
    a = np.asarray(im).astype(int); g = a[5, 5]
    ys = np.where((np.abs(a - g).sum(2) > 40).any(1))[0]
    if len(ys) == 0:
        return im
    return im.crop((0, max(ys.min() - 30, 0), im.width, min(ys.max() + 30, im.height)))


def sheet(cfg, SC):
    fd = f"{REPO}/assets/fonts/"
    fnt = ImageFont.truetype(fd + next(f for f in os.listdir(fd) if f.endswith((".ttf", ".otf"))), 22)
    small = ImageFont.truetype(fnt.path, 17)
    W = 1800
    blocks = []

    def header(t):
        im = Image.new("RGB", (W, 40), (250, 246, 236)); ImageDraw.Draw(im).text((10, 8), t, fill=(40, 30, 20), font=fnt); blocks.append(im)

    header(cfg["title"])
    wide = [i for i, s in enumerate(SC) if s[3]]
    if wide:
        header(SC[wide[0]][0])
        blocks.append(crop_rows(Image.open(f"{R}/sc_{wide[0]:02d}.png").convert("RGB").resize((W, W))))
    small_ids = [i for i in range(len(SC)) if i not in wide]
    cell = 445
    for k in range(0, len(small_ids), 4):
        row = Image.new("RGB", (W, cell + 30), (250, 246, 236)); d = ImageDraw.Draw(row)
        for j, i in enumerate(small_ids[k:k + 4]):
            row.paste(Image.open(f"{R}/sc_{i:02d}.png").convert("RGB").resize((cell, cell)), (j * (cell + 5), 30))
            d.text((j * (cell + 5) + 4, 6), SC[i][0][:46], fill=(40, 30, 20), font=small)
        blocks.append(row)
    for i in wide[1:]:
        header(SC[i][0])
        blocks.append(crop_rows(Image.open(f"{R}/sc_{i:02d}.png").convert("RGB").resize((W, W))))
    if cfg["icons"]:
        header("Item icons (assets/icons): 256 / 128 / 64 on the HUD cream, 48 px check on dark green")
        ic = Image.new("RGB", (W, 300), (255, 247, 230))
        step = W // max(len(cfg["icons"]), 4)
        for j, n in enumerate(cfg["icons"]):
            x = j * step + 10
            for img, pos in ((Image.open(f"{REPO}/assets/icons/{n}.png").resize((180, 180)), (x, 10)),
                             (Image.open(f"{REPO}/assets/icons/{n}_128.png"), (x + 185, 10)), (Image.open(f"{REPO}/assets/icons/{n}_64.png"), (x + 185, 150))):
                ic.paste(img, pos, img)
            dk = Image.new("RGB", (64, 64), (40, 50, 35)); i48 = Image.open(f"{REPO}/assets/icons/{n}_64.png").resize((48, 48)); dk.paste(i48, (8, 8), i48)
            ic.paste(dk, (x + 255, 150))
            ImageDraw.Draw(ic).text((x, 260), n, fill=(40, 30, 20), font=small)
        blocks.append(ic)
    labels = " | ".join(l for _, l in cfg["grounds"]) + f" | {cfg['atlas']} (1024 px, 4 x 4)"
    header("Ground: " + labels)
    gr = Image.new("RGB", (W, 600), (255, 255, 255))
    for j, (n, _) in enumerate(cfg["grounds"]):
        gr.paste(Image.open(f"{L}/_render/ground/{n}_tile3x3.png").convert("RGB").resize((596, 596)), (j * 600, 2))
    at = Image.open(f"{REPO}/assets/textures/imposters/{cfg['atlas']}.png").convert("RGBA")
    bg = Image.new("RGBA", at.size, cfg["atlas_bg"] + (255,)); bg.alpha_composite(at)
    gr.paste(bg.convert("RGB").resize((596, 596)), (len(cfg["grounds"]) * 600, 2))
    blocks.append(gr)
    H = sum(b.height for b in blocks)
    out = Image.new("RGB", (W, H), (255, 255, 255)); y = 0
    for b in blocks:
        out.paste(b, (0, y)); y += b.height
    out.save(f"{L}/compare_{REGION}.png", optimize=True)
    print("wrote", f"{L}/compare_{REGION}.png", out.size)


if __name__ == "__main__":
    cfg = CFG[REGION]
    SC = cfg["scenes"]()
    if "--sheet-only" not in sys.argv:
        render(SC)
    sheet(cfg, SC)
