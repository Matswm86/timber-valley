"""WCAG contrast (my calc) for the M3-M5 accents against their grounds, plus ground-tile means.
  python3 tools/lookdev/contrast_m345.py"""
import os
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def lum(rgb):
    c = [x / 255 for x in rgb]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def mean(name):
    a = np.asarray(Image.open(f"{REPO}/assets/textures/ground/{name}.png").convert("RGB")).reshape(-1, 3)
    m = tuple(int(round(x)) for x in a.mean(0))
    return m, a.std(0).round(1)


grounds = {}
for g in ("grass_coast", "sand_beach", "snow_frost", "snow_packed", "station_paving", "grass_v1", "grass_maple", "dirt_path"):
    if os.path.exists(f"{REPO}/assets/textures/ground/{g}.png"):
        m, s = mean(g)
        grounds[g] = m
        print(f"ground {g}: mean #{m[0]:02x}{m[1]:02x}{m[2]:02x} std {s}")
pairs = [("harbour navy #1e3a64", "#1e3a64", "grass_coast"), ("harbour navy", "#1e3a64", "sand_beach"),
         ("signal red #cc3333", "#cc3333", "grass_coast"), ("signal red", "#cc3333", "#1e3a64"),
         ("signal red", "#cc3333", "#f7f5ed"), ("redwood bark #8f452b", "#8f452b", "grass_coast"),
         ("redwood canopy #265c38", "#265c38", "grass_coast"),
         ("alpine red #c8283a", "#c8283a", "snow_frost"), ("alpine red", "#c8283a", "snow_packed"),
         ("frost fir #2f5e4e", "#2f5e4e", "snow_frost"), ("dry lumber #e8a25a", "#e8a25a", "snow_frost"),
         ("station brass #c99a2e", "#c99a2e", "station_paving"), ("station brass", "#c99a2e", "grass_v1"),
         ("station maroon #6e2430", "#6e2430", "station_paving"),
         ("icon outline #3a2618", "#3a2618", "#fff7e6"), ("icon outline", "#3a2618", "grass_coast"),
         ("icon outline", "#3a2618", "snow_frost"), ("navy vs river blue #408ac2", "#1e3a64", "#408ac2")]
for label, a, b in pairs:
    bb = grounds.get(b) if not b.startswith("#") else hx(b)
    if bb is None:
        continue
    print(f"{label} vs {b}: {ratio(hx(a), bb):.2f}:1")
