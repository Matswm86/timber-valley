# M5 assets: Grand Timber Station (the finale, GDD 7.7)

Built 2026-10-03 on branch `v4-m345`. Review sheet: `tools/lookdev/compare_m5.png`. Licences: `SOURCES.md` (all own work,
CC0). Builder: `tools/lookdev/build_m5.py` (shared helpers in `tools/lookdev/m345_lib.py`), report
`tools/lookdev/build_m5_report.json`. Rebuild commands at the end.

Same rules as the earlier ASSETS files: one mesh, one material and one embedded texture per GLB, every texture 512 px or
less, Godot +Z = front, +Y up. All 22 files in `station/` were load-checked in Godot 4.6.2 (`load()` + `instantiate()`,
0 errors). No new items or icons: the Station takes goods that already exist (bookcase, canoe, cabin_kit, mast, guitar).

Accent: **station brass `#c99a2e`** `Color(0.788, 0.604, 0.18)` (clock, trims, finials, loco bands) on cream sandstone
`#e6d6b8`, with **station maroon `#6e2430`** `Color(0.43, 0.14, 0.19)` for roofs and rolling stock (DESIGN.md section 16).
The five platform slots each wear their own valley's accent, and five pennants on the station roof repeat them.

## 1. Models: `res://assets/models_v3/station/`

### 1.1 The capstone (world units)
| File | Use | Tris (per stage) | Size x/y/z (m) | Anchors |
|---|---|---:|---|---|
| `grand_station.glb` | `cap_station` (0, -52), 6 BuildSite stages | 2940 (248 / 992 / 216 / 556 / 612 / 316) | 16.2 / 11.1 / 8.7 | A **through-station** over the rail line. Origin = pad. The track runs along X through the hall at **station-local z +1.0** (world z -51 with the origin at (0, -52)): lay `maple/rail_straight_4m.glb` there with rot 90, rail top y 0.18. The **north-south walkway** (the V1 -> V3 gate path) runs straight through arches at **x -1.4..1.4** in both long walls; plank crossing flush with the rail top at (0, 0.15, 1.0). Platforms (top y 0.4) either side of the track, cut at the walkway. Stages: 1 platforms + crossing + paving, 2 lower walls + arches + corner piers, 3 clerestory, 4 maroon train-shed vault with a glazed ridge and brass ribs, 5 clock tower over the south (camera) entrance + canopy, 6 spire, brass finial and vane, sign board, five valley pennants. **Sign board face (0, 4.25, 5.11)**: Label3D "GRAND TIMBER STATION" (dark brown, two lines). Collision: two wall boxes (15.2, 3.0, 0.3) at (0, 1.5, -2.65) and (0, 1.5, 4.65) with the walkway gap x -1.4..1.4 left open, plus the four corner piers (0.9, 4.8, 0.9) at (+-7.6, 2.4, -2.65 / 4.65) |
| `station_plot.glb` | the site before / while stage 1 rises | 652 | 15.5 / 1.9 / 8.1 | survey stakes, rope around the footprint (walkway left open), stone pile, cut blocks, a "COMING SOON" board face at (3.5, 1.3, 5.24). Same origin; hide it when stage 1 rises |

**Layout warning (please check before placing):** with the origin at (0, -52) the station reaches world z -54.65 (north
wall) to **-46.4** (tower front and canopy), and x -8.1..8.1. The Home Valley palisade is at z -47 and the Highland Gate
model at (0, -46.6) (it spans x +-2.75, z -47.7..-45.5), so the south facade and the gate overlap by about 1 m.
Two ways out, both layout calls:
- **A (recommended):** once `cap_station` is bought, shrink the Highland Gate away (its doors already do this) and let the
  station's walk-through arch be the gate; the station replaces the gate visually.
- **B:** move the rail line and the station 1.2 m north (track z -52.2, origin (0, -53.2)). The south face then ends at
  z -47.6, clear of the palisade, but the north wall reaches z -56.4, through the Maple Highlands wall at z -55, which
  then needs a 16 m opening there. The V3 handcar stop at (-6, -57.8) stays clear (1.4 m).

