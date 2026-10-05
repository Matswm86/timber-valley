extends Node

## Dev-only: screenshots of every HUD screen with a button, and a measured check of each visible
## button against the MWM Play child-touch rules (1080x1920): hit area >= 200 px both ways, acts
## on release, nothing tappable in the bottom 256 px wrist strip, the top-left 232 px square
## free. Then the same inside a host app (Engine meta "mwm_play_shell") and with a fake 120 px
## camera cutout. Run under Xvfb with --resolution 1080x1920, CAPTURE_DIR=<dir>.

const MIN_HIT := 200.0
const WRIST := 256.0
const CORNER := 232.0

var out_dir: String = OS.get_environment("CAPTURE_DIR")
var main: Node
var world: World
var _fails: int = 0


func _ready() -> void:
	var ids := []
	for u in World.UNLOCKS:
		var id: String = u.id
		if not (id.length() > 2 and id[0] == "r" and id[1].is_valid_int()):
			ids.append(id)
	var f := FileAccess.open(Game.SAVE_PATH, FileAccess.WRITE)
	f.store_string(JSON.stringify({"version": 4, "money": 100, "total_earned": 40000, "unlocked": ids,
		"upgrades": {"capacity": 6, "speed": 1, "axe": 0, "machines": 2, "workers": 1, "prices": 0},
		"piles": {}, "finished": true, "sound_on": true, "music_on": false}))
	f.close()
	Game.load_game()
	await _boot()
	await _screens("standalone")
	# Inside a host app.
	Engine.set_meta(&"mwm_play_shell", true)
	await _boot()
	await _screens("shell")
	if Game.hud.has_method("apply_safe_area"):
		Game.hud.set("fake_safe_top", 120.0)
		Game.hud.call("apply_safe_area")
		await _frames(5)
		await _shot("shell_cutout_120")
		_measure("shell_cutout_120")
		Engine.remove_meta(&"mwm_play_shell")
		await _boot()
		Game.hud.set("fake_safe_top", 120.0)
		Game.hud.call("apply_safe_area")
		await _frames(5)
		await _shot("standalone_cutout_120")
		_measure("standalone_cutout_120")
	print("KIDUI %s (%d failed)" % ["PASS" if _fails == 0 else "FAIL", _fails])
	get_tree().quit(1 if _fails > 0 else 0)


func _boot() -> void:
	if main:
		main.queue_free()
		await _frames(3)
	main = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	world = main.get_node("World")
	await _frames(40)
	Game.hud.close_valley_card()


func _screens(tag: String) -> void:
	if tag == "shell":
		var h: Hud = Game.hud
		_check("shell: own menu hidden", not h.menu_btn.visible)
		_check("shell: own sound and music hidden", not h.sound_btn.is_visible_in_tree() and not h.music_btn.is_visible_in_tree())
		Game.sound_on = false
		AudioServer.set_bus_mute(0, false)
		Sfx.apply_sound_setting()
		_check("shell: saved mute does not mute the Master bus", not AudioServer.is_bus_mute(0))
		Game.sound_on = true
	else:
		_check("standalone: menu shown", Game.hud.menu_btn.visible)
	await _shot(tag + "_01_hud")
	_measure(tag + "_01_hud")
	for i in 6:
		world.player.stack.push(Items.make("log"), false)
	await _frames(10)
	await _shot(tag + "_02_carrying")
	_measure(tag + "_02_carrying")
	world.player.dump()
	await _frames(10)
	Game.hud.open_upgrades(1)
	await _frames(15)
	await _shot(tag + "_03_upgrades")
	_measure(tag + "_03_upgrades")
	Game.hud.close_upgrades()
	Game.hud.open_upgrades(2)
	await _frames(15)
	await _shot(tag + "_04_upgrades_board2")
	_measure(tag + "_04_upgrades_board2")
	Game.hud.close_upgrades()
	Game.hud.menu_panel.visible = true
	await _frames(5)
	await _shot(tag + "_05_menu")
	_measure(tag + "_05_menu")
	Game.hud.menu_panel.visible = false
	Game.hud.show_valley_card(1, "Next: cross the River Bridge")
	await _frames(15)
	await _shot(tag + "_06_valley_card")
	_measure(tag + "_06_valley_card")
	Game.hud.close_valley_card()
	await _frames(5)


## Every visible button in the HUD against the rules. Prints one line per button.
func _measure(tag: String) -> void:
	var vs := get_viewport().get_visible_rect().size
	var corner := Rect2(0, 0, CORNER, CORNER)
	for n in Game.hud.find_children("*", "BaseButton", true, false):
		var b := n as BaseButton
		if not b.is_visible_in_tree():
			continue
		var r := b.get_global_rect()
		var why: Array[String] = []
		if r.size.x < MIN_HIT or r.size.y < MIN_HIT:
			why.append("small")
		if r.end.y > vs.y - WRIST + 0.5:
			why.append("in wrist strip")
		if r.intersects(corner):
			why.append("in top-left corner")
		if b.action_mode != BaseButton.ACTION_MODE_BUTTON_RELEASE:
			why.append("acts on press")
		if not why.is_empty():
			_fails += 1
		print("%s %s  %s rect=(%d,%d %dx%d) %s" % ["FAIL" if not why.is_empty() else "ok  ", tag, _label(b),
			r.position.x, r.position.y, r.size.x, r.size.y, ", ".join(why)])


func _check(what: String, ok: bool) -> void:
	if not ok:
		_fails += 1
	print("%s %s" % ["ok  " if ok else "FAIL", what])


func _label(b: BaseButton) -> String:
	if b is Button and (b as Button).text != "":
		return "'%s'" % (b as Button).text
	for c in b.find_children("*", "Control", true, false):
		if c.get("kind") != null and str(c.get("kind")) != "":
			return "icon:" + str(c.get("kind"))
	return b.name


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(name: String) -> void:
	if out_dir == "":
		return
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("%s/%s.png" % [out_dir, name])
	print("SHOT %s %dx%d" % [name, img.get_width(), img.get_height()])
