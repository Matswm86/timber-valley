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
	# The autoload loaded the last run's save before it was deleted: build sites (rent), orders and
	# the finished flag must not leak in either.
	Game.sites.clear()
	Game.orders.clear()
	Game.complete = false
	Game.finished = false
	for k in Game.UPGRADES:
		Game.upgrade_levels[k] = 0
	if mode == "m1":
		await _m1()
		get_tree().quit()
		return
	if mode == "m2":
		await _m2()
		get_tree().quit()
		return
	if mode == "census":
		await _census_mode()
		get_tree().quit()
		return
	if mode == "safety":
		await _safety()
		get_tree().quit()
		return
	if mode == "m3":
		await _m3()
		get_tree().quit()
		return
	if mode == "m4":
		await _m4()
		get_tree().quit()
		return
	if mode == "m5":
		await _m5()
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
	await _pad_icon_shot()
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
		if not _is_v1(u.id):
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


## Job 2: pads whose title names a product show its icon beside the price. Two test-only pads
## (not wired to any unlock) next to the player, one small and one big.
func _pad_icon_shot() -> void:
	# Open ground south of the yard, between the start path and the market.
	_teleport(Vector3(3.8, 0, 12.2))
	var small := UnlockPad.new().setup("test_icon_a", 70, "Hire a Plank Carrier", Vector2(2.4, 2.4))
	small.position = Vector3(1.6, 0, 8.6)
	world.add_child(small)
	var big := UnlockPad.new().setup("test_icon_b", 1200, "Carpentry: Chairs", Vector2(3.2, 3.2))
	big.position = Vector3(5.9, 0, 8.4)
	world.add_child(big)
	await _frames(30)
	await _shot("03b_pad_icons")
	small.queue_free()
	big.queue_free()
	await _frames(2)


## A pad's price from Balance.UNLOCKS (so the bot follows any rebalance).
func _cost(id: String) -> int:
	for u in World.UNLOCKS:
		if u.id == id:
			return int(u.cost)
	return 0


## Home Valley pad ids (later valleys are prefixed r2_, r3_, ...).
func _is_v1(id: String) -> bool:
	return not (id.length() > 2 and id[0] == "r" and id[1].is_valid_int() and id[2] == "_")


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
	var vp := get_viewport()
	print("PASS %s visible_draws=%d shadow_draws=%d visible_tris=%d shadow_tris=%d" % [name,
		vp.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE, Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME),
		vp.get_render_info(Viewport.RENDER_INFO_TYPE_SHADOW, Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME),
		vp.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE, Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME),
		vp.get_render_info(Viewport.RENDER_INFO_TYPE_SHADOW, Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME)])
	if OS.get_environment("CAPTURE_CENSUS") != "":
		_frustum_census(name)
	if OS.get_environment("CAPTURE_ABLATE") != "" and (name.begins_with("m1/1") or name.begins_with("m1/2") or OS.get_environment("CAPTURE_ABLATE") == "all"):
		await _shadow_ablation(name)
		await _visible_ablation(name)



# ---------------------------------------------------------------- M1: Birch Bend

