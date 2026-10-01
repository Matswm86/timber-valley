class_name Balance
extends RefCounted

## Every cost, price and rate in one place (GDD section 8.2). Pads for Valley 2 come from
## docs/balance/unlocks_regions.csv; positions nudged where a pad sat in the river or on a zone.

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
# region upgrades: base cost per valley, growth 1.8, max 5
const REGION_UPGRADES := {
	2: {"saws": 8000, "crew": 11000, "fame": 13000},
	3: {"saws": 50000, "crew": 65000, "fame": 80000},
	4: {"saws": 160000, "crew": 210000, "fame": 270000},
	5: {"saws": 510000, "crew": 680000, "fame": 850000},
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
}
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
	{"id": "r2_bridge", "cost": 11000, "req": ["lodge"], "title": "River Bridge to Birch Bend", "pad": Vector3(-20.5, 0, -6)},
	{"id": "r2_lathe", "cost": 13000, "req": ["r2_bridge"], "title": "Veneer Lathe", "pad": Vector3(-45, 0, -6)},
	{"id": "r2_grove2", "cost": 6700, "req": ["r2_lathe"], "title": "More Birches", "pad": Vector3(-55, 0, 6)},
	{"id": "r2_office", "cost": 8000, "req": ["r2_lathe"], "title": "Riverside Office", "pad": Vector3(-34, 0, 11)},
	{"id": "r2_jack1", "cost": 13000, "req": ["r2_grove2"], "title": "Hire a Birch Lumberjack", "pad": Vector3(-50, 0, 2)},
	{"id": "r2_hauler1", "cost": 16000, "req": ["r2_jack1"], "title": "Hire a Veneer Carrier", "pad": Vector3(-40, 0, -2)},
	{"id": "r2_flume", "cost": 21000, "req": ["r2_jack1"], "title": "Log Flume", "pad": Vector3(-60, 0, -22)},
	{"id": "r2_cashier", "cost": 19000, "req": ["r2_hauler1"], "title": "Riverside Cashier", "pad": Vector3(-35, 0, 0)},
	{"id": "r2_press", "cost": 33000, "req": ["r2_hauler1"], "title": "Plywood Press", "pad": Vector3(-45, 0, -18)},
	{"id": "r2_jack2", "cost": 40000, "req": ["r2_flume"], "title": "Hire 2 Flume Lumberjacks", "pad": Vector3(-56, 0, -26)},
	{"id": "r2_belt_lp", "cost": 45000, "req": ["r2_press"], "title": "Conveyor: Lathe to Press", "pad": Vector3(-42, 0, -12)},
	{"id": "r2_hauler2", "cost": 51000, "req": ["r2_press"], "title": "Hire a Plywood Carrier", "pad": Vector3(-38.5, 0, -14.5)},
	{"id": "r2_press2", "cost": 74000, "req": ["r2_belt_lp"], "title": "Second Plywood Press", "pad": Vector3(-45, 0, -28)},
	{"id": "r2_boatshop", "cost": 94000, "req": ["r2_press2"], "title": "Boat Workshop: Canoes", "pad": Vector3(-40, 0, -38)},
	{"id": "r2_barge", "cost": 110000, "req": ["r2_boatshop"], "title": "Barge Landing", "pad": Vector3(-33, 0, -36)},
	{"id": "r2_belt_pb", "cost": 120000, "req": ["r2_barge"], "title": "Conveyor: Presses to Boat Workshop", "pad": Vector3(-43, 0, -33)},
	{"id": "r2_belt_bb", "cost": 130000, "req": ["r2_barge"], "title": "Conveyor: Boat Workshop to Barge", "pad": Vector3(-35, 0, -41.5)},
	{"id": "r2_jack3", "cost": 150000, "req": ["r2_belt_pb"], "title": "Forester Camp: West Grove + 2 Lumberjacks", "pad": Vector3(-68, 0, -14)},
	{"id": "r2_boathouse", "cost": 210000, "req": ["r2_belt_bb", "r2_jack3"], "title": "Build the Boathouse", "pad": Vector3(-68, 0, 8)},
]
## Pads drawn at the large 3.2 m size.
const BIG_PADS := [
	"carpentry", "sawmill2", "cnc", "factory", "dock", "lodge", "office",
	"r2_bridge", "r2_lathe", "r2_office", "r2_press", "r2_press2", "r2_boatshop", "r2_barge", "r2_boathouse",
]
## Landmarks that finish a valley and show the "Valley complete" card.
const LANDMARKS := {"lodge": 1, "r2_boathouse": 2}
## Valley gateways: the pad that opens the next valley (later gates go here too). Outside the
## tutorials the guide arrow always points at an unpaid gateway, affordable or not.
## "gate" = the closed gate in the valley wall that glows; "path" = the route the glow takes
## into the new valley once the gateway is paid.
const GATEWAYS := {
	"r2_bridge": {"region": 2, "gate": Vector3(-23.2, 0, -6), "path": [Vector3(-20.5, 0, -6), Vector3(-30.2, 0, -6), Vector3(-41.0, 0, -6)]},
}
