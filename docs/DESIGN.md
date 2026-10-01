# Timber Valley - design spec

Sections 1-9 of the studio template are not filled in yet. This file holds the **look-dev**
part (section 10 tier + section 11 look-dev test), written 2026-09-30 on branch `lookdev-test`.

## 10. Visual tier

**Premium stylized 3D.** Soft, rounded, gradient-lit models with baked contact shadows. No voxel
or block look. References:
- **Game District idle/arcade titles** (e.g. their lumber and pizza idle games): take the round
  blob trees, the dark-bottom/light-top gradient on every surface, and the soft dark ring where
  objects meet the ground.
- **KayKit Forest Nature Pack** (the source of most new nature models): take the gradient-atlas
  approach, where one colour ramp per material is the whole texture and there is no fine detail.

Mood: a sunny, soft toy valley. Warm light from above, cool shadows, nothing sharp.

## 11. Look-dev test: starting area (models_v3)

### What "Game District-like" means here, concretely
1. **Silhouettes are round.** No visible 90-degree edge on anything bigger than a hand. Bevels
   are about 10-20% of the part's size. Trees are blobs or stacked soft cones, not cubes or boxy pyramids.
2. **Every surface has a vertical gradient.** It runs from about 0.8x brightness at the bottom
   to 1.0x at the top (baked in the texture) and on top of the per-material colour ramp.
3. **AO ships inside the asset.** Crevices and ground contact go down to about 45% brightness
   and never to black. It is baked with a ground plane, so every prop sits in its own soft shadow.
4. **Colour, not detail.** Textures are 128-512 px colour gradients. The only surface detail is
   large and soft (tree rings, bark streaks, plank grain).
5. **Few big shapes.** A log pile is 9 fat logs, not 30 thin ones.

### Palette (60 / 30 / 10)
| Role | Hex | Godot |
|---|---|---|
| 60 - canopy light (top of ramp) | `#89c43f` | `Color(0.537, 0.769, 0.247)` |
| 60 - canopy mid | `#46973b` | `Color(0.275, 0.592, 0.231)` |
| 60 - canopy dark (bottom of ramp) | `#036a37` | `Color(0.012, 0.416, 0.216)` |
| 60 - pine green | `#409454` | `Color(0.25, 0.58, 0.33)` |
| 30 - bark / trunk | `#c36532` | `Color(0.765, 0.396, 0.196)` |
| 30 - log side | `#9e663d` | `Color(0.62, 0.40, 0.24)` |
| 30 - cut wood / log end | `#edc285` | `Color(0.93, 0.76, 0.52)` |
| 30 - stone (warm grey; round 2, was blue-grey `#aab8be` and went navy in shadow) | `#998e80` | `Color(0.60, 0.555, 0.50)` |
| 10 - flower red (play accent) | `#ed544d` | `Color(0.93, 0.33, 0.30)` |
| 10 - flower yellow | `#fad640` | `Color(0.98, 0.84, 0.25)` |
| sky top (existing World.gd) | `#519ef2` | `Color(0.32, 0.62, 0.95)` |

### Lighting direction
The key light stays where World.gd has it: `DirectionalLight3D` at `rotation_degrees = (-52, -38, 0)`,
warm `Color(1.0, 0.93, 0.8)`. The baked textures hold only direction-free terms (AO and the
vertical gradient), so the sun can move without the assets disagreeing with it.

### Godot settings I recommend (not applied; dev's call)
- **Swap paths:** `res://assets/models/<kit>/<name>.glb` -> `res://assets/models_v3/<kit>/<name>.glb`.
  The file names, scale and pivots are compatible: trees and scatter keep the trunk/source origin
  at (0,0,0); props match the Kenney footprint centre and sit at y = 0, not Kenney's -0.05.
  Forward is the same as Kenney (fence along X, crate long along Z).
- **Border forest must use `<name>_far.glb` AND be chunked.** Today `_border_forest` puts
  about 2,970 trees into 12 MultiMeshes. Godot culls a MultiMesh only as a whole, so all of them
  render every frame: about 530k tris with Kenney (my calc). The full v3 trees would push that to
  about 1.8M, and `_far` (170 tris) brings it back to about 505k, which is still 5x the 100k budget.
  Split each kind into about 16 m x 16 m chunks (one `MultiMeshInstance3D` per chunk) and set
  `visibility_range_end = 60`. Frustum culling then drops most chunks, since the portrait camera
  sees roughly 20 x 30 m. Use the full models only for `ChopTree` (close to the camera, a few dozen at most).
