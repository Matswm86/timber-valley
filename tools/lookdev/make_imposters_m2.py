"""Maple Highlands border-forest imposters, same recipe as make_imposters_m1.py (game camera pitch 52 deg, 4 facings,
albedo only, 140 px per model unit, ground at y 246 of each 256 px cell), packed 4 x 4 into a 1024 px atlas:
cells 0-3 tree_mapleA, 4-7 tree_mapleB, 8-11 tree_mapleC, 12-15 tree_pineTallB_detailed (so a V3 edge chunk needs
only this one atlas). The shader needs one change: the grid is 4, not 8 (ASSETS_M2.md section 6).
  python3 tools/lookdev/make_imposters_m2.py
"""
import json, os, subprocess
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
K = "/home/mm/MWM/projects/game-studio/tools/assetkit/um.sh"
os.environ.setdefault("BLENDER", "/home/mm/.local/bin/blender")
TMP = f"{REPO}/tools/lookdev/_render/imposters_m2"
OUT = f"{REPO}/assets/textures/imposters"
KINDS = ["tree_mapleA", "tree_mapleB", "tree_mapleC", "tree_pineTallB_detailed"]
CELL, PPU, GROUND_Y, FACINGS = 256, 140, 246, 4
m2 = json.load(open(f"{REPO}/tools/lookdev/build_m2_report.json"))
v3 = json.load(open(f"{REPO}/tools/lookdev/build_report.json"))


def info(kind):
    if kind.startswith("tree_maple"):
        return f"{REPO}/assets/models_v3/maple/{kind}_far.glb", m2[kind + "_far"]["size_godot"][1]
    return f"{REPO}/assets/models_v3/nature/{kind}_far.glb", v3[kind + "_far"]["size"][2]


def one(kind):
    path, h = info(kind)
    subprocess.run([K, "render3d", path, f"{TMP}/{kind}", "--preset", "iso8", "--headings", str(FACINGS),
                    "--elevation", "52", "--canvas", str(CELL), "--measure", "height", "--length", str(round(h * PPU)),
                    "--ground-y", str(GROUND_Y), "--sun", "0", "--ambient", "19.6", "--samples", "48"], check=True, capture_output=True)
    print("imposter", kind)


os.makedirs(OUT, exist_ok=True)
with ThreadPoolExecutor(1) as ex:   # 4 parallel Blender jobs failed on this box (2026-10-01)
    list(ex.map(one, KINDS))
frames = [f"{TMP}/{k}/idle_{i:02d}_000.png" for k in KINDS for i in range(FACINGS)]
subprocess.run([K, "sprite", "sheet", f"{OUT}/border_trees_atlas_m2.png", *frames, "--cols", "4"], check=True)
meta = dict(cell_px=CELL, cols=4, rows=4, px_per_unit=PPU, ground_y_px=GROUND_Y, camera_pitch_deg=52, facings=FACINGS,
            note="same card as border_trees_atlas.json; the shader grid is 4 (not 8); cell = kind_index * facings + facing",
            kinds={k: [i * FACINGS + f for f in range(FACINGS)] for i, k in enumerate(KINDS)})
json.dump(meta, open(f"{OUT}/border_trees_atlas_m2.json", "w"), indent=1)
