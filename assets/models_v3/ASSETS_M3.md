# M3 assets: Redwood Coast (Valley 4)

Built 2026-10-01 on branch `v4-m345`. Review sheet: `tools/lookdev/compare_m3.png`. Licences: `SOURCES.md` (all own work,
CC0). Builder: `tools/lookdev/build_m3.py` (shared helpers in `tools/lookdev/m345_lib.py`), report
`tools/lookdev/build_m3_report.json`. Rebuild commands at the end.

Same rules as `ASSETS_M1.md` / `ASSETS_M2.md`: one mesh, one material and one embedded texture per GLB (albedo x height
gradient x baked AO, contact shadow included), every texture 512 px or less. Godot +Z = front (toward the camera), +Y up.
All 45 files (41 in `redwood/` + 4 items) were load-checked in Godot 4.6.2 (`load()` + `instantiate()`, 0 errors, one
surface with an albedo texture each).
- **kenney units** (trees, nature props): same convention as `models_v3/nature`, so World scales them by about 2.2-3.6,
  and redwoods by a further 1.6 (GDD 7.2).
- **world units** (machines, buildings, vehicles, items): metres at scale 1.0.
- **Build sites** (ship hull, Lighthouse): ONE GLB with child MeshInstances `stage1` .. `stageN` sharing one material and
  texture; every stage's origin is the building origin, so `stage.scale.y` 0.01 -> 1 (TRANS_BACK, 0.6 s) raises it.

Region accent: **harbour navy `#1e3a64`** `Color(0.118, 0.227, 0.392)` on machines, roofs, hulls and ironwork, with
**signal red `#cc3333`** `Color(0.8, 0.2, 0.2)` as the 10% pop (lighthouse stripes, buoys, boot-top, warning lamps).
Redwood bark `#8f452b`, canopy `#265c38` / `#357345`, timber heartwood `#db8061` (DESIGN.md section 14).

## 1. Models: `res://assets/models_v3/redwood/`

### 1.1 Trees and nature (kenney units)
| File | Use | Tris | Tex | Size x/y/z (units) | Notes |
|---|---|---:|---:|---|---|
| `tree_redwoodA.glb` | Redwood chop tree, classic tiered crown | 642 | 512 | 0.49 / 1.88 / 0.43 | trunk base at origin, buttressed foot |
| `tree_redwoodB.glb` | Redwood chop tree, tallest and slimmest | 642 | 512 | 0.40 / 2.06 / 0.38 | |
| `tree_redwoodC.glb` | Redwood chop tree, broken double top | 598 | 512 | 0.45 / 1.73 / 0.45 | |
| `tree_redwood{A,B,C}_far.glb` | Border forest mesh fallback | 173 | 256 | | imposters preferred (section 6) |
| `stump_redwood.glb` | Stump for kind "redwood" | 374 | 256 | 0.61 / 0.26 / 0.62 | wide, five root lobes, salmon ring top |
| `log_stack_redwood.glb` | Yard prop (mill, forester spots) | 580 | 256 | 0.59 / 0.36 / 0.80 | scale 2.2-2.4 |
| `dune_grass.glb` | Deco scatter near the shore | 186 | 128 | 0.39 / 0.38 / 0.34 | marram tufts on a sand mound; `cast_shadow = OFF` |
| `driftwood.glb` | Deco scatter on sand | 63 | 128 | 0.63 / 0.12 / 0.26 | `cast_shadow = OFF` |
| `beach_rock.glb` | Deco scatter on sand and grass | 100 | 256 | 0.47 / 0.23 / 0.31 | warm grey, not blue-grey |

Redwood size at game scale (my calc): `randf_range(2.3, 2.8) * 1.6` makes them 6.9-9.2 m tall; the widest (A) is 0.78
units after the 1.6x, inside the 0.79 path/arrow limit (DESIGN.md 11). Collision radius 0.45 m (GDD) is about 1.5x the
trunk at the foot.

