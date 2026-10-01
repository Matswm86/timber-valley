class_name Models
extends RefCounted

## Every Birch Bend (M1) model path in one place, so swapping an asset is one edit.
## Assets from assets/models_v3/ASSETS_M1.md (graphic-designer, 2026-10-01).
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
	# V1 vehicles kept as they were
	"truck": "res://assets/models/car/truck-flat.glb",
	"bridge_plank": "res://assets/models/nature/bridge_wood.glb",
	"gate_fence": "res://assets/models_v3/nature/fence_simple.glb",
}

## Border forest imposter atlas (ASSETS_M1.md section 5); the _far meshes stay as fallback.
const IMPOSTER_ATLAS := "res://assets/textures/imposters/border_trees_atlas.png"
const IMPOSTER_JSON := "res://assets/textures/imposters/border_trees_atlas.json"

## Ground tiles, 4 x 4 m per tile.
const GROUND := {
	1: "res://assets/textures/ground/grass_v1.png",
	2: "res://assets/textures/ground/grass_birch.png",
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
}


static func path(key: String) -> String:
	return str(PATHS[key])


static func make(key: String) -> Node3D:
	return (load(path(key)) as PackedScene).instantiate()
