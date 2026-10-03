# M4 assets: Frost Peaks (Valley 5)

Built 2026-10-01..03 on branch `v4-m345`. Review sheet: `tools/lookdev/compare_m4.png`. Licences: `SOURCES.md` (all own
work, CC0). Builder: `tools/lookdev/build_m4.py` (shared helpers in `tools/lookdev/m345_lib.py`), report
`tools/lookdev/build_m4_report.json`. Rebuild commands at the end.

Same rules as `ASSETS_M1.md`..`ASSETS_M3.md`: one mesh, one material and one embedded texture per GLB (albedo x height
gradient x baked AO), every texture 512 px or less. Godot +Z = front (toward the camera), +Y up. All 47 files (42 in
`frost/` + 5 items) were load-checked in Godot 4.6.2 (`load()` + `instantiate()`, 0 errors). The one exception to "one
texture" is `kiln_glow.glb`: it has no texture on purpose, only an emissive colour (imports as `emission_enabled = true`,
`emission = (1.0, 0.48, 0.12)`, `emission_energy_multiplier = 1.0`).
- **kenney units** (trees, nature props): World scales them by about 2.2-3.6, and frost firs by a further 1.15 (GDD 7.2).
- **world units** (machines, buildings, vehicles, items): metres at scale 1.0.
- **Build site** (Summit Observatory): ONE GLB with child MeshInstances `stage1` .. `stage6`, as in M2/M3.

Region accent: **alpine red `#c8283a`** `Color(0.784, 0.157, 0.227)` on machines, roofs, the cable car, the train and
ironwork. Snow `#f2f6fc` sits on every roof, cap and ledge, but stops short of the eaves so a red band always outlines a
building against the snow (DESIGN.md section 15). Firs are blue-green `#2f5e4f` / `#407561`.

## 1. Models: `res://assets/models_v3/frost/`

### 1.1 Trees and nature (kenney units)
| File | Use | Tris | Tex | Size x/y/z (units) | Notes |
|---|---|---:|---:|---|---|
| `tree_frostfirA.glb` | Frost fir chop tree, 4 tiers | 661 | 512 | 0.44 / 1.89 / 0.44 | trunk base at origin, snow collar on every tier, snow tip |
| `tree_frostfirB.glb` | Frost fir chop tree, tall and slim | 661 | 512 | 0.40 / 2.16 / 0.39 | |
| `tree_frostfirC.glb` | Frost fir chop tree, short and wide, 3 tiers | 513 | 512 | 0.48 / 1.71 / 0.47 | |
| `tree_frostfirD.glb` | Heavily snowed fir (border forest, or a 4th chop variant) | 661 | 512 | 0.48 / 1.99 / 0.50 | wider snow collars |
| `tree_frostfir{A,B,C,D}_far.glb` | Border forest mesh fallback | 183 | 256 | | one tapered cone + snow cap; imposters preferred (section 6) |
| `stump_frost.glb` | Stump for kind "frost" | 248 | 256 | 0.61 / 0.28 / 0.61 | snow on the ring top and around the foot |
| `log_stack_frost.glb` | Yard prop (kiln, forester spots) | 990 | 256 | 0.60 / 0.43 / 0.66 | snow on top; scale 2.2-2.4 |
| `snow_drift.glb` | Deco scatter | 128 | 128 | 0.60 / 0.16 / 0.38 | `cast_shadow = OFF` |
| `snow_rock.glb` | Deco scatter | 160 | 256 | 0.37 / 0.26 / 0.36 | warm-grey rock, snow cap |
| `snow_bush.glb` | Deco scatter (replaces flowers in V5) | 120 | 128 | 0.39 / 0.22 / 0.34 | juniper under snow |

Fir size at game scale (my calc): `randf_range(2.3, 2.8) * 1.15` makes them 5.0-7.0 m tall; the widest (D) is 0.58 units
after the 1.15x, well inside the 0.79 path/arrow limit.

