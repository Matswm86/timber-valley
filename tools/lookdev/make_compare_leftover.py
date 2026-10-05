"""Old vs new review sheet for the leftover replacements (tools/lookdev/compare_leftover.png).
Old = crops of the last in-game screenshots (screenshots_v3/, before this pass) or, where no clean shot exists,
the Kenney model rendered with the same review camera. New = render_scenes.py with the v3 GLBs fitted together
exactly as ASSETS_LEFTOVER.md places them (belt run, market, truck at the dock, ...).
  python3 tools/lookdev/make_compare_leftover.py
"""
import json, os, random, subprocess
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
L = f"{REPO}/tools/lookdev"
R = f"{L}/_render/leftover"
V3 = f"{REPO}/assets/models_v3"
KEN = f"{REPO}/tools/kenney_models"
SS = f"{REPO}/screenshots_v3"
BLENDER = "/home/mm/.local/bin/blender"
rep = json.load(open(f"{L}/build_leftover_report.json"))
GRASS = (0.45, 0.66, 0.25)


def P(path, pos=(0, 0, 0), rot_y=0, scale=1):
    return {"glb": path, "pos": list(pos), "rot_y": rot_y, "scale": scale}


def belt_run(pts, x0=0.0):
    """Conveyor pieces exactly as Conveyor._build_segment would place them (see ASSETS_LEFTOVER.md 2.1)."""
    import math
    parts, boxes = [], []
    for a, b in zip(pts, pts[1:]):
        ln = math.dist(a, b)
        cx, cz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        yaw = math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))   # local +Z along a->b
        parts.append({"glb": f"{V3}/shared/belt_rails.glb", "pos": [cx, 0, cz], "rot_y": yaw, "scale": [1, 1, ln + 0.8]})
        n = int(ln / 1.6) + 1
        for i in range(n + 1):
            t = -ln / 2 + ln * i / max(n, 1)
            parts.append(P(f"{V3}/shared/belt_legs.glb", (cx + math.sin(math.radians(yaw)) * t, 0, cz + math.cos(math.radians(yaw)) * t), yaw))
        horiz = abs(b[0] - a[0]) > abs(b[1] - a[1])
        boxes.append({"size": [ln + 0.8, 0.12, 0.8] if horiz else [0.8, 0.12, ln + 0.8], "pos": [cx, 0.49, cz], "rgb": [0.55, 0.57, 0.6]})
    for (p, q) in ((pts[0], pts[1]), (pts[-1], pts[-2])):
        yaw = math.degrees(math.atan2(q[0] - p[0], q[1] - p[1]))
        d = 0.4 / math.dist(p, q)
        parts.append(P(f"{V3}/shared/belt_end.glb", (p[0] - (q[0] - p[0]) * d, 0, p[1] - (q[1] - p[1]) * d), yaw))
    return parts, boxes


def palisade():
    rnd = random.Random(2)
    out = []
    for row, z in enumerate((0.0, -0.9)):
        for k in range(18):
            out.append({"glb": f"{V3}/shared/palisade_post.glb", "pos": [k * 0.31 + row * 0.15, 0, z], "rot_y": rnd.uniform(0, 360),
                        "scale": [1, rnd.uniform(0.95, 1.3), 1]})
    return out