### 1.2 Platform slots (world units, GDD 7.7: one per valley next to its handcar stop)
| File | Valley / goods | Tris | Size x/y/z (m) | Anchors |
|---|---|---:|---|---|
| `platform_slot_v1.glb` | V1, 120 bookcase (orange) | 492 | 3.7 / 2.6 / 2.6 | stone slab top y 0.2; **pallet bay = goods pile and DROP square at (-0.55, 0.28, 0.1)**, 1.8 x 1.8; sign board in the valley accent, **face (1.1, 1.9, -0.78)**: Label3D "STATION 34/120" (cream text) plus the item icon; brass emblem above it; double lamp at the back left. Put it on the stop's side away from the track |
| `platform_slot_v2.glb` | V2, 40 canoe (river blue) | 492 | same | same anchors. The canoe is 2.0 m long along Z: use `rows 1` so the pile stays inside the bay |
| `platform_slot_v3.glb` | V3, 40 cabin_kit (teal) | 492 | same | same anchors |
| `platform_slot_v4.glb` | V4, 30 mast (navy) | 492 | same | same anchors; masts are 2.4 m along Z and overhang the 1.8 m bay by 0.3 m each side, which reads fine |
| `platform_slot_v5.glb` | V5, 20 guitar (alpine red) | 492 | same | same anchors |

### 1.3 Rail line and the Timber Express (world units)
| File | Use | Tris | Size x/y/z (m) | Anchors |
|---|---|---:|---|---|
| (existing) `maple/rail_straight_4m.glb` | the z -51 line, x -75..75 | 276 | | tile every 4.0 m with rot 90 |
| `rail_bridge_8m.glb` | river crossing at x -27 (river 6.4 m) | 788 | 2.4 / 2.4 / 9.2 | along Z like the rail tile (rot 90 for the east-west line), centred on the river; rails at y 0.18 and gauge 1.0 match the tiles; maroon lattice trusses (top chord y 1.6), stone abutments at z +-4.2 |
| `rail_road_crossing_4m.glb` | road crossing at x 17 | 192 | 2.9 / 0.18 / 4.0 | along Z (rot 90): planks flush with the rail top between and beside the rails, white stop bars at +-1.3. Add the M3 `crossing_post` + `crossing_arm` pair if trucks should stop |
| `express_loco.glb` | Timber Express loco (end cutscene, 12 s loop) | 1544 | 1.9 / 2.4 / 5.4 | maroon steam loco with brass bands, red drivers; **front at -Z** like the other locos; gauge 1.0, wheels on rail top y 0.18; origin = track centre at ground |
| `express_tender.glb` | log tender behind the loco | 736 | 1.8 / 2.2 / 2.6 | couple **3.4 m** behind the loco centre (+Z); loaded with logs |
| `express_coach.glb` | passenger coach (2-3) | 892 | 2.0 / 2.9 / 4.5 | maroon / cream with brass lining; tender centre to first coach centre 3.8, coaches 4.6 apart |
| `handcar_stop_station.glb` | optional handcar stop for a station tile | 532 | 4.2 / 2.6 / 0.5 | same anchors as `maple/handcar_stop.glb`, maroon. Only if the Station gets a handcar tile; the GDD has none |

For the loop: the GDD rail runs x -75..75 at z -51; the train only needs to run east-west past every valley's edge, so
a straight run out and back (the M2 train already backs out) is cheaper than a real loop.

