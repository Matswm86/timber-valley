# M1 assets: Birch Bend, item models, icons, ground tiles, border imposters

Built 2026-10-01 on branch `lookdev-test`. Review sheet: `tools/lookdev/compare_m1.png`. Licences: `SOURCES.md`
(all own work, CC0). Rebuild commands are listed at the end.

Every GLB has one mesh, one material and one embedded texture (albedo x height gradient x baked AO, contact
shadow included), like the rest of models_v3. Axes are the same as Kenney/models_v3: Godot +Z points toward the
camera ("front"), +Y is up.

Two unit conventions:
- **kenney units** (trees and nature props): same as `models_v3/nature`, so World scales them by about 2.2-3.6.
- **world units** (machines, buildings, items): metres. Use them at scale 1.0.

## 1. Birch Bend models: `res://assets/models_v3/birch/`

| File | Use | Units | Tris | Tex | Size x/y/z in Godot (m or units) | Anchors (Godot, model local) |
|---|---|---|---:|---:|---|---|
| `tree_birchA.glb` | Birch chop tree, single trunk | kenney | 693 | 512 | 0.66 / 1.85 / 0.60 | trunk base at origin |
| `tree_birchB.glb` | Birch chop tree, tall and slim | kenney | 670 | 512 | 0.54 / 2.02 / 0.51 | trunk base at origin |
| `tree_birchC.glb` | Birch chop tree, twin trunk | kenney | 694 | 512 | 0.77 / 1.78 / 0.70 | trunk base at origin |
| `tree_birchA_far.glb` | Border forest (mesh fallback) | kenney | 173 | 256 | 0.55 / 1.77 / 0.53 | as above |
| `tree_birchB_far.glb` | Border forest (mesh fallback) | kenney | 173 | 256 | 0.46 / 1.98 / 0.46 | as above |
| `tree_birchC_far.glb` | Border forest (mesh fallback) | kenney | 180 | 256 | 0.67 / 1.66 / 0.57 | as above |
| `stump_birch.glb` | Stump left after chopping a birch (replaces `stump_roundDetailed` for kind "birch") | kenney | 356 | 256 | 0.46 / 0.22 / 0.46 | scale 2.2 like today |
| `log_stack_birch.glb` | Yard prop by the lathe and the forester camp | kenney | 936 | 256 | 0.60 / 0.41 / 0.66 | sits on y = 0 |
| `reeds.glb` | Cattail clumps on the river banks and by the boathouse | kenney | 198 | 128 | 0.25 / 0.64 / 0.17 | double-sided; `cast_shadow = OFF` |
| `lilypads.glb` | On the river / pond surface | kenney | 432 | 128 | 0.47 / 0.06 / 0.39 | place at water y (river mesh y = 0.06); shadow OFF |
| `veneer_lathe.glb` | Veneer Lathe body (`r2_lathe`) | world | 1552 | 512 | 3.0 / 1.6 / 1.95 | log spin axis along X at (0, 0.98, 0); peeled sheet slides to +Z onto a tray at z +0.78; motor behind at z -0.72 |
| `veneer_lathe_log.glb` | The spinning birch log (separate so it can rotate) | world | 164 | 256 | 1.5 / 0.48 / 0.48 | pivot = log centre; put at (0, 0.98, 0), spin around X |
| `plywood_press.glb` | Plywood Press body (`r2_press`, `r2_press2`) | world | 1428 | 512 | 2.2 / 3.18 / 1.67 | bed top y 0.60, plywood on the bed up to y 0.79; crown underside y 2.27 |
| `plywood_press_plate.glb` | Moving press plate + piston rod (add to `Machine.arms` or tween it) | world | 152 | 128 | 1.45 / 1.04 / 1.05 | pivot = top of the plate; tween y 1.35 (up) to 0.93 (pressing) |
| `boat_workshop.glb` | Boat Workshop body (`r2_boatshop`) | world | 1324 | 512 | 4.5 / 2.85 / 3.0 | open front (+Z); lean-to roof over the back 60% only so the camera sees the canoe on the trestles at z +0.6 |
| `riverside_office.glb` | Riverside Office (`r2_office`) | world | 1556 | 512 | 3.9 / 3.15 / 3.76 | door + porch at +Z; yellow sign board face at (0, 2.05, 1.33): put a Label3D "OFFICE" at z 1.40 |
| `barge.glb` | River barge for `r2_barge` (the generalised TruckDock vehicle) | world | 1796 | 512 | 2.8 / 2.5 / 6.05 | waterline at y 0 (place at river water y); deck top y 0.49; bow at -Z (it sails north); free cargo deck x -1.1..1.1, z -2.7..+1.6 (6 canoes = 3 across x 2 long); wheelhouse at z +2.25 |
| `barge_landing.glb` | Pier for the barge export pile (`r2_barge`) | world | 708 | 512 | 4.22 / 2.24 / 5.0 | deck top y 0.40; river edge is +X (bollards at x 1.85); same 4.2 x 5.0 footprint as the TruckDock slab |
| `flume_straight.glb` | Log flume, 2 m segment (`r2_flume`) | world | 308 | 256 | 2.0 / 1.12 / 1.09 | runs along X from -1.0 to +1.0; floor top y 0.75; inner walls at z +-0.30; wall top y 1.09; water plane y 0.95, 2.0 x 0.6 |
| `flume_chute.glb` | Flume start: hopper = the birch_log DROP square | world | 652 | 256 | 2.5 / 1.47 / 1.66 | hopper centre at x -0.7 (zone centre), yellow rim y 1.35; trough exits at x +1.0, so the first straight goes at x +2.0 |
| `flume_end.glb` | Flume end: spout onto the lathe input pile | world | 440 | 256 | 1.93 / 1.12 / 1.09 | trough from x -1.0, spout tips down to about (1.0, 0.6, 0); centre = last straight + 2.0 |
| `boathouse.glb` | Boathouse landmark (`r2_boathouse`, money only) | world | 1448 | 512 | 7.0 / 5.51 / 11.05 | house 6.0 x 8.0 on a 6.4 x 8.4 stone plinth, centred on the origin; boat door + jetty with a canoe toward +Z (jetty reaches z +6.6); blocker (6.4, 3.0, 8.4) |