belt_parts, belt_boxes = belt_run([(0, 0), (5, 0), (5, -4), (8, -4)])
H = "home"
SCENES = {
    # name: (old source, new parts, new boxes)
    "sawmill": (("crop", f"{SS}/v1_regress/04_yard.jpg", (0, 460, 620, 900)),
                [P(f"{V3}/{H}/sawmill_body_orange.glb")], [{"size": [4.3, 0.05, 0.8], "pos": [0, 0.52, 0.2], "rgb": [0.55, 0.57, 0.6]}]),
    "sawmill2 (green)": (None, [P(f"{V3}/{H}/sawmill_body_green.glb")], [{"size": [4.3, 0.05, 0.8], "pos": [0, 0.52, 0.2], "rgb": [0.55, 0.57, 0.6]}]),
    "belts (modular)": (("crop", f"{SS}/v1_regress/04_yard.jpg", (600, 500, 1080, 1300)), belt_parts, belt_boxes),
    "CNC + cog": (("crop", f"{SS}/v1_regress/07_sawmill2_cnc.jpg", (60, 0, 500, 330)),
                  [P(f"{V3}/{H}/cnc_router.glb"), P(f"{V3}/{H}/cnc_cog.glb", (0, 2.45, 0))], []),
    "bookcase factory + arms": (("crop", f"{SS}/v1_regress/08_factory.jpg", (0, 430, 440, 1000)),
                                [P(f"{V3}/{H}/bookcase_factory.glb"), P(f"{V3}/{H}/factory_arm.glb", (-2.3, 0.22, 1.2), 30),
                                 P(f"{V3}/{H}/factory_arm.glb", (2.4, 0.22, 1.2), -30)], []),
    "mega saw + crane + hook": (("crop", f"{SS}/v1_regress/12_megasaw.jpg", (0, 280, 1000, 900)),
                                [P(f"{V3}/{H}/megasaw_body.glb"), P(f"{V3}/{H}/megasaw_crane.glb", (-4.2, 0, -2.2), -20),
                                 P(f"{V3}/{H}/crane_hook.glb", (-1.2, 2.6, -1.3))],
                                [{"size": [8.2, 0.06, 2.2], "pos": [-0.6, 0.82, 0], "rgb": [0.55, 0.57, 0.6]}]),
    "carpentry + blade": (("crop", f"{SS}/v1_regress/06_carpentry.jpg", (500, 420, 1080, 1080)),
                          [P(f"{V3}/{H}/carpentry_shed.glb"), P(f"{V3}/{H}/saw_blade.glb", (0.8, 1.05, 0.35), 90)], []),
    "upgrade office": (None, [P(f"{V3}/{H}/office_hut.glb")], []),
    "grand lodge + windows": (("crop", f"{SS}/v1_regress/09_lodge.jpg", (0, 0, 1080, 1300)),
                              [P(f"{V3}/{H}/grand_lodge.glb"), P(f"{V3}/{H}/lodge_windows.glb")], []),
    "market (counters, till, canopy)": (("crop", f"{SS}/v1_regress/05_shop.jpg", (300, 400, 1080, 1900)),
                                        [P(f"{V3}/shared/shop_counter.glb", (0, 0, z)) for z in (2.6, 0.0, -2.6)] +
                                        [P(f"{V3}/shared/shop_till.glb", (0, 0, -5.2)), P(f"{V3}/shared/market_canopy.glb", (0, 0, -1.15))], []),
    "bridge": (("crop", f"{SS}/m1/19_bridge.jpg", (0, 600, 1080, 1300)), [P(f"{V3}/shared/bridge_river.glb")],
               [{"size": [7.4, 0.02, 9.0], "pos": [0, 0.04, 0], "rgb": [0.36, 0.66, 0.86]}]),
    "truck + dock": (("kenney", [P(f"{KEN}/car/truck-flat.glb", (3.5, 0, 0), 180, 1.7), P(f"{KEN}/factory/structure-yellow-tall.glb", (2.4, 0, -2.3), 0, 1.4),
                                 P(f"{KEN}/factory/structure-yellow-tall.glb", (2.4, 0, 2.3), 0, 1.4)],
                      [{"size": [4.2, 0.18, 5.0], "pos": [0.6, 0.09, 0], "rgb": [0.62, 0.6, 0.56]}]),
                     [P(f"{V3}/shared/truck_dock.glb"), P(f"{V3}/shared/truck_flatbed.glb", (3.5, 0, 0), 180)], []),
    "palisade": (None, palisade(), []),
    "road sign": (None, [P(f"{V3}/{H}/road_sign.glb")], []),
}


def render_all():
    jobs = []
    for i, (name, (old, parts, boxes)) in enumerate(SCENES.items()):
        jobs.append({"out": f"{R}/new_{i:02d}.png", "parts": parts, "boxes": boxes, "ground": GRASS, "size": 600})
        if old and old[0] == "kenney":
            jobs.append({"out": f"{R}/old_{i:02d}.png", "parts": old[1], "boxes": old[2], "ground": GRASS, "size": 600})
    os.makedirs(R, exist_ok=True)
    json.dump(jobs, open(f"{R}/scenes.json", "w"), indent=1)
    subprocess.run([BLENDER, "-b", "--python", f"{L}/render_scenes.py", "--", f"{R}/scenes.json"], check=True, capture_output=True)


def sheet():
    try:
        font = ImageFont.truetype(f"{REPO}/assets/fonts/" + next(f for f in os.listdir(f"{REPO}/assets/fonts") if f.endswith((".ttf", ".otf"))), 22)
    except (StopIteration, OSError):
        font = ImageFont.load_default()
    cell = 420
    cols = 2   # pairs per row
    names = list(SCENES)
    rows = (len(names) + cols - 1) // cols
    W = cols * (2 * cell + 20)
    im = Image.new("RGB", (W, 60 + rows * (cell + 40)), (250, 246, 236))
    dr = ImageDraw.Draw(im)
    dr.text((12, 14), "Leftover prototype graphics: OLD (in-game screenshot or Kenney) | NEW v3 (review camera = game pitch, Godot sun)",
            fill=(40, 30, 20), font=font)
    for i, n in enumerate(names):
        old = SCENES[n][0]
        x = (i % cols) * (2 * cell + 20); y = 60 + (i // cols) * (cell + 40)
        if old is None:
            o = Image.new("RGB", (cell, cell), (215, 210, 200))
            ImageDraw.Draw(o).text((20, cell // 2 - 12), "no clean in-game shot", fill=(90, 80, 70), font=font)
        elif old[0] == "crop":
            o = Image.open(old[1]).convert("RGB").crop(old[2])
            o.thumbnail((cell, cell)); bg = Image.new("RGB", (cell, cell), (215, 210, 200)); bg.paste(o, ((cell - o.width) // 2, (cell - o.height) // 2)); o = bg
        else:
            o = Image.open(f"{R}/old_{i:02d}.png").convert("RGB").resize((cell, cell))
        nw = Image.open(f"{R}/new_{i:02d}.png").convert("RGB").resize((cell, cell))
        im.paste(o, (x, y + 30)); im.paste(nw, (x + cell + 4, y + 30))
        dr.text((x + 4, y + 4), f"{n}", fill=(40, 30, 20), font=font)
    im.save(f"{L}/compare_leftover.png", optimize=True)
    print("wrote", f"{L}/compare_leftover.png", im.size)


if __name__ == "__main__":
    render_all()
    sheet()
