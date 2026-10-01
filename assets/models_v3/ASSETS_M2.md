# M2 assets: Maple Highlands (Valley 3)

Built 2026-10-01 on branch `v3-m2`. Review sheet: `tools/lookdev/compare_m2.png`. Licences: `SOURCES.md` (all own work,
CC0). Builder: `tools/lookdev/build_m2.py`, report `tools/lookdev/build_m2_report.json`. Rebuild commands at the end.

Same rules as `ASSETS_M1.md`: one mesh, one material and one embedded texture per GLB (albedo x height gradient x baked AO,
contact shadow included). Godot +Z = front (toward the camera), +Y up. All 42 files (38 in `maple/` + 4 items) were load-checked in Godot 4.6
(`load()` + `instantiate()`, 0 errors).
- **kenney units** (trees, nature props): same convention as `models_v3/nature`, so World scales them by about 2.2-3.6.
- **world units** (machines, buildings, vehicles, items): metres at scale 1.0.
- **Build sites** (5 houses, Clock Tower): ONE GLB with child MeshInstances `stage1` .. `stageN` that share one material
  and texture. Every stage's origin is the building origin at ground level, so `stage.scale.y` 0.01 -> 1 (TRANS_BACK,
  0.6 s) makes it "rise from the ground" (GDD 7.6 B).

Region accent: **highland teal `#2a9d8f`** `Color(0.165, 0.616, 0.561)` on machines, roofs and ironwork (DESIGN.md
section 13). Maple canopies are red `#d94f2e`, orange `#ed8a2b` and gold `#f0b53a`. Bark is grey `#8a8278`.

## 1. Models: `res://assets/models_v3/maple/`

### 1.1 Trees and nature (kenney units)
| File | Use | Tris | Tex | Size x/y/z (units) | Notes |
|---|---|---:|---:|---|---|
| `tree_mapleA.glb` | Maple chop tree, round red/orange crown | 686 | 512 | 0.70 / 1.66 / 0.73 | trunk base at origin |
| `tree_mapleB.glb` | Maple chop tree, taller, orange/gold | 686 | 512 | 0.65 / 1.86 / 0.64 | |
| `tree_mapleC.glb` | Maple chop tree, wide and low, gold/red | 686 | 512 | 0.77 / 1.50 / 0.74 | widest, within the 0.79 (1.05 x Kenney) limit |
| `tree_maple{A,B,C}_far.glb` | Border forest mesh fallback | 173 | 256 | | imposters preferred (section 6) |
| `stump_maple.glb` | Stump for kind "maple" | 428 | 256 | 0.58 / 0.23 / 0.56 | three fallen leaves around it |
| `log_stack_maple.glb` | Yard prop (beam saw, forester spots) | 936 | 256 | 0.60 / 0.41 / 0.66 | scale 2.2-2.4 |
| `leaf_pile.glb` | Deco scatter (replaces some flowers in V3) | 296 | 128 | 0.48 / 0.13 / 0.53 | `cast_shadow = OFF` |
| `bush_autumn.glb` | Deco scatter (with or instead of `plant_bush`) | 218 | 256 | 0.52 / 0.29 / 0.38 | |

