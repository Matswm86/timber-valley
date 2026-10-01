class_name Balance
extends RefCounted

## Every cost, price and rate in one place (GDD section 8.2). Pads for Valley 2 come from
## docs/balance/unlocks_regions.csv; positions nudged where a pad sat in the river or on a zone
## (Maple Highlands moves are listed in docs/GDD.md, "M2 layout").

const PRICES := {
	"plank": 3, "chair": 8, "table": 20, "bookcase": 45,
	"veneer": 8, "plywood": 40, "canoe": 300,
	"beam": 30, "floorboard": 12, "cabin_kit": 260,
	"timber": 70, "deckboard": 30, "mast": 500,
	"dry_lumber": 90, "skis": 400, "sled": 1500, "guitar": 2000,
}
## Which valley sells an item (its Local Fame applies to the price).
const ITEM_REGION := {
	"plank": 1, "chair": 1, "table": 1, "bookcase": 1,
	"veneer": 2, "plywood": 2, "canoe": 2,
	"beam": 3, "floorboard": 3, "cabin_kit": 3,
}
## pine regrow stays 8.0 s: that is what Valley 1 ships today (GDD block says 7.0).
const TREES := {
	"broad": {"log": "log", "logs": 3, "hits": 3, "regrow": 7.0, "scale": 1.0},
	"pine": {"log": "log", "logs": 4, "hits": 4, "regrow": 8.0, "scale": 1.0},
	"birch": {"log": "birch_log", "logs": 4, "hits": 4, "regrow": 8.0, "scale": 1.0},
	"maple": {"log": "maple_log", "logs": 5, "hits": 5, "regrow": 9.0, "scale": 1.1},
	"redwood": {"log": "red_log", "logs": 8, "hits": 7, "regrow": 14.0, "scale": 1.6},
	"frost": {"log": "frost_log", "logs": 6, "hits": 6, "regrow": 12.0, "scale": 1.15},
}
## Per-model scale factor that replaces the kind's "scale" (designer flag b, 2026-10-01): the
## wide maple C stays at 1.0 so paths and the guide arrow stay visible next to groves.
const TREE_SCALE_OVERRIDE := {"tree_mapleC": 1.0}
# id: [in_a, n_a, in_b, n_b, out, n_out, cycle_s]  ("" = no second input)
const MACHINES := {
	"lathe": ["birch_log", 2, "", 0, "veneer", 6, 1.2],
	"press": ["veneer", 3, "", 0, "plywood", 1, 1.5],
	"boatshop": ["plywood", 4, "", 0, "canoe", 1, 3.0],
	"beamsaw": ["maple_log", 1, "", 0, "beam", 2, 1.4],
	"planer": ["maple_log", 1, "", 0, "floorboard", 4, 1.6],
	"kitfactory": ["beam", 2, "floorboard", 4, "cabin_kit", 1, 2.0],
	"redmill": ["red_log", 1, "", 0, "timber", 2, 1.5],
	"decksaw": ["timber", 1, "", 0, "deckboard", 3, 1.2],
	"mastlathe": ["red_log", 3, "", 0, "mast", 1, 4.0],
	"skiworks": ["dry_lumber", 2, "", 0, "skis", 1, 2.0],
	"sledshop": ["dry_lumber", 3, "skis", 1, "sled", 1, 3.0],
	"luthier": ["dry_lumber", 4, "", 0, "guitar", 1, 5.0],
}
## Output pile size per machine id when it differs from the default 48.
const MACHINE_OUT_CAP := {"boatshop": 12, "mastlathe": 12, "luthier": 12}
const KILN := {"batch": 20, "bake_s": 16.0, "idle_start_s": 6.0}
const RENT_PER_HOUSE := 15  # $/s base, x Local Fame
const SHIP_REWARD := 14000
const SHIP_MIN_INTERVAL := 45.0
const ORDER := {"lines_min": 2, "lines_max": 3, "base_qty": 10, "qty_per_order": 4, "qty_cap": 60, "pay_mult": 1.6, "gap_s": 15.0}
# region upgrades: base cost per valley, growth 1.8, max 5 (rebalance 2026-10-01,
# docs/balance/rebalance_2026-10-01.md)
const REGION_UPGRADES := {
	2: {"saws": 2200, "crew": 1400, "fame": 3400},
	3: {"saws": 13000, "crew": 8000, "fame": 19000},
	4: {"saws": 51000, "crew": 32000, "fame": 77000},
	5: {"saws": 180000, "crew": 120000, "fame": 280000},
}
const REGION_UPGRADE_GROWTH := 1.8
const REGION_UPGRADE_MAX := 5
const REGION_UPGRADE_INFO := {
	"saws": {"name": "Sharp Saws", "desc": "Machines here 25% faster"},
	"crew": {"name": "Crew Coffee", "desc": "Crew here faster, +2 carry"},
	"fame": {"name": "Local Fame", "desc": "+10% prices and shoppers here"},
}
const GLOBAL_EXT := {"capacity": [2500, 4], "speed": [3000, 2], "axe": [2000, 3]}  # [base, extra levels], growth 1.75
const CUSTOMERS_PER_REGION := 20

