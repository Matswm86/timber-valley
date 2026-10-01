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
	# Valley state from the last run's save must not leak in (ledger would pay a sleeping valley).
	Game.ledger.clear()
	Game.region_upgrades.clear()
	Game.region_stats.clear()
	Game.offline_pending = 0
	Game.finished = false
	for k in Game.UPGRADES:
		Game.upgrade_levels[k] = 0
	if mode == "m1":
		await _m1()
		get_tree().quit()
		return
	if mode == "chars":
		await _chars()
		get_tree().quit()
		return
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
				world.r1.get_children().filter(func(c): return c is Customer).size(), p.global_position.snapped(Vector3.ONE * 0.1)])
		await get_tree().process_frame
		t += dt
	Engine.time_scale = 1.0
	world.player.input_vector = Vector2.ZERO


func _showcase() -> void:
	Game.add_money(20000)
	for u in World.UNLOCKS:
		if str(u.id).begins_with("r2_"):
			continue
		Game.unlock(u.id)
		await _frames(2)
	if Game.hud:
		Game.hud.finish_panel.visible = false
		Game.hud.valley_card.visible = false
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
	# Laptop render stats (CPU lavapipe): triangles include the shadow pass. Not phone fps.
	print("SHOT %s tris=%d draws=%d objects=%d" % [name,
		RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME),
		RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME),
		RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_OBJECTS_IN_FRAME)])



# ---------------------------------------------------------------- M1: Birch Bend

## CAPTURE_MODE=m1: start from an original (version 1) save with the Lodge built, walk onto
## the River Bridge pad and buy it, cross into Birch Bend, buy the lathe, play the Birch Bend
## mini-tutorial, then unlock every r2 pad and shoot each area. Also checks valley sleep.
func _m1() -> void:
	var v1_ids := []
	for u in World.UNLOCKS:
		if not str(u.id).begins_with("r2_"):
			v1_ids.append(u.id)
	var f := FileAccess.open(Game.SAVE_PATH, FileAccess.WRITE)
	f.store_string(JSON.stringify({"money": 11500, "total_earned": 40000, "unlocked": v1_ids,
		"upgrades": {"capacity": 4, "speed": 3, "axe": 3, "machines": 3, "workers": 3, "prices": 3},
		"piles": {}, "finished": true, "sound_on": true}))
	f.close()
	Game.load_game()
	main = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	world = main.get_node("World")
	await _frames(40)
	await _shot("m1/01_start_from_lodge_save")
	print("M1 money=%d pads=%s" % [Game.money, world.pads.keys()])
	# Walk the last stretch to the bridge pad for real and pay it.
	_teleport(Vector3(-13.5, 0, -6))
	await _frames(20)
	await _shot("m1/02_bridge_pad")
	var ok := await _walk_to(Vector3(-20.5, 0, -6), 12.0, func() -> bool: return Game.is_unlocked("r2_bridge"))
	print("M1 bridge bought=%s money=%d" % [Game.is_unlocked("r2_bridge"), Game.money])
	await _frames(30)
	# Cross the bridge on foot (the river walls only open here).
	ok = await _walk_to(Vector3(-36, 0, -6), 14.0)
	print("M1 crossed=%s pos=%s region=%d r1_awake=%s r2_awake=%s" % [ok, world.player.global_position.snapped(Vector3.ONE * 0.1), world.current_region(), world.r1.awake, world.r2.awake])
	await _frames(20)
	await _shot("m1/03_birch_bend_arrival")
	# Buy the lathe from the pad, then play the mini-tutorial with the guide arrow.
	Game.add_money(14000)
	await _walk_to(Vector3(-45, 0, -6), 12.0, func() -> bool: return Game.is_unlocked("r2_lathe"))
	print("M1 lathe bought=%s" % Game.is_unlocked("r2_lathe"))
	await _frames(40)
	await _bot_goal(70.0)
	print("M1 tutorial veneer_shelf=%d lathe_out=%d coins=%d money=%d" % [world.shop2.shelf("veneer").count(), world.machines.lathe.output.count(), world.shop2.coin_value, Game.money])
	await _shot("m1/08_after_tutorial")
	# Unlock everything in Birch Bend and let it run.
	Game.add_money(2000000)
	for u in World.UNLOCKS:
		if str(u.id).begins_with("r2_") and not Game.is_unlocked(u.id):
			Game.unlock(u.id)
			await _frames(2)
	await _frames(5)
	await _shot("m1/09_valley_card")
	Game.hud.valley_card.visible = false
	Engine.time_scale = 4.0
	_teleport(Vector3(-42, 0, -20))
	await _frames(600)
	Engine.time_scale = 1.0
	var spots := {
		"m1/10_lathe_market": Vector3(-42, 0, -2), "m1/11_market": Vector3(-40, 0, 6),
		"m1/12_office": Vector3(-35, 0, 11), "m1/13_presses": Vector3(-44, 0, -22),
		"m1/14_flume_chute": Vector3(-57, 0, -22), "m1/15_flume_to_lathe": Vector3(-50, 0, -10),
		"m1/16_boatshop_barge": Vector3(-37, 0, -36), "m1/17_boathouse": Vector3(-67, 0, 8),
		"m1/18_west_grove_camp": Vector3(-68, 0, -16), "m1/19_bridge": Vector3(-27, 0, -6),
	}
	for k in spots:
		_teleport(spots[k])
		await _frames(30)
		await _shot(k)
	_teleport(Vector3(-34, 0, 13.4))
	await _frames(25)
	await _shot("m1/20_riverside_upgrades")
	# Valley sleep: far west, Valley 1 must sleep and pay its ledger; far east, Birch Bend sleeps.
	_teleport(Vector3(-74, 0, -40))
	await _frames(30)
	var m0 := Game.money
	await _wait_seconds(5.0)
	print("M1 SLEEP far-west r1_awake=%s r2_awake=%s r1_rate=%.1f r2_rate=%.1f money_delta_5s=%d" % [world.r1.awake, world.r2.awake, world.r1.rate(), world.r2.rate(), Game.money - m0])
	await _shot("m1/21_far_west")
	_teleport(Vector3(12, 0, -20))
	await _frames(30)
	m0 = Game.money
	await _wait_seconds(5.0)
	print("M1 SLEEP far-east r1_awake=%s r2_awake=%s r2_rate=%.1f money_delta_5s=%d" % [world.r1.awake, world.r2.awake, world.r2.rate(), Game.money - m0])
	await _shot("m1/22_home_valley_while_v2_sleeps")
	_teleport(Vector3(0, 0, 4))
	await _frames(30)
	await _shot("m1/23_start_camera_full_game")
	Game.save_game()
	print("M1 ledger=%s stats=%s" % [Game.ledger, Game.region_stats])
	for r in [world.r1, world.r2]:
		print("CENSUS %s %s" % [r.name, _census(r)])