### 1.2 Machines (world units; Machine piles at x -2.7 / +2.7 unless noted)
| File | Pad | Tris | Size x/y/z (m) | Anchors (Godot, `m.body` local) |
|---|---|---:|---|---|
| `beam_saw.glb` | `r3_beamsaw` (2, -64) | 1008 | 3.9 / 1.66 / 1.85 | roller bed top y 0.68 along X; `mouth_in` (-1.6, 0.7, 0), `cut_point` (0, 0.7, 0), `mouth_out` (1.3, 0.75, 0); blocker (3.9, 1.4, 1.4) at offset (0, 0, -0.1) |
| `beam_saw_blade.glb` | spinner | 464 | r 0.55 | pivot at (0, 0.95, 0.05): `var b := m.add_model(path, Vector3(0, 0.95, 0.05), 1.0); m.spinners.append(b)`. Disc normal = local Z, so it spins about FORWARD like the old blades |
| `planer_mill.glb` | `r3_planer` (2, -78) | 1248 | 3.6 / 2.92 / 2.47 | infeed table x -1.8..-0.7, outfeed x 0.8..1.8, both top y 0.9; `mouth_in` (-1.4, 0.95, 0), `mouth_out` (1.2, 0.95, 0); cyclone behind at (1.1, *, -1.15) up to y 2.92; blockers (3.6, 1.5, 1.4) and (0.9, 3.0, 0.9) at offset (1.1, 0, -1.15) |
| `planer_roller.glb` | spinner | 116 | 0.26 x 1.0 | feed roller, axis = local Z, at (-0.66, 1.0, 0); `m.spinners.append(...)` |
| `kit_factory.glb` | `r3_kitfactory` (6, -90), **Assembler** | 2548 | 5.0 / 3.27 / 4.14 | two intake roller tables from the -X side at z -1.2 (beams) and z +1.2 (floorboards); put the piles/DROP squares at **(-3.2, 0, -1.45)** = beam input and **(-3.2, 0, +1.45)** = floorboard input; output pile at **(3.2, 0, 0)**; `mouth_in` beams (-2.1, 0.9, -1.2), floorboards (-2.1, 0.9, 1.2); `mouth_out` (2.3, 0.9, 0); assembly table top y 0.93 at (0.1, *, 0); back wall + teal lean-to roof over z < -0.5; blocker (4.6, 3.2, 4.0) |
| `kit_factory_press.glb` | `Machine.plates` | 92 | 1.12 x 1.1 | pivot = top of the plate; `m.plates.append(m.add_model(path, Vector3(0.1, 1.75, 0), 1.0))`, `m.plate_up = 1.75`, `m.plate_down = 1.5` (it stops on the strapped kit, top 1.49) |