Budgets met (my count from `tools/lookdev/build_m1_report.json`): chop trees 670-694 tris (limit 700), `_far`
173-180 (target about 170), every prop and building at most 1,796 (limit 2,000).

Notes for the builder:
- **Chop trees:** add kind "birch" with `["tree_birchA", "tree_birchB", "tree_birchC"]`, scale
  `randf_range(2.3, 2.8)` like the broadleaf trees, and `stump_birch` for the stump. The widest (C) is 0.77
  units, within the 1.05x Kenney limit (0.79), so the path and guide arrow stay visible.
- **Machines:** the bodies fill the space between the `Machine` input pile (x -2.7) and output pile (x +2.7).
  Input is on -X and output on +X, as in V1. Add them with `m.add_model(path, Vector3.ZERO, 1.0)`.
- The Birch Bend accent is **river blue** `#408ac2` on machines and roofs. V1 uses orange, green and red.
  Keep it, because it shows the player which valley they are in.

## 2. Item models: `res://assets/models_v3/items/` (world units, scale 1.0)

These are drop-in replacements for `Items.DEFS`. The sizes match today's in-game sizes (Kenney furniture x its
DEFS scale). log and plank were procedural before; they are now GLBs, so drop their `"proc"` key. Swap by
editing the one dict:

```gdscript
const DEFS := {
	"log": {"path": "res://assets/models_v3/items/item_log.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.31, "cell": Vector2(1.05, 0.36)},
	"plank": {"path": "res://assets/models_v3/items/item_plank.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.11, "cell": Vector2(1.0, 0.4)},
	"chair": {"path": "res://assets/models_v3/items/item_chair.glb", "scale": 1.0, "rot": Vector3(0, 180, 0), "layer": 0.36, "cell": Vector2(0.5, 0.5)},
	"table": {"path": "res://assets/models_v3/items/item_table.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.36, "cell": Vector2(0.95, 0.55)},
	"bookcase": {"path": "res://assets/models_v3/items/item_bookcase.glb", "scale": 1.0, "rot": Vector3(-90, 0, 0), "layer": 0.34, "cell": Vector2(0.6, 1.15)},
	"birch_log": {"path": "res://assets/models_v3/items/item_birch_log.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.31, "cell": Vector2(1.05, 0.36)},
	"veneer": {"path": "res://assets/models_v3/items/item_veneer.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.05, "cell": Vector2(1.0, 0.5)},
	"plywood": {"path": "res://assets/models_v3/items/item_plywood.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.12, "cell": Vector2(1.0, 0.6)},
	"canoe": {"path": "res://assets/models_v3/items/item_canoe.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.35, "cell": Vector2(0.7, 2.0)},
	"coin": {"path": "", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.075, "cell": Vector2(0.36, 0.36)},
}
```

| File | Item id | Tris | Tex | Size x/y/z (m) |
|---|---|---:|---:|---|
| `item_log.glb` | log | 140 | 256 | 0.95 / 0.32 / 0.32 (along X) |
| `item_plank.glb` | plank | 108 | 256 | 0.95 / 0.10 / 0.34 |
| `item_chair.glb` | chair | 252 | 256 | 0.38 / 0.89 / 0.37 (back at -Z before the 180 deg DEFS turn, like Kenney) |
| `item_table.glb` | table | 220 | 256 | 0.88 / 0.34 / 0.47 |
| `item_bookcase.glb` | bookcase | 376 | 256 | 0.51 / 1.06 / 0.31 (shelves face +Z, so they face up after the -90 deg DEFS turn) |
| `item_birch_log.glb` | birch_log | 140 | 256 | 0.95 / 0.32 / 0.32 |
| `item_veneer.glb` | veneer | 128 | 128 | 0.91 / 0.09 / 0.48 (thin sheet, peeled end curls up 7 cm; curls nest when stacked) |
| `item_plywood.glb` | plywood | 108 | 256 | 0.95 / 0.11 / 0.56 (layered edge) |
| `item_canoe.glb` | canoe | 548 | 256 | 0.69 / 0.40 / 2.00 (along Z; upswept ends rise 5 cm above the 0.35 layer and are hidden by the canoe above) |

Items are kept light because piles hold up to 48 of them. The heaviest full pile is 48 bookcases = 18k tris
(my calc). Kenney chair/table/bookcase used flat colours; these are baked like the rest of v3.

## 3. Icons: `res://assets/icons/`

Rendered from the item GLBs above with one camera: `um render3d --preset iso8 --headings 1 --elevation 35
--forward-yaw -30`. Then `um sprite fit --smooth`, with a 3 px dark-brown outline `#3a2618` so each icon reads
on both the cream pill and the green HUD. Sizes: `<id>.png` 256 master, `<id>_128.png` for shop buttons (96 px
tall today), `<id>_64.png` for the HUD. The HUD has no item icons yet; the nearest existing size is the coin at
58 px, so draw the 64 px file in a 58-64 px `TextureRect` (`expand_mode = EXPAND_IGNORE_SIZE`,
`stretch_mode = STRETCH_KEEP_ASPECT_CENTERED`). All nine were checked at 48 px on dark green and still read.

```gdscript
const ICONS := {
	"log": "res://assets/icons/log_64.png",
	"plank": "res://assets/icons/plank_64.png",
	"chair": "res://assets/icons/chair_64.png",
	"table": "res://assets/icons/table_64.png",
	"bookcase": "res://assets/icons/bookcase_64.png",
	"birch_log": "res://assets/icons/birch_log_64.png",
	"veneer": "res://assets/icons/veneer_64.png",
	"plywood": "res://assets/icons/plywood_64.png",
	"canoe": "res://assets/icons/canoe_64.png",
}
```
Replace `_64` with `_128` or nothing for the larger files. Contrast of the outline (my calc): 13.4:1 on the HUD cream
`Color(1.0, 0.97, 0.9)`, 4.8:1 on the HUD green `Color(0.33, 0.66, 0.34)`, and 5.3:1 on the Birch Bend grass.
The coin has no icon because the HUD draws it (CoinIcon.gd).

## 4. Ground tiles: `res://assets/textures/ground/`

| File | Use | Mean colour (my calc) |
|---|---|---|
| `grass_v1.png` | V1 meadow (matches today's `grass_a`/`grass_b` mix) | `#529427` |
| `grass_birch.png` | V2 Birch Bend "lighter spring green", with a few pale fallen birch leaves | `#74ae39` |
| `dirt_path.png` | Paths and plazas in both valleys (matches today's `dirt`/`dirt_dark`) | `#d0ab74` |

512 x 512 RGB, one tile = **4 x 4 m**. They are rendered from an own Blender material whose noise and Voronoi run on a
4D torus, so the tile repeats exactly. They then went through `um sprite seamless` and were checked with
`um sprite tile-preview` (edge-wrap difference is 0.9, the same as neighbouring pixels inside the tile, my calc).
The contrast is kept low (std 4-7 of 255): large soft patches and tufts, no photographic grain.
Import them with mipmaps on and VRAM compression.

**What `ground.gdshader` expects today:** it has no albedo texture. The colour comes from the uniforms
`grass_a`, `grass_b`, `dirt`, `dirt_dark` and `shore`, mixed by `noise_tex` (large patches, `p * 0.018`) and
`detail_tex` (fine, `p * 0.21`). Both are `NoiseTexture2D` made in `World._ground()`. Paths and plazas come
from the `paths[32]` / `plazas[24]` uniforms. To plug the tiles in (about 6 lines):

```glsl
uniform sampler2D grass_tex : source_color, repeat_enable, filter_linear_mipmap;
uniform sampler2D dirt_tex : source_color, repeat_enable, filter_linear_mipmap;
uniform float tile_m = 4.0;
// in fragment(), replace the two grass lines and the dirt_col line:
vec3 grass = texture(grass_tex, p / tile_m).rgb * mix(0.94, 1.06, smoothstep(0.35, 0.7, n));
vec3 dirt_col = texture(dirt_tex, p / tile_m + vec2(0.37, 0.61)).rgb;
```
Keep `n` (large variation, which also breaks the 4 m repeat) and `n2` (path-edge wobble). Per region, set
`grass_tex` to grass_v1 (V1) or grass_birch (V2); `dirt_tex` is dirt_path in both. Cost: two extra texture reads
per ground pixel. That is cheap on phones, and the tufts are visible at the camera's roughly 60 px per metre.

## 5. Border-forest imposters: `res://assets/textures/imposters/`

**Verdict: use imposters for the border forest. They win on both draw calls and triangles (my calc).**
The camera never rotates or changes pitch, so one card rendered from the game camera looks like the mesh.

| Setup (one valley edge in view) | Visible border trees | Triangles | Draw calls |
|---|---:|---:|---:|
| Today: 12 MultiMeshes of `_far` meshes, never culled (V1 map, about 2,970 trees) | all | about 505k + the same again in the shadow pass | 12 + 12 shadow |
| `_far` meshes chunked 16 x 16 m (DESIGN.md advice), about 5 chunks touched | about 400 | about 68k + about 68k shadow | about 60 + 60 shadow (12 kinds per chunk) |
| **Imposters chunked 16 x 16 m, one atlas MultiMesh per chunk, `cast_shadow = OFF`** | about 400 | **about 800** | **about 5** |

Numbers use the view I measured from the camera settings (offset (0, 8.4, 6.6), vertical FOV 45, portrait):
about 16 x 18 m of ground, plus about 5 m for tree height, and density `area / 3.2` (my calc). What the card
costs:
- The atlas is 2048 x 2048, about 5.6 MB of VRAM with ASTC/ETC2 and mipmaps (my calc).
- Alpha-scissor pixels skip early-Z, so check the fill rate with PerfOverlay at a valley edge.
- The border trees no longer cast real shadows. Most are beyond the 30 m shadow distance anyway. If the forest
  floor looks too bright, darken the ground outside the valley rects in `ground.gdshader`; it costs nothing.
- Trees at the very top of the screen are seen about 20 degrees flatter than the 52 degree render. With fog on
  and the trees at the edge of the frame, I expect it to go unnoticed. Confirm this on a device screenshot.
The `_far` meshes stay as the fallback.

Files:
- `border_trees_atlas.png`: 8 x 8 cells of 256 px, 60 used. There are 15 kinds (the 12 in
  `World._border_forest` plus the 3 birches), 4 facings each, rendered with `um render3d --preset iso8
  --headings 4 --elevation 52`. The cells are albedo only (sun 0, uniform white sky), so Godot's sun, ambient
  and fog light the card like the ground.
- `border_trees_atlas.json`: cell indices per kind (`cell = kind_index * 4 + facing`), `px_per_unit = 140`,
  and `ground_y_px = 246`.

Card setup: build one mesh once. It is a quad `256/140 = 1.83` units square, with its pivot 10 px above the
bottom edge (the tree base), tilted back **52 degrees** around X so that it faces the camera. Use it in a
MultiMesh with `use_custom_data = true`, per-instance scale 2.4-3.6 as today, no Y rotation (the facing cell gives
the variety), and `INSTANCE_CUSTOM.r = cell / 255.0`.

```glsl
shader_type spatial;
render_mode cull_disabled, specular_disabled;
uniform sampler2D atlas : source_color, filter_linear_mipmap;
void vertex() {
	float cell = floor(INSTANCE_CUSTOM.r * 255.0 + 0.5);
	UV = (UV + vec2(mod(cell, 8.0), floor(cell / 8.0))) / 8.0;
	NORMAL = normalize((VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz); // world up: lit like the ground
}
void fragment() {
	vec4 c = texture(atlas, UV);
	ALBEDO = c.rgb;
	ALPHA = c.a;
	ALPHA_SCISSOR_THRESHOLD = 0.5;
}
```
(The `NORMAL` line points the card normal straight up, so it gets the same sun and ambient as the ground.)

## Rebuild
```bash
cd /home/mm/MWM/projects/timber-valley
/home/mm/.local/bin/blender -b --python tools/lookdev/build_m1.py    # models (items + birch), report -> tools/lookdev/build_m1_report.json
python3 tools/lookdev/render_m1_review.py                            # review renders (um render3d)
python3 tools/lookdev/make_icons_m1.py                               # icons (um render3d + um sprite fit/preview)
tools/lookdev/make_ground_m1.sh                                      # ground tiles (Blender + um sprite seamless/tile-preview)
python3 tools/lookdev/make_imposters_m1.py                           # imposter atlas (um render3d + um sprite sheet)
python3 tools/lookdev/make_compare_m1.py                             # tools/lookdev/compare_m1.png
```