## CAPTURE_MODE=m1: start from an original (version 1) save with the Lodge built, walk onto
## the River Bridge pad and buy it, cross into Birch Bend, buy the lathe, play the Birch Bend
## mini-tutorial, then unlock every r2 pad and shoot each area. Also checks valley sleep.
func _m1() -> void:
	var v1_ids := []
	for u in World.UNLOCKS:
		if _is_v1(u.id):
			v1_ids.append(u.id)
	var f := FileAccess.open(Game.SAVE_PATH, FileAccess.WRITE)
	f.store_string(JSON.stringify({"money": _cost("r2_bridge") + 500, "total_earned": 40000, "unlocked": v1_ids,
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
	await _gateway_check()
	# Walk the last stretch to the bridge pad for real and pay it.
	_teleport(Vector3(-13.5, 0, -6))
	await _frames(20)
	await _shot("m1/02_bridge_pad")
	var ok := await _walk_to(Vector3(-20.5, 0, -6), 12.0, func() -> bool: return Game.is_unlocked("r2_bridge"))
	print("M1 bridge bought=%s money=%d" % [Game.is_unlocked("r2_bridge"), Game.money])
	# Gateway paid: the arch folds away and the glow drifts along the bridge into Birch Bend.
	await _wait_seconds(0.7)
	await _shot("m1/02b_gateway_opened_glow_on_bridge")
	await _frames(30)
	# Cross the bridge on foot (the river walls only open here).
	ok = await _walk_to(Vector3(-36, 0, -6), 14.0)
	print("M1 crossed=%s pos=%s region=%d r1_awake=%s r2_awake=%s" % [ok, world.player.global_position.snapped(Vector3.ONE * 0.1), world.current_region(), world.r1.awake, world.r2.awake])
	await _frames(20)
	await _shot("m1/03_birch_bend_arrival")
	# Buy the lathe from the pad, then play the mini-tutorial with the guide arrow.
	Game.add_money(_cost("r2_lathe") + 1000)
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



## Mats (2026-10-01) built the Lodge, could not afford the bridge yet and got no arrow at all.
## From the Lodge-complete save with less money than the bridge costs, the arrow must target the
## r2_bridge pad; the valley card names it; closing the card pans the camera to it and back.
func _gateway_check() -> void:
	var keep := Game.money
	Game.money = _cost("r2_bridge") / 3
	_teleport(Vector3(1.0, 0, -29.0))
	await _frames(20)
	var g := world._goal()
	var bp: Vector3 = (world.pads["r2_bridge"] as Node3D).global_position
	var on_pad := g[0] != null and (g[0] as Vector3).distance_to(bp) < 0.1
	print("GATEWAY arrow money=%d target=%s bridge_pad=%s guide_visible=%s hint='%s' %s" % [Game.money, g[0], bp, world.guide.visible, g[1], "PASS" if on_pad and world.guide.visible else "FAIL"])
	await _shot("m1/00a_gateway_arrow_short_of_money")
	Game.hud.show_valley_card(1, world.gateway_line("lodge"))
	if not Game.hud.valley_card_closed.is_connected(world.pan_to_gateway):
		Game.hud.valley_card_closed.connect(world.pan_to_gateway)
	await _frames(5)
	await _shot("m1/00b_valley_card_names_gateway")
	Game.hud.close_valley_card()
	await _wait_seconds(0.75)
	var cam_d := Vector2(world._cam_pos.x - bp.x, world._cam_pos.z - bp.z).length()
	print("GATEWAY pan mid cam_to_pad=%.1f %s" % [cam_d, "PASS" if cam_d < 1.5 else "FAIL"])
	await _shot("m1/00c_card_closed_pan_at_gateway")
	await _wait_seconds(1.2)
	var back_d := Vector2(world._cam_pos.x - world.player.global_position.x, world._cam_pos.z - world.player.global_position.z).length()
	print("GATEWAY pan back cam_to_player=%.1f %s" % [back_d, "PASS" if back_d < 1.0 else "FAIL"])
	Game.money = keep


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
		if _is_v1(u.id):
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


## Geometry inside the camera frustum, by owner (first ancestor with a class_name script) and
## surface count. Surfaces approximate draws in the visible pass; "sh" = shadow-casting surfaces.
func _frustum_census(tag: String) -> void:
	var cam := get_viewport().get_camera_3d()
	var planes := cam.get_frustum()
	var out := {}
	for n in get_tree().root.find_children("*", "GeometryInstance3D", true, false):
		var g := n as GeometryInstance3D
		if not g.is_visible_in_tree():
			continue
		var surf := 1
		if g is MeshInstance3D:
			var m := (g as MeshInstance3D).mesh
			if m == null:
				continue
			surf = m.get_surface_count()
		elif g is MultiMeshInstance3D:
			var mm := (g as MultiMeshInstance3D).multimesh
			if mm == null or mm.mesh == null or mm.instance_count == 0:
				continue
			surf = mm.mesh.get_surface_count()
		elif g is Label3D:
			surf = 2 if (g as Label3D).outline_size > 0 else 1
		var box := g.global_transform * g.get_aabb()
		var inside := true
		for p in planes:
			var pl: Plane = p
			var c := box.get_center()
			var e := box.size * 0.5
			var r := absf(pl.normal.x) * e.x + absf(pl.normal.y) * e.y + absf(pl.normal.z) * e.z
			if pl.distance_to(c) > r:
				inside = false
				break
		if not inside:
			continue
		var owner_name := "scenery"
		var p: Node = g
		while p:
			if p.has_meta("item"):
				var holder: Node = p.get_parent()
				owner_name = "item@%s" % (holder.get_script().get_global_name() if holder and holder.get_script() else (holder.name if holder else "-"))
				break
			var s: Script = p.get_script()
			if s and s.get_global_name() != "" and p != g:
				owner_name = s.get_global_name()
				break
			if p is World:
				break
			p = p.get_parent()
		var k := "%s/%s" % [owner_name, g.get_class()]
		if owner_name == "item@ItemStack" and OS.get_environment("CAPTURE_DEBUG") != "":
			var itn: Node = g
			while itn and not itn.has_meta("item"):
				itn = itn.get_parent()
			var tw: Variant = itn.get_meta("tw") if itn.has_meta("tw") else null
			print("  LOOSE %s holder=%s landed=%s tw_valid=%s tw_running=%s" % [itn.name, itn.get_parent().get_path(), itn.has_meta("landed"), tw != null and (tw as Tween).is_valid(), tw != null and (tw as Tween).is_valid() and (tw as Tween).is_running()])
		if not out.has(k):
			out[k] = [0, 0]
		out[k][0] += surf
		if g.cast_shadow != GeometryInstance3D.SHADOW_CASTING_SETTING_OFF and not (g is Label3D):
			out[k][1] += surf
	_shadow_census(tag, cam)
	var keys := out.keys()
	keys.sort_custom(func(a, b): return out[a][0] > out[b][0])
	var parts := []
	for k in keys:
		parts.append("%s=%d(sh%d)" % [k, out[k][0], out[k][1]])
	print("FRUSTUM %s %s" % [tag, " ".join(parts)])



## Shadow casters the directional light can reach: inside the side planes of the frustum (grown
## 6 m toward the light) and within its 30 m shadow distance. Counts surfaces, not splits.
func _shadow_census(tag: String, cam: Camera3D) -> void:
	var planes := cam.get_frustum()
	var out := {}
	var cp := cam.global_position
	for n in get_tree().root.find_children("*", "GeometryInstance3D", true, false):
		var g := n as GeometryInstance3D
		if not g.is_visible_in_tree() or g.cast_shadow == GeometryInstance3D.SHADOW_CASTING_SETTING_OFF or g is Label3D:
			continue
		var surf := 1
		if g is MeshInstance3D:
			if (g as MeshInstance3D).mesh == null:
				continue
			surf = (g as MeshInstance3D).mesh.get_surface_count()
		elif g is MultiMeshInstance3D:
			var mm := (g as MultiMeshInstance3D).multimesh
			if mm == null or mm.mesh == null or mm.instance_count == 0:
				continue
			surf = mm.mesh.get_surface_count()
		var box := g.global_transform * g.get_aabb()
		var c := box.get_center()
		var e := box.size * 0.5
		var rad := e.length()
		if c.distance_to(cp) - rad > 30.0:
			continue
		var inside := true
		for i in planes.size():
			if i == 0 or i == 1:
				continue
			var pl: Plane = planes[i]
			var r := absf(pl.normal.x) * e.x + absf(pl.normal.y) * e.y + absf(pl.normal.z) * e.z
			if pl.distance_to(c) > r + 6.0:
				inside = false
				break
		if not inside:
			continue
		var owner_name := "scenery"
		var p: Node = g
		while p:
			if p.has_meta("item"):
				var holder: Node = p.get_parent()
				owner_name = "item@%s" % (holder.get_script().get_global_name() if holder and holder.get_script() else (holder.name if holder else "-"))
				break
			var s: Script = p.get_script()
			if s and s.get_global_name() != "" and p != g:
				owner_name = s.get_global_name()
				break
			if p is World:
				break
			p = p.get_parent()
		var k := "%s/%s" % [owner_name, g.get_class()]
		if OS.get_environment("CAPTURE_DEBUG") != "" and owner_name in ["Machine", "Region", "World"]:
			print("  CASTER %s merged=%s static=%s proxied=%s" % [g.get_path(), g.has_meta("merged"), g.has_meta("static"), g.has_meta("proxied")])
		out[k] = int(out.get(k, 0)) + surf
	var keys := out.keys()
	keys.sort_custom(func(a, b): return out[a] > out[b])
	var parts := []
	var total := 0
	for k in keys:
		parts.append("%s=%d" % [k, out[k]])
		total += int(out[k])
	print("SHADOWSET %s total=%d %s" % [tag, total, " ".join(parts)])



## Real shadow-pass cost per caster category: turn the category's shadows off for one frame and
## read how many shadow draws disappear (cascades cull with a light-space box, so a frustum
## estimate undercounts).
func _shadow_ablation(tag: String) -> void:
	var vp := get_viewport()
	var keep_scale := Engine.time_scale
	Engine.time_scale = 0.0
	await RenderingServer.frame_post_draw
	var base := vp.get_render_info(Viewport.RENDER_INFO_TYPE_SHADOW, Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME)
	var cats := {}
	for n in get_tree().root.find_children("*", "GeometryInstance3D", true, false):
		var g := n as GeometryInstance3D
		if g.cast_shadow == GeometryInstance3D.SHADOW_CASTING_SETTING_OFF or not g.is_visible_in_tree():
			continue
		var cat := "other"
		var p: Node = g
		while p:
			if p.has_meta("item"):
				cat = "loose_item"
				break
			var sc: Script = p.get_script()
			if sc and sc.get_global_name() != "" and p != g:
				cat = sc.get_global_name()
				break
			p = p.get_parent()
		if g.name.begins_with("Deco_"):
			cat = "deco"
		if not cats.has(cat):
			cats[cat] = []
		(cats[cat] as Array).append(g)
	var parts := []
	for cat in cats:
		var list: Array = cats[cat]
		var saved := []
		for g in list:
			saved.append((g as GeometryInstance3D).cast_shadow)
			(g as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var now := vp.get_render_info(Viewport.RENDER_INFO_TYPE_SHADOW, Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME)
		for i in list.size():
			(list[i] as GeometryInstance3D).cast_shadow = saved[i]
		parts.append([cat, base - now, list.size()])
	parts.sort_custom(func(a, b): return a[1] > b[1])
	var txt := []
	for p in parts:
		txt.append("%s=-%d(n%d)" % p)
	print("ABLATE %s shadow_draws=%d %s" % [tag, base, " ".join(txt)])
	await RenderingServer.frame_post_draw
	Engine.time_scale = keep_scale


## Visible-pass cost of Label3D nodes and zone ground markers: hide each set for a frame.
func _visible_ablation(tag: String) -> void:
	var vp := get_viewport()
	var keep_scale := Engine.time_scale
	Engine.time_scale = 0.0
	await RenderingServer.frame_post_draw
	var base := vp.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE, Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME)
	var base_t := vp.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE, Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME)
	var sets := {"label3d": [], "zone_marker": [], "deco": [], "itemstack_mm": []}
	for n in get_tree().root.find_children("*", "GeometryInstance3D", true, false):
		var g := n as GeometryInstance3D
		if not g.visible:
			continue
		if g is Label3D:
			sets.label3d.append(g)
		elif g.get_parent() is Zone and g == (g.get_parent() as Zone).marker:
			sets.zone_marker.append(g)
		elif g.name.begins_with("Deco_") or (g is MultiMeshInstance3D and g.get_parent() is World and g.visibility_range_end > 0.0 and g.material_override == null):
			sets.deco.append(g)
		elif g is MultiMeshInstance3D and g.get_parent() is ItemStack:
			sets.itemstack_mm.append(g)
	var parts := []
	for k in sets:
		for g in sets[k]:
			(g as Node3D).visible = false
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var now := vp.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE, Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME)
		var now_t := vp.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE, Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME)
		for g in sets[k]:
			(g as Node3D).visible = true
		parts.append("%s=-%d/-%dk(n%d)" % [k, base - now, (base_t - now_t) / 1000, (sets[k] as Array).size()])
	print("VABLATE %s visible_draws=%d %s" % [tag, base, " ".join(parts)])
	await RenderingServer.frame_post_draw
	Engine.time_scale = keep_scale


