"""Player face review sheet -> tools/lookdev/player_options.png. Needs the renders from render_heads.py:
  blender -b --python tools/lookdev/render_heads.py -- tools/lookdev/_render/player/opt cur=<old male-e> a1=... a2=... a3=... a4=...
  blender -b --python tools/lookdev/render_heads.py -- tools/lookdev/_render/player/line male-e=... (all 12 variants)
  python3 tools/lookdev/make_player_options.py"""
from PIL import Image, ImageDraw, ImageFont
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
R = "_render/player"
fd = "../../assets/fonts/"; f = [x for x in os.listdir(fd) if x.endswith((".ttf", ".otf"))][0]
F = ImageFont.truetype(fd + f, 24); S = ImageFont.truetype(fd + f, 17)
im = Image.new("RGB", (2000, 1330), (250, 246, 236)); d = ImageDraw.Draw(im)
d.text((12, 10), "Player candidates (close-up + game camera 52 deg). Shipped: candidate 2 -> character-male-e.glb", fill=(40, 30, 20), font=F)
labels = [("cur", "OLD male-e: bald, ginger, heavy brows"), ("a1", "alt-1: Knight, brown hair, red plaid"),
          ("a2", "2 SHIPPED: mustard beanie, red plaid"), ("a3", "alt-3: Mage, dark hair, red plaid"), ("a4", "alt-4: Barbarian, red beanie, brown beard")]
for i, (k, t) in enumerate(labels):
    x = i * 400
    im.paste(Image.open(f"{R}/opt/{k}_face.png").convert("RGB"), (x, 50))
    im.paste(Image.open(f"{R}/opt/{k}_game.png").convert("RGB").crop((50, 50, 250, 250)).resize((300, 300)), (x + 50, 455))
    d.rectangle((x, 760, x + 398, 790), fill=(30, 30, 30) if k != "a2" else (200, 60, 40)); d.text((x + 6, 764), t, fill=(255, 255, 255), font=S)
d.text((12, 805), "New player among every worker / customer variant (game camera). Only the player wears red plaid and a cap.", fill=(40, 30, 20), font=F)
names = ["male-e", "male-a", "male-b", "male-c", "male-d", "male-f", "female-a", "female-b", "female-c", "female-d", "female-e", "female-f"]
for i, n in enumerate(names):
    x = i * 166 + 8
    im.paste(Image.open(f"{R}/line/{n}_game.png").convert("RGB").crop((60, 40, 240, 260)).resize((160, 196)), (x, 850))
    d.text((x + 4, 1050), ("PLAYER " if n == "male-e" else "") + n, fill=(40, 30, 20), font=S)
    im.paste(Image.open(f"{R}/line/{n}_face.png").convert("RGB").resize((160, 160)), (x, 1080))
d.text((12, 1250), "Face edit: brows thinner, raised 2.5 cm, inner ends higher; the skin-coloured mouth strip became a dark smile (build_chars.py, own work).", fill=(40, 30, 20), font=S)
d.text((12, 1280), "female-a recoloured red -> teal/cream and female-f hood mustard -> cream, so no worker or customer reads like the player.", fill=(40, 30, 20), font=S)
im.save("player_options.png", optimize=True)
print("wrote player_options.png", im.size)