### 1.2 Machines (world units)
| File | Pad | Tris | Size x/y/z (m) | Anchors (Godot, `m.body` local) |
|---|---|---:|---|---|
| `redwood_mill.glb` | `r4_redmill` (32, -20) | 1248 | 4.6 / 3.1 / 2.4 | twin-arbor headrig. Carriage bed along X, bed top y 0.71, log line z 0.15. Put the piles at **x -3.0 / +3.0** (the slab reaches x +-2.3). `mouth_in` (-1.7, 1.0, 0.15), `cut_point` (0, 0.95, 0.15), `mouth_out` (1.45, 0.85, 0.15); blocker (4.6, 2.0, 2.3) at offset (0, 0, -0.05) |
| `redwood_mill_blade.glb` | spinner x2 | 516 | r 0.78 | main saw: `m.spinners.append(m.add_model(path, Vector3(0, 0.8, 0.15), 1.0))`; top saw = the same file at scale 0.56: `m.add_model(path, Vector3(0.22, 1.72, 0.15), 0.56)`. Disc normal = local Z, so both spin about FORWARD like every blade |
| `deck_saw.glb` | `r4_decksaw` (32, -32) | 1048 | 3.5 / 1.6 / 1.6 | gang resaw table, table top y 0.87; piles x -2.7 / +2.7; `mouth_in` (-1.4, 0.9, 0), `mouth_out` (1.2, 0.9, 0); blocker (3.4, 1.3, 1.6) at offset (0, 0, -0.2) |
| `deck_saw_gang.glb` | spinner | 708 | r 0.35, 0.6 deep | three blades on one axle along local Z: `m.spinners.append(m.add_model(path, Vector3(0, 0.92, 0), 1.0))` |
| `mast_lathe.glb` | `r4_mastlathe` (50, -24) | 1176 | 4.7 / 1.7 / 2.0 | bed along X (x -2.4..2.2), navy headstock at -X, tailstock at +X, yellow tool carriage at the front; finished mast on a rack at the back (z -0.95). Piles at **x -3.0 / +3.0**; the mast output pile is long along Z (cell 0.4 x 2.4). `mouth_in` (-1.3, 1.1, 0), `mouth_out` (1.6, 1.0, 0.5); blocker (4.6, 1.6, 1.9) at offset (-0.1, 0, -0.15) |
| `mast_lathe_log.glb` | spinner | 220 | 0.41 / 0.41 / 3.1 | built along Z (half bark, half turned spar). Lay it on the bed with rot_y 90: `m.spinners.append(m.add_model(path, Vector3(0, 1.12, 0), 1.0, 90.0))`. `rotate_object_local(FORWARD)` then turns it about its own long axis |

