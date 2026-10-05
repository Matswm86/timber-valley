extends Node

## Host-app re-entry test (MWM Play). The host keeps the Game autoload alive but parked while
## another game runs, and calls Game.load_game() again on every enter. This checks that a
## second (and third) load_game() gives the same state as the first, that offline earnings are
## counted once, that a save in between does not pay the break again, and that the old
## user://save.json moves to the new save name. Backs up and restores both save files.
## Run: godot --headless --audio-driver Dummy res://tests/reentry_test.tscn

const OLD_PATH := "user://save.json"

var _fails: int = 0
var _backups: Dictionary = {}


func _ready() -> void:
	for p in [Game.SAVE_PATH, OLD_PATH]:
		if FileAccess.file_exists(p):
			_backups[p] = FileAccess.get_file_as_string(p)
	_remove(OLD_PATH)
	var now := int(Time.get_unix_time_from_system())
	var rate := 100.0
	var save := {
		"version": 4, "money": 5000, "total_earned": 9000, "unlocked": ["trees2", "office", "jack1"],
		"upgrades": {"capacity": 2, "speed": 1}, "ledger": {"2": rate}, "offline_pending": 250,
		"saved_at": now - 3600, "piles": {"sawmill1:in": 4}, "finished": false, "sound_on": true,
	}
	var want := 250 + int(3600 * rate * Balance.OFFLINE_RATE)
	print("expected offline_pending after a 1 h break: %d" % want)

	# 1. App start, then two host enters with no save in between.
	_write(Game.SAVE_PATH, save)
	var got: Array[int] = []
	var money: Array[int] = []
	for i in 3:
		Game.load_game()
		got.append(Game.offline_pending)
		money.append(Game.money)
	print("offline_pending after load 1/2/3: %s" % str(got))
	print("money after load 1/2/3: %s" % str(money))
	_check("load 1 pays the break once", absi(got[0] - want) <= 50, str(got[0]))
	_check("load 2 = load 1 (no double count)", absi(got[1] - got[0]) <= 50, str(got))
	_check("load 3 = load 1 (no double count)", absi(got[2] - got[0]) <= 50, str(got))
	_check("money unchanged by reloads", money[0] == 5000 and money[1] == 5000 and money[2] == 5000, str(money))
	_check("upgrades unchanged by reloads", Game.level("capacity") == 2 and Game.level("speed") == 1 and Game.level("axe") == 0, str(Game.upgrade_levels))
	_check("unlocks unchanged by reloads", Game.unlocked_ids.size() == 3, str(Game.unlocked_ids.keys()))

	# 2. Leave the game (host saves), come straight back: the break is not paid again.
	Game.save_game()
	Game.load_game()
	print("offline_pending after save + load: %d" % Game.offline_pending)
	_check("save + quick reload keeps the pile, adds nothing", absi(Game.offline_pending - got[0]) <= 50, str(Game.offline_pending))

	# 3. Collect the pile, save, reload twice: stays 0.
	var paid := Game.collect_offline()
	Game.load_game()
	Game.load_game()
	print("collected %d, offline_pending after 2 reloads: %d, money %d" % [paid, Game.offline_pending, Game.money])
	_check("collected pile does not come back", Game.offline_pending == 0, str(Game.offline_pending))
	_check("collected money kept", Game.money == 5000 + paid, str(Game.money))

	# 4. A 30 min break in another game after leaving: paid once on the next enter.
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(Game.SAVE_PATH))
	d["saved_at"] = now - 1800
	_write(Game.SAVE_PATH, d)
	Game.load_game()
	var a := Game.offline_pending
	Game.load_game()
	var b := Game.offline_pending
	var want30 := int(1800 * rate * Balance.OFFLINE_RATE)
	print("30 min break: load 1 %d, load 2 %d (expected %d)" % [a, b, want30])
	_check("30 min break paid once", absi(a - want30) <= 50 and absi(b - a) <= 50, "%d, %d" % [a, b])

	# 5. Full scene round trip: enter, play frames, leave (save), enter again.
	Game.collect_offline()
	var main: Node = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	await _frames(20)
	Game.save_game()
	main.queue_free()
	await _frames(3)
	var m1 := Game.money
	Game.load_game()
	main = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	await _frames(20)
	_check("scene round trip keeps money", Game.money >= m1, "%d vs %d" % [Game.money, m1])
	_check("scene round trip: no offline pile", Game.offline_pending == 0, str(Game.offline_pending))
	main.queue_free()
	await _frames(3)

	# 6. The old save name moves to the new one (only when they differ).
	if Game.SAVE_PATH != OLD_PATH:
		_remove(Game.SAVE_PATH)
		var old := save.duplicate()
		old["saved_at"] = now - 10
		old["money"] = 777
		_write(OLD_PATH, old)
		Game.load_game()
		_check("old save.json read", Game.money == 777, str(Game.money))
		_check("new save file written", FileAccess.file_exists(Game.SAVE_PATH), Game.SAVE_PATH)
		_check("old save.json moved away", not FileAccess.file_exists(OLD_PATH), OLD_PATH)
		Game.load_game()
		_check("second load after move same money", Game.money == 777, str(Game.money))
	else:
		print("skip  save rename (SAVE_PATH is still %s)" % OLD_PATH)

	for p in [Game.SAVE_PATH, OLD_PATH]:
		_remove(p)
		if _backups.has(p):
			var fw := FileAccess.open(p, FileAccess.WRITE)
			fw.store_string(_backups[p])
			fw.close()
	print("REENTRY %s (%d failed)" % ["PASS" if _fails == 0 else "FAIL", _fails])
	get_tree().quit(1 if _fails > 0 else 0)


func _write(path: String, d: Dictionary) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(JSON.stringify(d))
	f.close()


func _remove(path: String) -> void:
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))


func _check(what: String, ok: bool, got: String) -> void:
	if not ok:
		_fails += 1
	print("%s  %s%s" % ["ok  " if ok else "FAIL", what, "" if ok else "  (got %s)" % got])


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame
