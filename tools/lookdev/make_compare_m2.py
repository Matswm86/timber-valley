"""Review sheet for M2 Maple Highlands -> tools/lookdev/compare_m2.png. Every model is shown at the game pitch with
the Godot sun (render_scenes.py), fitted together as ASSETS_M2.md places them (machine + spinner, train on track at
the platform, handcar stop, build-site stages). Plus the tree lineup vs V1/V2 trees, icons, ground tile, imposters.
  python3 tools/lookdev/make_compare_m2.py
"""
import json, os, subprocess
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
L = f"{REPO}/tools/lookdev"
R = f"{L}/_render/m2"
V3 = f"{REPO}/assets/models_v3"
MP = f"{V3}/maple"
BLENDER = "/home/mm/.local/bin/blender"
OLIVE = (0.5, 0.57, 0.22)
rep = json.load(open(f"{L}/build_m2_report.json"))


def P(path, pos=(0, 0, 0), rot_y=0, scale=1, keep=None):
    d = {"glb": path, "pos": list(pos), "rot_y": rot_y, "scale": scale}
    if keep:
        d["keep"] = keep
    return d


def track(z0, n, x=0.0, rot=0):
    return [P(f"{MP}/rail_straight_4m.glb", (x, 0, z0 + 4 * i), rot) for i in range(n)]


trees = [("nature", "tree_default"), ("birch", "tree_birchA"), ("maple", "tree_mapleA"), ("maple", "tree_mapleB"), ("maple", "tree_mapleC"),
         ("maple", "tree_mapleA_far"), ("maple", "stump_maple"), ("maple", "log_stack_maple"), ("maple", "leaf_pile"), ("maple", "bush_autumn")]
SC = [
    ("Trees at game scale 2.5: V1 default, V2 birch, maple A/B/C, maple A _far, stump, log stack, leaf pile, autumn bush",
     [P(f"{V3}/{f}/{n}.glb", (i * 2.3, 0, 0), 0, 2.5) for i, (f, n) in enumerate(trees)], 1.05),
    ("Beam Saw + beam_saw_blade (spinner)", [P(f"{MP}/beam_saw.glb"), P(f"{MP}/beam_saw_blade.glb", (0, 0.95, 0.05))], 1.15),
    ("Planer Mill + planer_roller (spinner)", [P(f"{MP}/planer_mill.glb"), P(f"{MP}/planer_roller.glb", (-0.66, 1.0, 0))], 1.15),
    ("Cabin Kit Factory (assembler) + press head", [P(f"{MP}/kit_factory.glb"), P(f"{MP}/kit_factory_press.glb", (0.1, 1.75, 0))], 1.15),
    ("Forklift carrying a cabin kit", [P(f"{MP}/forklift.glb"), P(f"{V3}/items/item_cabin_kit.glb", (0, 0.2, 1.05))], 1.3),
    ("Highland Railway: platform, track, loco + 3 wagons with kits, buffer stop",
     [P(f"{MP}/rail_platform.glb", (-3.5, 0, 2))] + track(-6, 5) + [P(f"{MP}/train_loco.glb", (0, 0, -2.5)),
      P(f"{MP}/train_wagon.glb", (0, 0, 1.3)), P(f"{MP}/train_wagon.glb", (0, 0, 4.9)), P(f"{MP}/train_wagon.glb", (0, 0, 8.5)),
      P(f"{MP}/rail_bumper.glb", (0, 0, 12.1), 180)] +
     [P(f"{V3}/items/item_cabin_kit.glb", (dx, 0.92, z + dz)) for z in (1.3, 4.9) for dx in (-0.45, 0.45) for dz in (-0.5, 0.5)], 1.05),
    ("Handcar stop: track, handcar, sign, 3 destination tiles",
     track(-4, 2, 0, 90) + [P(f"{MP}/handcar.glb", (0, 0, 0), 90), P(f"{MP}/handcar_stop.glb", (0, 0, -2.0)),
      P(f"{MP}/handcar_tile.glb", (-2.0, 0, 2.2)), P(f"{MP}/handcar_tile.glb", (0, 0, 2.2)), P(f"{MP}/handcar_tile.glb", (2.0, 0, 2.2))], 1.1),
    ("Highland Office", [P(f"{MP}/highland_office.glb")], 1.15),
    ("Builders' Yard: counters, till, teal canopy", [P(f"{V3}/shared/shop_counter.glb", (0, 0, z)) for z in (2.6, 0.0, -2.6)] +
     [P(f"{V3}/shared/shop_till.glb", (0, 0, -5.2)), P(f"{MP}/market_canopy_teal.glb", (0, 0, -1.15))], 1.1),
    ("Highland Gate closed (doors) | open", [P(f"{MP}/highland_gate.glb", (-3.2, 0, 0)), P(f"{MP}/highland_gate_doors.glb", (-3.2, 0, 0)),
                                           P(f"{MP}/highland_gate.glb", (3.2, 0, 0))], 1.1),
    ("Cottage stages 1 / 2 / 3 / 4 (BuildSite)", [P(f"{MP}/house_cottage.glb", (i * 6.5, 0, 0), 0, 1, [f"stage{k}" for k in range(1, i + 2)])
                                                  for i in range(4)], 1.05),
    ("Village: farmhouse, barn, school, inn (complete)", [P(f"{MP}/house_farmhouse.glb", (0, 0, 0)), P(f"{MP}/house_barn.glb", (7.5, 0, 0)),
                                                         P(f"{MP}/house_school.glb", (15, 0, 0)), P(f"{MP}/house_inn.glb", (22.5, 0, 0))], 1.05),
    ("Clock Tower stages 1-6 (landmark)", [P(f"{MP}/clock_tower.glb", (i * 5.0, 0, 0), 0, 1, [f"stage{k}" for k in range(1, i + 2)])
                                           for i in range(6)], 1.05),
    ("Props: build plot, beam cart, lantern, buffer stop, maple log stack x2.4",
     [P(f"{MP}/build_plot.glb"), P(f"{MP}/beam_cart.glb", (4.0, 0, 0), 30), P(f"{MP}/lantern_post.glb", (6.0, 0, 0)),
      P(f"{MP}/rail_bumper.glb", (8.0, 0, 0)), P(f"{MP}/log_stack_maple.glb", (10.0, 0, 0), 0, 2.4)], 1.1),
]


