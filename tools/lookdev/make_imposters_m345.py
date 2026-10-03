"""Border-forest imposters for M3-M5, same card as make_imposters_m1.py / _m2.py (game pitch 52 deg, 4 facings, albedo
only, 140 px per model unit, ground at y 246 of each 256 px cell), packed 4 x 4 into a 1024 px atlas (shader grid 4,
ASSETS_M2.md section 6). cell = kind_index * 4 + facing.
  python3 tools/lookdev/make_imposters_m345.py m3|m4|m5
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
K = "/home/mm/MWM/projects/game-studio/tools/assetkit/um.sh"
os.environ.setdefault("BLENDER", "/home/mm/.local/bin/blender")
REGION = sys.argv[1]
TMP = f"{REPO}/tools/lookdev/_render/imposters_{REGION}"
OUT = f"{REPO}/assets/textures/imposters"
KINDS = {"m3": [("redwood", "tree_redwoodA"), ("redwood", "tree_redwoodB"), ("redwood", "tree_redwoodC"), ("nature", "tree_pineTallB_detailed")],
         "m4": [("frost", "tree_frostfirA"), ("frost", "tree_frostfirB"), ("frost", "tree_frostfirC"), ("frost", "tree_frostfirD")],
         "m5": [("station", "tree_station_lime"), ("station", "tree_station_cone"), ("maple", "tree_mapleA"), ("nature", "tree_default")]}[REGION]
CELL, PPU, GROUND_Y, FACINGS = 256, 140, 246, 4
reports = {}


def info(folder, kind):
    if folder == "nature":
        v3 = json.load(open(f"{REPO}/tools/lookdev/build_report.json"))
        return f"{REPO}/assets/models_v3/nature/{kind}_far.glb", v3[kind + "_far"]["size"][2]
    rp = {"redwood": "m3", "frost": "m4", "station": "m5", "maple": "m2"}[folder]
    rep = json.load(open(f"{REPO}/tools/lookdev/build_{rp}_report.json"))
    return f"{REPO}/assets/models_v3/{folder}/{kind}_far.glb", rep[kind + "_far"]["size_godot"][1]


def one(fk):
    folder, kind = fk
    path, h = info(folder, kind)
    subprocess.run([K, "render3d", path, f"{TMP}/{kind}", "--preset", "iso8", "--headings", str(FACINGS),
                    "--elevation", "52", "--canvas", str(CELL), "--measure", "height", "--length", str(round(h * PPU)),
                    "--ground-y", str(GROUND_Y), "--sun", "0", "--ambient", "19.6", "--samples", "48"], check=True, capture_output=True)
    print("imposter", kind)


os.makedirs(OUT, exist_ok=True)
with ThreadPoolExecutor(1) as ex:
    list(ex.map(one, KINDS))
frames = [f"{TMP}/{k}/idle_{i:02d}_000.png" for _, k in KINDS for i in range(FACINGS)]
name = f"border_trees_atlas_{REGION}"
subprocess.run([K, "sprite", "sheet", f"{OUT}/{name}.png", *frames, "--cols", "4"], check=True)
meta = dict(cell_px=CELL, cols=4, rows=4, px_per_unit=PPU, ground_y_px=GROUND_Y, camera_pitch_deg=52, facings=FACINGS,
            note="same card as border_trees_atlas.json; the shader grid is 4 (not 8); cell = kind_index * facings + facing",
            kinds={k: [i * FACINGS + f for f in range(FACINGS)] for i, (_, k) in enumerate(KINDS)})
json.dump(meta, open(f"{OUT}/{name}.json", "w"), indent=1)
