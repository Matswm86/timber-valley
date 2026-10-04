extends Node

## Dev-only pacing probe (headless). Loads a save that owns a given set of pads, then either runs a
## valley with no player input (automation), or plays a valley opening with a scripted player, or
## loads the Grand Timber Station platforms valley by valley. Logs piles, worker states, shoppers
## and income. Env:
##   PROBE_MODE    "auto" (no player), "play" (scripted player), "station" (platforms);
##                 legacy: "v2" = auto in Birch Bend, "v4" = play Redwood Coast up to r4_cashier
##   PROBE_REGION  valley 2-5 (auto, play)
##   PROBE_CP      auto: last owned pad of that valley (UNLOCKS prefix); v2 also takes
##                 hauler1 | jack2 | hauler2 | jack3
##   PROBE_START_CP play: start owning the valley's pads up to this one
##   PROBE_UNTIL   play: stop once this pad is bought (default: the valley landmark, and its
##                 building finished)
##   PROBE_SECONDS game seconds (auto default 360, play default 4200 cap)
##   PROBE_FROM    auto: start of the steady-state window for the summary (default 120 s)
##   PROBE_LEDGER  play: carried-in income "low" (no region upgrades bought earlier), default 3/3/3
##   PROBE_RUP     auto: region upgrades of the probed valley "saws,crew,fame" (default none)
##   PROBE_LV      auto: global upgrades "cap" (backpack 4, rest 3; default) or "max"
## Run: godot --headless --fixed-fps 60 --audio-driver Dummy --path . res://tests/pacing_probe.tscn

const V2_CP := {"hauler1": "r2_hauler1", "jack2": "r2_jack2", "hauler2": "r2_hauler2", "jack3": "r2_jack3"}
## Carried-in income when a valley opens: measured ledgers (rebalance_2026-10-01.md section 1 for
## V1-V3, m345_2026-10-03.md for V4). Model = region upgrades 3/3/3, low = none.
const LEDGER := {"r1": 95.1, "r2": 214.5, "r3": 741.6, "r4": 1500.3}
const LEDGER_LOW := {"r1": 95.1, "r2": 139.4, "r3": 457.6, "r4": 707.5}
const MAX_UPS := {"capacity": 6, "speed": 5, "axe": 5, "machines": 5, "workers": 5, "prices": 5}

var world: World
var mode: String = OS.get_environment("PROBE_MODE")
var region: int = int(OS.get_environment("PROBE_REGION"))
var t: float = 0.0
## pile name -> {"stack", "full_t" (current stretch), "max_full", "win_sum", "in", "out", "last"}
var piles: Dictionary = {}
## worker instance id -> {"name", "states": {state: seconds}, "win": {...}, "now"}
var workers: Dictionary = {}
var _win_from: float = 120.0


static func region_of(id: String) -> int:
	if id.begins_with("cap_"):
		return 6
	if id.length() > 3 and id[0] == "r" and id[1].is_valid_int() and id[2] == "_":
		return int(id[1])
	return 1


## Cheapest-first order of a valley's pads, each bought once its requirements are owned.
static func purchase_order(rid: int, owned_before: Array) -> Array:
	var owned := {}
	for id in owned_before:
		owned[id] = true
	var out: Array = []
	while true:
		var best: Dictionary = {}
		for u in World.UNLOCKS:
			if region_of(u.id) != rid or owned.has(u.id):
				continue
			var ok := true
			for r in u.req:
				if not owned.has(r):
					ok = false
			if ok and (best.is_empty() or int(u.cost) < int(best.cost)):
				best = u
		if best.is_empty():
			break
		owned[best.id] = true
		out.append(best.id)
	return out


func _ready() -> void:
	if mode == "v2":
		mode = "auto"
		region = 2
	elif mode == "v4":
		mode = "play"
		region = 4
	var ups := {"capacity": 4, "speed": 3, "axe": 3, "machines": 3, "workers": 3, "prices": 3}
	if OS.get_environment("PROBE_LV") == "max" or mode != "auto":
		ups = MAX_UPS.duplicate()
	var low := OS.get_environment("PROBE_LEDGER") == "low"
	var ids: Array = []
	var rup := {}
	var ledger := {}
	if mode == "station":
		region = 6
		for u in World.UNLOCKS:
			ids.append(u.id)
	elif mode == "play":
		for u in World.UNLOCKS:
			if region_of(u.id) < region:
				ids.append(u.id)
		ids.append(Balance.VALLEY_GATE[region])
		# PROBE_START_CP: start later in the valley, owning its pads up to this one (purchase order).
		var start_cp := OS.get_environment("PROBE_START_CP")
		if start_cp != "":
			for id in purchase_order(region, ids.duplicate()):
				ids.append(id)
				if id == start_cp:
					break
		for r in range(1, region):
			ledger["r%d" % r] = (LEDGER_LOW if low else LEDGER)["r%d" % r]
			if r > 1 and not low:
				rup[str(r)] = {"saws": 3, "crew": 3, "fame": 3}
	else:
		var cp: String = OS.get_environment("PROBE_CP")
		cp = V2_CP.get(cp, cp)
		for u in World.UNLOCKS:
			if region_of(u.id) < region:
				ids.append(u.id)
		# Valley 2 keeps the UNLOCKS order (the 2026-10-04 Birch Bend tables); later valleys own
		# the pads a cheapest-first player has bought by the time it buys PROBE_CP.
		var order: Array = []
		if region == 2:
			for u in World.UNLOCKS:
				if region_of(u.id) == 2:
					order.append(u.id)
		else:
			order = purchase_order(region, ids)
		for id in order:
			ids.append(id)
			if id == cp:
				break
		if OS.get_environment("PROBE_RUP") != "":
			var rp := OS.get_environment("PROBE_RUP").split(",")
			rup = {str(region): {"saws": int(rp[0]), "crew": int(rp[1]), "fame": int(rp[2])}}
	# Earlier valleys are finished: their houses and landmarks stand. Repeatable slipways and the
	# probed valley's own sites start empty; station platforms start empty.
	var sites := {}
	for sid in Balance.BUILD_SITES:
		var info: Dictionary = Balance.BUILD_SITES[sid]
		if sid in ids and int(info.get("region", 3)) < region and not info.get("repeat", false) and not info.get("platform", false):
			sites[sid] = (info.goods as Dictionary).duplicate()
	Game.apply_save({"version": 4, "money": 0, "total_earned": 0, "unlocked": ids, "upgrades": ups,
		"region_upgrades": rup, "ledger": ledger, "region_stats": {}, "sites": sites, "piles": {},
		"finished": true, "sound_on": false})
	Game.sound_on = false
	Game.complete = false
	Game.orders.clear()
	var main: Node = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	world = main.get_node("World")
	await _frames(5)
	Engine.time_scale = 2.0
	if mode == "play":
		await _run_play()
	elif mode == "station":
		await _run_station()
	else:
		await _run_auto()
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _env_f(key: String, dflt: float) -> float:
	return float(OS.get_environment(key)) if OS.get_environment(key) != "" else dflt


# ---------------------------------------------------------------- automation only

func _run_auto() -> void:
	var secs := _env_f("PROBE_SECONDS", 360.0)
	_win_from = _env_f("PROBE_FROM", 120.0)
	var reg: Region = world.regions[region]
	world.player.global_position = Balance.HANDCAR_STOPS[region].land
	world._cam_pos = world.player.global_position
	_collect_piles(reg)
	var e_win := -1.0
	var next_log := 10.0
	var last_e := _earned(region)
	if OS.get_environment("PROBE_PRINT_ORDER") != "":
		var before: Array = []
		for u in World.UNLOCKS:
			if region_of(u.id) < region:
				before.append(u.id)
		print("ORDER %d %s" % [region, " ".join(purchase_order(region, before))])
	print("PROBE auto region=%d cp=%s lv=%s rup=%s piles=%s" % [region, OS.get_environment("PROBE_CP"),
		OS.get_environment("PROBE_LV"), OS.get_environment("PROBE_RUP"), piles.keys()])
	while t < secs:
		await get_tree().process_frame
		var dt := get_process_delta_time()
		t += dt
		if t >= _win_from and e_win < 0.0:
			e_win = _earned(region)
		_sample_piles(dt)
		_sample_workers(reg, dt)
		if t >= next_log:
			next_log += 10.0
			var e := _earned(region)
			print("t=%3.0f $/min=%6.0f shoppers=%2d | %s | %s %s" % [t, (e - last_e) * 6.0, _shoppers(reg), _pile_line(), _worker_line(), _site_line()])
			last_e = e
	_summary((_earned(region) - e_win) / maxf(t - _win_from, 1.0) * 60.0)
	var dir := OS.get_environment("CAPTURE_DIR")
	if dir != "" and OS.get_environment("PROBE_SHOT_AT") != "":
		# PROBE_SHOT_AT="name:x:z;name:x:z": the player stands there, game camera.
		Engine.time_scale = 1.0
		for spec in OS.get_environment("PROBE_SHOT_AT").split(";"):
			var f := spec.split(":")
			world.player.global_position = Vector3(float(f[1]), 0, float(f[2]))
			await _wait(float(f[3]) if f.size() > 3 else 2.0)
			await _save("%s/%s.jpg" % [dir, f[0]])
	elif region == 2 and dir != "":
		await _v2_shots(dir)


## Money booked to the valley plus coins waiting at its tills.
func _earned(rid: int) -> float:
	var e := float(Game.stats(rid).get("earned", 0))
	for s in (world.regions[rid] as Region).find_children("*", "Shop", true, false):
		e += float((s as Shop).coin_value)
	return e


## Build sites and the cargo order of the probed valley: goods delivered / needed.
func _site_line() -> String:
	var out: Array = []
	for sid in world.sites:
		var info: Dictionary = Balance.BUILD_SITES[sid]
		if int(info.get("region", 3)) != region and not (region == 6 and info.get("platform", false)):
			continue
		var have: Dictionary = Game.sites.get(sid, {})
		var parts: Array = []
		for item in info.goods:
			parts.append("%s %d/%d" % [item, int(have.get(item, 0)), int(info.goods[item])])
		out.append("%s[%s]" % [sid, ", ".join(parts)])
	if region == 4 and Game.orders.has("lines"):
		var parts2: Array = []
		for item in Game.orders.lines:
			parts2.append("%s %d/%d" % [item, int(Game.orders.lines[item][1]), int(Game.orders.lines[item][0])])
		out.append("order%d[%s]" % [int(Game.orders.get("n", 0)), ", ".join(parts2)])
	return ("| " + " ".join(out)) if not out.is_empty() else ""


func _v2_shots(dir: String) -> void:
	Engine.time_scale = 1.0
	var lathe: Machine = world.machines.lathe
	var p := world.player
	p.global_position = Vector3(-47.5, 0, -13.5)
	await _wait(1.5)
	await _save(dir + "/v2_belt_game_camera.jpg")
	world.set_process(false)
	world.camera.global_position = Vector3(-46.0, 4.2, -6.5)
	world.camera.look_at(Vector3(-46.5, 0.6, -11.5), Vector3.UP)
	await _wait(0.4)
	await _save(dir + "/v2_belt_closeup.jpg")
	world.set_process(true)
	p.global_position = lathe.out_zone.global_position
	await _wait(3.0)
	print("SHOTS player carries %d %s (capacity %d)" % [p.stack.count(), p.stack.top_type(), p.capacity()])
	await _save(dir + "/v2_player_veneer.jpg")
	world.set_process(false)
	world.camera.global_position = p.global_position + Vector3(4.5, 2.2, 0.5)
	world.camera.look_at(p.global_position + Vector3(0, 1.4, 0), Vector3.UP)
	await _wait(0.3)
	await _save(dir + "/v2_player_veneer_side.jpg")
	world.set_process(true)
	p.global_position = Vector3(-36.0, 0, 4.0)
	await _wait(2.0)
	await _save(dir + "/v2_market.jpg")


func _wait(sec: float) -> void:
	var w := 0.0
	while w < sec:
		await get_tree().process_frame
		w += get_process_delta_time()