### 1.3 Workers, rail and train (world units)
| File | Use | Tris | Size x/y/z (m) | Anchors |
|---|---|---:|---|---|
| `forklift.glb` | Forklift hauler (`r3_forklift1`) | 928 | 1.2 / 2.25 / 2.65 | forks to **+Z** (Walker turns the model's +Z to the walk direction, like the characters); fork tines y 0.07..0.12 over z 0.73..1.58, x +-0.22; **carried ItemStack at (0, 0.2, 1.05)** instead of the character's (0, 0.62, 0.42). It is a static model with no skeleton: give the Walker a tiny model node with a no-op `update_state()`. Optional bob: `position.y = sin(t * 12) * 0.01` while moving |
| `rail_straight_4m.glb` | Track for the train and the handcar stops | 276 | 1.6 / 0.18 / 4.0 | along **Z**, centred, gauge 1.0, rail top **y 0.18**, flat rail ends: tile every 4.0 m (rot 90 for east-west). 5 sleepers |
| `rail_bumper.glb` | Buffer stop at a track end | 348 | 1.6 / 0.87 / 0.78 | faces +Z (rot 180 to face a train arriving from -Z) |
| `train_loco.glb` | Highland Railway loco (`r3_rail`) | 1020 | 1.8 / 2.49 / 4.7 | **front at -Z** (drives toward -Z at rotation 0, like the barge); wheels on y 0.18; origin = track centre on the ground |
| `train_wagon.glb` | Wagon (3, or 5 with `r3_rail2`) | 584 | 1.8 / 1.33 / 3.6 | deck top **y 0.92**, deck 1.8 x 3.2: `ItemStack(cols 2, rows 2)` at (0, 0.92, 0) = 4 kits; couple at +3.6 m along +Z, loco centre to first wagon centre 3.8 m |
| `rail_platform.glb` | Train TruckDock | 676 | 4.05 / 2.73 / 6.04 | deck top **y 0.40** over x -1.6..2.4, z -3..3; export pile at (0.6, 0.4, 0); **track centre line at dock-local x +3.5**; shelter, bell and lamp at the back |
| `handcar.glb` | Decor on each handcar stop's track | 444 | 1.3 / 1.54 / 1.6 | sits on the rails (wheels on y 0.18); along Z |
| `handcar_stop.glb` | Hub sign + bench + lamp (V1 (-7, 12), V2 (-34, 8), V3 (4, -56), ...) | 532 | 4.2 / 2.57 / 0.48 | sign board face at z +0.07, centre (0, 2.0, 0): Label3D "HANDCAR" at (0, 2.0, 0.09), dark-brown text |
| `handcar_tile.glb` | One destination tile (GDD 7.6 E) | 264 | 1.6 / 0.08 / 1.6 | top y 0.075; Label3D with the valley name flat on it at y 0.09 (rotation -90 X), dark-brown text |

**Layout warning (train):** at the CSV spot (13, -100) an unrotated platform puts the track at x 16.5. That is on the road
(x 15.2..18.8), and the train would arrive from the south along it. Turn the platform so the track runs east-west north
of the road end (rot_y -90: track along z -103.5), or move the dock west. This is a layout call; the models work at any
rotation.

### 1.4 Buildings and landmark (world units)
| File | Pad | Tris (per stage) | Size x/y/z (m) | Anchors |
|---|---|---:|---|---|
| `highland_gate.glb` | `r3_gate` (0, -50) | 824 | 5.5 / 4.26 / 2.13 | put it in the V1 north palisade at **(0, 0, -46.6)**; clear passage x -1.35..1.35 along Z; sign board face (0, 2.95, 1.13): Label3D "MAPLE HIGHLANDS" at z 1.16; leave a 2.8 m gap in the palisade line and in the `_wall` at z -47 |
| `highland_gate_doors.glb` | closed gate (before `r3_gate`) | 392 | 2.66 / 2.55 / 0.21 | same origin as the gate; shrink to 0.01 and free on unlock, like the Birch gate fence |
| `highland_office.glb` | `r3_office` (8, -56) | 708 | 4.3 / 4.21 / 4.47 | door + porch at +Z; yellow sign board face (0, 2.1, 1.55): Label3D "OFFICE" at z 1.62, same style as the Riverside Office; blocker (3.8, 3.0, 3.2); upgrade zone at +Z 3.4 |
| `market_canopy_teal.glb` | Builders' Yard (10, -62) | 1424 | 1.02 / 2.49 / 10.3 | V3 version of `shared/market_canopy.glb`; place exactly as ASSETS_LEFTOVER.md 2.9. Counters and till are the shared ones |
| `build_plot.glb` | Empty village plot (before stage 1) | 398 | 5.1 / 0.74 / 4.9 | 5 x 5 stakes + rope + stones; hide it when stage 1 rises |
| `house_cottage.glb` | `r3_house1` (-17, -62) | 1192 (88 / 440 / 320 / 344) | 5.1 / 4.72 / 4.6 | cream walls, red roof, flower box |
| `house_farmhouse.glb` | `r3_house2` (-17, -70) | 1328 (88 / 440 / 320 / 480) | 5.9 / 4.86 / 5.41 | ochre walls, slate roof, porch roof, dormer; door at x -1.2 |
| `house_barn.glb` | `r3_house3` (-17, -78) | 1268 (44 / 440 / 388 / 396) | 5.85 / 5.03 / 5.9 | red, gambrel roof, big X-braced doors and hayloft facing +Z, hay bales at +X |
| `house_school.glb` | `r3_house4` (-17, -86) | 1400 (88 / 440 / 456 / 416) | 6.1 / 6.6 / 5.0 | white walls, teal roof, bell turret with a gold bell |
| `house_inn.glb` | `r3_house5` (-17, -94) | 1572 (88 / 528 / 632 / 324) | 6.1 / 7.23 / 5.65 | two storeys: stone ground floor, half-timbered upper floor, hanging sign at +X |
| `clock_tower.glb` | `r3_clocktower` (-10, -112) | 1816 (88 / 352 / 400 / 568 / 300 / 108) | 4.0 / 12.25 / 4.55 | 6 stages: plinth, stone shaft + door, timber shaft, clock (faces +Z, +X, -X), belfry + gold bell, teal spire + vane; collision (4.0, 6.0, 4.0) |

House stages: 1 = stone plinth + step, 2 = timber frame, 3 = walls + door + windows, 4 = roof + chimney + details.
Doors face +Z (the camera). Plots are 8 m apart along Z, so put the BuildSite slot squares on the street side (+X,
about x -12.8, stacked along Z) and not in front of the door, where the next plot starts.

### 1.5 Props (world units)
| File | Use | Tris |
|---|---|---:|
| `lantern_post.glb` | Village street and hub lamps | 144 |
| `beam_cart.glb` | Builders' Yard decor (hand cart with beams) | 632 |

## 2. Swap dicts

```gdscript
# Models.gd PATHS: add
	"maple_trees": [
		"res://assets/models_v3/maple/tree_mapleA.glb",
		"res://assets/models_v3/maple/tree_mapleB.glb",
		"res://assets/models_v3/maple/tree_mapleC.glb",
	],
	"maple_stump": "res://assets/models_v3/maple/stump_maple.glb",
	"log_stack_maple": "res://assets/models_v3/maple/log_stack_maple.glb",
	"leaf_pile": "res://assets/models_v3/maple/leaf_pile.glb",
	"bush_autumn": "res://assets/models_v3/maple/bush_autumn.glb",
	"beamsaw": "res://assets/models_v3/maple/beam_saw.glb",
	"beamsaw_blade": "res://assets/models_v3/maple/beam_saw_blade.glb",
	"planer": "res://assets/models_v3/maple/planer_mill.glb",
	"planer_roller": "res://assets/models_v3/maple/planer_roller.glb",
	"kitfactory": "res://assets/models_v3/maple/kit_factory.glb",
	"kitfactory_press": "res://assets/models_v3/maple/kit_factory_press.glb",
	"forklift": "res://assets/models_v3/maple/forklift.glb",
	"rail": "res://assets/models_v3/maple/rail_straight_4m.glb",
	"rail_bumper": "res://assets/models_v3/maple/rail_bumper.glb",
	"train_loco": "res://assets/models_v3/maple/train_loco.glb",
	"train_wagon": "res://assets/models_v3/maple/train_wagon.glb",
	"rail_platform": "res://assets/models_v3/maple/rail_platform.glb",
	"handcar": "res://assets/models_v3/maple/handcar.glb",
	"handcar_stop": "res://assets/models_v3/maple/handcar_stop.glb",
	"handcar_tile": "res://assets/models_v3/maple/handcar_tile.glb",
	"highland_gate": "res://assets/models_v3/maple/highland_gate.glb",
	"highland_gate_doors": "res://assets/models_v3/maple/highland_gate_doors.glb",
	"highland_office": "res://assets/models_v3/maple/highland_office.glb",
	"market_canopy_teal": "res://assets/models_v3/maple/market_canopy_teal.glb",
	"build_plot": "res://assets/models_v3/maple/build_plot.glb",
	"house_cottage": "res://assets/models_v3/maple/house_cottage.glb",
	"house_farmhouse": "res://assets/models_v3/maple/house_farmhouse.glb",
	"house_barn": "res://assets/models_v3/maple/house_barn.glb",
	"house_school": "res://assets/models_v3/maple/house_school.glb",
	"house_inn": "res://assets/models_v3/maple/house_inn.glb",
	"clock_tower": "res://assets/models_v3/maple/clock_tower.glb",
	"lantern_post": "res://assets/models_v3/maple/lantern_post.glb",
	"beam_cart": "res://assets/models_v3/maple/beam_cart.glb",
```

```gdscript
# Items.DEFS: add (cells and layers are the GDD 7.3 numbers; models are sized to fit them)
	"maple_log": {"path": "res://assets/models_v3/items/item_maple_log.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.31, "cell": Vector2(1.05, 0.36)},
	"beam": {"path": "res://assets/models_v3/items/item_beam.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.28, "cell": Vector2(1.2, 0.3)},
	"floorboard": {"path": "res://assets/models_v3/items/item_floorboard.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.07, "cell": Vector2(1.0, 0.25)},
	"cabin_kit": {"path": "res://assets/models_v3/items/item_cabin_kit.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.6, "cell": Vector2(1.0, 1.0)},
```
| File | Item | Tris | Size x/y/z (m) |
|---|---|---:|---|
| `items/item_maple_log.glb` | maple_log | 140 | 0.95 / 0.32 / 0.32, grey bark, along X |
| `items/item_beam.glb` | beam | 108 | 1.15 / 0.27 / 0.27, square, ring ends |
| `items/item_floorboard.glb` | floorboard | 100 | 0.96 / 0.06 / 0.23, tongue on +Z, groove on -Z: stacked boards nest |
| `items/item_cabin_kit.glb` | cabin_kit | 724 | 0.88 / 0.56 / 0.94, beams + boards on skids, two teal straps, red tag on the front-right corner |

The heaviest full pile is the kit factory's 48-kit output = 35k tris (my calc), a third of the 100k budget. Keep a
hauler or belt on it so it rarely fills. If the PerfOverlay shows it at a valley edge, ask for a 300-tri kit (fewer
beam ends); I have not built that version.

```gdscript
# Models.ICONS: add (64 px; _128 and the 256 master exist too)
	"maple_log": "res://assets/icons/maple_log_64.png",
	"beam": "res://assets/icons/beam_64.png",
	"floorboard": "res://assets/icons/floorboard_64.png",
	"cabin_kit": "res://assets/icons/cabin_kit_64.png",
# Models.GROUND: add
	3: "res://assets/textures/ground/grass_maple.png",
```

Tree kind (GDD 7.2 / Balance): `"maple": {"log": "maple_log", "logs": 5, "hits": 5, "regrow": 9.0, "scale": 1.1}` with
models `PATHS.maple_trees`, stump `PATHS.maple_stump`, scale `randf_range(2.3, 2.8) * 1.1`. Note: with the GDD's 1.1,
the widest maple (C) is 0.84 units, over the 0.79 path/arrow limit (DESIGN.md 11). Keep C out of groves next to
paths, or use 1.0 for C.

## 3. Icons: `res://assets/icons/`
`maple_log`, `beam`, `floorboard`, `cabin_kit`, each as `<id>.png` (256), `_128`, `_64`. The camera, outline and sizes are
identical to M1 (`um render3d --preset iso8 --headings 1 --elevation 35 --forward-yaw -30`, 3 px outline `#3a2618`).
All four were checked at 48 px on dark green and still read (floorboard is the weakest: a thin pale board).
Outline contrast (my calc): 13.4:1 on the HUD cream, 4.9:1 on the HUD green, 4.1:1 on the Maple Highlands grass.

## 4. Ground: `res://assets/textures/ground/grass_maple.png`
512 x 512 RGB, 4 x 4 m per tile, autumn olive (GDD 9.3) with faint fallen orange leaves. Mean `#809236` (my calc),
std 3-6 of 255. Same Blender 4D-torus material as M1 plus `um sprite seamless` / `tile-preview`. Plug it in as
`grass_tex` on the V3 ground plane exactly as ASSETS_M1.md section 4 describes; `dirt_tex` stays `dirt_path.png`.

## 5. Valley 3 deco scatter (suggested sets for a `_scatter_deco_v3`)
Same counts formula as V2. Swap `flower_redA` / `flower_yellowA` for `leaf_pile` (110) and `bush_autumn` (90), and keep
`grass`, `grass_large`, `rock_*` and mushrooms. The grass clumps are V1 green, so cut them by about half: autumn ground
with fewer bright tufts reads more like the Highlands.

## 6. Border-forest imposters: `res://assets/textures/imposters/border_trees_atlas_m2.png`
1024 x 1024, **4 x 4 cells** of 256 px: `tree_mapleA` 0-3, `tree_mapleB` 4-7, `tree_mapleC` 8-11,
`tree_pineTallB_detailed` 12-15. One V3 edge chunk needs only this atlas: about 1.4 MB of VRAM with ETC2/ASTC and mips
(my calc). Same card, camera, pixels per unit (140) and ground row (246) as the M1 atlas
(`border_trees_atlas_m2.json`). One shader change makes it work with both atlases:
```glsl
uniform float grid = 8.0;   // border_trees_atlas.png = 8, border_trees_atlas_m2.png = 4
UV = (UV + vec2(mod(cell, grid), floor(cell / grid))) / grid;
```
Then give V3 chunks a second ShaderMaterial with `atlas = border_trees_atlas_m2.png`, `grid = 4.0` and
`cell = kind_index * 4 + facing` from the json.

## Rebuild
```bash
cd /home/mm/MWM/projects/timber-valley
/home/mm/.local/bin/blender -b --python tools/lookdev/build_m2.py        # models (GPU OptiX bake when present)
python3 tools/lookdev/make_icons_m2.py                                  # icons
tools/lookdev/make_ground_m2.sh                                         # grass_maple + 3x3 preview
python3 tools/lookdev/make_imposters_m2.py                              # border_trees_atlas_m2
python3 tools/lookdev/make_compare_m2.py                                # tools/lookdev/compare_m2.png
```