### 1.3 Vehicles and harbour (world units)
| File | Use | Tris | Size x/y/z (m) | Anchors |
|---|---|---:|---|---|
| `log_skidder.glb` | Log Skidder (`r4_skidder1`, `r4_skidder2`) | 1624 | 1.8 / 2.2 / 3.9 | cab + dozer blade at **+Z** (Walker turns +Z to the walk direction, like the forklift). Log bunk at the back: **carried ItemStack at (0, 1.04, -1.2)**, logs across (along X) like every pile; with cap 16 use `rows 2` so the stack stays about 3.4 m tall. Static model: wrap it like `ForkliftModel` (no-op `update_state`, optional bob) |
| `forklift_navy.glb` | Harbor forklift (`r4_forklift`) | 928 | 1.2 / 2.25 / 2.65 | identical to `maple/forklift.glb` (same anchors: ItemStack at (0, 0.2, 1.05)), painted navy. `ForkliftModel.setup_forklift()` needs a model key argument, or a second setup function |
| `cargo_ship.glb` | Order Board ship (`r4_orders`) | 1740 | 3.7 / 5.5 / 11.0 | **bow at -Z** (sails toward -Z at rotation 0, like the barge); origin = waterline under the hull centre, hull reaches y -0.7. Deck y 1.25; bridge and funnel at the stern (+Z); horn at (0.25, 4.1, 4.0) for the "order filled" horn puff. Moor it with its side to the pier, i.e. rot_y 90 or -90 |
| `fishing_boat.glb` | Shopper boats (`r4_harbor`) | 592 | 1.9 / 3.0 / 4.6 | bow at -Z, origin = waterline; two benches top y 0.75 at z -0.2 and z -1.0 (seats x -0.45, 0, 0.45); wheelhouse at the stern (+Z). Tie up at the pier end (72, 8) |
| `pier_straight_4m.glb` | Fishing pier / order dock deck | 896 | 4.0 / 2.0 / 3.1 | along **X**, 3.0 wide, **deck top y 0.3**, flat ends: tile every 4.0 m (rot 90 for a north-south pier). Piles reach y -1.7 so they stand in the sea |
| `pier_end.glb` | Pier head (sea end at +X) | 1668 | 4.2 / 4.3 / 3.1 | same section as the straight; bollards at (1.6, 0.45, +-1.1), ladder at x 2.08, tyre fenders, rope coil, harbour lamp at (1.5, *, -1.3) |
| `order_board.glb` | Cargo Order Board (`r4_orders`) (64, 12) | 504 | 3.3 / 3.0 / 1.1 | board face **z +0.07**; navy header strip centre (0, 2.42): Label3D "CARGO ORDER" in cream; three manifest rows at **y 2.05, 1.72, 1.39**: item icon Sprite3D at x -0.9, Label3D "20 / 34 timber" from x -0.55 (dark-brown text); brass bell at (1.65, 2.08, 0) for the bell ring. The dock DROP square goes in front at about (0, 0, 1.8) |
| `dock_crane.glb` | Order dock decor | 140 | 1.6 / 1.4 / 1.6 | pedestal; turntable top **y 1.42** |
| `dock_crane_jib.glb` | Crane cab + jib (moving part) | 312 | 4.5 / 2.6 / 1.1 | pivot = turntable: `add_model(path, crane_pos + Vector3(0, 1.42, 0))`; jib points +X with the hook at (3.3, 0.9..1.2, 0). Swing `rotation.y` 0 -> 1.2 rad and back over 1.5 s when an order ships (or add it to `Machine.arms`) |
| `buoy.glb` | Channel buoy (water or quay) | 196 | 0.9 / 1.7 / 0.9 | origin at the waterline; bob `position.y = sin(t * 1.6) * 0.06` |

### 1.4 Ship building (world units)
| File | Pad | Tris (per stage) | Size x/y/z (m) | Anchors |
|---|---|---:|---|---|
| `slipway.glb` | `r4_slipway` (62, -26), `r4_slipway2` (62, -40) | 1484 | 18.4 / 5.4 / 4.3 | origin = where `ship_hull.glb` goes. Sliding ways along **X**: the land part runs x -6..4 at ground level with keel blocks (top **y 0.62**) under the hull; a ramp drops from x 4 to y -1.6 at x 12 (put the sea, +X, there). Scaffold and winch hut at the back (-Z); yellow sign board face at (-5.3, 2.2, -1.21): Label3D "SLIPWAY" and the "Next ship in 0:12" line at z -1.19. Put the three slot squares (timber, deckboard, mast) on the camera side at about (-3, 0, 2.6), (0, 0, 2.6), (3, 0, 2.6) |
| `ship_hull.glb` | repeatable BuildSite on the slipway | 2412 (914 / 248 / 656 / 594) | 11.1 / 9.4 / 2.9 | three-masted schooner, long along X, **bow at +X (the sea)**, keel bottom on the keel blocks (y 0.62). stage1 keel, stem, sternpost, ribs and stringers; stage2 planked open hull (dark hold inside, red boot-top); stage3 deck, navy sheer strake, white rails, deckhouse, wheel; stage4 three masts with furled sails, gaffs, bowsprit, rigging, red pennant. **Launch** (GDD 7.6 B, 4 s): tween the hull node `position.x += 8`, `position.y -= 1.2` and `rotation.z` 0 -> -0.05 (TRANS_SINE, EASE_IN), splash at x +6, then hide it, reset to the slipway at stage 0 and let the stages rise again. Collision while it sits on the slipway: box (9.0, 3.0, 2.8) at (0, 1.5, 0) |