### 1.4 Square props and trees
| File | Use | Tris | Notes |
|---|---|---:|---|
| `tree_station_lime.glb` (kenney units) | clipped lime on a straight stem, station square | 577 | 0.64 wide; scale 2.3-2.8 like V1 trees. Not a chop tree |
| `tree_station_cone.glb` (kenney units) | cone topiary | 321 | 0.37 wide |
| `tree_station_{lime,cone}_far.glb` | mesh fallback | 103 | imposters preferred (section 4) |
| `station_bench.glb` | platforms, square | 396 | |
| `clock_post.glb` | brass two-faced platform clock, 3.2 m | 388 | |
| `flower_planter.glb` | sandstone planter, red and yellow flowers | 384 | |
| `luggage_cart.glb` | cart with trunks | 368 | |
| `station_lamp.glb` | double-globe lamp | 352 | |

## 2. Swap dicts

```gdscript
# Models.gd PATHS: add
	"grand_station": "res://assets/models_v3/station/grand_station.glb",
	"station_plot": "res://assets/models_v3/station/station_plot.glb",
	"platform_slots": [
		"res://assets/models_v3/station/platform_slot_v1.glb",
		"res://assets/models_v3/station/platform_slot_v2.glb",
		"res://assets/models_v3/station/platform_slot_v3.glb",
		"res://assets/models_v3/station/platform_slot_v4.glb",
		"res://assets/models_v3/station/platform_slot_v5.glb",
	],
	"rail_bridge": "res://assets/models_v3/station/rail_bridge_8m.glb",
	"rail_road_crossing": "res://assets/models_v3/station/rail_road_crossing_4m.glb",
	"express_loco": "res://assets/models_v3/station/express_loco.glb",
	"express_tender": "res://assets/models_v3/station/express_tender.glb",
	"express_coach": "res://assets/models_v3/station/express_coach.glb",
	"handcar_stop_station": "res://assets/models_v3/station/handcar_stop_station.glb",
	"station_trees": [
		"res://assets/models_v3/station/tree_station_lime.glb",
		"res://assets/models_v3/station/tree_station_cone.glb",
	],
	"station_bench": "res://assets/models_v3/station/station_bench.glb",
	"clock_post": "res://assets/models_v3/station/clock_post.glb",
	"flower_planter": "res://assets/models_v3/station/flower_planter.glb",
	"luggage_cart": "res://assets/models_v3/station/luggage_cart.glb",
	"station_lamp": "res://assets/models_v3/station/station_lamp.glb",
```
`platform_slots[region - 1]` gives the slot for a valley. No Items.DEFS or ICONS additions.

```gdscript
# Models.GROUND: add (station square / platform plaza)
	"station": "res://assets/textures/ground/station_paving.png",
```

## 3. Ground: `res://assets/textures/ground/station_paving.png`
512 x 512 (opaque, alpha 255), 4 x 4 m per tile, warm sandstone paving with soft joints. Mean `#d1bd9f` (my calc). It is meant for a
small plaza plane under the station and its square (the station sits in the border-forest belt, outside every valley's
ground plane), or as a `dirt_tex` override for that plaza.

## 4. Border-forest imposters: `res://assets/textures/imposters/border_trees_atlas_m5.png`
1024 x 1024, 4 x 4 cells: `tree_station_lime` 0-3, `tree_station_cone` 4-7, `tree_mapleA` 8-11, `tree_default` 12-15
(`border_trees_atlas_m5.json`). It covers the belt along the rail line between Home Valley and the Highlands, where the
station square meets both forests. Same card and shader change as the M2 atlas (`grid = 4.0`).

## 5. Not made / open
- **Layout clash** with the Highland Gate (section 1.1): a layout call for the Godot side or Mats.
- **The 12 s Express cutscene path** and the confetti / camera pull-out are Godot work.
- **No new icons:** the Station has no new product.

## Rebuild
```bash
cd /home/mm/MWM/projects/timber-valley
/home/mm/.local/bin/blender -b --python tools/lookdev/build_m5.py        # models
tools/lookdev/make_ground_m345.sh station_paving                         # plaza tile + 3x3 preview
python3 tools/lookdev/make_imposters_m345.py m5                         # border_trees_atlas_m5
python3 tools/lookdev/make_compare_m345.py m5                           # tools/lookdev/compare_m5.png
```
