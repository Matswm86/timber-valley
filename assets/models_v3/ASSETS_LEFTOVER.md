# Leftover prototype graphics -> v3 replacements (Home Valley + Birch Bend)

Built 2026-10-01 on branch `v3-m2`. Review sheet (old in-game vs new): `tools/lookdev/compare_leftover.png`.
Builder: `tools/lookdev/build_leftover.py` (report `tools/lookdev/build_leftover_report.json`). All own work, CC0.

Every GLB has one mesh, one material and one embedded texture (albedo x height gradient x baked AO with a ground
contact shadow), like the rest of models_v3, and was load-checked in Godot 4.6 (`load()` + `instantiate()`, 0 errors).
Units are metres and the scale is always **1.0**. Axes match Godot: +Z is toward the camera ("front"), +Y is up.
"Origin" below is the node the old code built into (`m.body`, `root`, `seg`, ...), so the new file goes at
`Vector3.ZERO` unless a position is given.

After this pass, no Kenney model is loaded by `scripts/` (the 23 `res://assets/models/...` loads listed in section 1).
Kept as code on purpose: `ChainSaw` (animated teeth), the belt top surface (`belt.gdshader` scrolls it), the Mega Saw's
giant log (it shrinks while being cut), ground/river/water shaders, `Zone` markers, `UnlockPad` tiles, the guide arrow and
particles. The river "walls" in `World._bounds()` are collision only and have no visuals, so there is nothing to replace.

## 1. Map: old -> new

| # | Old (file: line in today's code) | New file | Tris | Notes |
|---|---|---|---:|---|
| 1 | `_dress_sawmill()` boxes, feet, frame, control box, 5-log pile (World.gd 648-697), frame orange | `home/sawmill_body_orange.glb` | 1412 | sawmill1 |
| 2 | same, frame green | `home/sawmill_body_green.glb` | 1412 | sawmill2 |
| 3 | `_shed()` + `survival/workbench`, `survival/chest`, `survival/signpost-single` (`_build_office`) | `home/office_hut.glb` | 1592 | open hut, desk, cash chest, notice board with a green up-arrow |
| 4 | `_shed()` + `survival/workbench`, `workbench-grind`, `furniture/chair` (`_build_carpentry`) | `home/carpentry_shed.glb` | 1704 | workbench + vise, orange saw bench, chair in progress |
| 5 | `Machine.add_saw_blade()` cylinder + 8 box teeth | `home/saw_blade.glb` | 496 | spinner, disc normal = local Z |
| 6 | `_build_cnc()` base box + `factory/machine-window`, `screen-small`, `lever-single` | `home/cnc_router.glb` | 1232 | gantry router, screen stand, lever box |
| 7 | `factory/cog-a` (CNC spinner) | `home/cnc_cog.glb` | 360 | spinner, faces the camera |
| 8 | `_build_factory()` base + `factory/machine-fortified`, `machine`, `hopper-square`, `structure-yellow-tall` (chimney) | `home/bookcase_factory.glb` | 1820 | open-front hall, brick chimney, hopper, saw unit, press, roller table |
| 9 | `factory/robot-arm-a`, `robot-arm-b` | `home/factory_arm.glb` (use twice) | 608 | pivot = base, reaches toward -Z |
| 10 | `_build_lodge()` cylinders, roof boxes, door, windows, porch + `furniture/bench`, `loungeChair` | `home/grand_lodge.glb` | 2228 | log cabin, red roof, porch, bench, rocking chair, flower boxes |
| 11 | lodge window glow boxes | `home/lodge_windows.glb` | 8 | **emissive**, not baked |
| 12 | MegaSaw bed, rails, gantry, mound (MegaSaw.gd 31-77) | `home/megasaw_body.glb` | 1520 | |
| 13 | `factory/crane.glb` (MegaSaw) | `home/megasaw_crane.glb` | 844 | tower crane |
| 14 | MegaSaw `_crane_hook` box | `home/crane_hook.glb` | 208 | origin = hook bottom |
| 15 | road sign logs + board (`"roadsign"`) | `home/road_sign.glb` | 580 | |
| 16 | Conveyor rails (2 BoxMesh per segment) | `shared/belt_rails.glb` | 300 | stretch along Z |
| 17 | Conveyor legs (2 BoxMesh per station) | `shared/belt_legs.glb` | 220 | one leg pair |
| 18 | (new) | `shared/belt_end.glb` | 460 | optional end roller |
| 19 | palisade `Shapes.log_mesh(0.16, 1.0)` MultiMesh (`_palisades`, `_palisades_v2`) | `shared/palisade_post.glb` | 56 | was about 84 tris per post |
| 20 | 5 x `nature/bridge_wood.glb` (`_river`, Models "bridge_plank") | `shared/bridge_river.glb` | 1788 | one piece, 2.6 m walkway |
| 21 | Shop counter boxes (`Shop.add_shelf`) | `shared/shop_counter.glb` | 308 | |
| 22 | Shop till boxes + `survival/chest` (`Shop._build_till`) | `shared/shop_till.glb` | 668 | cash chest with gold coins |
| 23 | Shop canopy (12 stripe boxes + 3 posts, `Shop._build_canopy`) | `shared/market_canopy.glb` (V1, V2) / `maple/market_canopy_teal.glb` (V3) | 1424 | |
| 24 | `car/truck-flat.glb` x 1.7 (TruckDock, Models "truck") | `shared/truck_flatbed.glb` | 1796 | scale 1.0 |
| 25 | TruckDock slab + 2 x `factory/structure-yellow-tall` | `shared/truck_dock.glb` | 588 | |
| 26 | road PlaneMesh grey + 40 dash PlaneMeshes (`_road`) | `assets/textures/ground/road_tile.png` | - | 512 px = 3.6 m x 4 m |

