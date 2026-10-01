"""Review sheet for M1: Birch Bend models, tree scale lineup, item icons, ground tiles, border imposters.
Needs the renders from render_m1_review.py, make_icons_m1.py, make_ground_m1.sh, make_imposters_m1.py.
  python3 tools/lookdev/make_compare_m1.py   -> tools/lookdev/compare_m1.png
"""
import json, os, subprocess
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
L = f"{REPO}/tools/lookdev"
K = "/home/mm/MWM/projects/game-studio/tools/assetkit/um.sh"
os.environ.setdefault("BLENDER", "/home/mm/.local/bin/blender")
GRASS = (137, 180, 90, 255)
W = 1800
rep = json.load(open(f"{L}/build_m1_report.json"))
try:
    FONT = ImageFont.truetype(f"{REPO}/assets/fonts/" + next(f for f in os.listdir(f"{REPO}/assets/fonts") if f.endswith((".ttf", ".otf"))), 26)
    SMALL = ImageFont.truetype(FONT.path, 17)
except (StopIteration, OSError):
    FONT = SMALL = ImageFont.load_default()

blocks = []


def header(text):
    im = Image.new("RGBA", (W, 44), (250, 246, 236, 255))
    ImageDraw.Draw(im).text((12, 8), text, fill=(40, 30, 20), font=FONT)
    blocks.append(im)


def lit(name, size):
    base = Image.new("RGBA", (512, 512), GRASS)
    d = f"{L}/_render/m1/{name}"
    base.alpha_composite(Image.open(f"{d}/idle_00_000_s.png").convert("RGBA"))
    base.alpha_composite(Image.open(f"{d}/idle_00_000.png").convert("RGBA"))
    return base.resize((size, size), Image.LANCZOS)


# 1. models
header("Birch Bend models (assets/models_v3/birch): game camera pitch 52 deg, um render3d. Label = tris")
names = [n for n in rep if rep[n]["folder"] == "birch" and not n.startswith("tree_")]
cell, cols = 300, 6
rows = (len(names) + cols - 1) // cols
im = Image.new("RGBA", (W, rows * cell), GRASS)
dr = ImageDraw.Draw(im)
for i, n in enumerate(names):
    x, y = (i % cols) * cell, (i // cols) * cell
    im.alpha_composite(lit(n, cell), (x, y))
    dr.rectangle((x, y, x + cell, y + 24), fill=(30, 30, 30, 200))
    dr.text((x + 6, y + 3), f"{n}  {rep[n]['tris']}", fill=(255, 255, 255), font=SMALL)
blocks.append(im)

# 2. trees at one scale next to the v3 broadleaf + pine
header("Birch trees vs v3 tree_default / pine at the same scale; right: the _far versions (~170 tris)")
lineup = [("nature", "tree_default"), ("nature", "tree_pineTallA_detailed"), ("birch", "tree_birchA"), ("birch", "tree_birchB"),
          ("birch", "tree_birchC"), ("birch", "tree_birchA_far"), ("birch", "tree_birchB_far"), ("birch", "tree_birchC_far")]
row = Image.new("RGBA", (W, 330), GRASS)
for i, (folder, n) in enumerate(lineup):
    out = f"{L}/_render/m1_lineup/{n}"
    h = json.load(open(f"{L}/build_report.json")).get(n, rep.get(n))["size"][2]
    if not os.path.exists(f"{out}/idle_00_000.png") or os.environ.get("RERENDER"):
        subprocess.run(
            [K, "render3d", f"{REPO}/assets/models_v3/{folder}/{n}.glb", out, "--preset", "iso8", "--headings", "1",
             "--elevation", "52", "--canvas", "384", "--measure", "height", "--length", str(round(h * 150)),
             "--ground-y", "350", "--shadows", "--samples", "32"], check=True, capture_output=True)
    b = Image.new("RGBA", (384, 384), GRASS)
    b.alpha_composite(Image.open(f"{out}/idle_00_000_s.png").convert("RGBA"))
    b.alpha_composite(Image.open(f"{out}/idle_00_000.png").convert("RGBA"))
    b = b.crop((40, 20, 344, 384)).resize((220, 264), Image.LANCZOS)
    row.alpha_composite(b, (i * 225, 0))
    tr = rep[n]["tris"] if n in rep else json.load(open(f"{L}/build_report.json"))[n]["tris"]
    ImageDraw.Draw(row).text((i * 225 + 6, 272), f"{n}\n{tr} tris", fill=(20, 30, 10), font=SMALL)
blocks.append(row)

# 3. icons
header("Item icons (assets/icons): 256 master, 128 shop, 64 HUD on the HUD cream pill, 48 px check on dark")
items = ["log", "plank", "chair", "table", "bookcase", "birch_log", "veneer", "plywood", "canoe"]
ic = Image.new("RGBA", (W, 420), (255, 247, 230, 255))
dr = ImageDraw.Draw(ic)
for i, n in enumerate(items):
    x = i * 198 + 6
    ic.alpha_composite(Image.open(f"{REPO}/assets/icons/{n}.png").resize((190, 190), Image.LANCZOS), (x, 4))
    ic.alpha_composite(Image.open(f"{REPO}/assets/icons/{n}_128.png"), (x + 31, 196))
    ic.alpha_composite(Image.open(f"{REPO}/assets/icons/{n}_64.png"), (x + 10, 336))
    dk = Image.new("RGBA", (64, 64), (40, 50, 35, 255))
    dk.alpha_composite(Image.open(f"{REPO}/assets/icons/{n}_64.png").resize((48, 48), Image.LANCZOS), (8, 8))
    ic.alpha_composite(dk, (x + 100, 336))
    dr.text((x + 4, 402), n, fill=(40, 30, 20), font=SMALL)
blocks.append(ic)

# 4. ground
header("Ground tiles (assets/textures/ground, 512 px = 4 m): 3x3 tile-preview each - grass_v1, grass_birch, dirt_path")
gr = Image.new("RGBA", (W, 600), (255, 255, 255, 255))
for i, n in enumerate(["grass_v1", "grass_birch", "dirt_path"]):
    gr.paste(Image.open(f"{L}/_render/ground/{n}_tile3x3.png").convert("RGBA").resize((596, 596), Image.LANCZOS), (i * 600 + 2, 2))
blocks.append(gr)

# 5. imposters
header("Border-forest imposters (assets/textures/imposters/border_trees_atlas.png, albedo; Godot lights the card)")
at = Image.open(f"{REPO}/assets/textures/imposters/border_trees_atlas.png").convert("RGBA")
imp = Image.new("RGBA", (W, 460), GRASS)
bg = Image.new("RGBA", at.size, GRASS); bg.alpha_composite(at)
imp.alpha_composite(bg.resize((900, 900), Image.LANCZOS).crop((0, 0, 900, 450)), (0, 5))
imp.alpha_composite(bg.resize((900, 900), Image.LANCZOS).crop((0, 450, 900, 900)), (900, 5))
blocks.append(imp)

H = sum(b.height for b in blocks)
sheet = Image.new("RGB", (W, H), (255, 255, 255))
y = 0
for b in blocks:
    sheet.paste(b.convert("RGB"), (0, y)); y += b.height
sheet.save(f"{L}/compare_m1.png", optimize=True)
print("wrote", f"{L}/compare_m1.png", sheet.size)
