extends Node

## Dev-only: boots the game from a clean save, lets a bot follow the guide arrow
## through the tutorial, then unlocks everything and takes screenshots. Run under Xvfb.

var out_dir: String = OS.get_environment("CAPTURE_DIR")
var mode: String = OS.get_environment("CAPTURE_MODE")
var main: Node
var world: World


func _ready() -> void:
	if FileAccess.file_exists(Game.SAVE_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(Game.SAVE_PATH))
	Game.money = 0
	Game.total_earned = 0
	Game.unlocked_ids.clear()
	Game.pile_counts.clear()
	main = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	world = main.get_node("World")
	await _frames(30)
	await _shot("01_start")
	if mode == "shots":
		await _showcase()
		get_tree().quit()
		return
	await _bot_play(90.0)
	print("BOT money=%d earned=%d unlocked=%s" % [Game.money, Game.total_earned, Game.unlocked_ids.keys()])
	await _shot("03_after_bot")
	await _showcase()
	get_tree().quit()


func _bot_play(seconds: float) -> void:
	Engine.time_scale = 3.0
	var t := 0.0
	var shot_taken := false
	var detour := 0.0
	var stuck := 0.0
	while t < seconds:
		var g := world._goal()
		var p := world.player
		var dt := get_process_delta_time() * Engine.time_scale
		if g[0] != null:
			var d: Vector3 = (g[0] as Vector3) - p.global_position
			d.y = 0
			var v := Vector2(d.x, d.z).normalized() if d.length() > 0.6 else Vector2.ZERO
			# Walk around buildings: if pushing but not moving, sidestep for a moment.
			if v != Vector2.ZERO and Vector2(p.velocity.x, p.velocity.z).length() < 0.8:
				stuck += dt
			else:
				stuck = 0.0
			if stuck > 0.25:
				detour = 0.7
				stuck = 0.0
			if detour > 0.0:
				detour -= dt
				v = v.rotated(1.3)
			p.input_vector = v
		else:
			p.input_vector = Vector2.ZERO
		if not shot_taken and p.stack.count() >= 3:
			shot_taken = true
			Engine.time_scale = 1.0
			await _frames(3)
			await _shot("02_carrying")
			Engine.time_scale = 3.0
		if int(t / 5.0) != int((t - dt) / 5.0):
			var saw: Machine = world.machines.sawmill1
			print("t=%.0f hint='%s' back=%d:%s saw_in=%d saw_out=%d shelf=%d coins=%d money=%d customers=%d pos=%s" % [
				t, g[1], p.stack.count(), p.stack.top_type(), saw.input.count(), saw.output.count(),
				world.shop.shelf("plank").count(), world.shop.coin_value, Game.money,
				world.get_children().filter(func(c): return c is Customer).size(), p.global_position.snapped(Vector3.ONE * 0.1)])
		await get_tree().process_frame
		t += dt
	Engine.time_scale = 1.0
	world.player.input_vector = Vector2.ZERO


func _showcase() -> void:
	Game.add_money(20000)
	for u in World.UNLOCKS:
		Game.unlock(u.id)
		await _frames(2)
	if Game.hud:
		Game.hud.finish_panel.visible = false
	Engine.time_scale = 4.0
	await _frames(400)
	Engine.time_scale = 1.0
	var spots := {
		"04_yard": Vector3(2, 0, -2), "05_shop": Vector3(9, 0, 2), "06_carpentry": Vector3(0, 0, -12),
		"07_sawmill2_cnc": Vector3(3, 0, -22), "08_factory": Vector3(4, 0, -34), "09_lodge": Vector3(-10, 0, -36),
		"10_forest": Vector3(-12, 0, -14), "12_megasaw": Vector3(11, 0, -10.5), "13_belts": Vector3(4, 0, 2),
	}
	for k in spots:
		world.player.global_position = spots[k]
		world._cam_pos = spots[k]
		await _frames(25)
		await _shot(k)
	world.player.global_position = Vector3(-3.5, 0, 10.0)
	world._cam_pos = world.player.global_position
	await _frames(20)
	await _shot("11_upgrades")


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(name: String) -> void:
	if out_dir == "":
		return
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_jpg("%s/%s.jpg" % [out_dir, name], 0.85)
	print("SHOT ", name)
