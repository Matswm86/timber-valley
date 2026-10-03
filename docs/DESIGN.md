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
  so they read against the grass. The player (2026-10-01) is a friendly lumberjack: brown hair under a mustard knit
  beanie, red-and-black plaid, raised brows and a smile. He is the only character in red and the only one with a cap.
  Review: `tools/lookdev/player_options.png`.
  Wiring: `assets/models_v3/chars/WIRING.md`.
- Covered 2026-10-01: the code-built sawmills, sheds, CNC, factory, lodge, Mega Saw, market, dock, truck, bridge,
  belts, palisade and road now have v3 replacements: `assets/models_v3/ASSETS_LEFTOVER.md`.

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

## 13. Maple Highlands (M2, 2026-10-01)

Asset list, anchors and swap dicts: `assets/models_v3/ASSETS_M2.md`. Review sheet: `tools/lookdev/compare_m2.png`.
References: **Stardew Valley's fall season** (take the red/orange/gold canopy mix over olive ground and the warm village
of small painted houses), and **Townscaper** (take the simple house silhouettes with one strong roof colour each, and
the build-up of a building in readable steps).
Mood: a crisp autumn hill village, warm canopies, one cool accent on everything people built.

| Role | Hex | Godot |
|---|---|---|
| 60 - V3 grass, autumn olive (ground tile mean) | `#809236` | `Color(0.502, 0.573, 0.212)` |
| 60 - maple canopy red | `#d94f2e` | `Color(0.85, 0.31, 0.18)` |
| 60 - maple canopy orange | `#ed8a2b` | `Color(0.93, 0.54, 0.17)` |
| 60 - maple canopy gold | `#f0b53a` | `Color(0.94, 0.71, 0.23)` |
| 30 - maple bark, grey | `#8a8278` | `Color(0.54, 0.51, 0.47)` |
| 30 - cut maple / beams | `#f5d9a8` | `Color(0.96, 0.85, 0.66)` |
| 30 - **region accent: highland teal** (machines, roofs, ironwork, train) | `#2a9d8f` | `Color(0.165, 0.616, 0.561)` |
| 30 - teal dark (frames, straps) | `#1c6b63` | `Color(0.11, 0.42, 0.39)` |
| 10 - cabin-kit tag red | `#db332e` | `Color(0.86, 0.2, 0.18)` |
| 10 - village walls: cream / ochre / barn red / white | `#f7edd6` / `#edc26e` / `#bd382b` / `#f7f2e6` | |

Why teal: it is complementary to the red/orange canopies, so machines stand out from the forest. It is clear of Home's
orange/green, Birch Bend's river blue `#408ac2` (33 deg of hue away) and purple.
Contrast (my calc): teal and the olive grass have the same luminance (1.0:1), so they separate by hue only. Teal against
the dirt plazas is 1.5:1, and the yellow trims, cream panels and baked AO base outline every teal object.

Do / don't:
- Do keep teal for things people built (machines, roofs, train, gate, office). Trees and ground stay warm.
- Do put every teal machine on a dirt plaza. Never stand a teal body flat on bare olive grass.
- Do keep the maple trunk short and grey under a round crown. The grey trunk is what tells a maple from the V1 tree at a distance.
- Do raise build sites stage by stage with the shipped `stageN` nodes; never swap in a whole house at once.
- Don't give houses colours from another valley's accent (no river-blue roofs). The village uses cream, ochre, barn red,
  white and teal only.
- Don't use the GDD's "red frame" for the beam saw. Red disappears against red canopies, so it is teal like the other V3 machines.

## 14. Redwood Coast (M3, 2026-10-01)

Asset list, anchors and swap dicts: `assets/models_v3/ASSETS_M3.md`. Review sheet: `tools/lookdev/compare_m3.png`.
References: **Firewatch** (take the tall red-brown trunks under dark crowns, and how small the people and buildings feel
under them), and **Alba: A Wildlife Adventure** (take the bright working harbour: white boats and walls, a red-and-white
lighthouse, warm sand).
Mood: a busy timber harbour on a cool coast, warm trunks and sand, navy on everything that floats or works.

