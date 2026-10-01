#!/usr/bin/env bash
# Ground tiles: render own Blender materials, then make them tile with the studio sprite tool and check seams.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
K=/home/mm/MWM/projects/game-studio/tools/assetkit/um.sh
R="$REPO/tools/lookdev/_render/ground"; O="$REPO/assets/textures/ground"
mkdir -p "$O"
/home/mm/.local/bin/blender -b --python "$REPO/tools/lookdev/make_ground_m2.py" | grep GROUND
for n in grass_maple; do
  "$K" sprite seamless "$R/${n}_raw.png" "$O/$n.png"
  "$K" sprite tile-preview "$O/$n.png" "$R/${n}_tile3x3.png"
done