### 1.2 Machines (world units)
| File | Pad | Tris | Size x/y/z (m) | Anchors (Godot, `m.body` local) |
|---|---|---:|---|---|
| `drying_kiln.glb` | `r5_kiln` (40, -66), `r5_kiln2` (40, -82), `r5_kiln3` (40, -98), **Batch** | 1204 | 4.0 / 4.0 / 2.9 | stone kiln house, snowy red barrel roof, chimney at the back right. Input pile/DROP square at **(-2.7, 0, 0.3)** (takes up to 20 frost_log), output pile at **(2.7, 0, 0.3)**. `mouth_in` (-1.0, 0.9, 1.2) (logs fly in through the door), `mouth_out` (0.6, 0.6, 1.4) (lumber pops out through the door, GDD 11: one by one, 0.05 s apart); blocker (3.3, 2.5, 2.7) at offset (0, 0, 0) |
| `kiln_door.glb` | kiln door (moving part) | 392 | 1.48 / 1.5 / 0.17 | **hinge = origin; place at (-0.72, 0.2, 1.26)** on the kiln. Closed = rotation 0 (while baking); open = `rotation.y` -1.75 rad (swings out toward the camera; tween 0.4 s with the "ding") |
| `kiln_glow.glb` | chimney mouth + two vent slits (emissive) | 36 | | origin = kiln origin. Ramp the material's `emission_energy_multiplier` 0 -> 3 over the bake (GDD 7.6 D) and back to 0 when the door opens. Duplicate the material per kiln (`mesh.surface_get_material(0).duplicate()`) so the three kilns glow independently. `cast_shadow = OFF` |
| `ski_workshop.glb` | `r5_skiworks` (48, -76) | 1468 | 4.2 / 3.0 / 3.1 | open shed (snowy lean-to over the back half), steam box, bending press with skis. Piles x -2.7 / +2.7; `mouth_in` (-1.25, 0.6, 0.65), `mouth_out` (0.9, 1.0, 0.2); blocker (3.6, 2.0, 2.8) |
| `ski_press.glb` | `Machine.plates` | 84 | 1.42 / 0.73 / 0.5 | pivot = top of the plate: `m.plates.append(m.add_model(path, Vector3(0, 1.55, 0.2), 1.0))`, `m.plate_up = 1.55`, `m.plate_down = 1.08` (stops on the skis) |
| `sled_workshop.glb` | `r5_sledshop` (56, -88), **Assembler** | 1936 | 5.0 / 3.2 / 4.1 | same layout as the Cabin Kit Factory: piles/DROP squares at **(-3.2, 0, -1.45) dry_lumber** and **(-3.2, 0, 1.45) skis**, output at **(3.2, 0, 0)**; `mouth_in` lumber (-2.1, 0.9, -1.2), skis (-2.1, 0.9, 1.2); `mouth_out` (2.3, 0.9, 0); assembly table top y 0.93; log back wall + snowy red lean-to over z < -0.5; blocker (4.6, 3.0, 4.0) |
| `sled_workshop_arm.glb` | `Machine.arms` | 152 | 0.26 / 0.98 / 1.45 | pivot = the post axis: `m.arms.append(m.add_model(path, Vector3(0.9, 0, -1.2), 1.0))`; the drill head reaches +Z over the table and swings with the arm code (`rotation.y = sin(t * 3) * 0.9`) |
| `luthier_workshop.glb` | `r5_luthier` (44, -96) | 2328 | 4.4 / 3.1 / 3.3 | open log workshop, three guitars on the back wall, workbench with a guitar, glue pot and clamps. Piles x -2.7 / +2.7 (output 12 guitars); `mouth_in` (-1.0, 1.0, 0.2), `mouth_out` (0.8, 1.0, 0.4); blocker (3.8, 2.0, 3.0) |
| `luthier_sander.glb` | spinner | 124 | r 0.28 | sanding disc, normal = local Z: `m.spinners.append(m.add_model(path, Vector3(1.15, 1.32, 0.56), 1.0))` |

### 1.3 Vehicles, train and cable car (world units)
| File | Use | Tris | Size x/y/z (m) | Anchors |
|---|---|---:|---|---|
| `snowcat.glb` | Snowcat hauler (`r5_snowcat`) | 1436 | 1.9 / 2.1 / 3.1 | plow at **+Z** (Walker turns +Z to the walk direction); **carried ItemStack at (0, 1.05, -0.75)**, cargo bed 1.35 x 1.15 with red side boards. Static model: wrap it like `ForkliftModel`. Optional bob `sin(t * 10) * 0.008` |
| `mountain_loco.glb` | Mountain train (`r5_express_r5`) | 1224 | 1.7 / 3.0 / 3.6 | alpine electric loco, red with a cream band, pantograph; **front at -Z** like `maple/train_loco.glb`; gauge 1.0, wheels on rail top y 0.18; origin = track centre at ground. Track = `maple/rail_straight_4m.glb` + `maple/rail_bumper.glb` |
| `mountain_wagon.glb` | guitar wagon (2-3 behind the loco) | 496 | 1.8 / 1.1 / 3.6 | low red sides; **deck top y 0.92**, deck 1.8 x 3.2: `ItemStack(cols 2, rows 2)` at (0, 0.92, 0) = 4 guitars per layer (10 per trip = 2 wagons + a part layer, or 3 wagons). Couple 3.6 m apart along +Z; loco centre to first wagon centre 3.6 |
| `rail_platform_alpine.glb` | Express Platform (70, -80) | 784 | 4.1 / 2.8 / 6.0 | identical layout to `maple/rail_platform.glb` (deck top y 0.40 over x -1.6..2.4, z -3..3; export pile at (0.6, 0.4, 0); **track centre at dock-local x +3.5**), red roof under snow |
| `cablecar_station_bottom.glb` | `r5_cablecar` gate pad (50, -47), V4 side | 572 | 4.4 / 5.9 / 4.4 | stone base, four red posts, red gable roof (eave y 4.8). Boarding deck at **+Z** (top y 0.48); yellow sign board face (0, 3.3, 1.79): Label3D "CABLE CAR". Haul rope height **y 4.2**, leaving along -Z |
| `cablecar_station_top.glb` | top station (50, -58), V5 side | 660 | 4.4 / 6.0 / 4.4 | same building with snow on the roof. **Turn it rot_y 180** so its deck faces the Frost Peaks side (-Z) and the rope arrives from +Z |
| `cablecar_bullwheel.glb` | bull-wheel in each station (moving part) | 236 | r 1.3 | horizontal wheel, **axis = Godot Y**, pivot at its centre: place at station-local (0, 4.2, 0) and spin `rotation.y += 2.0 * delta` while a car rides (not a Machine spinner: those turn about local Z) |
| `cablecar_gondola.glb` | gondola (moving part) | 584 | 1.6 / 3.8 / 1.6 | **origin = the grip on the rope (y 0)**; red cabin hangs below, floor at y -3.75, doors at +Z. At a station put it at station-local (0, 4.2, 1.3): its floor then sits at 0.45, level with the deck. Ride = tween 4 s along the rope (GDD 9.1) with the fade |
| `cablecar_cable_1m.glb` | haul rope | 20 | 0.06 / 0.07 / 1.0 | 1 m along Z, flat ends: `scale.z` = span (11 m between the two station centres), centred between them at y 4.2 |
| `cablecar_chain.glb` | closed state before `r5_cablecar` | 200 | 3.3 / 1.0 / 0.1 | origin = bottom-station origin: chain across the boarding deck at z 1.6 with a red "CLOSED" plate (Label3D at (0, 1.19, 1.66)). Shrink to 0.01 and free on unlock |
| `handcar_stop_alpine.glb` | V5 handcar stop (46, -60) | 640 | 4.2 / 2.6 / 0.5 | same anchors as `maple/handcar_stop.glb`, red posts, snow on the top beam |
| `handcar_alpine.glb` | handcar on the V5 stop's track | 444 | 1.3 / 1.5 / 1.6 | same as `maple/handcar.glb`, red frame |

### 1.4 Buildings and landmark (world units)
| File | Pad | Tris (per stage) | Size x/y/z (m) | Anchors |
|---|---|---:|---|---|
| `mountain_office.glb` | `r5_office` (34, -58) | 1376 | 4.5 / 4.1 / 4.7 | log walls on a stone base, red roof under snow. Same anchors as the Highland Office: door at +Z, yellow sign face (0, 2.1, 1.67): Label3D "OFFICE" at z 1.69; blocker (3.8, 3.0, 3.2); upgrade zone +Z 3.4 |
| `market_canopy_alpine.glb` | Ski Lodge market (`r5_skilodge`, 60, -62) | 1424 | 1.0 / 2.5 / 10.3 | red / cream stripes; place exactly as ASSETS_LEFTOVER.md 2.9 with the shared counters and till |
| `ski_lodge.glb` | backdrop chalet behind the Ski Lodge market | 1308 | 7.6 / 6.2 / 6.4 | two storeys, wide snowy eaves, red balcony. Front (+Z) faces the counters: stand it about 8 m behind (-Z of) the canopy centre. Yellow sign on the balcony rail, face (0, 2.38, 3.26): Label3D "SKI LODGE" at z 3.28. Blocker (6.0, 4.0, 4.6) |
| `summit_observatory.glb` | `r5_observatory` (66, -114) | 2812 (624 / 300 / 632 / 584 / 484 / 188) | 6.3 / 10.0 / 6.5 | 6 stages: rocky outcrop + stone plinth + steps, stone drum + red door, timber upper floor with windows, red balcony ring + dome base, white dome with red ribs and the slit, telescope (gold ring) + flag mast + weather station. Door faces +Z; collision cylinder r 2.4, h 8 |

### 1.5 Props (world units)
| File | Use | Tris |
|---|---|---:|
| `ski_rack.glb` | lodge and market decor (three pairs of skis) | 720 |
| `snowman.glb` | village and lodge decor | 608 |
| `alpine_lamp.glb` | streets, lodge, cable car | 192 |
| `firewood_snow.glb` | office, lodge, kiln yard | 620 |

## 2. Swap dicts

```gdscript
# Models.gd PATHS: add
	"frost_trees": [
		"res://assets/models_v3/frost/tree_frostfirA.glb",
		"res://assets/models_v3/frost/tree_frostfirB.glb",
		"res://assets/models_v3/frost/tree_frostfirC.glb",
	],
	"frost_stump": "res://assets/models_v3/frost/stump_frost.glb",
	"frostfir_snowy": "res://assets/models_v3/frost/tree_frostfirD.glb",
	"log_stack_frost": "res://assets/models_v3/frost/log_stack_frost.glb",
	"snow_drift": "res://assets/models_v3/frost/snow_drift.glb",
	"snow_rock": "res://assets/models_v3/frost/snow_rock.glb",
	"snow_bush": "res://assets/models_v3/frost/snow_bush.glb",
	"kiln": "res://assets/models_v3/frost/drying_kiln.glb",
	"kiln_door": "res://assets/models_v3/frost/kiln_door.glb",
	"kiln_glow": "res://assets/models_v3/frost/kiln_glow.glb",
	"skiworks": "res://assets/models_v3/frost/ski_workshop.glb",
	"ski_press": "res://assets/models_v3/frost/ski_press.glb",
	"sledshop": "res://assets/models_v3/frost/sled_workshop.glb",
	"sledshop_arm": "res://assets/models_v3/frost/sled_workshop_arm.glb",
	"luthier": "res://assets/models_v3/frost/luthier_workshop.glb",
	"luthier_sander": "res://assets/models_v3/frost/luthier_sander.glb",
	"snowcat": "res://assets/models_v3/frost/snowcat.glb",
	"mountain_loco": "res://assets/models_v3/frost/mountain_loco.glb",
	"mountain_wagon": "res://assets/models_v3/frost/mountain_wagon.glb",
	"rail_platform_alpine": "res://assets/models_v3/frost/rail_platform_alpine.glb",
	"cablecar_bottom": "res://assets/models_v3/frost/cablecar_station_bottom.glb",
	"cablecar_top": "res://assets/models_v3/frost/cablecar_station_top.glb",
	"cablecar_bullwheel": "res://assets/models_v3/frost/cablecar_bullwheel.glb",
	"cablecar_gondola": "res://assets/models_v3/frost/cablecar_gondola.glb",
	"cablecar_cable": "res://assets/models_v3/frost/cablecar_cable_1m.glb",
	"cablecar_chain": "res://assets/models_v3/frost/cablecar_chain.glb",
	"mountain_office": "res://assets/models_v3/frost/mountain_office.glb",
	"market_canopy_alpine": "res://assets/models_v3/frost/market_canopy_alpine.glb",
	"ski_lodge": "res://assets/models_v3/frost/ski_lodge.glb",
	"handcar_stop_alpine": "res://assets/models_v3/frost/handcar_stop_alpine.glb",
	"handcar_alpine": "res://assets/models_v3/frost/handcar_alpine.glb",
	"observatory": "res://assets/models_v3/frost/summit_observatory.glb",
	"ski_rack": "res://assets/models_v3/frost/ski_rack.glb",
	"snowman": "res://assets/models_v3/frost/snowman.glb",
	"alpine_lamp": "res://assets/models_v3/frost/alpine_lamp.glb",
	"firewood_snow": "res://assets/models_v3/frost/firewood_snow.glb",
```