Draw calls (my count from the code, belts and palisades excluded): rows 1-15 and 20-26 replace about 210 MeshInstance
nodes in Valley 1 with 25 GLB instances. The node counts are lodge 44, the two sawmills 38, office + carpentry 26, market 24,
road 41, Mega Saw 11, factory 7, CNC 5, bridge 5, dock 4 and sign 3. Kenney sub-meshes come on top of that. Each conveyor
segment goes from 3 + 2 x legs nodes to 2 + legs.

## 2. How to place each one

### 2.1 Conveyor (`Conveyor._build_segment`): modular pieces
Today each segment is a `Node3D` `seg` with `Basis.looking_at(b - a)` (local -Z points from a to b), a belt box
`len + 0.8` long, two rails and leg pairs every 1.6 m. New:
```gdscript
const RAILS := preload("res://assets/models_v3/shared/belt_rails.glb")
const LEGS := preload("res://assets/models_v3/shared/belt_legs.glb")
# keep the belt MeshInstance3D (BELT_SHADER) exactly as today, then replace the two rails:
var rails: Node3D = RAILS.instantiate()
rails.scale = Vector3(1, 1, len + 0.8)   # 1 m piece with flat ends: stretching along Z is clean
seg.add_child(rails)
# and the leg loop: one GLB per station instead of two BoxMesh legs
for i in n + 1:
	var z := -len * 0.5 + len * float(i) / maxf(n, 1)
	var lg: Node3D = LEGS.instantiate()
	lg.position = Vector3(0, 0, z)
	seg.add_child(lg)
```
- `belt_rails.glb`: z -0.5..0.5, rails at x +-0.45, yellow lip top **y 0.642** (old rail top 0.65), grey side frame
  y 0.33..0.55, and a skirt under the belt. The belt top stays at `HEIGHT` 0.55.
- `belt_legs.glb`: legs at x +-0.35, y 0..0.4 (the old legs were `HEIGHT - 0.1` = 0.45 tall), plus a cross brace and feet.
- `belt_end.glb` (optional): a drum across the belt at y 0.48 plus yellow side plates. Put one at `points[0] - dir * 0.4`
  and one at `points[-1] + dir * 0.4`, with `basis = seg.basis` of the first and last segment. It hides the square
  belt-box ends at the piles.
- Batching (your parallel work): legs are identical per station, so one MultiMesh of `belt_legs` per region works.
  Use `World._first_mesh()` for the mesh. The rails need per-segment scale, which a MultiMesh transform also carries.

### 2.2 Sawmills (`_dress_sawmill(m, frame)`)
Delete the `_box` calls for the bed, rails, feet, frame, crossbar, cap, control box and button, and the 5 `Shapes.log_node`
pile logs. Add:
```gdscript
var body_path := "res://assets/models_v3/home/sawmill_body_%s.glb" % ("orange" if frame.r > 0.6 else "green")
m.add_model(body_path, Vector3.ZERO, 1.0)
```
Keep the belt MeshInstance (y 0.52, 4.3 long), the ChainSaw at (0, 1.28, 0.2), mouths, dust and the blocker. The
geometry uses the same coordinates as the old boxes: bed top y 0.5, rails at z -0.42 and 0.82 (top 0.63), frame posts at
x +-0.75 z -0.45 (top cap y 2.92), control box at (1.4, 0.8, -0.75), log pile around (-1.2, 0, -1.25). The bed colour
stays V1 blue `Color(0.2, 0.5, 0.86)`.

### 2.3 Upgrade Office (`_build_office`)
Replace `_shed(root, ...)` and the three `_model(...)` calls with
`_model("res://assets/models_v3/home/office_hut.glb", Vector3.ZERO, 1.0, 0, root)`. The footprint is the same 3.2 x 2.4
(roof overhang to 4.3 x 3.0); collision and zone are unchanged. The lean-to roof now covers the back 50% and is high at
the back, so the camera sees the desk.

### 2.4 Carpentry (`_build_carpentry`)
Replace `_shed(m.body, 3.6, 2.6, 2.3, ...)` and the three `m.add_model(...)` calls with
`m.add_model("res://assets/models_v3/home/carpentry_shed.glb", Vector3.ZERO, 1.0)`. The saw bench top is y 0.95 at
(0.8, *, 0.3) with a slot along Z, so the blade at (0.8, 1.05, 0.35) sticks up through it like before.
For the blade, change `Machine.add_saw_blade(pos, radius)` to load the GLB into the same pivot:
```gdscript
var pivot := Node3D.new()
pivot.position = pos
var blade: Node3D = load("res://assets/models_v3/home/saw_blade.glb").instantiate()
blade.scale = Vector3.ONE * (radius / 0.3)   # the GLB is r 0.3
pivot.add_child(blade)                       # disc normal = local Z, so the existing spin about FORWARD works
body.add_child(pivot)
spinners.append(pivot)
return pivot
```
The caller's `saw.rotation_degrees.y = 90` stays.

### 2.5 CNC (`_build_cnc`)
Replace the base `_box` and the four `m.add_model(...)` calls with
`m.add_model("res://assets/models_v3/home/cnc_router.glb", Vector3.ZERO, 1.0)` and
`var cog := m.add_model("res://assets/models_v3/home/cnc_cog.glb", Vector3(0, 2.45, 0), 1.0)` followed by
`m.spinners.append(cog)`. The cog now faces the camera and spins about local Z (it used to lie flat). Table top y 0.93;
mouths (-1.1, 1.0, 0) and (1.1, 0.8, 0) still land on the table. Blocker unchanged.