# ---------------------------------------------------------------- M2: Maple Highlands

## CAPTURE_MODE=m2: start from an M1-complete save (Boathouse built), follow the arrow to the
## Highland Gate, buy it, walk through, buy the beam saw and play the Highlands mini-tutorial,
## ride the handcar home and back, fill a house's first stage by hand, then unlock everything,
## finish the Clock Tower and shoot each area. Also checks rent and valley sleep with 3 valleys.
func _m2() -> void:
	var m1_ids := []
	for u in World.UNLOCKS:
		if not str(u.id).begins_with("r3_"):
			m1_ids.append(u.id)
	var f := FileAccess.open(Game.SAVE_PATH, FileAccess.WRITE)
	f.store_string(JSON.stringify({"version": 2, "money": _cost("r3_gate") * 3 / 4, "total_earned": 2500000, "unlocked": m1_ids,
		"upgrades": {"capacity": 6, "speed": 5, "axe": 5, "machines": 5, "workers": 5, "prices": 5},
		"region_upgrades": {"2": {"saws": 2, "crew": 2, "fame": 2}}, "ledger": {"r1": 150.0, "r2": 420.0},
		"region_stats": {"1": {"time": 1200.0, "earned": 40000}, "2": {"time": 3000.0, "earned": 1500000}},
		"piles": {}, "finished": true, "sound_on": true}))
	f.close()
	Game.load_game()
	main = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	world = main.get_node("World")
	await _frames(40)
	await _shot("m2/01_start_from_m1_save")
	print("M2 money=%d pads=%s" % [Game.money, world.pads.keys()])
	# The arrow points at the Highland Gate even when it is not affordable.
	var keep := Game.money
	Game.money = _cost("r3_gate") / 4
	_teleport(Vector3(1.0, 0, -28.0))
	await _frames(20)
	var g := world._goal()
	var gp: Vector3 = (world.pads["r3_gate"] as Node3D).global_position
	var on_gate := g[0] != null and (g[0] as Vector3).distance_to(gp) < 0.1
	print("GATEWAY3 arrow target=%s gate_pad=%s guide_visible=%s hint='%s' %s" % [g[0], gp, world.guide.visible, g[1], "PASS" if on_gate and world.guide.visible else "FAIL"])
	await _shot("m2/02_highland_gate_arrow")
	var line: String = world.gateway_line("r2_boathouse")
	Game.hud.show_valley_card(2, line)
	if not Game.hud.valley_card_closed.is_connected(world.pan_to_gateway):
		Game.hud.valley_card_closed.connect(world.pan_to_gateway)
	await _frames(5)
	print("GATEWAY3 card line='%s' %s" % [line.replace("\n", " "), "PASS" if line.contains("Highland Gate") else "FAIL"])
	await _shot("m2/03_boathouse_card_names_gate")
	Game.hud.close_valley_card()
	await _wait_seconds(0.75)
	var cam_d := Vector2(world._cam_pos.x - gp.x, world._cam_pos.z - gp.z).length()
	print("GATEWAY3 pan mid cam_to_pad=%.1f %s" % [cam_d, "PASS" if cam_d < 1.5 else "FAIL"])
	await _shot("m2/04_pan_at_highland_gate")
	await _wait_seconds(1.2)
	Game.money = maxi(keep, _cost("r3_gate") + 10000)
	# Walk onto the gate pad and pay it, then walk through the gate into the Highlands.
	_teleport(Vector3(2.8, 0, -39.0))
	await _frames(20)
	await _shot("m2/05_gate_pad_glow")
	await _walk_to(Vector3(0, 0, -42.4), 12.0, func() -> bool: return Game.is_unlocked("r3_gate"))
	print("M2 gate bought=%s money=%d" % [Game.is_unlocked("r3_gate"), Game.money])
	await _wait_seconds(0.7)
	await _shot("m2/06_gate_opened")
	var ok := await _walk_to(Vector3(0, 0, -60), 16.0)
	print("M2 crossed=%s pos=%s region=%d awake r1=%s r2=%s r3=%s" % [ok, world.player.global_position.snapped(Vector3.ONE * 0.1), world.current_region(), world.r1.awake, world.r2.awake, world.r3.awake])
	await _frames(20)
	await _shot("m2/07_highlands_arrival")
	# Buy the beam saw, then play the mini-tutorial with the guide arrow.
	Game.add_money(_cost("r3_beamsaw") + 1000)
	await _walk_to(Vector3(2.5, 0, -64.5), 14.0, func() -> bool: return Game.is_unlocked("r3_beamsaw"))
	print("M2 beamsaw bought=%s" % Game.is_unlocked("r3_beamsaw"))
	await _frames(40)
	await _bot_goal3(45.0)
	var saw: Machine = world.machines.beamsaw
	print("M2 tutorial beam_shelf=%d saw_out=%d coins=%d money=%d" % [world.shop3.shelf("beam").count(), saw.output.count(), world.shop3.coin_value, Game.money])
	await _shot("m2/08_after_tutorial")
	# Handcar: Highlands -> Home Valley, then Home Valley -> Highlands.
	await _handcar_ride(3, 1, "m2/09_handcar_arrived_home")
	await _handcar_ride(1, 3, "m2/10_handcar_back_in_highlands")
	# Village Plot 1: pay the plot, carry 20 beams onto its beam square: stage 1 rises.
	var total := 0
	for u in World.UNLOCKS:
		if str(u.id).begins_with("r3_"):
			total += int(u.cost)
	Game.add_money(total)
	for id in ["r3_grove2", "r3_office", "r3_jack1", "r3_forklift1", "r3_cashier", "r3_planer", "r3_house1"]:
		Game.unlock(id)
		await _frames(2)
	var site: BuildSite = world.sites["r3_house1"]
	_teleport(site.global_position + Vector3(4.2, 0, 1.4))
	await _frames(10)
	while not world.player.stack.is_empty():
		world.player.stack.take_and_free()
	for i in 20:
		world.player.stack.push(Items.make("beam"), false)
	await _frames(5)
	await _walk_to(site.zone_of("beam").global_position, 8.0, func() -> bool: return world.player.stack.is_empty())
	await _wait_seconds(1.6)
	var shown := 0
	for st in site.stages:
		if st.visible:
			shown += 1
	print("SITE house1 delivered=%s fraction=%.2f stages_shown=%d/%d %s" % [site.delivered, site.fraction(), shown, site.stages.size(), "PASS" if shown >= 1 else "FAIL"])
	await _shot("m2/11_house_stage1_by_hand")
	# Everything in the Highlands, then let the crews, forklift, belts and train run.
	for u in World.UNLOCKS:
		if str(u.id).begins_with("r3_") and not Game.is_unlocked(u.id):
			Game.unlock(u.id)
			await _frames(2)
	if Game.hud:
		Game.hud.valley_card.visible = false
	_teleport(Vector3(2, 0, -80))
	Engine.time_scale = 4.0
	await _frames(900)
	Engine.time_scale = 1.0
	var fk: Worker = world.forklift
	print("M2 forklift pos=%s load=%d:%s house1=%s house2=%s" % [fk.global_position.snapped(Vector3.ONE * 0.1), fk.stack.count(), fk.stack.top_type(), world.sites["r3_house1"].delivered, world.sites["r3_house2"].delivered])
	var spots := {
		"m2/20_entrance_stop_office": Vector3(0, 0, -59), "m2/21_beamsaw_market": Vector3(6, 0, -65),
		"m2/22_market": Vector3(11, 0, -64), "m2/23_planer_belts": Vector3(3, 0, -77),
		"m2/24_kitfactory": Vector3(5, 0, -89), "m2/25_rail_platform": Vector3(8, 0, -101),
		"m2/26_village_south": Vector3(-13, 0, -66), "m2/27_village_north": Vector3(-13, 0, -88),
		"m2/28_clocktower_site": Vector3(-9, 0, -108), "m2/29_north_ridge_groves": Vector3(-2, 0, -104),
		"m2/30_gate_from_highlands": Vector3(0, 0, -53), "m2/31_home_handcar_stop": Vector3(-8, 0, 10),
		"m2/32_birch_handcar_stop": Vector3(-34, 0, 5),
	}
	for k in spots:
		_teleport(spots[k])
		await _frames(30)
		await _shot(k)
	# Train: wait for it at the platform.
	_teleport(Vector3(8, 0, -101))
	var tw := 0.0
	var dock: TruckDock = world.machines.rail
	while tw < 25.0 and dock.state != TruckDock.State.LOADING:
		await get_tree().process_frame
		tw += get_process_delta_time()
	await _frames(10)
	print("TRAIN state=%s wagons=%d loaded=%d pile=%d" % [dock.state, dock.beds.size(), dock._loaded(), dock.pile.count()])
	await _shot("m2/33_train_at_platform")
	# Finish every house and the Clock Tower (goods pushed into the site intakes): rent + card.
	for id in Balance.BUILD_SITES:
		var s2: BuildSite = world.sites[id]
		for item in s2.goods:
			var need: int = s2.room(item)
			for i in need:
				s2.intake_of(item).push(Items.make(item), false)
		await _frames(3)
	await _frames(30)
	print("SITES done=%d rent_rate=%.1f card_visible=%s card_title='%s'" % [Game.houses_done(), Game.rent_rate(), Game.hud.valley_card.visible, (Game.hud.valley_card.find_child("Title", true, false) as Label).text])
	await _shot("m2/34_clocktower_valley_card")
	Game.hud.valley_card.visible = false
	_teleport(Vector3(-13, 0, -80))
	await _frames(40)
	await _shot("m2/35_village_finished")
	_teleport(Vector3(-9, 0, -107))
	await _frames(40)
	await _shot("m2/36_clocktower_finished")
	# Sleep: Birch Bend far west -> the Highlands sleep; rent still pays.
	_teleport(Vector3(-74, 0, -40))
	await _frames(30)
	var m0 := Game.money
	await _wait_seconds(5.0)
	print("M2 SLEEP far-west awake r1=%s r2=%s r3=%s r3_rate=%.1f rent=%.1f money_delta_5s=%d" % [world.r1.awake, world.r2.awake, world.r3.awake, world.r3.rate(), Game.rent_rate(), Game.money - m0])
	_teleport(Vector3(0, 0, -50))
	await _frames(30)
	var awake := 0
	for r in [world.r1, world.r2, world.r3]:
		if r.awake:
			awake += 1
	print("M2 SLEEP at-gate awake r1=%s r2=%s r3=%s count=%d %s" % [world.r1.awake, world.r2.awake, world.r3.awake, awake, "PASS" if awake <= 2 else "FAIL"])
	Game.save_game()
	print("M2 ledger=%s sites=%s" % [Game.ledger, Game.sites])
	for r in [world.r1, world.r2, world.r3]:
		print("CENSUS %s %s" % [r.name, _census(r)])