## Global upgrades (office in Valley 1). Cost = base x 1.75^level.
const UPGRADES := {
	"capacity": {"name": "Bigger Backpack", "desc": "Carry 4 more items", "base": 30, "max": 6},
	"speed": {"name": "Running Shoes", "desc": "Walk 12% faster", "base": 40, "max": 5},
	"axe": {"name": "Sharper Axe", "desc": "Chop trees faster", "base": 35, "max": 5},
	"machines": {"name": "Oiled Machines", "desc": "Machines work 25% faster", "base": 90, "max": 5},
	"workers": {"name": "Coffee Break", "desc": "Workers walk faster, carry more", "base": 120, "max": 5},
	"prices": {"name": "Good Reputation", "desc": "Customers pay 10% more", "base": 150, "max": 5},
}
const UPGRADE_GROWTH := 1.75

## Exports (generalised TruckDock): items per trip, seconds away between trips.
const EXPORTS := {
	"truck": {"cap": 8, "away": 5.0},
	"barge": {"cap": 6, "away": 8.0},
	# 3 wagons x 4 kits = 12 per trip; Longer Train (r3_rail2) couples 2 more (20 per trip).
	"train": {"cap": 12, "away": 10.0, "wagons": 3},
}
const RAIL2_WAGONS := 2
## Forklift hauler (GDD 7.5): faster, carries more, serves several piles (the fullest first).
## max_load_h caps a load of bulky items (cabin kits) at this stack height in metres.
const FORKLIFT := {"speed": 4.5, "cap": 20, "max_load_h": 2.4}
## A cabin kit is 724 tris: piles draw at most this many (designer flag d: a full 48-kit pile
## was about 35k tris). The pile keeps its real count; only the drawn tower is capped.
const KIT_PILE_DRAWN := 12
## Handcar fast travel (GDD 7.6 E): stand on a tile hold_s, fade out, move, fade in.
const HANDCAR := {"hold_s": 0.8, "fade_s": 0.3}
## One stop per valley hub: "pos" = sign + tiles, "land" = where a rider arrives (off the tiles),
## "side" = which side (-1 west, 1 east) the handcar track sits on.
## GDD 7.6 E spots nudged off buildings and pads (V1 office, V2 office, V3 gate road).
const HANDCAR_STOPS := {
	1: {"pos": Vector3(-8.5, 0, 11.2), "land": Vector3(-5.6, 0, 10.0), "side": -1},
	2: {"pos": Vector3(-35.6, 0, 3.4), "land": Vector3(-35.6, 0, 6.6), "side": 1},
	3: {"pos": Vector3(-6.0, 0, -57.8), "land": Vector3(-1.4, 0, -57.4), "side": -1},
}
## Valley open = its gateway is paid (Home Valley always).
const VALLEY_GATE := {1: "", 2: "r2_bridge", 3: "r3_gate"}
## Build sites (GDD 7.6 B): the pad pays the money slot, then goods fill the slots; stage k of N
## rises at k/N of the goods. Houses pay rent (+10% Builders' Yard shoppers each) once done.
## slot_x/slot_z: where the slot squares start (world), stepped along z (houses) or x (tower).
const BUILD_SITES := {
	"r3_house1": {"model": "house_cottage", "pos": Vector3(-17, 0, -62), "goods": {"beam": 30, "floorboard": 40}, "stages": 4, "rent": true},
	"r3_house2": {"model": "house_farmhouse", "pos": Vector3(-17, 0, -70), "goods": {"beam": 40, "floorboard": 50, "cabin_kit": 2}, "stages": 4, "rent": true},
	"r3_house3": {"model": "house_barn", "pos": Vector3(-17, 0, -78), "goods": {"beam": 50, "floorboard": 60, "cabin_kit": 4}, "stages": 4, "rent": true},
	"r3_house4": {"model": "house_school", "pos": Vector3(-17, 0, -86), "goods": {"beam": 60, "floorboard": 70, "cabin_kit": 6}, "stages": 4, "rent": true},
	"r3_house5": {"model": "house_inn", "pos": Vector3(-17, 0, -94), "goods": {"beam": 70, "floorboard": 80, "cabin_kit": 8}, "stages": 4, "rent": true},
	"r3_clocktower": {"model": "clock_tower", "pos": Vector3(-10, 0, -112), "goods": {"beam": 120, "floorboard": 100, "cabin_kit": 12}, "stages": 6, "rent": false},
}
## Forester Camp (r2_jack3, Mats 2026-10-01): its crew size, and every birch regrows this much
## faster once it is bought.
const FORESTER_CAMP := {"crew": 3, "birch_regrow_mult": 0.6}
## Log flume (Valley 2): a Conveyor with a water look.
const FLUME := {"speed": 3.5, "spacing": 0.5, "bob_m": 0.06, "bob_hz": 3.0}