### 1.5 Buildings, gateway and landmark (world units)
| File | Pad | Tris (per stage) | Size x/y/z (m) | Anchors |
|---|---|---:|---|---|
| `crossing_post.glb` | `r4_crossing` (19, -20), Level Crossing | 564 | 1.2 / 2.8 / 0.7 | white crossbuck with red rim and twin red lamps face +Z. **Boom hinge at post-local (0.12, 1.05, 0)**, pointing +X. The road runs along Z (x 15.2..18.8) and the crossing path along X at z -20: west post at (14.9, 0, -21.6) rot 0, east post at (19.1, 0, -18.4) rot 180. Blink the lamps by swapping two tiny emissive quads, or skip it |
| `crossing_arm.glb` | barrier boom (moving part) | 384 | 4.1 / 0.48 / 0.22 | pivot = origin (hinge), 3.6 m red/white boom along +X, counterweight at -X. **Down = rotation 0 (across the road), up = `rotation.z` 80 deg**; tween 0.5 s. Lower both while a truck must stop (GDD 9.1: trucks stop 1 s when the player is on the crossing) |
| `crossing_closed.glb` | road-fence gap before `r4_crossing` | 620 | 0.7 / 1.6 / 3.0 | red/white plank barricade, 3.0 m along Z; stand it in the x 19.2 fence gap at z -20 and shrink it to 0.01 on unlock (like the Highland Gate doors) |
| `handcar_stop_navy.glb` | V4 handcar stop (26, 10) | 532 | 4.2 / 2.6 / 0.5 | same anchors as `maple/handcar_stop.glb` (sign face z +0.07, centre (0, 2.0, 0)), navy posts and lamp |
| `handcar_navy.glb` | handcar on the V4 stop's track | 444 | 1.3 / 1.5 / 1.6 | same as `maple/handcar.glb`, navy frame |
| `harbor_office.glb` | `r4_office` (28, 8) | 1028 | 4.3 / 4.1 / 4.5 | white weatherboards, navy roof, brass portholes, life ring. Door + porch at +Z; yellow sign board face (0, 2.1, 1.55): Label3D "OFFICE" at z 1.62; blocker (3.8, 3.0, 3.2); upgrade zone +Z 3.4 (same as the Highland Office) |
| `market_canopy_navy.glb` | Harbor Market (66, -2) | 1424 | 1.0 / 2.5 / 10.3 | V4 version of `shared/market_canopy.glb` (navy / cream stripes); place it exactly as ASSETS_LEFTOVER.md 2.9. Counters and till are the shared ones |
| `lighthouse.glb` | `r4_lighthouse` (72, -44) | 2012 (520 / 232 / 212 / 152 / 604 / 292) | 4.8 / 14.0 / 4.6 | 6 stages: rock base + plinth, white lower tower + navy door, red band + windows, white upper tower, navy gallery + rail + lantern, red dome + vane. Door faces +Z; collision cylinder r 1.6, h 10. The lantern glass (y 10.3..11.5) is pale yellow in the texture; if you want it to glow, add an OmniLight3D at (0, 10.9, 0) (range 6) rather than a second material |

### 1.6 Props (world units)
| File | Use | Tris |
|---|---|---:|
| `fish_crates.glb` | quay and market decor | 224 |
| `anchor_prop.glb` | harbour decor (anchor on a rock) | 276 |
| `bollard.glb` | quay edges, slipway | 188 |
| `harbor_lamp.glb` | harbour streets, pier, office | 172 |

## 2. Swap dicts