## Walks onto the tile for `to` at the stop in valley `from`; PASS when the player lands at `to`.
func _handcar_ride(from: int, to: int, shot: String) -> void:
	var stop: Node3D = world._stops[from]
	var tile := Vector3.INF
	for z in stop.get_children():
		if z is Zone and z.label and z.label.text.replace("\n", " ") == str(Balance.REGIONS[to].name).to_upper():
			tile = (z as Zone).global_position
	var land: Vector3 = Balance.HANDCAR_STOPS[to].land
	_teleport(Balance.HANDCAR_STOPS[from].land)
	await _frames(10)
	await _walk_to(tile, 6.0)
	var t := 0.0
	while t < 4.0 and world.player.global_position.distance_to(land) > 0.5:
		await get_tree().process_frame
		t += get_process_delta_time()
	await _wait_seconds(0.5)
	var d := world.player.global_position.distance_to(land)
	print("HANDCAR %d->%d tile=%s arrived=%.1fm region=%d t=%.2fs %s" % [from, to, tile, d, world.current_region(), t, "PASS" if d < 0.6 else "FAIL"])
	await _shot(shot)


## Follows the guide arrow in the Highlands (mini-tutorial).
func _bot_goal3(seconds: float) -> void:
	Engine.time_scale = 2.0
	var t := 0.0
	var detour := 0.0
	var stuck := 0.0
	var p := world.player
	var shot := false
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
		if not shot and p.stack.top_type() == "maple_log" and p.stack.count() >= 4:
			shot = true
			Engine.time_scale = 1.0
			await _frames(3)
			await _shot("m2/07b_carrying_maple_logs")
			Engine.time_scale = 2.0
		if int(t / 5.0) != int((t - dt) / 5.0):
			var saw: Machine = world.machines.beamsaw
			print("t=%.0f hint='%s' back=%d:%s saw_in=%d saw_out=%d shelf=%d coins=%d" % [
				t, g[1], p.stack.count(), p.stack.top_type(), saw.input.count(), saw.output.count(),
				world.shop3.shelf("beam").count(), world.shop3.coin_value])
		await get_tree().process_frame
		t += dt
	Engine.time_scale = 1.0
	p.input_vector = Vector2.ZERO


# ---------------------------------------------------------------- M3-M5: Redwood Coast, Frost Peaks, Station

## Ids of every pad in valleys up to `last` (cap_ pads count as valley 6).
func _ids_upto(last: int) -> Array:
	var out := []
	for u in World.UNLOCKS:
		var r := 1
		var id: String = u.id
		if id.begins_with("cap_"):
			r = 6
		elif not _is_v1(id):
			r = int(id[1])
		if r <= last:
			out.append(id)
	return out


## Delivered goods for every finished build site among `ids` (houses, landmarks; not slipways).
func _sites_done(ids: Array) -> Dictionary:
	var out := {}
	for sid in Balance.BUILD_SITES:
		var info: Dictionary = Balance.BUILD_SITES[sid]
		if sid in ids and not bool(info.get("repeat", false)):
			out[sid] = (info.goods as Dictionary).duplicate()
	return out


func _write_save(ids: Array, money: int, extra: Dictionary = {}) -> void:
	var d := {"version": 4, "money": money, "total_earned": 9000000, "unlocked": ids,
		"upgrades": {"capacity": 6, "speed": 5, "axe": 5, "machines": 5, "workers": 5, "prices": 5},
		"region_upgrades": {"2": {"saws": 3, "crew": 3, "fame": 3}, "3": {"saws": 3, "crew": 3, "fame": 3}},
		"ledger": {"r1": 95.0, "r2": 280.0, "r3": 740.0}, "region_stats": {"1": {"time": 1400.0, "earned": 60000}},
		"sites": _sites_done(ids), "piles": {}, "finished": true, "sound_on": true}
	for k in extra:
		d[k] = extra[k]
	var f := FileAccess.open(Game.SAVE_PATH, FileAccess.WRITE)
	f.store_string(JSON.stringify(d))
	f.close()
	Game.load_game()
	main = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	world = main.get_node("World")


## Arrow at the next gateway while short of money, the landmark card names it, the pan visits it.
func _gateway_flow(tag: String, gate_id: String, landmark: String, region: int) -> void:
	var keep := Game.money
	Game.money = _cost(gate_id) / 4
	var gp: Vector3 = (world.pads[gate_id] as Node3D).global_position
	_teleport(gp + Vector3(-6.0, 0, 4.0))
	await _frames(20)
	var g := world._goal()
	var on_gate := g[0] != null and (g[0] as Vector3).distance_to(gp) < 0.1
	print("GATEWAY %s arrow target=%s pad=%s guide=%s hint='%s' %s" % [gate_id, g[0], gp, world.guide.visible, g[1], "PASS" if on_gate and world.guide.visible else "FAIL"])
	await _shot("%s/02_gateway_arrow" % tag)
	var line: String = world.gateway_line(landmark)
	Game.hud.show_valley_card(region, line)
	if not Game.hud.valley_card_closed.is_connected(world.pan_to_gateway):
		Game.hud.valley_card_closed.connect(world.pan_to_gateway)
	await _frames(5)
	var gate_title := ""
	for u in World.UNLOCKS:
		if u.id == gate_id:
			gate_title = u.title
	print("GATEWAY %s card line='%s' %s" % [gate_id, line.replace("\n", " "), "PASS" if line.contains(gate_title) else "FAIL"])
	await _shot("%s/03_landmark_card_names_gateway" % tag)
	Game.hud.close_valley_card()
	await _wait_seconds(0.75)
	var cam_d := Vector2(world._cam_pos.x - gp.x, world._cam_pos.z - gp.z).length()
	print("GATEWAY %s pan mid cam_to_pad=%.1f %s" % [gate_id, cam_d, "PASS" if cam_d < 1.5 else "FAIL"])
	await _shot("%s/04_pan_at_gateway" % tag)
	await _wait_seconds(1.2)
	Game.money = maxi(keep, _cost(gate_id) + 20000)


## Follows the guide arrow (any valley's mini-tutorial) for `seconds` of game time.
func _bot_follow(seconds: float, tag: String, carry_item: String) -> void:
	Engine.time_scale = 2.0
	var t := 0.0
	var detour := 0.0
	var stuck := 0.0
	var p := world.player
	var shot := false
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
		if not shot and p.stack.top_type() == carry_item and p.stack.count() >= 4:
			shot = true
			Engine.time_scale = 1.0
			await _frames(3)
			await _shot("%s/07b_carrying_%s" % [tag, carry_item])
			Engine.time_scale = 2.0
		if int(t / 5.0) != int((t - dt) / 5.0):
			print("%s t=%.0f hint='%s' back=%d:%s money=%d" % [tag, t, g[1], p.stack.count(), p.stack.top_type(), Game.money])
		await get_tree().process_frame
		t += dt
	Engine.time_scale = 1.0
	p.input_vector = Vector2.ZERO


func _unlock_region(prefix: String) -> void:
	var total := 0
	for u in World.UNLOCKS:
		if str(u.id).begins_with(prefix):
			total += int(u.cost)
	Game.add_money(total)
	for u in World.UNLOCKS:
		if str(u.id).begins_with(prefix) and not Game.is_unlocked(u.id):
			Game.unlock(u.id)
			await _frames(2)
	if Game.hud:
		Game.hud.valley_card.visible = false


func _shots(spots: Dictionary, frames: int = 30) -> void:
	# A tall carried tower from a tutorial would hide the view: throw it away first.
	world.player.dump()
	for k in spots:
		_teleport(spots[k])
		await _frames(frames)
		await _shot(k)


func _awake_count() -> int:
	var n := 0
	for rid in world.regions:
		if (world.regions[rid] as Region).awake:
			n += 1
	return n