| Role | Hex | Godot |
|---|---|---|
| 60 - V4 coastal grass (ground tile mean) | `#6e9546` | `Color(0.431, 0.584, 0.275)` |
| 60 - sand (paths, plazas, shore) | `#e0cb9e` | `Color(0.878, 0.796, 0.62)` |
| 60 - redwood canopy deep / light | `#265c38` / `#357345` | `Color(0.15, 0.36, 0.22)` / `Color(0.21, 0.45, 0.27)` |
| 30 - redwood bark, red-brown | `#8f452b` | `Color(0.56, 0.27, 0.17)` |
| 30 - timber heartwood | `#db8061` | `Color(0.86, 0.5, 0.38)` |
| 30 - deckboard | `#784d36` | `Color(0.47, 0.3, 0.21)` |
| 30 - **region accent: harbour navy** (machines, roofs, hulls, ironwork) | `#1e3a64` | `Color(0.118, 0.227, 0.392)` |
| 30 - navy dark (frames, cabs) | `#13253f` | `Color(0.075, 0.145, 0.255)` |
| 10 - signal red (lighthouse stripes, buoys, boot-top, warning lamps) | `#cc3333` | `Color(0.8, 0.2, 0.2)` |
| 10 - hull white / sail | `#f7f5ed` / `#f5edd6` | |

Why navy: it is the one cool colour in a warm valley (red trunks, sand, heartwood), so every machine and hull separates
from the forest by temperature and value. It is clear of purple, of Home's orange/green and of Maple's teal. It is a blue,
so it was checked against Birch Bend's river blue: navy is much darker, 3.05:1 apart (my calc), and the two valleys are
never on screen together (V2 is far west, V4 east of the road).
Contrast (my calc): navy on the coastal grass 3.28:1, on sand 7.16:1; signal red on hull white 4.71:1; redwood canopy on
the grass 2.27:1 (the trunk and the baked AO base carry the edge).

Do / don't:
- Do keep navy for things people built (machines, roofs, hulls, ironwork, the skidder and forklift). Trees and ground
  stay warm.
- Do keep signal red to the 10%: lighthouse stripes, buoys, the hull boot-top, beacons and crossing lamps. A red machine
  body would merge with the red trunks.
- Do stand machines on sand plazas (7.2:1) rather than on grass (3.3:1).
- Do keep the redwood trunk bare and visible for its lower third. The red-brown column under a dark crown is what tells a
  redwood from the V1 pine at camera distance.
- Do raise the ship and the Lighthouse with the shipped `stageN` nodes; the ship's stage 2 is an open hull on purpose
  (the deck arrives with stage 3).
- Don't scale redwoods past 1.6x: the widest (A) is then 0.78 units, at the 0.79 path/arrow limit. They are 7-9 m tall
  at game scale; keep groves at least 4 m from paths on the camera side (+Z) so a trunk never hides the player.
- Don't use river blue or teal anywhere in V4, and no blue-grey rock (warm grey `#948a7d` only).

## 15. Frost Peaks (M4, 2026-10-03)

Asset list, anchors and swap dicts: `assets/models_v3/ASSETS_M4.md`. Review sheet: `tools/lookdev/compare_m4.png`.
References: **A Short Hike** (take the snowy peak with a few warm, lived-in buildings and simple tiered firs), and
**Norwegian and Swiss ski villages** (take the red-painted woodwork, the red cable car and train against white snow).
Mood: a bright cold mountain workshop town, white snow, blue-green firs, red on everything people built, and one warm
orange glow from the kilns.

