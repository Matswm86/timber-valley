"""Review renders of every M1 model with the studio sprite tool (um render3d), from the game's camera pitch
(~52 deg), one facing, shadow pass included. Output: tools/lookdev/_render/m1/<name>/idle_00_000(_s).png.
  python3 tools/lookdev/render_m1_review.py [name ...]
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
K = "/home/mm/MWM/projects/game-studio/tools/assetkit/um.sh"
os.environ.setdefault("BLENDER", "/home/mm/.local/bin/blender")
rep = json.load(open(f"{REPO}/tools/lookdev/build_m1_report.json"))
only = sys.argv[1:]


def one(name):
    r = rep[name]
    if r["folder"] != "birch":
        return
    w = max(r["size"][0], r["size"][1]); h = r["size"][2]
    # longest horizontal side in px so the whole model (incl. height seen at 52 deg) fits a 512 canvas
    length = int(min(330, 330 * w / max(w, h * 0.95)))
    out = f"{REPO}/tools/lookdev/_render/m1/{name}"
    subprocess.run([K, "render3d", f"{REPO}/assets/models_v3/birch/{name}.glb", out, "--preset", "iso8", "--headings", "1",
                    "--elevation", "52", "--forward-yaw", "25", "--canvas", "512", "--length", str(length),
                    "--ground-y", "400" if h > w else "300", "--shadows", "--samples", "32"], check=True, capture_output=True)
    print("rendered", name, length)


with ThreadPoolExecutor(3) as ex:
    list(ex.map(one, [n for n in rep if not only or n in only]))