## CAPTURE_MODE=m3: from an M2-complete save (Clock Tower built) to the Level Crossing, the
## Redwood Coast mini-tutorial, the handcar, then every pad: cargo orders and two slipways run
## with no player, the Lighthouse finishes and its card names the Cable Car.
func _m3() -> void:
	var ids := _ids_upto(3)
	_write_save(ids, _cost("r4_crossing") * 3 / 4)
	await _frames(40)
	await _shot("m3/01_start_from_m2_save")
	print("M3 money=%d pads=%s" % [Game.money, world.pads.keys()])
	await _gateway_flow("m3", "r4_crossing", "r3_clocktower", 3)
	_teleport(Vector3(8.0, 0, -18.0))
	await _frames(20)
	await _shot("m3/05_crossing_pad_glow")
	await _walk_to(Vector3(13.0, 0, -19.5), 12.0, func() -> bool: return Game.is_unlocked("r4_crossing"))
	print("M3 crossing bought=%s money=%d" % [Game.is_unlocked("r4_crossing"), Game.money])
	await _wait_seconds(0.7)
	await _shot("m3/06_crossing_opened")
	# Stand on the crossing: the barrier arms come down and the truck waits.
	_teleport(Vector3(17.0, 0, -20.0))
	await _wait_seconds(1.0)
	print("M3 crossing arms_down=%.2f holds_truck=%s %s" % [world.coast._arms_down, world.crossing_holds(Vector3(17, 0, -14)), "PASS" if world.coast._arms_down > 0.9 and world.crossing_holds(Vector3(17, 0, -14)) else "FAIL"])
	await _shot("m3/06b_on_crossing_arms_down")
	var ok := await _walk_to(Vector3(27, 0, -20), 12.0)
	print("M3 crossed=%s pos=%s region=%d awake=%d r1=%s r4=%s" % [ok, world.player.global_position.snapped(Vector3.ONE * 0.1), world.current_region(), _awake_count(), world.r1.awake, world.r4.awake])
	await _frames(20)
	await _shot("m3/07_redwood_arrival")
	Game.add_money(_cost("r4_redmill") + 1000)
	await _walk_to(Vector3(32, 0, -20), 14.0, func() -> bool: return Game.is_unlocked("r4_redmill"))
	print("M3 redmill bought=%s" % Game.is_unlocked("r4_redmill"))
	await _frames(40)
	await _bot_follow(50.0, "m3", "red_log")
	var mill: Machine = world.machines.redmill
	print("M3 tutorial timber_shelf=%d mill_out=%d coins=%d money=%d %s" % [world.coast.shop4.shelf("timber").count(), mill.output.count(), world.coast.shop4.coin_value, Game.money,
		"PASS" if world.coast.shop4.shelf("timber").count() + mill.output.count() + world.coast.shop4.coin_value > 0 else "FAIL"])
	await _shot("m3/08_after_tutorial")
	# Handcar: Redwood Coast -> Home Valley -> Redwood Coast.
	await _handcar_ride(4, 1, "m3/09_handcar_home")
	await _handcar_ride(1, 4, "m3/10_handcar_back_coast")
	# Every pad, then let it run with the player parked at the handcar stop.
	await _unlock_region("r4_")
	var launches := [0]
	var orders_done := [0]
	for sid in ["r4_slipway", "r4_slipway2"]:
		(world.sites[sid] as BuildSite).launched.connect(func(_i: String, _h: Node3D) -> void: launches[0] += 1)
	world.coast.orders.filled.connect(func(_v: int) -> void: orders_done[0] += 1)
	_teleport(Balance.HANDCAR_STOPS[4].land)
	# 2x, not 4x: at 4x the rendered frame steps get coarse (one transfer per frame).
	Engine.time_scale = 2.0
	var t := 0.0
	var shot_launch := false
	while t < 600.0:
		await get_tree().process_frame
		t += get_process_delta_time() * Engine.time_scale
		if int(t / 30.0) != int((t - get_process_delta_time() * Engine.time_scale) / 30.0):
			var s1: BuildSite = world.sites.r4_slipway
			var s2: BuildSite = world.sites.r4_slipway2
			print("M3 run t=%.0f launches=%d orders=%d order=%s ship1=%s ship2=%s light=%s" % [t, launches[0], orders_done[0], Game.orders.get("lines"), s1.delivered, s2.delivered, world.sites.r4_lighthouse.delivered])
		if launches[0] >= 1 and not shot_launch:
			shot_launch = true
			Engine.time_scale = 1.0
			_teleport(Vector3(66, 0, -22))
			await _wait_seconds(1.6)
			await _shot("m3/11_ship_launch")
			_teleport(Balance.HANDCAR_STOPS[4].land)
			Engine.time_scale = 2.0
		if launches[0] >= 2 and orders_done[0] >= 1:
			break
	Engine.time_scale = 1.0
	print("M3 AUTOMATION launches=%d orders=%d game_s=%.0f %s" % [launches[0], orders_done[0], t, "PASS" if launches[0] >= 2 and orders_done[0] >= 1 else "FAIL"])
	await _shots({
		"m3/20_crossing_from_coast": Vector3(25, 0, -19), "m3/21_redwood_mill": Vector3(32, 0, -17),
		"m3/22_harbor_market": Vector3(64, 0, -2), "m3/23_pier_boats": Vector3(72, 0, 5),
		"m3/24_office_handcar_platform": Vector3(32, 0, 9), "m3/25_decksaw_belts": Vector3(33, 0, -29),
		"m3/26_mastlathe": Vector3(50, 0, -21), "m3/27_slipways": Vector3(64, 0, -29),
		"m3/28_order_board_ship": Vector3(68, 0, 9), "m3/29_lighthouse_site": Vector3(68, 0, -40),
		"m3/30_north_groves_cablecar_pad": Vector3(46, 0, -39), "m3/31_cliff_far_groves": Vector3(32, 0, -38),
		"m3/32_groves_forklift": Vector3(44, 0, -6),
	})
	_teleport(Vector3(28, 0, 8.0))
	await _frames(25)
	await _shot("m3/33_harbor_upgrades")
	# Finish the Lighthouse (goods pushed into its intakes): Valley complete card names the Cable Car.
	var lh: BuildSite = world.sites.r4_lighthouse
	_teleport(Vector3(68, 0, -40))
	await _frames(10)
	for item in lh.goods:
		for i in lh.room(item):
			lh.intake_of(item).push(Items.make(item), false)
	await _frames(40)
	var title := (Game.hud.valley_card.find_child("Title", true, false) as Label).text
	var body := (Game.hud.valley_card.find_child("Body", true, false) as Label).text
	print("M3 LIGHTHOUSE done=%s card='%s' body_names_cable=%s cable_pad=%s %s" % [lh.done, title, body.contains("Cable Car"), world.pads.has("r5_cablecar") or Game.is_unlocked("r5_cablecar"),
		"PASS" if lh.done and title.contains("Redwood Coast") and (world.pads.has("r5_cablecar") or Game.is_unlocked("r5_cablecar")) else "FAIL"])
	await _shot("m3/34_lighthouse_valley_card")
	Game.hud.valley_card.visible = false
	await _frames(40)
	await _shot("m3/35_lighthouse_built")
	# Sleep: Birch Bend far west; at most 2 valleys awake anywhere.
	var worst := 0
	for spot in [Vector3(-74, 0, -40), Vector3(0, 0, -50), Vector3(20, 0, -20), Vector3(50, 0, -40), Vector3(-6, 0, -60)]:
		_teleport(spot)
		await _frames(20)
		worst = maxi(worst, _awake_count())
	print("M3 SLEEP max_awake=%d %s ledger=%s" % [worst, "PASS" if worst <= 2 else "FAIL", Game.ledger])
	Game.save_game()


## CAPTURE_MODE=m4: from an M3-complete save (Lighthouse built) up the Cable Car, the Frost Peaks
## mini-tutorial (fill the kiln, it bakes), every pad (kilns, snowcat, mountain train), and the
## Observatory card naming the Grand Timber Station.
func _m4() -> void:
	var ids := _ids_upto(4)
	_write_save(ids, _cost("r5_cablecar") * 3 / 4, {"ledger": {"r1": 95.0, "r2": 280.0, "r3": 740.0, "r4": 1500.0}})
	await _frames(40)
	await _shot("m4/01_start_from_m3_save")
	print("M4 money=%d pads=%s" % [Game.money, world.pads.keys()])
	await _gateway_flow("m4", "r5_cablecar", "r4_lighthouse", 4)
	_teleport(Vector3(47, 0, -34.5))
	await _frames(20)
	await _shot("m4/05_cablecar_pad")
	await _walk_to((world.pads["r5_cablecar"] as Node3D).global_position, 12.0, func() -> bool: return Game.is_unlocked("r5_cablecar"))
	print("M4 cablecar bought=%s" % Game.is_unlocked("r5_cablecar"))
	await _wait_seconds(0.8)
	await _shot("m4/06_cablecar_built")
	# Onto the ride tile (the ride is under test here, not the walk).
	_teleport(FrostPeaks.CABLE_TILE_BOTTOM)
	var t := 0.0
	while t < 4.0 and world.player.global_position.distance_to(FrostPeaks.CABLE_LAND_TOP) > 0.5:
		await get_tree().process_frame
		t += get_process_delta_time()
	await _wait_seconds(0.5)
	var d := world.player.global_position.distance_to(FrostPeaks.CABLE_LAND_TOP)
	print("M4 CABLECAR up arrived=%.1fm region=%d awake=%d %s" % [d, world.current_region(), _awake_count(), "PASS" if d < 0.6 and world.current_region() == 5 else "FAIL"])
	await _shot("m4/07_frost_arrival")
	Game.add_money(_cost("r5_kiln") + 1000)
	await _walk_to(Vector3(40, 0, -66), 14.0, func() -> bool: return Game.is_unlocked("r5_kiln"))
	print("M4 kiln bought=%s" % Game.is_unlocked("r5_kiln"))
	await _frames(40)
	var kiln: Kiln = world.machines.kiln
	var baked := [false]
	await _bot_follow(45.0, "m4", "frost_log")
	var tk := 0.0
	while tk < 30.0 and kiln.output.count() == 0:
		if kiln.baking and not baked[0]:
			baked[0] = true
			await _shot("m4/08_kiln_baking_glow")
		await get_tree().process_frame
		tk += get_process_delta_time()
	print("M4 KILN baked=%s out=%d in=%d %s" % [baked[0], kiln.output.count(), kiln.input.count(), "PASS" if kiln.output.count() > 0 else "FAIL"])
	await _frames(20)
	await _shot("m4/09_kiln_batch_out")
	if not baked[0]:
		# The tutorial bake finished off screen: fill the kiln once more to film the glow.
		for i in maxi(int(Balance.KILN.batch) - kiln.input.count(), 0):
			kiln.input.push(Items.make("frost_log"), false)
		var tg := 0.0
		while tg < 12.0 and not kiln.baking:
			await get_tree().process_frame
			tg += get_process_delta_time()
		# In front of the kiln, clear of the handcar tiles.
		_teleport(Vector3(37.5, 0, -63.2))
		await _wait_seconds(5.0)
		print("M4 KILN glow baking=%s glow=%.2f" % [kiln.baking, kiln._glow.emission_energy_multiplier])
		await _shot("m4/08_kiln_baking_glow")
	await _unlock_region("r5_")
	_teleport(Balance.HANDCAR_STOPS[5].land)
	Engine.time_scale = 2.0
	t = 0.0
	var trips := 0
	var dock: TruckDock = world.machines.mtrain
	var last_state := dock.state
	while t < 300.0:
		await get_tree().process_frame
		t += get_process_delta_time() * Engine.time_scale
		if dock.state != last_state and dock.state == TruckDock.State.AWAY:
			trips += 1
		last_state = dock.state
		if int(t / 30.0) != int((t - get_process_delta_time() * Engine.time_scale) / 30.0):
			var ks := []
			for k in world.frost.kilns:
				ks.append("%s:%s/%d" % [k.name, "bake" if k.baking else "load", k.output.count()])
			print("M4 run t=%.0f kilns=%s skis_out=%d sled_out=%d guitar_out=%d lodge=%s train_trips=%d snowcat=%d:%s obs=%s" % [t, ks, world.machines.skiworks.output.count(),
				world.machines.sledshop.output.count(), world.machines.luthier.output.count(), [world.frost.lodge.shelf("dry_lumber").count(), world.frost.lodge.shelf("skis").count(), world.frost.lodge.shelf("sled").count()],
				trips, world.frost.snowcat.stack.count(), world.frost.snowcat.stack.top_type(), world.sites.r5_observatory.delivered])
	Engine.time_scale = 1.0
	print("M4 AUTOMATION train_trips=%d sled_shop_lumber_in=%d frost_earned=%d %s" % [trips, (world.machines.sledshop as Machine).input.count(), int(Game.stats(5).get("earned", 0)), "PASS" if trips >= 1 else "FAIL"])
	await _shots({
		"m4/20_cable_top_handcar_office": Vector3(41, 0, -59), "m4/21_kiln1_grove": Vector3(36, 0, -65),
		"m4/22_kilns_skiworks": Vector3(43, 0, -77), "m4/23_ski_lodge": Vector3(58, 0, -62),
		"m4/24_sledshop_snowcat": Vector3(53, 0, -86), "m4/25_luthier_kiln3": Vector3(47, 0, -96),
		"m4/26_express_platform": Vector3(66, 0, -79), "m4/27_observatory_site": Vector3(66, 0, -108),
		"m4/28_north_far_groves": Vector3(42, 0, -110), "m4/29_highland_line": Vector3(30, 0, -103),
	})
	# Mountain train at its platform.
	_teleport(Vector3(66, 0, -79))
	var tw := 0.0
	while tw < 30.0 and dock.state != TruckDock.State.LOADING:
		await get_tree().process_frame
		tw += get_process_delta_time()
	await _frames(10)
	print("M4 MTRAIN state=%s wagons=%d loaded=%d pile=%d" % [dock.state, dock.beds.size(), dock._loaded(), dock.pile.count()])
	await _shot("m4/30_mountain_train")
	_teleport(Vector3(35, 0, -57.5))
	await _frames(25)
	await _shot("m4/31_mountain_upgrades")
	var obs: BuildSite = world.sites.r5_observatory
	_teleport(Vector3(66, 0, -106))
	await _frames(10)
	for item in obs.goods:
		for i in obs.room(item):
			obs.intake_of(item).push(Items.make(item), false)
	await _frames(40)
	var title := (Game.hud.valley_card.find_child("Title", true, false) as Label).text
	var body := (Game.hud.valley_card.find_child("Body", true, false) as Label).text
	print("M4 OBSERVATORY done=%s card='%s' names_station=%s station_pad=%s %s" % [obs.done, title, body.contains("Grand Timber Station"), world.pads.has("cap_station"),
		"PASS" if obs.done and title.contains("Frost Peaks") and world.pads.has("cap_station") else "FAIL"])
	await _shot("m4/32_observatory_valley_card")
	Game.hud.valley_card.visible = false
	await _frames(40)
	await _shot("m4/33_observatory_built")
	await _handcar_ride(5, 3, "m4/34_handcar_to_highlands")
	await _handcar_ride(3, 5, "m4/35_handcar_back_frost")
	var worst := 0
	for spot in [Vector3(30, 0, -60), Vector3(47, 0, -50), Vector3(20, 0, -100), Vector3(70, 0, -110)]:
		_teleport(spot)
		await _frames(20)
		worst = maxi(worst, _awake_count())
	print("M4 SLEEP max_awake=%d %s ledger=%s" % [worst, "PASS" if worst <= 2 else "FAIL", Game.ledger])
	Game.save_game()


## CAPTURE_MODE=m5: from an M4-complete save (Observatory built): the Station pad, the station and
## the five platforms (porters carry goods), every platform filled, the Timber Express loop and
## the finish panel; then a reload that must not reopen it.
func _m5() -> void:
	var ids := _ids_upto(5)
	_write_save(ids, _cost("cap_station") * 3 / 4, {"ledger": {"r1": 95.0, "r2": 280.0, "r3": 740.0, "r4": 1500.0, "r5": 3000.0}})
	await _frames(40)
	await _shot("m5/01_start_from_m4_save")
	print("M5 money=%d pads=%s" % [Game.money, world.pads.keys()])
	await _gateway_flow("m5", "cap_station", "r5_observatory", 5)
	_teleport(Vector3(5.5, 0, -37))
	await _frames(20)
	await _shot("m5/05_station_pad")
	await _walk_to(Vector3(5.5, 0, -42.6), 12.0, func() -> bool: return Game.is_unlocked("cap_station"))
	print("M5 station bought=%s" % Game.is_unlocked("cap_station"))
	await _wait_seconds(1.5)
	await _shot("m5/06_station_site_rail")
	# Within 5 s of the purchase the player must see what to do next (Mats 2026-10-04).
	await _wait_seconds(0.8)
	await _shot("m5/06b_station_pan_to_platform")
	await _wait_seconds(2.2)
	var g5 := world._goal()
	print("M5 STATION GUIDE 5s hint='%s' arrow=%s guide_visible=%s %s" % [g5[1], g5[0], world.guide.visible,
		"PASS" if str(g5[1]).contains("Station 0/5") and world.guide.visible else "FAIL"])
	await _shot("m5/06c_station_guide_5s")
	# Platforms by each handcar stop; let the porters work for a while.
	Engine.time_scale = 4.0
	await _frames(600)
	Engine.time_scale = 1.0
	var plat := []
	for pid in GrandStation.PLATFORMS:
		plat.append("%s=%s" % [pid, world.sites[pid].delivered])
	print("M5 porters after 40 s: %s" % " ".join(plat))
	await _shots({
		"m5/07_platform_home": Vector3(-17, 0, 10), "m5/08_platform_birch": Vector3(-34, 0, 1),
		"m5/09_platform_highlands": Vector3(-15, 0, -56), "m5/10_platform_coast": Vector3(28, 0, 12),
		"m5/11_platform_frost": Vector3(30, 0, -57),
	})
	# Fill every platform (goods pushed into the intakes), the station rises, the Express runs.
	_teleport(Vector3(6, 0, -44))
	await _frames(10)
	for pid in GrandStation.PLATFORMS:
		var s: BuildSite = world.sites[pid]
		var reg: Region = world.regions[int(Balance.BUILD_SITES[pid].region)]
		_teleport(s.global_position + Vector3(0, 0, 5))
		await _frames(10)
		for item in s.goods:
			for i in s.room(item):
				s.intake_of(item).push(Items.make(item), false)
		await _frames(10)
		print("M5 platform %s done=%s awake=%s" % [pid, s.done, reg.awake])
	var tt := 0.0
	while tt < 5.0 and not world.station.cutscene:
		await get_tree().process_frame
		tt += get_process_delta_time()
	print("M5 EXPRESS started=%s" % world.station.cutscene)
	# Shots between the station passes (the train crosses x 0 at about 6 s).
	for k in 3:
		await _wait_seconds([2.0, 2.5, 4.0][k])
		await _shot("m5/%02d_express_%d" % [12 + k, k])
	tt = 0.0
	while tt < 10.0 and not Game.hud.finish_panel.visible:
		await get_tree().process_frame
		tt += get_process_delta_time()
	await _frames(10)
	print("M5 FINISH panel=%s complete=%s %s" % [Game.hud.finish_panel.visible, Game.complete, "PASS" if Game.hud.finish_panel.visible and Game.complete else "FAIL"])
	await _shot("m5/15_finish_panel")
	Game.hud.finish_panel.visible = false
	_teleport(Vector3(6, 0, -40))
	await _frames(40)
	await _shot("m5/16_grand_station_built")
	Game.save_game()
	# Reload: the finish panel must not reopen; orders and ships keep running.
	main.queue_free()
	await _frames(5)
	Game.load_game()
	main = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	world = main.get_node("World")
	await _frames(60)
	print("M5 RELOAD finish_panel=%s complete=%s orders=%s %s" % [Game.hud.finish_panel.visible, Game.complete, Game.orders.get("n"), "PASS" if not Game.hud.finish_panel.visible and Game.complete else "FAIL"])
	await _shot("m5/17_after_reload")


# ---------------------------------------------------------------- safety: stuck, drop, discard, pickup

## CAPTURE_MODE=safety (Mats 2026-10-03): the Mega Saw is bought with the player standing on its
## pad and the player must walk away; a player dropped inside its collision gets unstuck; the DROP
## button and the discard bin empty the stack; walking past a PICK square takes nothing; a
## player carrying planks does not chop a tree.
func _safety() -> void:
	var ids := []
	for u in World.UNLOCKS:
		if _is_v1(u.id) and u.id not in ["megasaw", "belt_mega", "lodge"]:
			ids.append(u.id)
	_write_save(ids, _cost("megasaw") + 100)
	await _frames(40)
	var pad: Vector3 = (world.pads["megasaw"] as Node3D).global_position
	_teleport(pad)
	var t := 0.0
	while t < 6.0 and not Game.is_unlocked("megasaw"):
		await get_tree().process_frame
		t += get_process_delta_time()
	await _wait_seconds(1.6)
	await _shot("safety/01_megasaw_built_on_player")
	var p0 := world.player.global_position
	var inside := world._overlaps(p0)
	await _walk_to(p0 + Vector3(-4.0, 0, 6.0), 4.0)
	var moved := world.player.global_position.distance_to(p0)
	print("SAFETY megasaw bought=%s overlap_after_build=%s moved_away=%.1fm %s" % [Game.is_unlocked("megasaw"), inside, moved, "PASS" if not inside and moved > 3.0 else "FAIL"])
	await _shot("safety/02_walked_away_from_megasaw")
	# Unstuck: put the player in the middle of the Mega Saw's collision and push for 2.5 s.
	world.player.global_position = Vector3(9.6, 0, -13.2)
	world._cam_pos = world.player.global_position
	world.player.input_vector = Vector2(0, -1)
	await _wait_seconds(2.6)
	world.player.input_vector = Vector2.ZERO
	var free := not world._overlaps(world.player.global_position)
	print("SAFETY unstuck pos=%s free=%s %s" % [world.player.global_position.snapped(Vector3.ONE * 0.1), free, "PASS" if free else "FAIL"])
	await _shot("safety/03_unstuck")
	# DROP button: visible while carrying, empties the stack.
	_teleport(Vector3(2, 0, 2))
	for i in 6:
		world.player.stack.push(Items.make("log"), false)
	await _frames(10)
	var shown: bool = Game.hud.drop_btn.visible
	await _shot("safety/04_drop_button_carrying")
	Game.hud.drop_btn.pressed.emit()
	await _wait_seconds(0.3)
	await _shot("safety/05_dropped_tumbling")
	await _frames(10)
	print("SAFETY drop button shown=%s empty_after=%s hidden_after=%s %s" % [shown, world.player.stack.is_empty(), not Game.hud.drop_btn.visible, "PASS" if shown and world.player.stack.is_empty() and not Game.hud.drop_btn.visible else "FAIL"])
	# Discard bin: walking past keeps the stack, standing on it empties it.
	var bin: Vector3 = Balance.DISCARD_BINS[1]
	_teleport(bin + Vector3(-3, 0, 0))
	for i in 5:
		world.player.stack.push(Items.make("plank"), false)
	await _frames(5)
	await _walk_to(bin + Vector3(3, 0, 0), 3.0)
	var kept := world.player.stack.count()
	await _walk_to(bin, 3.0)
	await _wait_seconds(1.0)
	await _shot("safety/06_discard_bin")
	print("SAFETY discard bin passing_kept=%d standing_empty=%s %s" % [kept, world.player.stack.is_empty(), "PASS" if kept == 5 and world.player.stack.is_empty() else "FAIL"])
	# Pickup: walking straight over the sawmill's PICK square takes nothing; standing takes planks.
	var saw: Machine = world.machines.sawmill1
	for i in 8:
		saw.output.push(Items.make("plank"), false)
	var oz := saw.out_zone.global_position
	_teleport(oz + Vector3(0, 0, 3.0))
	await _frames(5)
	await _walk_to(oz + Vector3(0, 0, -3.0), 3.0)
	var passed := world.player.stack.count()
	await _walk_to(oz, 3.0)
	await _wait_seconds(1.0)
	var stood := world.player.stack.count()
	print("SAFETY pickup passing_took=%d standing_took=%d %s" % [passed, stood, "PASS" if passed == 0 and stood > 0 else "FAIL"])
	# Carrying planks: standing at a tree chops nothing.
	var tree: ChopTree = world._nearest_tree(world.player.global_position)
	_teleport(tree.global_position + Vector3(0.9, 0, 0))
	await _wait_seconds(1.5)
	var only_planks := world.player.stack.top_type() == "plank" and world.player.stack.count() == stood
	print("SAFETY no chop while carrying planks count=%d top=%s %s" % [world.player.stack.count(), world.player.stack.top_type(), "PASS" if only_planks else "FAIL"])


## CAPTURE_MODE=census: draw-call sources at the heaviest views (CAPTURE_CENSUS lists geometry).
func _census_mode() -> void:
	var upto := int(OS.get_environment("CENSUS_UPTO")) if OS.get_environment("CENSUS_UPTO") != "" else 3
	var ids := _ids_upto(upto)
	_write_save(ids, 100, {"complete": upto >= 6})
	await _frames(60)
	Game.hud.valley_card.visible = false
	Engine.time_scale = 4.0
	await _frames(300)
	Engine.time_scale = 1.0
	var spots := {"census/home_stop": Vector3(-8, 0, 10), "census/gate": Vector3(0, 0, -53), "census/shop": Vector3(9, 0, 2),
		"census/upgrades": Vector3(-3.5, 0, 10.0), "census/station": Vector3(6, 0, -40), "census/v3_market": Vector3(11, 0, -64)}
	for k in spots:
		_teleport(spots[k])
		await _frames(30)
		await _shot(k)