- **Scatter (`_scatter_deco`)** goes from about 127k to about 192k tris with v3 (my calc), all in
  single MultiMeshes. Chunk it the same way, or cut `grass`/`grass_large` counts by a third. The
  new clumps are bigger and read at lower density.
- **Shadows:** keep one shadow-casting sun. Lower `directional_shadow_max_distance` from 42 to about
  30 to sharpen the near cascade, and raise `shadow_blur` from 1.5 to about 2.0 for softer edges.
  Keep `cast_shadow = OFF` on grass, flowers and small rocks: the baked contact AO replaces their shadows.
- **Fill light:** the second `DirectionalLight3D` (fill) can go. Raise `ambient_light_energy` from
  0.75 to about 0.9 instead, because the baked AO now gives the form that the fill was faking. One fewer light pass.
- **Environment:** keep ACES, glow and fog. The KayKit ramps are already saturated, so try
  `adjustment_saturation` 1.1 instead of 1.22 and judge it on a device screenshot.
- **SSAO / SSIL / SDFGI:** not available in the Mobile renderer and not needed, because AO is baked per asset.
- **LightmapGI: not viable here.** It needs static geometry with UV2, baked in the editor into a
  saved scene. World.gd builds the whole valley at runtime, unlocks spawn buildings during
  play, trees fall and regrow, and nearly all nature is MultiMesh, which LightmapGI does not bake.
  Runtime baking is not available in exported Android builds. Per-asset baked AO plus the one
  real-time sun shadow is the right trade on a phone.

### Do / don't
- Do run new nature/prop models through `tools/lookdev/build_v3.py`, so they get the same gradient and AO bake.
- Do keep one mesh and one material per GLB, because `World._first_mesh` reads only the first mesh.
- Don't mix in photoreal or alpha-card foliage (e.g. the Quaternius Stylized Nature MegaKit
  leaf cards): overdraw on phones and a different style.
- Don't reintroduce flat Kenney colours next to v3 models in the same shot.
- Don't use blue-grey stone. Under the blue sky ambient it goes navy in shadow (round-1 rocks measured
  saturation 0.19 at hue 210 in full shadow; the warm-grey pebbles measure 0.04, near neutral, my calc).
- Don't let chop-forest trees get wider than 1.05x the Kenney footprint. Wider canopies hide the path and
  the guide arrow from the portrait camera.
- Characters are KayKit Adventurers (round, soft), recoloured per role in workwear colours; no greens,
  so they read against the grass. The player is the only red-shirt, bald, ginger-bearded character.
  Wiring: `assets/models_v3/chars/WIRING.md`.
- Not yet covered: the code-built sawmill, sheds and ground (BoxMesh/CylinderMesh in World.gd and
  Shapes.gd). They are the next biggest "prototype" tell once the nature is swapped.

## 12. Birch Bend (M1, 2026-10-01)

Asset list, anchors and swap dicts: `assets/models_v3/ASSETS_M1.md`. Review sheet: `tools/lookdev/compare_m1.png`.

| Role | Hex | Godot |
|---|---|---|
| 60 - V2 grass (ground tile mean) | `#74ae39` | `Color(0.455, 0.682, 0.224)` |
| 60 - birch canopy | `#a3d157` | `Color(0.64, 0.82, 0.34)` |
| 30 - birch bark (dark dashes `#433d3b`) | `#f0ebde` | `Color(0.94, 0.92, 0.87)` |
| 30 - machine and roof accent, river blue | `#408ac2` | `Color(0.25, 0.54, 0.76)` |
| 10 - boathouse red (Norwegian naust) | `#bd382b` | `Color(0.74, 0.22, 0.17)` |
| 10 - canoe red | `#db573d` | `Color(0.86, 0.34, 0.24)` |

Do / don't:
- Do keep river blue as the V2 machine colour (V1 is orange/green). It tells the player which valley they are in.
- Do keep the birch trunk white and visible under the canopy. It is how a birch reads from the camera.
- Don't give open workshops a full roof. The camera looks down at about 52 degrees, so a roof hides the product.
- Border forest: use the imposter atlas (ASSETS_M1.md section 5). The `_far` meshes are the fallback.
