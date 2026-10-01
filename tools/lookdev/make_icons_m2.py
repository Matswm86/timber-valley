"""M2 (Maple Highlands) item icons, identical pipeline and camera to make_icons_m1.py. Item icons for the HUD and shop, rendered from the item GLBs with the studio sprite tools.

Pipeline per item (one camera for all: um render3d --preset iso8, 1 facing, elevation 35, yaw -30):
  1. um render3d assets/models_v3/items/item_<id>.glb -> 512 px render (transparent)
  2. um sprite fit --smooth --size 240x240 (trim + one Lanczos scale), padded to 256 with a soft dark outline
  3. um sprite fit --smooth to 128 (shop) and 64 (HUD; the HUD coin draws at 58 px)
  4. um sprite preview for the review sheet
Output: assets/icons/<id>.png (256), assets/icons/<id>_128.png, assets/icons/<id>_64.png
  python3 tools/lookdev/make_icons_m2.py
"""
import json, os, subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageFilter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
K = "/home/mm/MWM/projects/game-studio/tools/assetkit/um.sh"
os.environ.setdefault("BLENDER", "/home/mm/.local/bin/blender")
ICONS = f"{REPO}/assets/icons"
TMP = f"{REPO}/tools/lookdev/_render/icons"
ITEMS = ["maple_log", "beam", "floorboard", "cabin_kit"]
OUTLINE = (58, 38, 24)   # dark warm brown, 3 px at 256
rep = json.load(open(f"{REPO}/tools/lookdev/build_m2_report.json"))


def um(*args):
    subprocess.run([K, *args], check=True, capture_output=True)


def outline(src, dst, px=3):
    im = Image.open(src).convert("RGBA")
    pad = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    pad.alpha_composite(im, ((256 - im.width) // 2, (256 - im.height) // 2))
    a = pad.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    ring = a.filter(ImageFilter.MaxFilter(px * 2 + 1)).filter(ImageFilter.GaussianBlur(0.8))
    base = Image.new("RGBA", pad.size, OUTLINE + (0,))
    base.putalpha(ring.point(lambda v: int(v * 0.9)))
    base.alpha_composite(pad)
    base.save(dst)


def one(item):
    name = f"item_{item}"
    w = max(rep[name]["size_godot"][0], rep[name]["size_godot"][2]); h = rep[name]["size_godot"][1]
    length = int(380 * w / max(w, h * 1.2))
    out = f"{TMP}/{item}"
    um("render3d", f"{REPO}/assets/models_v3/items/{name}.glb", out, "--preset", "iso8", "--headings", "1",
       "--elevation", "35", "--forward-yaw", "-30", "--canvas", "512", "--length", str(length), "--samples", "64")
    um("sprite", "fit", f"{out}/idle_00_000.png", f"{out}/fit240.png", "--size", "240x240", "--smooth")
    outline(f"{out}/fit240.png", f"{ICONS}/{item}.png")
    um("sprite", "fit", f"{ICONS}/{item}.png", f"{ICONS}/{item}_128.png", "--size", "128x128", "--smooth")
    um("sprite", "fit", f"{ICONS}/{item}.png", f"{ICONS}/{item}_64.png", "--size", "64x64", "--smooth")
    um("sprite", "preview", f"{ICONS}/{item}_64.png", f"{out}/preview64.png", "--scale", "3")
    print("icon", item)


os.makedirs(ICONS, exist_ok=True)
with ThreadPoolExecutor(3) as ex:
    list(ex.map(one, ITEMS))
