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
}

## Road surface: 512 px = full road width x 4 m, one cream dash per tile.
const ROAD_TILE := "res://assets/textures/ground/road_tile.png"

## Border forest imposter atlas (ASSETS_M1.md section 5); the _far meshes stay as fallback.
const IMPOSTER_ATLAS := "res://assets/textures/imposters/border_trees_atlas.png"
const IMPOSTER_JSON := "res://assets/textures/imposters/border_trees_atlas.json"
## Maple Highlands edge atlas (ASSETS_M2.md section 6): 4 x 4 cells.
const IMPOSTER_ATLAS_M2 := "res://assets/textures/imposters/border_trees_atlas_m2.png"

## Ground tiles, 4 x 4 m per tile.
const GROUND := {
	1: "res://assets/textures/ground/grass_v1.png",
	2: "res://assets/textures/ground/grass_birch.png",
	3: "res://assets/textures/ground/grass_maple.png",
	"dirt": "res://assets/textures/ground/dirt_path.png",
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
	for item in ["bookcase", "plywood", "veneer", "canoe", "floorboard", "beam", "chair", "table", "plank", "log"]:
		if t.contains(" %s " % item) or t.contains(" %ss " % item):
			return log_type if item == "log" else item
	return ""


static func path(key: String) -> String:
	return str(PATHS[key])


static func make(key: String) -> Node3D:
	return (load(path(key)) as PackedScene).instantiate()
