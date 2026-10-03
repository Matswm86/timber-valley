#!/usr/bin/env bash
# Ground tiles for M3-M5: render own Blender materials, make them tile with the studio sprite tool, check seams.
#   tools/lookdev/make_ground_m345.sh grass_coast sand_beach
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
K=/home/mm/MWM/projects/game-studio/tools/assetkit/um.sh
R="$REPO/tools/lookdev/_render/ground"; O="$REPO/assets/textures/ground"
mkdir -p "$O"
/home/mm/.local/bin/blender -b --python "$REPO/tools/lookdev/make_ground_m345.py" -- "$@" | grep GROUND
for n in "$@"; do
  "$K" sprite seamless "$R/${n}_raw.png" "$O/$n.png"
  "$K" sprite tile-preview "$O/$n.png" "$R/${n}_tile3x3.png"
done