func _save(path: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_jpg(path, 0.85)
	print("SHOT " + path)


func _collect_piles(root: Node) -> void:
	for s in root.find_children("*", "ItemStack", true, false):
		var st := s as ItemStack
		if st.persist_id == "" or piles.has(st.persist_id):
			continue
		var m := st.get_parent() as Machine
		# A machine output is "full" once the next cycle no longer fits.
		var slack := (m.out_per_cycle - 1) if m != null and m.output == st else 0
		piles[st.persist_id] = {"stack": st, "slack": slack, "full_t": 0.0, "max_full": 0.0, "in": 0, "out": 0, "last": st.count(), "win_sum": 0.0}
		# Every push and pop emits `changed`, so flows are counted even when both land in one frame.
		st.changed.connect(_on_pile_changed.bind(st.persist_id))


func _sample_piles(dt: float) -> void:
	for k in piles:
		var p: Dictionary = piles[k]
		var st: ItemStack = p.stack
		if not is_instance_valid(st):
			continue
		# A baking kiln closes its input (capacity 0): that counts as full.
		if st.count() >= st.capacity - int(p.slack):
			p.full_t += dt
			if t >= _win_from:
				p.win_sum += dt
			p.max_full = maxf(p.max_full, p.full_t)
		else:
			p.full_t = 0.0


func _on_pile_changed(c: int, k: String) -> void:
	if not piles.has(k):
		return
	var p: Dictionary = piles[k]
	if c > int(p.last):
		p.in += c - int(p.last)
	else:
		p.out += int(p.last) - c
	p.last = c


func _pile_line() -> String:
	var out: Array = []
	for k in piles:
		var st: ItemStack = piles[k].stack
		if is_instance_valid(st):
			out.append("%s=%d/%d" % [_short(k), st.count(), st.capacity])
	return " ".join(out)


func _short(k: String) -> String:
	return k.replace("shelf:", "shelf_").replace(":", "_")


## Worker state each frame: carry/walk/load/chop = working; blocked = standing at a full drop
## holding a load; no_tree = lumberjack with nothing grown; starved = hauler at an empty source
## (or a routed hauler with every source empty); no_route = routed hauler whose piles hold goods
## that have nowhere to go.
func _worker_state(w: Worker) -> String:
	var near_dest := w._delivering and Vector2(w.global_position.x - w.dest_pos.x, w.global_position.z - w.dest_pos.z).length() < 0.4
	if w._delivering:
		if near_dest and not w.stack.is_empty() and w.dest != null and not w.dest.can_accept(w.stack.top_type()):
			return "blocked"
		return "carry"
	if w.job == Worker.Job.LUMBERJACK:
		if w._target_tree == null:
			return "no_tree"
		return "chop"
	if w.source == null:
		if w.routed:
			for sp in w.sources:
				if not (sp[0] as ItemStack).is_empty():
					return "no_route"
		return "starved"
	var near_src := Vector2(w.global_position.x - w.source_pos.x, w.global_position.z - w.source_pos.z).length() < 0.4
	if near_src and w.source.is_empty():
		return "starved"
	return "load" if near_src else "walk"


func _worker_kind(w: Worker) -> String:
	if w.job == Worker.Job.LUMBERJACK:
		return "skid" if w.vehicle != "" else "jack"
	if w.forklift:
		return "fork"
	if w.vehicle != "":
		return w.vehicle
	return "rout" if w.routed else "haul"


func _sample_workers(root: Node, dt: float) -> void:
	for c in root.get_children():
		if not c is Worker:
			continue
		var w := c as Worker
		var id := w.get_instance_id()
		if not workers.has(id):
			workers[id] = {"name": _worker_kind(w) + str(workers.size()), "states": {}, "win": {}, "now": ""}
		var s := _worker_state(w)
		var rec: Dictionary = workers[id]
		rec.now = s
		rec.states[s] = float(rec.states.get(s, 0.0)) + dt
		if t >= _win_from:
			rec.win[s] = float(rec.win.get(s, 0.0)) + dt


func _worker_line() -> String:
	var out: Array = []
	for id in workers:
		var rec: Dictionary = workers[id]
		var w := instance_from_id(id) as Worker
		if w:
			out.append("%s:%s(%d)" % [rec.name, rec.now, w.stack.count()])
	return " ".join(out)


func _shoppers(root: Node) -> int:
	return root.find_children("*", "Customer", true, false).size()


func _summary(per_min: float) -> void:
	var win := maxf(t - _win_from, 1.0)
	print("SUMMARY region=%d cp=%s window=%.0f-%.0fs $/min=%.0f" % [region, OS.get_environment("PROBE_CP"), _win_from, t, per_min])
	for k in piles:
		var p: Dictionary = piles[k]
		var st: ItemStack = p.stack
		if not is_instance_valid(st):
			continue
		print("  pile %-16s max_full=%5.1fs full%%(window)=%5.1f in=%d out=%d end=%d/%d" % [_short(k), p.max_full, 100.0 * p.win_sum / win, p.in, p.out, st.count(), st.capacity])
	var idle_all := 0.0
	var tot_all := 0.0
	for id in workers:
		var rec: Dictionary = workers[id]
		var tot := 0.0
		for s in rec.win:
			tot += float(rec.win[s])
		var idle := 0.0
		for s in ["blocked", "no_tree", "starved", "no_route"]:
			idle += float(rec.win.get(s, 0.0))
		idle_all += idle
		tot_all += tot
		var parts: Array = []
		for s in rec.win:
			parts.append("%s %.0f%%" % [s, 100.0 * float(rec.win[s]) / maxf(tot, 0.01)])
		print("  worker %-8s idle=%5.1f%%  %s" % [rec.name, 100.0 * idle / maxf(tot, 0.01), ", ".join(parts)])
	print("  ALL WORKERS idle=%.1f%%" % (100.0 * idle_all / maxf(tot_all, 0.01)))
	print("  SITES " + _site_line())


# ---------------------------------------------------------------- scripted player

## Plays a valley from its gateway: buys the cheapest visible pad of the valley as soon as it can
## pay, otherwise follows the valley guide (chop, feed the first machine, stock the counter,
## collect cash). Region upgrades are not bought. Ends when PROBE_UNTIL is bought, or when the
## landmark pad is bought and its building stands.
func _run_play() -> void:
	var cap_s := _env_f("PROBE_SECONDS", 4200.0)
	var until: String = OS.get_environment("PROBE_UNTIL")
	if OS.get_environment("PROBE_MODE") == "v4" and until == "":
		until = "r4_cashier"
	var landmark := ""
	for lid in Balance.LANDMARKS:
		if int(Balance.LANDMARKS[lid]) == region:
			landmark = lid
	var p := world.player
	p.global_position = Balance.HANDCAR_STOPS[region].land
	if OS.get_environment("PROBE_START_MONEY") != "":
		Game.money = int(OS.get_environment("PROBE_START_MONEY"))
	if OS.get_environment("PROBE_START_POS") != "":
		var sp := OS.get_environment("PROBE_START_POS").split(",")
		p.global_position = Vector3(float(sp[0]), 0, float(sp[1]))
	world._cam_pos = p.global_position
	var reg: Region = world.regions[region]
	var states := {"work": 0.0, "buy": 0.0, "wait": 0.0}
	var step := {"work": 0.0, "buy": 0.0, "wait": 0.0}
	var gaps: Array = []
	var last_buy_t := 0.0
	var hand0 := 0.0
	var all0 := float(Game.total_earned)
	var next_log := 30.0
	var stuck := 0.0
	var detour := 0.0
	var best_d := INF
	var no_prog := 0.0
	var side := 1.0
	var last_target = null
	var owned := {}
	for id in Game.unlocked_ids:
		owned[id] = true
	var lm_bought_t := -1.0
	_collect_piles(reg)
	print("PROBE play region=%d start money=%d ledger=%s rent=%.1f" % [region, Game.money, Game.ledger, Game.rent_rate()])
	while t < cap_s:
		if until != "" and Game.is_unlocked(until):
			break
		if landmark != "" and Game.is_unlocked(landmark) and Game.site_done(landmark) and until == "":
			break
		# A handcar tile can carry the bot to another valley: a player would ride back.
		if not (world.regions[region] as Region).contains_point(p.global_position):
			p.global_position = Balance.HANDCAR_STOPS[region].land
			world._cam_pos = p.global_position
		# Cheapest visible unpaid pad of this valley.
		var pad: UnlockPad = null
		for id in world.pads:
			if region_of(id) != region or Game.is_unlocked(id) or not is_instance_valid(world.pads[id]):
				continue
			var cand: UnlockPad = world.pads[id]
			if pad == null or cand.cost - cand.paid_amount < pad.cost - pad.paid_amount:
				pad = cand
		var target = null
		var what := "wait"
		if pad and Game.money >= pad.cost - pad.paid_amount:
			target = pad.global_position
			what = "buy"
		else:
			var g: Array = _hand_goal(p.global_position) if _first_machine_owned() else _goal(p.global_position)
			if g[0] != null:
				target = g[0]
				# Before the first machine the guide only points at its pad: standing there is waiting.
				what = "work" if _first_machine_owned() else "wait"
		if target != null:
			var d: Vector3 = (target as Vector3) - p.global_position
			d.y = 0
			var v := Vector2(d.x, d.z).normalized() if d.length() > 0.5 else Vector2.ZERO
			if v != Vector2.ZERO and Vector2(p.velocity.x, p.velocity.z).length() < 0.8:
				stuck += get_process_delta_time()
			else:
				stuck = 0.0
			if stuck > 0.25:
				detour = 0.7
				stuck = 0.0
			# No progress toward the target for 4 s: go around the other side, for longer.
			var dist := d.length()
			if dist < best_d - 0.5:
				best_d = dist
				no_prog = 0.0
			else:
				no_prog += get_process_delta_time()
			if no_prog > 4.0:
				no_prog = 0.0
				best_d = dist
				side = -side
				detour = 2.0
			if detour > 0.0:
				detour -= get_process_delta_time()
				v = v.rotated(1.3 * side)
			p.input_vector = v
			if target != last_target:
				last_target = target
				best_d = INF
		else:
			p.input_vector = Vector2.ZERO
		await get_tree().process_frame
		var dt := get_process_delta_time()
		t += dt
		states[what] += dt
		step[what] += dt
		_sample_piles(dt)
		_sample_workers(reg, dt)
		for id in Game.unlocked_ids:
			if owned.has(id):
				continue
			owned[id] = true
			var hand := _earned(region)
			var cost := 0
			for u in World.UNLOCKS:
				if u.id == id:
					cost = int(u.cost)
			gaps.append(t - last_buy_t)
			print("BUY t=%7.1f %-14s cost=%7d gap=%6.1fs  work=%5.1fs buy=%4.1fs wait=%5.1fs (%.0f%% waiting)  valley_$=%8.0f all_$=%8.0f" % [
				t, id, cost, t - last_buy_t, step.work, step.buy, step.wait, 100.0 * step.wait / maxf(t - last_buy_t, 0.01), hand - hand0, float(Game.total_earned) - all0])
			last_buy_t = t
			hand0 = hand
			all0 = float(Game.total_earned)
			step = {"work": 0.0, "buy": 0.0, "wait": 0.0}
			if id == landmark:
				lm_bought_t = t
		if OS.get_environment("PROBE_TRACE") != "" and int(t * 2.0) != int((t - dt) * 2.0):
			print("TRACE t=%.1f pos=%s vel=%s input=%s what=%s target=%s" % [t, p.global_position.snapped(Vector3.ONE * 0.01), p.velocity.snapped(Vector3.ONE * 0.01), p.input_vector, what, target])
		if t >= next_log:
			next_log += 30.0
			print("t=%5.0f money=%8d doing=%s pos=%s back=%d:%s valley_$=%.0f | %s | %s %s" % [t, Game.money, what, p.global_position.snapped(Vector3.ONE * 0.1), p.stack.count(), p.stack.top_type(), _earned(region), _pile_line(), _worker_line(), _site_line()])
	p.input_vector = Vector2.ZERO
	var tot: float = states.work + states.buy + states.wait
	var sorted := gaps.duplicate()
	sorted.sort()
	var med: float = sorted[sorted.size() / 2] if not sorted.is_empty() else 0.0
	var mx: float = sorted[-1] if not sorted.is_empty() else 0.0
	var first10 := 0
	var acc := 0.0
	for g in gaps:
		acc += float(g)
		if acc <= 600.0:
			first10 += 1
	print("SUMMARY play region=%d t=%.0fs pads=%d median_gap=%.0fs max_gap=%.0fs pads_in_first_10min=%d work=%.0f%% buy=%.0f%% wait=%.0f%% valley_$=%.0f landmark_bought=%.0fs landmark_done=%s" % [
		region, t, gaps.size(), med, mx, first10, 100.0 * states.work / tot, 100.0 * states.buy / tot, 100.0 * states.wait / tot, _earned(region), lm_bought_t, str(landmark != "" and Game.site_done(landmark))])
	_win_from = 0.0
	_summary(0.0)


func _goal(pos: Vector3) -> Array:
	match region:
		3:
			return world._goal_v3(pos)
		4:
			return world.coast.goal(pos)
		5:
			return world.frost.goal(pos)
	return [null, ""]


## The first machine of each valley, its counter product, log and grove (the player's hand loop).
const HAND := {
	3: {"m": "beamsaw", "prod": "beam", "log": "maple_log", "trees": "maple"},
	4: {"m": "redmill", "prod": "timber", "log": "red_log", "trees": "redwood"},
	5: {"m": "kiln", "prod": "dry_lumber", "log": "frost_log", "trees": "frost"},
}


func _hand_shop() -> Shop:
	match region:
		3:
			return world.shop3
		4:
			return world.coast.shop4
		5:
			return world.frost.lodge
	return null


## A sensible player after the first machine: carries its goods to the counter, collects cash
## while there is no cashier, and only chops while the machine has room (logs it cannot deliver
## are dropped). [null, ""] = nothing useful to do (waiting).
func _hand_goal(pos: Vector3) -> Array:
	var h: Dictionary = HAND[region]
	var m = world.machines.get(h.m)
	var back := world.player.stack
	var shop := _hand_shop()
	var shelf_ok := shop != null and shop.is_open(h.prod) and not shop.shelf(h.prod).is_full()
	var inp: ItemStack = m.input
	var room := inp.capacity - inp.count()
	if back.top_type() == h.prod:
		return [shop.shelf_zone(h.prod).global_position, ""] if shelf_ok else [null, ""]
	if back.top_type() == h.log:
		if room <= 0:
			world.player.dump()
			return [null, ""]
		var t := world._nearest_tree(pos, h.trees)
		if (m.in_zone as Zone).contains(pos) or back.count() >= mini(world.player.capacity(), room) or t == null:
			return [(m.in_zone as Zone).global_position, ""]
		return [t.global_position, ""]
	if not back.is_empty():
		world.player.dump()
		return [null, ""]
	if shop and shop.coin_value > 0 and not shop.has_cashier:
		return [shop.coin_zone.global_position, ""]
	if shelf_ok and (m.output as ItemStack).count() >= 4:
		return [(m.out_zone as Zone).global_position, ""]
	if room >= 4:
		var t2 := world._nearest_tree(pos, h.trees)
		if t2:
			return [t2.global_position, ""]
	return [null, ""]


func _first_machine_owned() -> bool:
	return Game.is_unlocked(str({3: "r3_beamsaw", 4: "r4_redmill", 5: "r5_kiln"}.get(region, "")))


# ---------------------------------------------------------------- Grand Timber Station

## Everything owned up to the station pad, platforms empty. The player stands at each valley's
## handcar stop in turn (porters only work while their valley is awake) until its platform is full
## or PROBE_SECONDS (default 900) pass.
func _run_station() -> void:
	var cap_s := _env_f("PROBE_SECONDS", 900.0)
	_win_from = 0.0
	for rid in [1, 2, 3, 4, 5]:
		var pid := "cap_p%d" % rid
		var reg: Region = world.regions[rid]
		world.player.global_position = Balance.HANDCAR_STOPS[rid].land
		world._cam_pos = world.player.global_position
		piles.clear()
		workers.clear()
		_collect_piles(reg)
		t = 0.0
		var next_log := 30.0
		while t < cap_s and not Game.site_done(pid):
			await get_tree().process_frame
			var dt := get_process_delta_time()
			t += dt
			_sample_piles(dt)
			_sample_workers(reg, dt)
			if t >= next_log:
				next_log += 30.0
				var porter := ""
				for id in workers:
					if str(workers[id].name).begins_with("rout"):
						porter += "%s:%s " % [workers[id].name, workers[id].now]
				print("STATION %s t=%4.0f %s %s" % [pid, t, porter, _site_line()])
		var line := "PLATFORM %s done=%s t=%.0fs" % [pid, str(Game.site_done(pid)), t]
		for id in workers:
			var rec: Dictionary = workers[id]
			if not str(rec.name).begins_with("rout"):
				continue
			var tot := 0.0
			for s in rec.states:
				tot += float(rec.states[s])
			var parts: Array = []
			for s in rec.states:
				parts.append("%s %.0f%%" % [s, 100.0 * float(rec.states[s]) / maxf(tot, 0.01)])
			line += "  porter " + ", ".join(parts)
		print(line)