```gdscript
# Items.DEFS: add (cells and layers are the GDD 7.3 numbers; models are sized to fit them)
	"frost_log": {"path": "res://assets/models_v3/items/item_frost_log.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.33, "cell": Vector2(1.05, 0.4)},
	"dry_lumber": {"path": "res://assets/models_v3/items/item_dry_lumber.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.11, "cell": Vector2(1.0, 0.4)},
	"skis": {"path": "res://assets/models_v3/items/item_skis.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.12, "cell": Vector2(0.4, 1.6)},
	"sled": {"path": "res://assets/models_v3/items/item_sled.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.5, "cell": Vector2(0.8, 1.3)},
	"guitar": {"path": "res://assets/models_v3/items/item_guitar.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.2, "cell": Vector2(0.5, 1.2)},
```
| File | Item | Tris | Size x/y/z (m) |
|---|---|---:|---|
| `items/item_frost_log.glb` | frost_log | 200 | 0.95 / 0.32 / 0.30, fir log along X with a strip of snow on top |
| `items/item_dry_lumber.glb` | dry_lumber | 132 | 0.95 / 0.10 / 0.36, warm orange plank, toasted ends, red kiln stamp (tells it apart from the V1 plank) |
| `items/item_skis.glb` | skis | 160 | 0.25 / 0.13 / 1.52, pair along **Z**, tips up at -Z, red stripe, black bindings |
| `items/item_sled.glb` | sled | 180 | 0.68 / 0.43 / 1.33, along **Z**, red runners curled up at -Z, four slats, rope |
| `items/item_guitar.glb` | guitar | 328 | 0.37 / 0.12 / 1.19, face up along **Z**, body at +Z, headstock at -Z |

Full piles (my calc): 36 frost logs 7.2k tris, 48 dry lumber 6.3k, 48 skis 7.7k, 48 sleds 8.6k, 12 guitars 3.9k. No
`max_drawn` needed.

```gdscript
# Models.ICONS: add (64 px; _128 and the 256 master exist too)
	"frost_log": "res://assets/icons/frost_log_64.png",
	"dry_lumber": "res://assets/icons/dry_lumber_64.png",
	"skis": "res://assets/icons/skis_64.png",
	"sled": "res://assets/icons/sled_64.png",
	"guitar": "res://assets/icons/guitar_64.png",
# Models.GROUND: add
	5: "res://assets/textures/ground/snow_frost.png",
	"snow_packed": "res://assets/textures/ground/snow_packed.png",
```

