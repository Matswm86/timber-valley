"""Road tile for World._road(): 512 x 512 px = the full road width (3.6 m) x 4.0 m of road, repeats along the road
(vertical axis) only. Soft grey surface (today's Color(0.5, 0.49, 0.46)), darker worn edges, faint tyre tracks and
ONE cream centre dash (1.4 m long, 0.14 m wide, same as the 40 PlaneMesh dashes it replaces).
Own work (CC0).   python3 tools/lookdev/make_road_tile.py  -> assets/textures/ground/road_tile.png
Then: um sprite tile-preview (3x3) into tools/lookdev/_render/ground/road_tile_tile3x3.png
"""
import os, subprocess
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
K = "/home/mm/MWM/projects/game-studio/tools/assetkit/um.sh"
N = 512
rng = np.random.default_rng(7)


def periodic_noise(scale_px):
    """Smooth noise that wraps in both axes (FFT low-pass of white noise)."""
    f = np.fft.fftfreq(N)
    fx, fy = np.meshgrid(f, f)
    g = np.exp(-(fx ** 2 + fy ** 2) * (scale_px ** 2) * 2.0)
    n = np.real(np.fft.ifft2(np.fft.fft2(rng.standard_normal((N, N))) * g))
    return (n - n.mean()) / (n.std() + 1e-9)


base = np.array([0.5, 0.49, 0.46])
x = (np.arange(N) + 0.5) / N * 3.6                     # metres across
X = np.tile(x, (N, 1))
col = np.ones((N, N, 3)) * base
col *= (1 + 0.035 * periodic_noise(40))[..., None]       # big soft patches
col *= (1 + 0.02 * periodic_noise(6))[..., None]         # fine grain, kept faint
edge = np.clip(1 - np.minimum(X, 3.6 - X) / 0.35, 0, 1) ** 1.5
col *= (1 - 0.12 * edge)[..., None]                      # worn darker edges
for c in (0.95, 2.65):                                   # tyre tracks
    col *= (1 - 0.045 * np.exp(-((X - c) / 0.22) ** 2))[..., None]
y = (np.arange(N) + 0.5) / N * 4.0
Y = np.tile(y[:, None], (1, N))
dash = np.clip(1 - np.maximum(np.abs(X - 1.8) - 0.07, 0) / 0.012, 0, 1) * np.clip(1 - np.maximum(np.abs(Y - 2.0) - 0.7, 0) / 0.02, 0, 1)
col = col * (1 - dash[..., None]) + np.array([0.95, 0.9, 0.7]) * dash[..., None]
out = f"{REPO}/assets/textures/ground/road_tile.png"
Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8), "RGB").save(out)
subprocess.run([K, "sprite", "tile-preview", out, f"{REPO}/tools/lookdev/_render/ground/road_tile_tile3x3.png"], check=True)
print("wrote", out)