| Role | Hex | Godot |
|---|---|---|
| 60 - V5 snow (ground tile mean) | `#e3ebf5` | `Color(0.89, 0.922, 0.961)` |
| 60 - packed snow (paths, plazas) | `#cdd0d2` | `Color(0.804, 0.816, 0.824)` |
| 60 - frost fir, deep / light | `#2f5e4f` / `#407561` | `Color(0.18, 0.37, 0.31)` / `Color(0.25, 0.46, 0.38)` |
| 30 - **region accent: alpine red** (machines, roofs, cable car, train, ironwork) | `#c8283a` | `Color(0.784, 0.157, 0.227)` |
| 30 - alpine red dark (frames, trims) | `#8c1c29` | `Color(0.55, 0.11, 0.16)` |
| 30 - log walls | `#9e6b45` | `Color(0.62, 0.42, 0.27)` |
| 30 - roof and cap snow | `#f2f6fc` | `Color(0.95, 0.965, 0.99)` |
| 10 - dry lumber, warm orange | `#e89e52` | `Color(0.91, 0.62, 0.32)` |
| 10 - kiln glow (emissive, gameplay) | `#ff7a1f` | `Color(1.0, 0.48, 0.12)` |

Why alpine red: snow needs a dark, saturated accent to hold a silhouette, and red is the classic mountain-village colour.
It is clear of purple, of Home's orange (32 deg of hue away and much darker), of Maple's teal and of the Redwood navy.
Redwood uses red only as a 10% pop (lighthouse, buoys); here red is the 30% accent and the two valleys are never on screen
together.
Contrast (my calc): alpine red on snow 4.57:1, on packed snow 3.55:1; fir on snow 6.17:1; icon outline on snow 11.9:1.

Do / don't:
- Do keep red for things people built. Trees, ground and snow stay cool.
- Do stop roof snow short of the eaves: a red band must outline every roof, or a white roof vanishes into white ground
  from the 52 deg camera (checked on the review sheet).
- Do keep the kiln glow the only orange light in the valley; it tells the player which kiln is baking.
- Do keep the fir's snow collars on every tier. A plain dark cone reads as the V1 pine.
- Don't put green grass tufts or flowers on snow; use snow drifts, snow bushes and rocks.
- Don't make machines white or cream-bodied; cream is for trims and bands only.

## 16. Grand Timber Station (M5, 2026-10-03)

Asset list, anchors and swap dicts: `assets/models_v3/ASSETS_M5.md`. Review sheet: `tools/lookdev/compare_m5.png`.
References: **St Pancras / York station's arched train sheds** (take the long vault over the track, the clock over the
entrance and the brass details), and **Mini Metro's line colours** (take one clear colour per line, here one per valley,
on the platform slots and the roof pennants).
Mood: a grand, warm Victorian timber station that gathers every valley; it should feel like the finish line.

| Role | Hex | Godot |
|---|---|---|
| 60 - cream sandstone (walls) | `#e6d6b8` | `Color(0.9, 0.84, 0.72)` |
| 60 - station paving (plaza tile mean) | `#d1bd9f` | `Color(0.82, 0.741, 0.624)` |
| 30 - station maroon (roofs, loco, coaches, lamps) | `#6e2430` | `Color(0.43, 0.14, 0.19)` |
| 30 - darker sandstone (plinths, piers) | `#b8a385` | `Color(0.72, 0.64, 0.52)` |
| 10 - **accent: station brass** (clock, trims, ribs, finials, loco bands) | `#c99a2e` | `Color(0.788, 0.604, 0.18)` |
| 10 - valley colours on the platform slots and pennants | V1 `#ff731f`, V2 `#408ac2`, V3 `#2a9d8f`, V4 `#1e3a64`, V5 `#c8283a` | |

Why brass and maroon: gold reads as "the finish", and brass is the classic railway trim. Maroon holds the roof against
the sky and the forest; it is a dark red (hue 352), well away from purple. The Station is the only place where all five
valley accents appear together, and only as small flags and sign boards.
Contrast (my calc): maroon on the paving 5.87:1; brass on the paving 1.41:1 and on the V1 grass 1.45:1, so brass is
only ever a trim on sandstone or maroon, never a body colour on its own.

Do / don't:
- Do keep brass to trims, clocks, ribs and finials. A brass body would vanish on the paving.
- Do keep the walk-through arch open (x -1.4..1.4): the player walks through the station between Home and the Highlands.
- Do give each platform slot its own valley's accent; never paint them all brass.
- Don't add more valley colours to the station building than the five pennants.
- Don't use the station maroon or brass in any valley; they belong to the finale.