## Rough draw-call sources per valley: meshes inside carried/piled items, characters, labels, the rest.
func _census(root: Node) -> String:
	var c := {"item_meshes": 0, "character_meshes": 0, "label3d": 0, "other_meshes": 0, "particles": 0}
	for n in root.find_children("*", "", true, false):
		if n is Label3D:
			c.label3d += 1
		elif n is CPUParticles3D:
			c.particles += 1
		elif n is MeshInstance3D or n is MultiMeshInstance3D:
			var p: Node = n
			var kind := "other_meshes"
			while p and p != root:
				if p.has_meta("item"):
					kind = "item_meshes"
					break
				if p is CharacterModel:
					kind = "character_meshes"
					break
				p = p.get_parent()
			c[kind] += 1
	return str(c)


func _teleport(p: Vector3) -> void:
	world.player.global_position = p
	world.player.velocity = Vector3.ZERO
	world._cam_pos = p


func _wait_seconds(sec: float) -> void:
	var t := 0.0
	while t < sec:
		await get_tree().process_frame
		t += get_process_delta_time()


## Walks with the joystick toward a point; returns true when there (or when done() says so).
func _walk_to(target: Vector3, timeout: float, done: Callable = Callable()) -> bool:
	var p := world.player
	var t := 0.0
	var stuck := 0.0
	var detour := 0.0
	while t < timeout:
		if done.is_valid() and done.call():
			p.input_vector = Vector2.ZERO
			return true
		var d := target - p.global_position
		d.y = 0
		if d.length() < 0.4 and not done.is_valid():
			p.input_vector = Vector2.ZERO
			return true
		var v := Vector2(d.x, d.z).normalized() if d.length() > 0.2 else Vector2.ZERO
		var dt := get_process_delta_time()
		if v != Vector2.ZERO and Vector2(p.velocity.x, p.velocity.z).length() < 0.8:
			stuck += dt
		else:
			stuck = 0.0
		if stuck > 0.3:
			detour = 0.6
			stuck = 0.0
		if detour > 0.0:
			detour -= dt
			v = v.rotated(1.3)
		p.input_vector = v
		await get_tree().process_frame
		t += dt
	p.input_vector = Vector2.ZERO
	return false


## Follows the guide arrow (World._goal) like a player would; grabs Part A close-ups on the way.
func _bot_goal(seconds: float) -> void:
	Engine.time_scale = 2.0
	var t := 0.0
	var detour := 0.0
	var stuck := 0.0
	var got := {}
	var p := world.player
	while t < seconds:
		var g := world._goal()
		var dt := get_process_delta_time() * Engine.time_scale
		if g[0] != null:
			var d: Vector3 = (g[0] as Vector3) - p.global_position
			d.y = 0
			var v := Vector2(d.x, d.z).normalized() if d.length() > 0.6 else Vector2.ZERO
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
		var now := Time.get_ticks_msec() / 1000.0
		var chopping := now < p.chopping_until
		var moving := Vector2(p.velocity.x, p.velocity.z).length() > 1.5
		if not got.has("chop") and chopping and p.stack.count() >= 1:
			got["chop"] = true
			await _closeup("m1/04_pA_chop_birch")
			await _shot("m1/05_chopping_birch_game_camera")
		elif not got.has("carry") and p.stack.count() >= 4 and moving and not chopping:
			got["carry"] = true
			await _closeup("m1/06_pA_carry_walk")
		elif not got.has("walk") and p.stack.is_empty() and moving and t > 3.0:
			got["walk"] = true
			await _closeup("m1/07_pA_walk_empty")
		if int(t / 5.0) != int((t - dt) / 5.0):
			print("t=%.0f hint='%s' back=%d:%s lathe_in=%d lathe_out=%d shelf=%d coins=%d money=%d" % [
				t, g[1], p.stack.count(), p.stack.top_type(), world.machines.lathe.input.count(),
				world.machines.lathe.output.count(), world.shop2.shelf("veneer").count(), world.shop2.coin_value, Game.money])
		await get_tree().process_frame
		t += dt
	Engine.time_scale = 1.0
	p.input_vector = Vector2.ZERO