## Valley sleep and ledger (GDD section 10).
const WAKE_MARGIN := 24.0
const SLEEP_MARGIN := 30.0
const MAX_AWAKE := 2
const LEDGER_WINDOW_S := 120
## Offline earnings (Mats, 2026-09-30): up to 2 h at 50% of the ledger income.
const OFFLINE_MAX_S := 7200
const OFFLINE_RATE := 0.5

## Valleys: name and walkable interior (x, z, width, depth) in world metres.
const REGIONS := {
	1: {"name": "Home Valley", "rect": Rect2(-23.5, -47.0, 42.5, 62.5)},
	2: {"name": "Birch Bend", "rect": Rect2(-79.0, -47.0, 48.0, 62.5)},
	3: {"name": "Maple Highlands", "rect": Rect2(-23.5, -119.0, 42.5, 64.0)},
}

# Every purchasable step. Pads show once all "req" ids are owned.
const UNLOCKS := [
	{"id": "trees2", "cost": 10, "req": [], "title": "More Trees", "pad": Vector3(-9, 0, 5.8)},
	{"id": "office", "cost": 25, "req": [], "title": "Upgrade Office", "pad": Vector3(-3.5, 0, 10.5)},
	{"id": "jack1", "cost": 50, "req": ["trees2"], "title": "Hire a Lumberjack", "pad": Vector3(-4.6, 0, 2.5)},
	{"id": "hauler1", "cost": 70, "req": ["jack1"], "title": "Hire a Plank Carrier", "pad": Vector3(5.0, 0, -0.5)},
	{"id": "carpentry", "cost": 120, "req": ["hauler1"], "title": "Carpentry: Chairs", "pad": Vector3(2, 0, -13)},
	{"id": "hauler3", "cost": 160, "req": ["carpentry"], "title": "Hire a Chair Carrier", "pad": Vector3(6.5, 0, -8.5)},
	{"id": "pine", "cost": 180, "req": ["carpentry"], "title": "Pine Forest", "pad": Vector3(-9.5, 0, -10.5)},
	{"id": "cashier", "cost": 220, "req": ["carpentry"], "title": "Hire a Cashier", "pad": Vector3(7.0, 0, -3.8)},
	{"id": "sawmill2", "cost": 260, "req": ["pine"], "title": "Second Sawmill", "pad": Vector3(-3, 0, -24)},
	{"id": "jack2", "cost": 300, "req": ["sawmill2"], "title": "Hire a Lumberjack", "pad": Vector3(-8.0, 0, -20.5)},
	{"id": "hauler2", "cost": 320, "req": ["sawmill2"], "title": "Hire a Carrier: Sawmill to Carpentry", "pad": Vector3(0.6, 0, -18.8)},
	{"id": "cnc", "cost": 600, "req": ["hauler2"], "title": "CNC Workshop: Tables", "pad": Vector3(9, 0, -24)},
	{"id": "conveyor1", "cost": 700, "req": ["cnc"], "title": "Conveyor Belt", "pad": Vector3(3.0, 0, -20.2)},
	{"id": "hauler4", "cost": 750, "req": ["cnc"], "title": "Hire a Table Carrier", "pad": Vector3(13.0, 0, -19.5)},
	{"id": "factory", "cost": 1200, "req": ["conveyor1"], "title": "Robot Furniture Factory", "pad": Vector3(0, 0, -36)},
	{"id": "jack3", "cost": 900, "req": ["factory"], "title": "North Forest + 2 Lumberjacks", "pad": Vector3(-8.5, 0, -29.0)},
	{"id": "dock", "cost": 1500, "req": ["factory"], "title": "Truck Loading Dock", "pad": Vector3(13.5, 0, -36)},
	{"id": "conveyor2", "cost": 1300, "req": ["dock"], "title": "Factory Conveyor", "pad": Vector3(8.0, 0, -41.0)},
	{"id": "roadsign", "cost": 200, "req": ["carpentry"], "title": "Road Sign: More Shoppers", "pad": Vector3(13.0, 0, 9.5)},
	{"id": "belt_planks", "cost": 350, "req": ["cashier"], "title": "Conveyor: Sawmill to Market", "pad": Vector3(3.2, 0, 9.6)},
	{"id": "belt_saw2", "cost": 500, "req": ["hauler2"], "title": "Conveyor: Sawmill 2 to Carpentry", "pad": Vector3(-2.6, 0, -18.4)},
	{"id": "belt_chairs", "cost": 650, "req": ["hauler3", "belt_planks"], "title": "Conveyor: Chairs to Market", "pad": Vector3(8.0, 0, -8.0)},
	{"id": "megasaw", "cost": 2500, "req": ["factory"], "title": "MEGA Sawmill", "pad": Vector3(11.0, 0, -13.5)},
	{"id": "belt_mega", "cost": 1000, "req": ["megasaw"], "title": "Conveyor: Mega Sawmill to CNC", "pad": Vector3(9.5, 0, -18.4)},
	{"id": "lodge", "cost": 6000, "req": ["conveyor2", "jack3", "belt_mega"], "title": "Build the Grand Lodge", "pad": Vector3(-12, 0, -39)},
	# ---- Valley 2: Birch Bend (unlocks_regions.csv). Bridge pad moved from the river (-27) to the V1 bank.
	{"id": "r2_bridge", "cost": 2800, "req": ["lodge"], "title": "River Bridge to Birch Bend", "pad": Vector3(-20.5, 0, -6)},
	{"id": "r2_lathe", "cost": 3600, "req": ["r2_bridge"], "title": "Veneer Lathe", "pad": Vector3(-45, 0, -6)},
	{"id": "r2_grove2", "cost": 3200, "req": ["r2_lathe"], "title": "More Birches", "pad": Vector3(-55, 0, 6)},
	{"id": "r2_office", "cost": 3400, "req": ["r2_lathe"], "title": "Riverside Office", "pad": Vector3(-34, 0, 11)},
	{"id": "r2_jack1", "cost": 4700, "req": ["r2_grove2"], "title": "Hire a Birch Lumberjack", "pad": Vector3(-50, 0, 2)},
	{"id": "r2_hauler1", "cost": 5400, "req": ["r2_jack1"], "title": "Hire a Veneer Carrier", "pad": Vector3(-40, 0, -2)},
	{"id": "r2_flume", "cost": 6000, "req": ["r2_jack1"], "title": "Log Flume", "pad": Vector3(-60, 0, -22)},
	{"id": "r2_cashier", "cost": 6400, "req": ["r2_hauler1"], "title": "Riverside Cashier", "pad": Vector3(-35, 0, 0)},
	{"id": "r2_press", "cost": 8700, "req": ["r2_hauler1"], "title": "Plywood Press", "pad": Vector3(-45, 0, -18)},
	{"id": "r2_jack2", "cost": 9500, "req": ["r2_flume"], "title": "Hire 2 Flume Lumberjacks", "pad": Vector3(-56, 0, -26)},
	{"id": "r2_belt_lp", "cost": 11000, "req": ["r2_press"], "title": "Conveyor: Lathe to Press", "pad": Vector3(-42, 0, -12)},
	{"id": "r2_hauler2", "cost": 13000, "req": ["r2_press"], "title": "Hire a Plywood Carrier", "pad": Vector3(-38.5, 0, -14.5)},
	{"id": "r2_press2", "cost": 17000, "req": ["r2_belt_lp"], "title": "Second Plywood Press", "pad": Vector3(-45, 0, -28)},
	{"id": "r2_boatshop", "cost": 19000, "req": ["r2_press2"], "title": "Boat Workshop: Canoes", "pad": Vector3(-40, 0, -38)},
	{"id": "r2_barge", "cost": 21000, "req": ["r2_boatshop"], "title": "Barge Landing", "pad": Vector3(-33, 0, -36)},
	{"id": "r2_belt_pb", "cost": 23000, "req": ["r2_barge"], "title": "Conveyor: Presses to Boat Workshop", "pad": Vector3(-43, 0, -33)},
	{"id": "r2_belt_bb", "cost": 30000, "req": ["r2_barge"], "title": "Conveyor: Boat Workshop to Barge", "pad": Vector3(-35, 0, -41.5)},
	{"id": "r2_jack3", "cost": 37000, "req": ["r2_belt_pb"], "title": "Forester Camp: 3 Lumberjacks + Faster Birches", "pad": Vector3(-68, 0, -14)},
	{"id": "r2_boathouse", "cost": 63000, "req": ["r2_belt_bb", "r2_jack3"], "title": "Build the Boathouse", "pad": Vector3(-68, 0, 8)},
	# ---- Valley 3: Maple Highlands (unlocks_regions.csv). Gate pad on the Home Valley side, like the bridge.
	{"id": "r3_gate", "cost": 16000, "req": ["r2_boathouse"], "title": "Highland Gate", "pad": Vector3(0, 0, -42.4)},
	{"id": "r3_beamsaw", "cost": 20000, "req": ["r3_gate"], "title": "Beam Saw", "pad": Vector3(2.5, 0, -64.5)},
	{"id": "r3_grove2", "cost": 16000, "req": ["r3_beamsaw"], "title": "More Maples", "pad": Vector3(-8, 0, -72)},
	{"id": "r3_office", "cost": 17000, "req": ["r3_beamsaw"], "title": "Highland Office", "pad": Vector3(6.5, 0, -59.5)},
	{"id": "r3_jack1", "cost": 23000, "req": ["r3_grove2"], "title": "Hire a Maple Lumberjack", "pad": Vector3(-2.0, 0, -61.2)},
	{"id": "r3_forklift1", "cost": 28000, "req": ["r3_jack1"], "title": "Hire a Forklift: Beams", "pad": Vector3(6, 0, -69)},
	{"id": "r3_cashier", "cost": 37000, "req": ["r3_forklift1"], "title": "Builders' Yard Cashier", "pad": Vector3(12, 0, -58)},
	{"id": "r3_planer", "cost": 42000, "req": ["r3_forklift1"], "title": "Planer Mill: Floorboards", "pad": Vector3(2.5, 0, -78)},
	{"id": "r3_jack2", "cost": 46000, "req": ["r3_belt_bp"], "title": "Hire 2 Lumberjacks + North Maples", "pad": Vector3(-8, 0, -96)},
	{"id": "r3_house1", "cost": 42000, "req": ["r3_planer"], "title": "Village Plot 1: Cottage", "pad": Vector3(-17, 0, -62)},
	{"id": "r3_belt_bp", "cost": 45000, "req": ["r3_house1"], "title": "Conveyor: Beam Saw + Planer to Yard", "pad": Vector3(8, 0, -72)},
	{"id": "r3_kitfactory", "cost": 63000, "req": ["r3_belt_bp"], "title": "Cabin Kit Factory", "pad": Vector3(6, 0, -90)},
	{"id": "r3_house2", "cost": 63000, "req": ["r3_kitfactory"], "title": "Village Plot 2: Farmhouse", "pad": Vector3(-17, 0, -70)},
	{"id": "r3_rail", "cost": 72000, "req": ["r3_kitfactory"], "title": "Highland Railway", "pad": Vector3(13, 0, -100)},
	{"id": "r3_belt_kit", "cost": 75000, "req": ["r3_rail"], "title": "Conveyors: Kit Factory Feed + Rail", "pad": Vector3(9, 0, -94)},
	{"id": "r3_house3", "cost": 100000, "req": ["r3_belt_kit"], "title": "Village Plot 3: Barn", "pad": Vector3(-17, 0, -78)},
	{"id": "r3_jack3", "cost": 110000, "req": ["r3_belt_kit"], "title": "Hire 3 Lumberjacks + Ridge Maples", "pad": Vector3(-4, 0, -110)},
	{"id": "r3_rail2", "cost": 120000, "req": ["r3_jack3"], "title": "Longer Train", "pad": Vector3(15, 0, -102)},
	{"id": "r3_house4", "cost": 140000, "req": ["r3_rail2"], "title": "Village Plot 4: School", "pad": Vector3(-17, 0, -86)},
	{"id": "r3_house5", "cost": 150000, "req": ["r3_house4"], "title": "Village Plot 5: Inn", "pad": Vector3(-17, 0, -94)},
	{"id": "r3_clocktower", "cost": 280000, "req": ["r3_house5"], "title": "Build the Clock Tower", "pad": Vector3(-10, 0, -112)},
]
## Pads drawn at the large 3.2 m size.
const BIG_PADS := [
	"carpentry", "sawmill2", "cnc", "factory", "dock", "lodge", "office",
	"r2_bridge", "r2_lathe", "r2_office", "r2_press", "r2_press2", "r2_boatshop", "r2_barge", "r2_boathouse",
	"r3_gate", "r3_beamsaw", "r3_office", "r3_planer", "r3_kitfactory", "r3_rail",
	"r3_house1", "r3_house2", "r3_house3", "r3_house4", "r3_house5", "r3_clocktower",
]
## Landmarks that finish a valley and show the "Valley complete" card. A landmark that is a build
## site (the Clock Tower) shows it when the building is finished, not when its pad is paid.
const LANDMARKS := {"lodge": 1, "r2_boathouse": 2, "r3_clocktower": 3}
## Valley gateways: the pad that opens the next valley (later gates go here too). Outside the
## tutorials the guide arrow always points at an unpaid gateway, affordable or not.
## "gate" = the closed gate in the valley wall that glows; "path" = the route the glow takes
## into the new valley once the gateway is paid; "along" = the axis the closed gate spans;
## "arch_h" = height of the gold arch over the pad (default 3.0; lower where it would hide a gate sign).
const GATEWAYS := {
	"r2_bridge": {"region": 2, "gate": Vector3(-23.2, 0, -6), "along": "z", "path": [Vector3(-20.5, 0, -6), Vector3(-30.2, 0, -6), Vector3(-41.0, 0, -6)]},
	"r3_gate": {"region": 3, "gate": Vector3(0, 0, -46.6), "along": "x", "arch_h": 2.0, "path": [Vector3(0, 0, -42.4), Vector3(0, 0, -52.0), Vector3(0, 0, -60.0)]},
}