Tree kind (GDD 7.2 / Balance): `"frost": {"log": "frost_log", "logs": 6, "hits": 6, "regrow": 12.0, "scale": 1.15}` with
models `PATHS.frost_trees`, stump `PATHS.frost_stump`, scale `randf_range(2.3, 2.8) * 1.15`.

## 3. Icons: `res://assets/icons/`
`frost_log`, `dry_lumber`, `skis`, `sled`, `guitar`, each as `<id>.png` (256), `_128`, `_64`. Same camera, outline and sizes
as M1-M3. All five were checked at 48 px on dark green and still read (skis are the thinnest; the red stripe carries them).
Outline contrast (my calc): 13.4:1 on the HUD cream, 11.9:1 on the snow.

## 4. Ground: `res://assets/textures/ground/`
- `snow_frost.png`: 512 x 512 (opaque, alpha 255), 4 x 4 m per tile, white with a cool blue tint and soft wind patches ("snow white-blue",
  GDD 9.3). Mean `#e3ebf5` (my calc), std 2-4 of 255. Use it as `grass_tex` on the V5 ground plane.
- `snow_packed.png`: packed snow for paths and plazas ("dirt becomes packed snow"), mean `#cdd0d2`. Use it as the V5
  plane's `dirt_tex`.
Same Blender 4D-torus material as M1-M3 plus `um sprite seamless` / `tile-preview`.
**Exposure:** snow is near white. With ACES and glow on, check the V5 ground on a device screenshot; if it blows out,
multiply `grass_a/b` in the V5 ground material by about 0.92 rather than editing the tile.

## 5. Valley 5 deco scatter (suggested sets for a `_scatter_deco_v5`)
Same counts formula as earlier valleys. Replace grass clumps and flowers with `snow_drift` (140), `snow_bush` (90) and
`snow_rock` (70); keep a few `rock_*`. No green grass tufts on snow. Put `snowman` x2, `ski_rack` x2 and `alpine_lamp`
by the Ski Lodge, `firewood_snow` by the office and the kilns.

## 6. Border-forest imposters: `res://assets/textures/imposters/border_trees_atlas_m4.png`
1024 x 1024, 4 x 4 cells of 256 px: `tree_frostfirA` 0-3, `tree_frostfirB` 4-7, `tree_frostfirC` 8-11,
`tree_frostfirD` 12-15 (`border_trees_atlas_m4.json`). Same card, camera, pixels per unit and ground row as the earlier
atlases, so the M2 shader change (`grid = 4.0`) covers it. Scale the card by the fir's 1.15x like the mesh.

## 7. Not made / open
- **Lumberjacks in snow:** no winter clothing variant of the characters; they use the existing workwear.
- **Kiln smoke / sparks:** particles are Godot work (`Machine.add_smoke` at the chimney mouth, (0.9, 4.0, -0.75)).
- **Cable car pylons:** none. The span is 11 m and needs no pylon; a pylon would only add draw calls in the forest belt.
- **Orders in Frost Peaks** (GDD open question 5): the M3 `order_board.glb` works here too if Mats says yes; I made no
  second board.

## Rebuild
```bash
cd /home/mm/MWM/projects/timber-valley
/home/mm/.local/bin/blender -b --python tools/lookdev/build_m4.py        # models (GPU OptiX bake when present)
python3 tools/lookdev/make_icons_m345.py m4                             # icons
tools/lookdev/make_ground_m345.sh snow_frost snow_packed                 # ground tiles + 3x3 previews
python3 tools/lookdev/make_imposters_m345.py m4                         # border_trees_atlas_m4
python3 tools/lookdev/make_compare_m345.py m4                           # tools/lookdev/compare_m4.png
python3 tools/lookdev/contrast_m345.py                                  # contrast numbers (my calc)
```