```gdscript
# Models.gd PATHS: add
	"redwood_trees": [
		"res://assets/models_v3/redwood/tree_redwoodA.glb",
		"res://assets/models_v3/redwood/tree_redwoodB.glb",
		"res://assets/models_v3/redwood/tree_redwoodC.glb",
	],
	"redwood_stump": "res://assets/models_v3/redwood/stump_redwood.glb",
	"log_stack_redwood": "res://assets/models_v3/redwood/log_stack_redwood.glb",
	"dune_grass": "res://assets/models_v3/redwood/dune_grass.glb",
	"driftwood": "res://assets/models_v3/redwood/driftwood.glb",
	"beach_rock": "res://assets/models_v3/redwood/beach_rock.glb",
	"redmill": "res://assets/models_v3/redwood/redwood_mill.glb",
	"redmill_blade": "res://assets/models_v3/redwood/redwood_mill_blade.glb",
	"decksaw": "res://assets/models_v3/redwood/deck_saw.glb",
	"decksaw_gang": "res://assets/models_v3/redwood/deck_saw_gang.glb",
	"mastlathe": "res://assets/models_v3/redwood/mast_lathe.glb",
	"mastlathe_log": "res://assets/models_v3/redwood/mast_lathe_log.glb",
	"skidder": "res://assets/models_v3/redwood/log_skidder.glb",
	"forklift_navy": "res://assets/models_v3/redwood/forklift_navy.glb",
	"cargo_ship": "res://assets/models_v3/redwood/cargo_ship.glb",
	"fishing_boat": "res://assets/models_v3/redwood/fishing_boat.glb",
	"pier": "res://assets/models_v3/redwood/pier_straight_4m.glb",
	"pier_end": "res://assets/models_v3/redwood/pier_end.glb",
	"order_board": "res://assets/models_v3/redwood/order_board.glb",
	"dock_crane": "res://assets/models_v3/redwood/dock_crane.glb",
	"dock_crane_jib": "res://assets/models_v3/redwood/dock_crane_jib.glb",
	"slipway": "res://assets/models_v3/redwood/slipway.glb",
	"ship_hull": "res://assets/models_v3/redwood/ship_hull.glb",
	"harbor_office": "res://assets/models_v3/redwood/harbor_office.glb",
	"market_canopy_navy": "res://assets/models_v3/redwood/market_canopy_navy.glb",
	"crossing_post": "res://assets/models_v3/redwood/crossing_post.glb",
	"crossing_arm": "res://assets/models_v3/redwood/crossing_arm.glb",
	"crossing_closed": "res://assets/models_v3/redwood/crossing_closed.glb",
	"handcar_stop_navy": "res://assets/models_v3/redwood/handcar_stop_navy.glb",
	"handcar_navy": "res://assets/models_v3/redwood/handcar_navy.glb",
	"lighthouse": "res://assets/models_v3/redwood/lighthouse.glb",
	"buoy": "res://assets/models_v3/redwood/buoy.glb",
	"fish_crates": "res://assets/models_v3/redwood/fish_crates.glb",
	"anchor_prop": "res://assets/models_v3/redwood/anchor_prop.glb",
	"bollard": "res://assets/models_v3/redwood/bollard.glb",
	"harbor_lamp": "res://assets/models_v3/redwood/harbor_lamp.glb",
```

```gdscript
# Items.DEFS: add (cells and layers are the GDD 7.3 numbers; models are sized to fit them)
	"red_log": {"path": "res://assets/models_v3/items/item_red_log.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.42, "cell": Vector2(1.3, 0.5)},
	"timber": {"path": "res://assets/models_v3/items/item_timber.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.4, "cell": Vector2(1.3, 0.45)},
	"deckboard": {"path": "res://assets/models_v3/items/item_deckboard.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.09, "cell": Vector2(1.1, 0.35)},
	"mast": {"path": "res://assets/models_v3/items/item_mast.glb", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.4, "cell": Vector2(0.4, 2.4)},
```
| File | Item | Tris | Size x/y/z (m) |
|---|---|---:|---|
| `items/item_red_log.glb` | red_log | 140 | 1.20 / 0.41 / 0.41, thick red-brown log along X, salmon ring ends |
| `items/item_timber.glb` | timber | 120 | 1.24 / 0.38 / 0.42, big square heartwood timber, ring ends, navy mill stamp on top |
| `items/item_deckboard.glb` | deckboard | 80 | 1.05 / 0.08 / 0.32, dark board with three grooves on top |
| `items/item_mast.glb` | mast | 308 | 0.40 / 0.37 / 2.31, long along **Z** (like the canoe), tapered spar d 0.36 -> 0.22, iron bands, crosstrees near the top, navy tip |

Full piles (my calc): 36 red logs 5.0k tris, 48 timbers 5.8k, 48 deckboards 3.8k, 12 masts 3.7k. No `max_drawn` needed.

```gdscript
# Models.ICONS: add (64 px; _128 and the 256 master exist too)
	"red_log": "res://assets/icons/red_log_64.png",
	"timber": "res://assets/icons/timber_64.png",
	"deckboard": "res://assets/icons/deckboard_64.png",
	"mast": "res://assets/icons/mast_64.png",
# Models.GROUND: add
	4: "res://assets/textures/ground/grass_coast.png",
	"sand": "res://assets/textures/ground/sand_beach.png",
```

Tree kind (GDD 7.2 / Balance): `"redwood": {"log": "red_log", "logs": 8, "hits": 7, "regrow": 14.0, "scale": 1.6}` with
models `PATHS.redwood_trees`, stump `PATHS.redwood_stump`, scale `randf_range(2.3, 2.8) * 1.6`.

## 3. Icons: `res://assets/icons/`
`red_log`, `timber`, `deckboard`, `mast`, each as `<id>.png` (256), `_128`, `_64`. Camera, outline and sizes are identical
to M1/M2 (`um render3d --preset iso8 --headings 1 --elevation 35 --forward-yaw -30`, 3 px outline `#3a2618`). All four
were checked at 48 px on dark green and still read (the mast has crosstrees so it does not read as a spyglass).
Outline contrast (my calc): 13.4:1 on the HUD cream, 4.1:1 on the Redwood Coast grass.

## 4. Ground: `res://assets/textures/ground/`
- `grass_coast.png`: 512 x 512 (opaque, alpha 255), 4 x 4 m per tile, coastal grass with sandy patches and pale marram flecks. Mean
  `#6e9546` (my calc), std 3-5 of 255. Plug it in as `grass_tex` on the V4 ground plane as ASSETS_M1.md section 4 describes.
- `sand_beach.png`: 512 x 512 (opaque), warm sand with tiny shell flecks, mean `#e0cb9e`. Use it as the V4 plane's `dirt_tex`
  (paths and plazas become sand) and for the east shore strip ("sand blend toward the east shore", GDD 9.3): either a
  second plane along x 70..77 or a shore band in the ground shader.
Same Blender 4D-torus material as M1/M2 plus `um sprite seamless` / `tile-preview`.

## 5. Valley 4 deco scatter (suggested sets for a `_scatter_deco_v4`)
Same counts formula as V2/V3. Near the east shore (x > 66): `dune_grass` (120), `driftwood` (40), `beach_rock` (60).
Inland: keep `rock_*`, mushrooms and the V1 `grass` clumps at half count, no flowers (the redwood floor is shady), and add
`beach_rock` (40). Put `buoy` x3 on the water off the pier and `fish_crates`, `bollard`, `harbor_lamp` along the quay.

## 6. Border-forest imposters: `res://assets/textures/imposters/border_trees_atlas_m3.png`
1024 x 1024, 4 x 4 cells of 256 px: `tree_redwoodA` 0-3, `tree_redwoodB` 4-7, `tree_redwoodC` 8-11,
`tree_pineTallB_detailed` 12-15 (`border_trees_atlas_m3.json`). Same card, camera, pixels per unit (140) and ground row
(246) as the M1/M2 atlases, so the M2 shader change (`uniform float grid = 4.0`) covers it. The card must be scaled by
the redwood's 1.6x like the mesh.

## 7. Not made / open
- **Shipwright workers** (`r4_builders`): no new character. Reuse a carrier character (KayKit set in `chars/`) with the
  navy cap colour if you want them told apart; the GDD gives them no special model.
- **Sea:** the water surface, bow wave and launch splash are shader/particle work for the Godot side (the boats and the
  slipway ramp are built for a waterline at y 0, with the ground at y 0 inland).
- **Lighthouse beam:** not built; an OmniLight3D in the lantern is cheaper than a rotating beam mesh on a phone.

## Rebuild
```bash
cd /home/mm/MWM/projects/timber-valley
/home/mm/.local/bin/blender -b --python tools/lookdev/build_m3.py        # models (GPU OptiX bake when present)
python3 tools/lookdev/make_icons_m345.py m3                             # icons
tools/lookdev/make_ground_m345.sh grass_coast sand_beach                 # ground tiles + 3x3 previews
python3 tools/lookdev/make_imposters_m345.py m3                         # border_trees_atlas_m3
python3 tools/lookdev/make_compare_m345.py m3                           # tools/lookdev/compare_m3.png
python3 tools/lookdev/contrast_m345.py                                  # contrast numbers (my calc)
```
