"""Round-2 look-dev sheet: characters (Kenney -> KayKit models_v3/chars), broadleaf chop trees and small
rocks (Kenney -> round 1 -> round 2). Writes tools/lookdev/compare_round2.png.

Round-1 files are read from $ROUND1_DIR (default /home/mm/MWM/scratch/timber-valley-lookdev-round1/nature,
a copy of assets/models_v3/nature taken before the round-2 rebuild). Needs Pillow + headless Blender.
"""
import json, subprocess, os
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TMP = os.path.join(REPO, "tools", "lookdev", "_render")
R1 = os.environ.get("ROUND1_DIR", "/home/mm/MWM/scratch/timber-valley-lookdev-round1/nature")
BL = "/home/mm/.local/bin/blender"
os.makedirs(TMP, exist_ok=True)
W = 1800
CH = ["character-male-e", "character-male-a", "character-male-b", "character-male-c", "character-male-d",
      "character-male-f", "character-female-a", "character-female-b", "character-female-c", "character-female-d",
      "character-female-e", "character-female-f"]
KEN = f"{REPO}/tools/kenney_models"
V3 = f"{REPO}/assets/models_v3"
TREES = ["tree_default", "tree_oak", "tree_detailed", "tree_fat", "tree_default_dark"]
ROCKS = ["rock_smallA", "rock_smallC", "rock_smallD", "rock_largeA"]


def ch(path, action, hide=("Axe", "AxeUpgraded")):
    return {"file": path, "scale": 2.25, "action": action, "hide": list(hide)}


GROUPS = [
    ("Characters, idle (x2.25 as in game). Top: Kenney. Bottom: models_v3/chars (KayKit Adventurers, CC0)", 1.3, 2.2, 10, [
        ("BEFORE: Kenney", [ch(f"{KEN}/chars/{n}.glb", "idle") for n in CH]),
        ("AFTER: round 2", [ch(f"{V3}/chars/{n}.glb", "Idle") for n in CH]),
    ], [n.replace("character-", "") for n in CH]),
    ("Player in motion: walk, run, chop (Slice_Horizontal), chop (Chop), carry overlay pose, upgraded axe", 2.0, 2.4, 12, [
        ("BEFORE: Kenney", [ch(f"{KEN}/chars/character-male-e.glb", a, h) for a, h in (
            ("walk", ["Axe"]), ("sprint", ["Axe"]), ("attack-melee-right", []), ("attack-melee-right", []),
            ("holding-both", []), ("idle", []))]),
        ("AFTER: round 2", [ch(f"{V3}/chars/character-male-e.glb", a, h) for a, h in (
            ("Walking_A", ["Axe", "AxeUpgraded"]), ("Running_A", ["Axe", "AxeUpgraded"]), ("1H_Melee_Attack_Slice_Horizontal", ["AxeUpgraded"]),
            ("1H_Melee_Attack_Chop", ["AxeUpgraded"]), ("Carry_Pose", ["Axe", "AxeUpgraded"]), ("Idle", ["Axe"]))]),
    ], ["Walking_A", "Running_A", "Slice_Horizontal", "Attack_Chop", "Carry_Pose", "AxeUpgraded"]),
    ("Broadleaf chop trees (scale 2.5): width now at most 1.05x Kenney, full Kenney height", 2.9, 4.6, 1, [
        ("BEFORE: Kenney", [{"file": f"{KEN}/nature/{n}.glb", "scale": 2.5} for n in TREES]),
        ("ROUND 1: v3", [{"file": f"{R1}/{n}.glb", "scale": 2.5} for n in TREES]),
        ("AFTER: round 2", [{"file": f"{V3}/nature/{n}.glb", "scale": 2.5} for n in TREES]),
    ], TREES),
    ("Small rocks (scale 2.2): rounded warm-grey pebbles replace the stepped hex slabs", 2.3, 1.0, 1, [
        ("BEFORE: Kenney", [{"file": f"{KEN}/nature/{n}.glb", "scale": 2.2} for n in ROCKS]),
        ("ROUND 1: v3", [{"file": f"{R1}/{n}.glb", "scale": 2.2} for n in ROCKS]),
        ("AFTER: round 2", [{"file": f"{V3}/nature/{n}.glb", "scale": 2.2} for n in ROCKS]),
    ], ROCKS),
]
font = ImageFont.load_default(size=24)
small = ImageFont.load_default(size=15)
rows = []
for gi, (title, cell, hmax, frame, strips, labels) in enumerate(GROUPS):
    head = Image.new("RGB", (W, 42), (250, 248, 242))
    ImageDraw.Draw(head).text((12, 8), title, fill=(30, 30, 30), font=font)
    rows.append(head)
    n = len(strips[0][1])
    for si, (tag, items) in enumerate(strips):
        out = f"{TMP}/r2_g{gi}_{si}.png"
        spec = {"out": out, "cell": cell, "hmax": hmax, "px_per_m": W / (cell * n), "frame": frame,
                "samples": int(os.environ.get("SAMPLES", "48")), "items": items}
        json.dump(spec, open(f"{TMP}/r2_g{gi}_{si}.json", "w"))
        subprocess.run([BL, "-b", "--python", f"{REPO}/tools/lookdev/render_sheet.py", "--", f"{TMP}/r2_g{gi}_{si}.json"],
                       check=True, capture_output=True)
        im = Image.open(out).convert("RGB")
        im = im.resize((W, int(im.height * W / im.width)))
        dr = ImageDraw.Draw(im)
        dr.rectangle((0, 0, 170, 26), fill=(250, 248, 242))
        dr.text((8, 4), tag, fill=(30, 30, 30), font=small)
        if si == len(strips) - 1:
            cw = W / n
            for i, lbl in enumerate(labels):
                dr.rectangle((i * cw + 2, im.height - 22, i * cw + 8 + 8 * len(lbl[:18]), im.height - 2), fill=(40, 40, 40))
                dr.text((i * cw + 5, im.height - 20), lbl[:18], fill=(255, 255, 255), font=small)
        rows.append(im)
out = Image.new("RGB", (W, sum(r.height for r in rows)), (250, 248, 242))
y = 0
for r in rows:
    out.paste(r, (0, y)); y += r.height
out.save(f"{REPO}/tools/lookdev/compare_round2.png")
print("WROTE", f"{REPO}/tools/lookdev/compare_round2.png", out.size)
