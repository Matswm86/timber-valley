extends Node

## Save-migration test: an original single-valley save (version 1) must load with money,
## unlocks, upgrades and pile counts intact, show the River Bridge pad, and re-save as
## version 2. Also checks offline earnings (2 h cap, 50%). Backs up and restores user://save.json.
## Run: godot --headless --audio-driver Dummy res://tests/migration_test.tscn

const V1_IDS := [
	"trees2", "office", "jack1", "hauler1", "carpentry", "hauler3", "pine", "cashier", "sawmill2",
	"jack2", "hauler2", "cnc", "conveyor1", "hauler4", "factory", "jack3", "dock", "conveyor2",
	"roadsign", "belt_planks", "belt_saw2", "belt_chairs", "megasaw", "belt_mega", "lodge",
]

var _fails: int = 0
var _backup: String = ""


func _ready() -> void:
	if FileAccess.file_exists(Game.SAVE_PATH):
		_backup = FileAccess.get_file_as_string(Game.SAVE_PATH)
	# 1. Exactly the keys the shipped game writes (Game.gd at 563ae28): no "version".
	var old := {
		"money": 12345, "total_earned": 98765, "unlocked": V1_IDS,
		"upgrades": {"capacity": 3, "speed": 2, "axe": 4, "machines": 1, "workers": 5, "prices": 2},
		"piles": {"sawmill1:in": 5, "sawmill1:out": 9, "shelf:plank": 7, "dock:bookcase": 4},
		"finished": true, "sound_on": false,
	}
	_write(old)
	Game.load_game()
	var main: Node = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	# Piles are checked and re-saved before the first frame, before machines and shoppers move items.
	var w: World = main.get_node("World")
	var piles_now := [(w.machines.sawmill1 as Machine).input.count(), w.shop.shelf("plank").count(), (w.machines.dock as TruckDock).pile.count()]
	Game.save_game()
	var re: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(Game.SAVE_PATH))
	await _frames(10)
	_check("money intact", Game.money == 12345, str(Game.money))
	_check("total_earned intact", Game.total_earned == 98765, str(Game.total_earned))
	var missing := []
	for id in V1_IDS:
		if not Game.is_unlocked(id):
			missing.append(id)
	_check("all 25 V1 unlocks intact", missing.is_empty(), str(missing))
	_check("upgrades intact", Game.level("capacity") == 3 and Game.level("axe") == 4 and Game.level("workers") == 5, str(Game.upgrade_levels))
	_check("sawmill1 input pile = 5", piles_now[0] == 5, str(piles_now[0]))
	_check("plank shelf = 7", piles_now[1] == 7, str(piles_now[1]))
	_check("dock pile = 4", piles_now[2] == 4, str(piles_now[2]))
	_check("sound setting kept", Game.sound_on == false, str(Game.sound_on))
	_check("River Bridge pad shown", w.pads.has("r2_bridge"), str(w.pads.keys()))
	_check("finish panel stays closed", not Game.hud.finish_panel.visible, "")
	_check("valley card stays closed", not Game.hud.valley_card.visible, "")
	_check("no Birch Bend pads yet", not w.pads.has("r2_lathe"), "")
	_check("no offline pile from a v1 save", Game.offline_pending == 0, str(Game.offline_pending))
	_check("re-saved as version 2", int(re.get("version", 0)) == 2, str(re.get("version")))
	_check("re-save keeps unlocks", (re.unlocked as Array).size() == 25, str((re.unlocked as Array).size()))
	_check("re-save keeps piles", int((re.piles as Dictionary).get("sawmill1:in", -1)) == 5, str(re.piles))
	_check("re-save has ledger/region keys", re.has("ledger") and re.has("region_upgrades") and re.has("saved_at"), str(re.keys()))
	main.queue_free()
	await _frames(3)
	# 2. Offline: 1 h away at a ledger of 100 $/s -> 50% = $180,000; 10 h away caps at 2 h.
	var now := int(Time.get_unix_time_from_system())
	var v2 := re.duplicate(true)
	v2["ledger"] = {"r1": 60.0, "r2": 40.0}
	v2["offline_pending"] = 0
	v2["saved_at"] = now - 3600
	Game.apply_save(v2)
	_check("offline 1 h = 180000", absi(Game.offline_pending - 180000) <= 50, str(Game.offline_pending))
	v2["saved_at"] = now - 36000
	Game.apply_save(v2)
	_check("offline capped at 2 h = 360000", absi(Game.offline_pending - 360000) <= 50, str(Game.offline_pending))
	v2["saved_at"] = now - 20
	Game.apply_save(v2)
	_check("quick restart pays nothing", Game.offline_pending == 0, str(Game.offline_pending))
	# 3. Money format.
	var fm := [[999, "$999"], [12500, "$12.5K"], [1200, "$1.20K"], [3400000, "$3.40M"], [1200000000, "$1.20B"], [999999, "$1.00M"]]
	for f in fm:
		_check("fmt %d" % int(f[0]), Game.fmt(int(f[0])) == str(f[1]), Game.fmt(int(f[0])))
	if _backup != "":
		var fw := FileAccess.open(Game.SAVE_PATH, FileAccess.WRITE)
		fw.store_string(_backup)
	else:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(Game.SAVE_PATH))
	print("MIGRATION %s (%d failed)" % ["PASS" if _fails == 0 else "FAIL", _fails])
	get_tree().quit(1 if _fails > 0 else 0)


func _write(d: Dictionary) -> void:
	var f := FileAccess.open(Game.SAVE_PATH, FileAccess.WRITE)
	f.store_string(JSON.stringify(d))
	f.close()


func _check(what: String, ok: bool, got: String) -> void:
	if not ok:
		_fails += 1
	print("%s  %s%s" % ["ok  " if ok else "FAIL", what, "" if ok else "  (got %s)" % got])


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame
