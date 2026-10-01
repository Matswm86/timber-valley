extends Node

## Save-migration test: an original single-valley save (version 1) must load with money,
## unlocks, upgrades and pile counts intact, show the River Bridge pad, and re-save as the
## current version. Also checks offline earnings (2 h cap, 50%), and that an M1-complete save
## (version 2, Boathouse built) gets the Maple Highlands content. Backs up and restores user://save.json.
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
	_check("re-saved as version 3", int(re.get("version", 0)) == 3, str(re.get("version")))
	_check("re-save keeps unlocks", (re.unlocked as Array).size() == 25, str((re.unlocked as Array).size()))
	_check("re-save keeps piles", int((re.piles as Dictionary).get("sawmill1:in", -1)) == 5, str(re.piles))
	_check("re-save has ledger/region/sites keys", re.has("ledger") and re.has("region_upgrades") and re.has("saved_at") and re.has("sites"), str(re.keys()))
	_check("no Highland Gate pad before the Boathouse", not w.pads.has("r3_gate"), "")
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
	# 3. M1-complete save (version 2 as M1 wrote it, no "sites"): the Highlands open up.
	var m1_ids: Array = V1_IDS.duplicate()
	for u in Balance.UNLOCKS:
		if str(u.id).begins_with("r2_"):
			m1_ids.append(u.id)
	var m1 := {
		"version": 2, "money": 90000, "total_earned": 3000000, "unlocked": m1_ids,
		"upgrades": {"capacity": 6, "speed": 5, "axe": 5, "machines": 5, "workers": 5, "prices": 5},
		"region_upgrades": {"2": {"saws": 1, "crew": 2, "fame": 3}}, "ledger": {"r1": 150.0, "r2": 400.0},
		"region_stats": {"2": {"time": 3000.0, "earned": 1500000}}, "offline_pending": 0,
		"saved_at": int(Time.get_unix_time_from_system()) - 10,
		"piles": {"lathe:in": 6, "dock:canoe": 3}, "finished": true, "sound_on": true,
	}
	_write(m1)
	Game.load_game()
	main = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	w = main.get_node("World")
	await _frames(5)
	_check("M1 save: money intact", Game.money == 90000, str(Game.money))
	_check("M1 save: all V1 + V2 unlocks intact", Game.unlocked_ids.size() == m1_ids.size(), str(Game.unlocked_ids.size()))
	_check("M1 save: Birch Bend upgrades intact", Game.region_level(2, "fame") == 3, str(Game.region_upgrades))
	_check("M1 save: lathe pile = 6", (w.machines.lathe as Machine).input.count() == 6, str((w.machines.lathe as Machine).input.count()))
	_check("M1 save: Highland Gate pad shown", w.pads.has("r3_gate"), str(w.pads.keys()))
	_check("M1 save: no other Highlands pads yet", not w.pads.has("r3_beamsaw"), "")
	_check("M1 save: Highlands valley exists", w.r3 != null and w.regions.size() == 3, str(w.regions.keys()))
	_check("M1 save: gate closed", w._gate3_body != null and w._gate3_doors != null, "")
	_check("M1 save: arrow targets the gate", w.gateway_pad() == w.pads["r3_gate"], "")
	_check("M1 save: no build sites", Game.sites.is_empty(), str(Game.sites))
	Game.unlock("r3_gate")
	await _frames(5)
	_check("gate bought: beam saw pad shown", w.pads.has("r3_beamsaw"), str(w.pads.keys()))
	_check("gate bought: gate opens", w._gate3_body == null and w._gate3_doors == null, "")
	_check("gate bought: 3 handcar stops", w._stops.size() == 3, str(w._stops.keys()))
	for id in ["r3_beamsaw", "r3_grove2", "r3_jack1", "r3_forklift1", "r3_planer", "r3_house1"]:
		Game.unlock(id)
	await _frames(5)
	_check("house plot 1 is a build site", w.sites.has("r3_house1"), str(w.sites.keys()))
	# Sites only progress while their valley is awake: stand in the village first.
	w.player.global_position = Vector3(-12, 0, -62)
	w._cam_pos = w.player.global_position
	await _frames(3)
	_check("Highlands awake at the village", w.r3.awake, "")
	(w.sites["r3_house1"] as BuildSite).intake_of("beam").push(Items.make("beam"), false)
	await _frames(3)
	Game.save_game()
	var re3: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(Game.SAVE_PATH))
	_check("re-save version 3 with site progress", int(re3.get("version", 0)) == 3 and int((re3.sites as Dictionary).get("r3_house1", {}).get("beam", 0)) == 1, str(re3.get("sites")))
	main.queue_free()
	await _frames(3)
	# 4. Rent: a finished house pays 15 $/s, also offline (50%, with the ledger).
	var v3 := re3.duplicate(true)
	v3["sites"] = {"r3_house1": {"beam": 30, "floorboard": 40}}
	v3["ledger"] = {}
	v3["region_upgrades"] = {}
	v3["saved_at"] = int(Time.get_unix_time_from_system()) - 3600
	v3["offline_pending"] = 0
	Game.apply_save(v3)
	_check("finished house counts", Game.houses_done() == 1, str(Game.houses_done()))
	var rent := float(Balance.RENT_PER_HOUSE)
	_check("rent = RENT_PER_HOUSE $/s", is_equal_approx(Game.rent_rate(), rent), str(Game.rent_rate()))
	var want := int(3600 * rent * Balance.OFFLINE_RATE)
	_check("offline 1 h of rent = %d" % want, absi(Game.offline_pending - want) <= 30, str(Game.offline_pending))
	# 5. Money format.
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
