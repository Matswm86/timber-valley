class_name Models
extends RefCounted

## Every model path in one place, so swapping an asset is one edit.
## Assets from assets/models_v3/ASSETS_M1.md, ASSETS_LEFTOVER.md and ASSETS_M2.md (graphic-designer, 2026-10-01).
## "kenney" units = scaled ~2.2-3.6 like models_v3/nature; "world" units = metres, scale 1.0.

const PATHS := {
	# chop trees (kenney units)
	"birch_trees": [
		"res://assets/models_v3/birch/tree_birchA.glb",
		"res://assets/models_v3/birch/tree_birchB.glb",
		"res://assets/models_v3/birch/tree_birchC.glb",
	],
	"birch_stump": "res://assets/models_v3/birch/stump_birch.glb",
	"default_stump": "res://assets/models_v3/nature/stump_roundDetailed.glb",
	# props (kenney units)
	"log_stack_birch": "res://assets/models_v3/birch/log_stack_birch.glb",
	"reeds": "res://assets/models_v3/birch/reeds.glb",
	"lilypads": "res://assets/models_v3/birch/lilypads.glb",
	# machines and buildings (world units)
	"lathe": "res://assets/models_v3/birch/veneer_lathe.glb",
	"lathe_log": "res://assets/models_v3/birch/veneer_lathe_log.glb",
	"press": "res://assets/models_v3/birch/plywood_press.glb",
	"press_plate": "res://assets/models_v3/birch/plywood_press_plate.glb",
	"boatshop": "res://assets/models_v3/birch/boat_workshop.glb",
	"riverside_office": "res://assets/models_v3/birch/riverside_office.glb",
	"barge": "res://assets/models_v3/birch/barge.glb",
	"barge_landing": "res://assets/models_v3/birch/barge_landing.glb",
	"flume_straight": "res://assets/models_v3/birch/flume_straight.glb",
	"flume_chute": "res://assets/models_v3/birch/flume_chute.glb",
	"flume_end": "res://assets/models_v3/birch/flume_end.glb",
	"boathouse": "res://assets/models_v3/birch/boathouse.glb",
	"gate_fence": "res://assets/models_v3/nature/fence_simple.glb",
	# Home Valley buildings and machines (ASSETS_LEFTOVER.md, world units, scale 1.0)
	"sawmill_body_orange": "res://assets/models_v3/home/sawmill_body_orange.glb",
	"sawmill_body_green": "res://assets/models_v3/home/sawmill_body_green.glb",
	"office_hut": "res://assets/models_v3/home/office_hut.glb",
	"carpentry_shed": "res://assets/models_v3/home/carpentry_shed.glb",
	"saw_blade": "res://assets/models_v3/home/saw_blade.glb",
	"cnc_router": "res://assets/models_v3/home/cnc_router.glb",
	"cnc_cog": "res://assets/models_v3/home/cnc_cog.glb",
	"bookcase_factory": "res://assets/models_v3/home/bookcase_factory.glb",
	"factory_arm": "res://assets/models_v3/home/factory_arm.glb",
	"grand_lodge": "res://assets/models_v3/home/grand_lodge.glb",
	"lodge_windows": "res://assets/models_v3/home/lodge_windows.glb",
	"megasaw_body": "res://assets/models_v3/home/megasaw_body.glb",
	"megasaw_crane": "res://assets/models_v3/home/megasaw_crane.glb",
	"crane_hook": "res://assets/models_v3/home/crane_hook.glb",
	"road_sign": "res://assets/models_v3/home/road_sign.glb",
	# shared by every valley (world units)
	"belt_rails": "res://assets/models_v3/shared/belt_rails.glb",
	"belt_legs": "res://assets/models_v3/shared/belt_legs.glb",
	"belt_end": "res://assets/models_v3/shared/belt_end.glb",
	"palisade_post": "res://assets/models_v3/shared/palisade_post.glb",
	"bridge_river": "res://assets/models_v3/shared/bridge_river.glb",
	"shop_counter": "res://assets/models_v3/shared/shop_counter.glb",
	"shop_till": "res://assets/models_v3/shared/shop_till.glb",
	"market_canopy": "res://assets/models_v3/shared/market_canopy.glb",
	"truck": "res://assets/models_v3/shared/truck_flatbed.glb",
	"truck_dock": "res://assets/models_v3/shared/truck_dock.glb",
	# Maple Highlands (ASSETS_M2.md): trees and nature in kenney units, the rest in world units
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
	# Redwood Coast (ASSETS_M3.md): trees and nature in kenney units, the rest in world units
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
	# Frost Peaks (ASSETS_M4.md)
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
	# Grand Timber Station (ASSETS_M5.md)
	"grand_station": "res://assets/models_v3/station/grand_station.glb",
	"station_plot": "res://assets/models_v3/station/station_plot.glb",
	"platform_slots": [
		"res://assets/models_v3/station/platform_slot_v1.glb",
		"res://assets/models_v3/station/platform_slot_v2.glb",
		"res://assets/models_v3/station/platform_slot_v3.glb",
		"res://assets/models_v3/station/platform_slot_v4.glb",
		"res://assets/models_v3/station/platform_slot_v5.glb",
	],
	"platform_slot_v1": "res://assets/models_v3/station/platform_slot_v1.glb",
	"platform_slot_v2": "res://assets/models_v3/station/platform_slot_v2.glb",
	"platform_slot_v3": "res://assets/models_v3/station/platform_slot_v3.glb",
	"platform_slot_v4": "res://assets/models_v3/station/platform_slot_v4.glb",
	"platform_slot_v5": "res://assets/models_v3/station/platform_slot_v5.glb",
	"rail_bridge": "res://assets/models_v3/station/rail_bridge_8m.glb",
	"rail_road_crossing": "res://assets/models_v3/station/rail_road_crossing_4m.glb",
	"express_loco": "res://assets/models_v3/station/express_loco.glb",
	"express_tender": "res://assets/models_v3/station/express_tender.glb",
	"express_coach": "res://assets/models_v3/station/express_coach.glb",
	"station_bench": "res://assets/models_v3/station/station_bench.glb",
	"clock_post": "res://assets/models_v3/station/clock_post.glb",
	"flower_planter": "res://assets/models_v3/station/flower_planter.glb",
	"luggage_cart": "res://assets/models_v3/station/luggage_cart.glb",
	"station_lamp": "res://assets/models_v3/station/station_lamp.glb",
}