def render():
    jobs = [{"out": f"{R}/sc_{i:02d}.png", "parts": parts, "ground": OLIVE, "size": 900 if i in (0, 10, 11, 12) else 600, "pad": pad}
            for i, (_, parts, pad) in enumerate(SC)]
    os.makedirs(R, exist_ok=True)
    json.dump(jobs, open(f"{R}/scenes.json", "w"), indent=1)
    subprocess.run([BLENDER, "-b", "--python", f"{L}/render_scenes.py", "--", f"{R}/scenes.json"], check=True, capture_output=True)


def sheet():
    fd = f"{REPO}/assets/fonts/"
    fnt = ImageFont.truetype(fd + next(f for f in os.listdir(fd) if f.endswith((".ttf", ".otf"))), 22)
    small = ImageFont.truetype(fnt.path, 17)
    W = 1800
    blocks = []

    def header(t):
        im = Image.new("RGB", (W, 40), (250, 246, 236)); ImageDraw.Draw(im).text((10, 8), t, fill=(40, 30, 20), font=fnt); blocks.append(im)

    header("Maple Highlands (M2) v3 models, game pitch 52 deg + Godot sun. Accent: highland teal #2a9d8f")
    wide = [0, 10, 11, 12]
    for i in wide[:1]:
        header(SC[i][0])
        blocks.append(Image.open(f"{R}/sc_{i:02d}.png").convert("RGB").resize((W, W)).crop((0, 450, W, 1350)))
    small_ids = [i for i in range(len(SC)) if i not in wide]
    cell = 445
    for k in range(0, len(small_ids), 4):
        row = Image.new("RGB", (W, cell + 30), (250, 246, 236)); d = ImageDraw.Draw(row)
        for j, i in enumerate(small_ids[k:k + 4]):
            row.paste(Image.open(f"{R}/sc_{i:02d}.png").convert("RGB").resize((cell, cell)), (j * (cell + 5), 30))
            d.text((j * (cell + 5) + 4, 6), SC[i][0][:44], fill=(40, 30, 20), font=small)
        blocks.append(row)
    for i in wide[1:]:
        header(SC[i][0])
        im = Image.open(f"{R}/sc_{i:02d}.png").convert("RGB").resize((W, W))
        import numpy as np
        a = np.asarray(im).astype(int); g = a[5, 5]
        ys = np.where((np.abs(a - g).sum(2) > 40).any(1))[0]
        blocks.append(im.crop((0, max(ys.min() - 40, 0), W, min(ys.max() + 40, W))))
    header("Item icons (assets/icons): 256 / 128 / 64 on the HUD cream, 48 px check on dark green")
    ic = Image.new("RGB", (W, 300), (255, 247, 230))
    for j, n in enumerate(["maple_log", "beam", "floorboard", "cabin_kit"]):
        x = j * 440 + 10
        for img, pos in ((Image.open(f"{REPO}/assets/icons/{n}.png").resize((190, 190)), (x, 10)),
                         (Image.open(f"{REPO}/assets/icons/{n}_128.png"), (x + 200, 10)), (Image.open(f"{REPO}/assets/icons/{n}_64.png"), (x + 200, 150))):
            ic.paste(img, pos, img)
        dk = Image.new("RGB", (64, 64), (40, 50, 35)); i48 = Image.open(f"{REPO}/assets/icons/{n}_64.png").resize((48, 48)); dk.paste(i48, (8, 8), i48)
        ic.paste(dk, (x + 280, 150))
        ImageDraw.Draw(ic).text((x, 260), n, fill=(40, 30, 20), font=small)
    blocks.append(ic)
    header("Ground: grass_maple 3x3 tile-preview (4 m tiles) | Home road_tile 3x3 | border_trees_atlas_m2 (1024 px, 4 x 4)")
    gr = Image.new("RGB", (W, 600), (255, 255, 255))
    gr.paste(Image.open(f"{L}/_render/ground/grass_maple_tile3x3.png").convert("RGB").resize((596, 596)), (0, 2))
    gr.paste(Image.open(f"{L}/_render/ground/road_tile_tile3x3.png").convert("RGB").resize((596, 596)), (600, 2))
    at = Image.open(f"{REPO}/assets/textures/imposters/border_trees_atlas_m2.png").convert("RGBA")
    bg = Image.new("RGBA", at.size, (128, 146, 54, 255)); bg.alpha_composite(at)
    gr.paste(bg.convert("RGB").resize((596, 596)), (1202, 2))
    blocks.append(gr)
    H = sum(b.height for b in blocks)
    out = Image.new("RGB", (W, H), (255, 255, 255)); y = 0
    for b in blocks:
        out.paste(b, (0, y)); y += b.height
    out.save(f"{L}/compare_m2.png", optimize=True)
    print("wrote", f"{L}/compare_m2.png", out.size)


if __name__ == "__main__":
    render()
    sheet()
