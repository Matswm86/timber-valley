extends Node

## Global game state: money, unlocked buildings, upgrade levels, saving.

signal money_changed(value: int, delta: int)
signal unlocked(id: String)
signal upgraded(id: String, level: int)

const SAVE_PATH := "user://save.json"

const PRICES := {"plank": 3, "chair": 8, "table": 20, "bookcase": 45}

const UPGRADES := {
	"capacity": {"name": "Bigger Backpack", "desc": "Carry 4 more items", "base": 30, "max": 6},
	"speed": {"name": "Running Shoes", "desc": "Walk 12% faster", "base": 40, "max": 5},
	"axe": {"name": "Sharper Axe", "desc": "Chop trees faster", "base": 35, "max": 5},
	"machines": {"name": "Oiled Machines", "desc": "Machines work 25% faster", "base": 90, "max": 5},
	"workers": {"name": "Coffee Break", "desc": "Workers walk faster, carry more", "base": 120, "max": 5},
	"prices": {"name": "Good Reputation", "desc": "Customers pay 10% more", "base": 150, "max": 5},
}

var money: int = 0
var total_earned: int = 0
var unlocked_ids: Dictionary = {}
var upgrade_levels: Dictionary = {}
var pile_counts: Dictionary = {}
var finished: bool = false
var sound_on: bool = true

var player: Node3D
var hud: Node
var world: Node3D

var _save_timer: float = 0.0
var _piles: Dictionary = {}


func _ready() -> void:
	for k in UPGRADES:
		upgrade_levels[k] = 0
	load_game()


func _process(delta: float) -> void:
	_save_timer += delta
	if _save_timer > 8.0:
		_save_timer = 0.0
		save_game()


func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_PAUSED or what == NOTIFICATION_WM_CLOSE_REQUEST:
		save_game()


func add_money(amount: int) -> void:
	money += amount
	if amount > 0:
		total_earned += amount
	money_changed.emit(money, amount)


func spend(amount: int) -> bool:
	if money < amount:
		return false
	money -= amount
	money_changed.emit(money, -amount)
	return true


func price_of(item: String) -> int:
	var base: int = PRICES.get(item, 1)
	return int(round(base * (1.0 + 0.1 * level("prices"))))


func is_unlocked(id: String) -> bool:
	return unlocked_ids.has(id)


func unlock(id: String) -> void:
	if unlocked_ids.has(id):
		return
	unlocked_ids[id] = true
	unlocked.emit(id)
	save_game()


func level(id: String) -> int:
	return upgrade_levels.get(id, 0)


func upgrade_cost(id: String) -> int:
	var d: Dictionary = UPGRADES[id]
	return int(round(d.base * pow(1.75, level(id))))


func can_upgrade(id: String) -> bool:
	return level(id) < UPGRADES[id].max


func buy_upgrade(id: String) -> bool:
	if not can_upgrade(id) or not spend(upgrade_cost(id)):
		return false
	upgrade_levels[id] = level(id) + 1
	upgraded.emit(id, upgrade_levels[id])
	save_game()
	return true


# Derived stats used by gameplay code.
func player_capacity() -> int:
	return 8 + 4 * level("capacity")


func player_speed() -> float:
	return 5.2 * (1.0 + 0.12 * level("speed"))


func chop_time() -> float:
	return 0.32 * pow(0.8, level("axe"))


func machine_speed() -> float:
	return 1.0 + 0.25 * level("machines")


func worker_speed() -> float:
	return 3.2 * (1.0 + 0.15 * level("workers"))


func worker_capacity() -> int:
	return 6 + 2 * level("workers")


func register_pile(id: String, pile: Node) -> void:
	_piles[id] = pile


func saved_pile_count(id: String) -> int:
	return int(pile_counts.get(id, 0))


func save_game() -> void:
	var piles := {}
	for id in _piles:
		var p: Node = _piles[id]
		if is_instance_valid(p):
			piles[id] = p.count()
	pile_counts = piles
	var data := {
		"money": money,
		"total_earned": total_earned,
		"unlocked": unlocked_ids.keys(),
		"upgrades": upgrade_levels,
		"piles": piles,
		"finished": finished,
		"sound_on": sound_on,
	}
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		push_warning("save failed: %s" % FileAccess.get_open_error())
		return
	f.store_string(JSON.stringify(data))


func load_game() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		return
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		push_warning("save file unreadable, starting fresh")
		return
	money = int(data.get("money", 0))
	total_earned = int(data.get("total_earned", 0))
	for id in data.get("unlocked", []):
		unlocked_ids[str(id)] = true
	var ups: Dictionary = data.get("upgrades", {})
	for k in ups:
		if UPGRADES.has(k):
			upgrade_levels[k] = int(ups[k])
	pile_counts = data.get("piles", {})
	finished = bool(data.get("finished", false))
	sound_on = bool(data.get("sound_on", true))


func reset_game() -> void:
	if FileAccess.file_exists(SAVE_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
	money = 0
	total_earned = 0
	unlocked_ids.clear()
	pile_counts.clear()
	_piles.clear()
	finished = false
	for k in UPGRADES:
		upgrade_levels[k] = 0
	get_tree().reload_current_scene()