## Stand-ins for Redwood Coast, Frost Peaks and the Grand Timber Station until the graphic
## designer's models_v3/redwood, frost and station kits land (ASSETS_M3/M4/M5.md). Each is an
## existing v3 model, recoloured: "path" (+ "tint", multiplies every surface's albedo), "paths"
## for tree lists, or "parts" for a staged build site ([key or path, position, scale, rot_y] per
## stage, built as children stage1..stageN). Swapping in the real art = add the key to PATHS
## (PATHS wins), then delete it here. "scale"/"rot" only apply to the stand-in (item models).
const STANDINS := {
	# Every M3-M5 stand-in was replaced by the designer's art on 2026-10-03 (ASSETS_M3/M4/M5.md);
	# the mechanism stays for future kits.
}

## Road surface: 512 px = full road width x 4 m, one cream dash per tile.
const ROAD_TILE := "res://assets/textures/ground/road_tile.png"

## Border forest imposter atlas (ASSETS_M1.md section 5); the _far meshes stay as fallback.
const IMPOSTER_ATLAS := "res://assets/textures/imposters/border_trees_atlas.png"
const IMPOSTER_JSON := "res://assets/textures/imposters/border_trees_atlas.json"
## Maple Highlands edge atlas (ASSETS_M2.md section 6): 4 x 4 cells.
const IMPOSTER_ATLAS_M2 := "res://assets/textures/imposters/border_trees_atlas_m2.png"
## Redwood Coast and Frost Peaks edge atlases (ASSETS_M3/M4.md section 6): 4 x 4 cells.
const IMPOSTER_ATLAS_M3 := "res://assets/textures/imposters/border_trees_atlas_m3.png"
const IMPOSTER_ATLAS_M4 := "res://assets/textures/imposters/border_trees_atlas_m4.png"

## Ground tiles, 4 x 4 m per tile.
const GROUND := {
	1: "res://assets/textures/ground/grass_v1.png",
	2: "res://assets/textures/ground/grass_birch.png",
	3: "res://assets/textures/ground/grass_maple.png",
	# Redwood Coast and Frost Peaks (ASSETS_M3/M4.md section 4).
	4: "res://assets/textures/ground/grass_coast.png",
	5: "res://assets/textures/ground/snow_frost.png",
	"dirt": "res://assets/textures/ground/dirt_path.png",
	"sand": "res://assets/textures/ground/sand_beach.png",
	"snow_packed": "res://assets/textures/ground/snow_packed.png",
	"station": "res://assets/textures/ground/station_paving.png",
}

## HUD item icons (64 px).
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
	"maple_log": "res://assets/icons/maple_log_64.png",
	"beam": "res://assets/icons/beam_64.png",
	"floorboard": "res://assets/icons/floorboard_64.png",
	"cabin_kit": "res://assets/icons/cabin_kit_64.png",
	"red_log": "res://assets/icons/red_log_64.png",
	"timber": "res://assets/icons/timber_64.png",
	"deckboard": "res://assets/icons/deckboard_64.png",
	"mast": "res://assets/icons/mast_64.png",
	"frost_log": "res://assets/icons/frost_log_64.png",
	"dry_lumber": "res://assets/icons/dry_lumber_64.png",
	"skis": "res://assets/icons/skis_64.png",
	"sled": "res://assets/icons/sled_64.png",
	"guitar": "res://assets/icons/guitar_64.png",
}


## Shop and price-tag icons (128 px), same names as ICONS.
static func shop_icon(item: String) -> Texture2D:
	var p := str(ICONS.get(item, "")).replace("_64.png", "_128.png")
	return load(p) as Texture2D if p != "" and ResourceLoader.exists(p) else null


static func hud_icon(item: String) -> Texture2D:
	var p := str(ICONS.get(item, ""))
	return load(p) as Texture2D if p != "" and ResourceLoader.exists(p) else null


## The product a pad title names ("Carpentry: Chairs", "Hire a Plank Carrier"), or "".
## log_type: what "log" means in that valley (birch_log in Birch Bend, maple_log in the Highlands).
static func item_in_title(title: String, log_type: String = "log") -> String:
	var t := " " + title.to_lower().replace(":", " ") + " "
	if t.contains(" cabin kit"):
		return "cabin_kit"
	if t.contains(" dry lumber"):
		return "dry_lumber"
	if t.contains(" sleds "):
		return "sled"
	for item in ["bookcase", "plywood", "veneer", "canoe", "floorboard", "beam", "chair", "table", "plank",
			"timber", "deckboard", "mast", "skis", "guitar", "log"]:
		if t.contains(" %s " % item) or t.contains(" %ss " % item):
			return log_type if item == "log" else item
	return ""


static func path(key: String) -> String:
	if PATHS.has(key):
		return str(PATHS[key])
	return str(STANDINS[key].path)


## Tree model list for a key (PATHS lists win over stand-ins).
static func paths(key: String) -> Array:
	if PATHS.has(key):
		return PATHS[key]
	return STANDINS[key].paths


## True while the key is still drawn by a recoloured stand-in.
static func is_standin(key: String) -> bool:
	return not PATHS.has(key) and STANDINS.has(key)


## Stand-in tint (white for real art).
static func tint_of(key: String) -> Color:
	if is_standin(key):
		return STANDINS[key].get("tint", Color.WHITE)
	return Color.WHITE


## Stand-in item scale/rotation (identity for real art).
static func standin_scale(key: String) -> Vector3:
	return STANDINS[key].get("scale", Vector3.ONE) if is_standin(key) else Vector3.ONE


static func standin_rot(key: String) -> Vector3:
	return STANDINS[key].get("rot", Vector3.ZERO) if is_standin(key) else Vector3.ZERO


static func make(key: String) -> Node3D:
	if is_standin(key):
		var sd: Dictionary = STANDINS[key]
		if sd.has("parts"):
			return _make_staged(sd)
		var inst: Node3D = (load(str(sd.path)) as PackedScene).instantiate()
		tint(inst, sd.get("tint", Color.WHITE))
		if sd.has("scale"):
			inst.scale = sd.scale
		return inst
	return (load(path(key)) as PackedScene).instantiate()


## Instance of a model file, recoloured.
static func make_path(p: String, c: Color = Color.WHITE) -> Node3D:
	var inst: Node3D = (load(p) as PackedScene).instantiate()
	tint(inst, c)
	return inst


## Staged stand-in: children stage1..stageN at the building origin, one part each.
static func _make_staged(sd: Dictionary) -> Node3D:
	var root := Node3D.new()
	var parts: Array = sd.parts
	for i in parts.size():
		var part: Array = parts[i]
		var st := Node3D.new()
		st.name = "stage%d" % (i + 1)
		root.add_child(st)
		var p := str(part[0])
		var inst: Node3D = make(p) if not p.begins_with("res://") else make_path(p, sd.get("tint", Color.WHITE))
		inst.position = part[1]
		inst.scale = part[2] if part[2] is Vector3 else Vector3.ONE * float(part[2])
		inst.rotation_degrees.y = float(part[3])
		st.add_child(inst)
	return root


static var _tinted: Dictionary = {}


## Multiplies the albedo of every mesh under n by c (cached per mesh, so batching still works:
## every copy of a tinted stand-in shares one mesh and one material).
static func tint(n: Node, c: Color) -> void:
	if c == Color.WHITE:
		return
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.mesh:
			mi.mesh = _tinted_mesh(mi.mesh, c)


static func _tinted_mesh(src: Mesh, c: Color) -> Mesh:
	var k := "%d|%s" % [src.get_instance_id(), c]
	if _tinted.has(k):
		return _tinted[k]
	var dup := src.duplicate() as Mesh
	for s in dup.get_surface_count():
		var mat := dup.surface_get_material(s)
		if mat is BaseMaterial3D:
			var nm := (mat as BaseMaterial3D).duplicate() as BaseMaterial3D
			nm.albedo_color = Color(nm.albedo_color.r * c.r, nm.albedo_color.g * c.g, nm.albedo_color.b * c.b, nm.albedo_color.a)
			dup.surface_set_material(s, nm)
	_tinted[k] = dup
	return dup
