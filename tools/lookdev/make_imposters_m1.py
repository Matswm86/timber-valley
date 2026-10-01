"""Border-forest imposters: every _far tree used by World._border_forest (+ the 3 birches) rendered with
`um render3d` from the game camera pitch (52 deg, the camera never rotates), 4 facings each, albedo only
(sun 0; ambient 19.6 = white sky, because render3d scales the default 0.051 grey world: Godot lights the card), then packed into one atlas with `um sprite sheet`.

Same pixels-per-unit for every kind, so one quad size per world scale works for all cells.
Output: assets/textures/imposters/border_trees_atlas.png (8 x 8 cells of 256 px, 60 used)
        assets/textures/imposters/border_trees_atlas.json (cell index per kind/facing, quad size per unit)
  python3 tools/lookdev/make_imposters_m1.py
"""
import glob, json, os, subprocess
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
K = "/home/mm/MWM/projects/game-studio/tools/assetkit/um.sh"
os.environ.setdefault("BLENDER", "/home/mm/.local/bin/blender")
TMP = f"{REPO}/tools/lookdev/_render/imposters"
OUT = f"{REPO}/assets/textures/imposters"
KINDS = ["tree_pineTallA_detailed", "tree_pineTallB_detailed", "tree_pineTallC_detailed", "tree_pineTallD_detailed",
         "tree_pineRoundA", "tree_pineRoundC", "tree_default_dark", "tree_default", "tree_detailed", "tree_oak",
         "tree_fat", "tree_pineDefaultB", "tree_birchA", "tree_birchB", "tree_birchC"]
CELL, PPU, GROUND_Y, FACINGS = 256, 140, 246, 4
reports = {**json.load(open(f"{REPO}/tools/lookdev/build_report.json")), **json.load(open(f"{REPO}/tools/lookdev/build_m1_report.json"))}


def path(kind):
    folder = "birch" if "birch" in kind else "nature"
    return f"{REPO}/assets/models_v3/{folder}/{kind}_far.glb"


def one(kind):
    h = reports[kind + "_far"]["size"][2]
    subprocess.run([K, "render3d", path(kind), f"{TMP}/{kind}", "--preset", "iso8", "--headings", str(FACINGS),
                    "--elevation", "52", "--canvas", str(CELL), "--measure", "height", "--length", str(round(h * PPU)),
                    "--ground-y", str(GROUND_Y), "--sun", "0", "--ambient", "19.6", "--samples", "48"],
                   check=True, capture_output=True)
    print("imposter", kind)


os.makedirs(OUT, exist_ok=True)
with ThreadPoolExecutor(3) as ex:
    list(ex.map(one, KINDS))
frames = [f"{TMP}/{k}/idle_{i:02d}_000.png" for k in KINDS for i in range(FACINGS)]
subprocess.run([K, "sprite", "sheet", f"{OUT}/border_trees_atlas.png", *frames, "--cols", "8"], check=True)
meta = dict(cell_px=CELL, cols=8, rows=8, px_per_unit=PPU, ground_y_px=GROUND_Y, camera_pitch_deg=52, facings=FACINGS,
            note="quad width = cell_px / px_per_unit model units (x instance scale); pivot = (0.5, ground_y_px / cell_px); "
                 "tilt the quad to face the camera pitch; cell = kind_index * facings + facing",
            kinds={k: [i * FACINGS + f for f in range(FACINGS)] for i, k in enumerate(KINDS)})
json.dump(meta, open(f"{OUT}/border_trees_atlas.json", "w"), indent=1)
