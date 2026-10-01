"""Render Kenney (before) vs models_v3 (after) strips at in-game scale and stack them into compare.png.
Usage: python3 tools/lookdev/make_compare.py   (calls headless Blender; needs Pillow)"""
import json, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TMP = os.path.join(REPO, "tools", "lookdev", "_render")
os.makedirs(TMP, exist_ok=True)
BL = "/home/mm/.local/bin/blender"
GROUPS = [
    ("Trees (chop forest + border), scale 2.5", 2.9, 4.6, [
        ("nature", n, 2.5) for n in ["tree_default", "tree_oak", "tree_detailed", "tree_fat", "tree_default_dark",
                                     "tree_pineTallA_detailed", "tree_pineTallB_detailed", "tree_pineTallC_detailed",
                                     "tree_pineTallD_detailed", "tree_pineRoundA", "tree_pineRoundB", "tree_pineRoundC",
                                     "tree_pineDefaultA", "tree_pineDefaultB"]]),
    ("Border-forest variants (<name>_far.glb, 170 tris, 256 px)", 2.9, 4.6, [
        ("nature", n, 2.5, "_far") for n in ["tree_default", "tree_oak", "tree_detailed", "tree_fat", "tree_default_dark",
                                     "tree_pineTallA_detailed", "tree_pineTallB_detailed", "tree_pineTallC_detailed",
                                     "tree_pineTallD_detailed", "tree_pineRoundA", "tree_pineRoundC", "tree_pineDefaultB"]]),
    ("Scatter: bushes, grass, rocks, flowers, mushrooms, stump", 1.45, 1.3, [
        ("nature", "plant_bush", 2.8), ("nature", "plant_bushDetailed", 2.6), ("nature", "grass", 2.4),
        ("nature", "grass_large", 2.4), ("nature", "grass_leafs", 2.6), ("nature", "rock_smallA", 2.2),
        ("nature", "rock_smallC", 2.2), ("nature", "rock_smallD", 2.2), ("nature", "rock_largeA", 2.4),
        ("nature", "flower_redA", 2.6), ("nature", "flower_redC", 2.4), ("nature", "flower_yellowA", 2.6),
        ("nature", "flower_yellowB", 2.4), ("nature", "mushroom_redGroup", 2.2), ("nature", "mushroom_tanGroup", 2.2),
        ("nature", "stump_roundDetailed", 2.2)]),
    ("Starting-yard props", 2.6, 1.8, [
        ("nature", "log_stackLarge", 2.2), ("nature", "campfire_logs", 3.0), ("nature", "fence_simple", 2.0),
        ("survival", "barrel", 2.4), ("survival", "box-large", 2.2), ("survival", "signpost", 2.6)]),
]
W = 1800
font = ImageFont.load_default(size=26) if hasattr(ImageFont, "load_default") else None
small = ImageFont.load_default(size=15)
rows = []
for gi, (title, cell, hmax, items) in enumerate(GROUPS):
    strips = {}
    for tag, d in (("before", "models"), ("after", "models_v3")):
        spec = {"out": f"{TMP}/g{gi}_{tag}.png", "cell": cell, "hmax": hmax, "px_per_m": W / (cell * len(items)),
                "samples": int(os.environ.get("SAMPLES", "48")),
                "items": [{"file": f"{REPO}/assets/{d}/{it[0]}/{it[1]}{it[3] if len(it) > 3 and d == 'models_v3' else ''}.glb", "scale": it[2]} for it in items]}
        json.dump(spec, open(f"{TMP}/g{gi}_{tag}.json", "w"))
        subprocess.run([BL, "-b", "--python", f"{REPO}/tools/lookdev/render_sheet.py", "--", f"{TMP}/g{gi}_{tag}.json"],
                       check=True, capture_output=True)
        strips[tag] = Image.open(spec["out"]).convert("RGB")
    cw = W / len(items)
    head = Image.new("RGB", (W, 44), (250, 248, 242)); dr = ImageDraw.Draw(head)
    dr.text((12, 8), title, fill=(30, 30, 30), font=font)
    rows.append(head)
    for tag in ("before", "after"):
        im = strips[tag].resize((W, int(strips[tag].height * W / strips[tag].width)))
        dr = ImageDraw.Draw(im)
        dr.rectangle((0, 0, 190, 30), fill=(250, 248, 242))
        dr.text((8, 4), "BEFORE: Kenney" if tag == "before" else "AFTER: models_v3", fill=(30, 30, 30), font=small)
        if tag == "after":
            for i, it in enumerate(items):
                lbl = it[1].replace("tree_", "").replace("_detailed", "").replace("mushroom_", "mush_").replace("Group", "")
                dr.text((i * cw + 4, im.height - 20), lbl[:14], fill=(255, 255, 255), font=small)
        rows.append(im)
H = sum(r.height for r in rows)
out = Image.new("RGB", (W, H), (250, 248, 242))
y = 0
for r in rows:
    out.paste(r, (0, y)); y += r.height
out.save(f"{REPO}/tools/lookdev/compare.png")
print("WROTE", f"{REPO}/tools/lookdev/compare.png", out.size)