## Character close-up: camera at 40% of its normal offset for one frame, then back.
func _closeup(name: String) -> void:
	var keep := Engine.time_scale
	Engine.time_scale = 0.05
	world.cam_offset = Vector3(0, 8.4, 6.6) * 0.4
	world._cam_pos = world.player.global_position
	await _frames(2)
	await _shot(name)
	world.cam_offset = Vector3(0, 8.4, 6.6)
	Engine.time_scale = keep



# ---------------------------------------------------------------- Part A: characters

## CAPTURE_MODE=chars: low side-angle close-ups of the KayKit characters doing their jobs,
## next to counters, sheds and the till, to check the 1.8 m figures for clipping.
func _chars() -> void:
	main = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	world = main.get_node("World")
	await _frames(10)
	Game.add_money(50000)
	for u in World.UNLOCKS:
		if not str(u.id).begins_with("r2_"):
			Game.unlock(u.id)
			await _frames(2)
	Game.hud.valley_card.visible = false
	Engine.time_scale = 4.0
	await _frames(500)
	Engine.time_scale = 1.0
	var side := Vector3(3.2, 2.0, 3.6)
	# Player walks to a tree, chops it, then walks away carrying.
	_teleport(Vector3(-4.5, 0, 1.0))
	var tree: ChopTree = world._nearest_tree(world.player.global_position)
	var chop_shot := false
	var t := 0.0
	while t < 6.0 and not chop_shot:
		var d := tree.global_position - world.player.global_position
		world.player.input_vector = Vector2(d.x, d.z).normalized() if Vector2(d.x, d.z).length() > 0.9 else Vector2.ZERO
		if Time.get_ticks_msec() / 1000.0 < world.player.chopping_until and world.player.model.axe.visible:
			await _frames(4)
			await _view("chars/01_player_chop_side", world.player.global_position, side)
			chop_shot = true
		await get_tree().process_frame
		t += get_process_delta_time()
	world.player.input_vector = Vector2.ZERO
	t = 0.0
	while t < 6.0 and world.player.stack.count() < 3:
		await get_tree().process_frame
		t += get_process_delta_time()
	world.player.input_vector = Vector2(1, 0.3).normalized()
	await _frames(25)
	await _view("chars/02_player_carry_walk_side", world.player.global_position, side)
	world.player.input_vector = Vector2.ZERO
	await _frames(30)
	await _view("chars/03_player_carry_idle_front", world.player.global_position, Vector3(0.0, 1.6, 3.8))
	# A lumberjack at work and a hauler carrying.
	for w in world.r1.get_children():
		if w is Worker and (w as Worker).job == Worker.Job.LUMBERJACK and (w as Worker).chopping_until > Time.get_ticks_msec() / 1000.0 - 1.0:
			await _view("chars/04_lumberjack", (w as Worker).global_position, side)
			break
	for w in world.r1.get_children():
		if w is Worker and (w as Worker).job == Worker.Job.HAULER and not (w as Worker).stack.is_empty():
			await _view("chars/05_hauler_carrying", (w as Worker).global_position, side)
			break
	# Shop: shoppers at the counters and the till, the cashier, the canopy.
	await _view("chars/06_shop_counters_customers", world.shop.global_position + Vector3(1.5, 0, 0), Vector3(4.5, 2.4, 4.5))
	await _view("chars/07_till_cashier", world.shop.global_position + Vector3(0, 0, -5.2), Vector3(3.0, 1.8, 3.4))
	# Office shed and carpentry shed: roof heights against a 1.8 m figure.
	_teleport(Vector3(-3.5, 0, 10.6))
	await _frames(20)
	await _view("chars/08_office_shed", Vector3(-3.5, 0, 11.5), Vector3(3.5, 2.0, 4.5))
	_teleport(Vector3(-0.7, 0, -13.0))
	await _frames(20)
	await _view("chars/09_carpentry_shed", Vector3(2, 0, -13), Vector3(3.5, 2.2, 4.8))


## Shot from a custom camera offset around a point, then back to the game camera.
func _view(name: String, at: Vector3, offset: Vector3) -> void:
	world.set_process(false)
	world.camera.global_position = at + offset
	world.camera.look_at(at + Vector3(0, 0.9, 0), Vector3.UP)
	await _frames(2)
	await _shot(name)
	world.set_process(true)