### 2.6 Bookcase Factory (`_build_factory`)
Replace the base `_box` and the six `m.add_model(...)` calls with:
```gdscript
m.add_model("res://assets/models_v3/home/bookcase_factory.glb", Vector3.ZERO, 1.0)
m.arms.append(m.add_model("res://assets/models_v3/home/factory_arm.glb", Vector3(-2.3, 0.22, 1.2), 1.0))
m.arms.append(m.add_model("res://assets/models_v3/home/factory_arm.glb", Vector3(2.4, 0.22, 1.2), 1.0))
m.add_smoke(Vector3(-1.9, 3.8, -1.5))   # chimney top is y 3.7 now
```
The hopper rim is at y 1.47 around (-2.25, -0.55), matching `mouth_in` (-2.2, 1.4, -0.4). The roller table runs to x 2.25
at z 0.35, matching `mouth_out` (2.2, 0.9, 0.4). The arms reach toward -Z (into the hall) at rest yaw 0, and
`Machine._process` swings them +-0.9 rad as before. Remove the `chimney` node name lookup if anything used it (nothing
in scripts/ does today).

### 2.7 Grand Lodge (`_build_lodge`)
Replace everything from the log loop down to the lounge chair with:
```gdscript
_model("res://assets/models_v3/home/grand_lodge.glb", Vector3.ZERO, 1.0, 0, root)
var win := _model("res://assets/models_v3/home/lodge_windows.glb", Vector3.ZERO, 1.0, 0, root)
for mi in win.find_children("*", "MeshInstance3D", true, false):
	(mi as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
```
Footprint 7 x 5 walls (logs overhang to 7.5 x 5.5), porch to z +4.5, ridge y 5.2 and chimney top y 6.2 at (2.2, *, -0.8):
set the smoke to `Vector3(2.2, 6.4, -0.8)`. `lodge_windows.glb` holds two warm panes per window at z 2.815 with emission
`Color(1.0, 0.82, 0.5)` x 1.6 (the old glow boxes). Collision (7.4, 4, 5.4) and plaza are unchanged.

### 2.8 Mega Saw (`MegaSaw.setup`)
Replace the bed, the two rails, the three gantry boxes and the mound with
`body.add_child(load("res://assets/models_v3/home/megasaw_body.glb").instantiate())`. Keep the belt (y 0.82), the
ChainSaw at (1.6, 2.35, 0) and the giant log. Crane:
```gdscript
var crane: Node3D = load("res://assets/models_v3/home/megasaw_crane.glb").instantiate()
crane.position = Vector3(-4.2, 0, -2.2)
crane.rotation_degrees.y = -20     # jib (+X, y 6.25, tip x 4.4) points over the log drop path; scale 1.0 (was 1.5)
body.add_child(crane)
```
Hook: replace the `Shapes.box_node` inside `_crane_hook` with
`_crane_hook.add_child(load("res://assets/models_v3/home/crane_hook.glb").instantiate())`. Its origin is the hook
bottom, and the cable runs up 3.0 m like the old box.

### 2.9 Market (`Shop`): valid for every valley
- `_build_till()`: replace both `_box` calls and the chest with
  `root.add_child(load("res://assets/models_v3/shared/shop_till.glb").instantiate())`. Counter 1.3 x 0.9 x 1.6, top y 0.96.
  The cash chest sits at the old chest spot (0, 0.96, 0.3) and is symmetric, so it needs no mirror.
- `add_shelf()`: replace both `_box` calls with `shop_counter.glb` at (0, 0, 0). Top **y 0.62** = the ItemStack height.
  Symmetric in X, so mirrored markets work.
- `_build_canopy()`: replace the stripes and posts with
  ```gdscript
  var path := "res://assets/models_v3/maple/market_canopy_teal.glb" if region == 3 else "res://assets/models_v3/shared/market_canopy.glb"
  var c: Node3D = load(path).instantiate()
  c.position = Vector3(0, 0, (3.9 + till_z - 1.0) * 0.5)   # = -1.15: the canopy is 10.1 m long, centred
  c.rotation_degrees.y = 0.0 if side > 0.0 else 180.0       # 180 deg = the mirrored layout (cloth at x -0.95)
  add_child(c)
  ```
  Cloth x 0.45..1.47 tilted 14 deg down outward, top y 2.49, posts at x 0.55, z -5.05 / 0 / +5.05.

### 2.10 Export truck + dock (`TruckDock.setup`, `Models.PATHS["truck"]`)
- Replace the slab MeshInstance and the two `structure-yellow-tall` posts with `truck_dock.glb` at (0, 0, 0). The slab is
  at x +0.6 like today, top **y 0.18** (pile at y 0.18 unchanged), with a timber bumper on the road edge (+X) and two
  yellow lamp posts at (2.25, 0, +-2.3).
- Truck: `Models.PATHS["truck"] = "res://assets/models_v3/shared/truck_flatbed.glb"` and set `model.scale = Vector3.ONE`
  (was 1.7). Cab at +Z like the Kenney truck (TruckDock still turns it 180 deg). The flatbed top is **y 1.25** over
  z -2.35..0.5, so `bed.position = (0, 1.25, -0.9)` is unchanged. Size 2.32 x 2.35 x 4.75 (Kenney x1.7: 2.55 x 2.21 x 4.67).

### 2.11 Palisades (`_palisades`, `_palisades_v2`, and Valley 3's later)
```gdscript
var post := _first_mesh("res://assets/models_v3/shared/palisade_post.glb")
mm.mesh = post[0]                         # and drop mmi.material_override (the texture is in the mesh)
# transform: base is at y 0 now, so position y = 0 (was hgt * 0.5); keep Basis(...).scaled(Vector3(1, hgt, 1))
xforms.append(Transform3D(basis, Vector3(p.x, 0.0, p.y)))
```
r 0.16, height 1.0 with a pointed pale top, 56 tris (my count: the V1 lines are about 480 posts, 27k tris, down from about
40k with the 14-sided CylinderMesh). Chunk it with `_multimesh()` like the forest so it culls.

### 2.12 River bridge (`_river`, `Models.PATHS["bridge_plank"]`)
Replace the 5-piece loop with
`_model("res://assets/models_v3/shared/bridge_river.glb", Vector3(RIVER_X, 0, BRIDGE_Z), 1.0, 0)`. Deck top **y 0.10**
(water y 0.06), walkway z -1.3..1.3 (GDD: 2.4 m clear), handrails at z +-1.33 (inside the corridor walls at +-1.4),
spans x -4.3..4.3 plus bank stones to +-4.76. Point `Models.PATHS["bridge_plank"]` at the same file or drop the key.

### 2.13 Road (`_road`)
```gdscript
mat.albedo_texture = load("res://assets/textures/ground/road_tile.png")
mat.uv1_scale = Vector3(1, 170.0 / 4.0, 1)   # tile = full road width x 4 m
mat.albedo_color = Color.WHITE
```
and delete the 40 dash MeshInstances. The tile carries one cream dash per 4 m (1.4 m x 0.14 m, the same spacing as
today), worn darker edges and faint tyre tracks. It repeats along the road only. Import it with mipmaps.

### 2.14 Road sign (`"roadsign"`)
Replace the two `Shapes.log_node` posts and the board `_box` with `road_sign.glb` at `sg` (0, 0, 0). The board face is at
z +0.07, centre y 2.1, so the existing Label3D at (0, 2.1, 0.09) sits on it. There is a small green roof on top.

## 3. Not changed, on purpose
- **ChainSaw.gd**: rounded-box bar with moving teeth. Its look matches v3 already, and baking it would kill the
  tooth animation.
- **UnlockPad / Zone / guide arrow**: these are UI on the ground. Their flat look is a readability choice.
- **Birch gate prop** already uses `nature/fence_simple.glb` (v3).

## Rebuild
```bash
cd /home/mm/MWM/projects/timber-valley
/home/mm/.local/bin/blender -b --python tools/lookdev/build_leftover.py      # models (GPU OptiX bake when present)
python3 tools/lookdev/make_road_tile.py                                       # road tile + 3x3 preview
python3 tools/lookdev/make_compare_leftover.py                                # tools/lookdev/compare_leftover.png
```
