class_name Shop
extends Node3D

## Market by the road: counters for each product, a till with a coin pile, and shoppers.

const SHELF_X := 0.0
const PLAYER_SIDE := -1.7
const CUSTOMER_SIDE := 1.5

var shelves: Dictionary = {}
var queues: Dictionary = {"till": []}
var coins: ItemStack
var coin_zone: Zone
var coin_value: int = 0
var has_cashier: bool = false
var cashier: Walker
var road_x: float = 7.0
var till_z: float = -5.2
## Valley this market belongs to (Local Fame, ledger, earnings).
var region: int = 1
var region_node: Region
## 1 = player side west, shoppers east (Valley 1). -1 mirrors it (Birch Bend, shoppers from the west).
var side: float = 1.0
## Unlock that boosts shoppers x1.7 ("" = none).
var sign_unlock: String = "roadsign"
var customer_cap: int = Balance.CUSTOMERS_PER_REGION
## Optional shopper route (local spawn/exit points plus a world waypoint on the lane).
var spawn_local: Vector3 = Vector3.INF
var exit_local: Vector3 = Vector3.INF
var lane_via: Vector3 = Vector3.INF
var _spawn_timer: float = 0.5
var _cashier_timer: float = 0.0
var _wood_mat: StandardMaterial3D
var _wood_dark: StandardMaterial3D


func setup(region_id: int = 1, mirror: float = 1.0) -> Shop:
	name = "Shop" if region_id == 1 else "Shop%d" % region_id
	region = region_id
	side = mirror
	_wood_mat = StandardMaterial3D.new()
	_wood_mat.albedo_color = Color(0.78, 0.55, 0.34)
	_wood_mat.roughness = 0.8
	_wood_dark = StandardMaterial3D.new()
	_wood_dark.albedo_color = Color(0.52, 0.34, 0.2)
	_wood_dark.roughness = 0.85
	_build_till()
	_build_canopy()
	# Canopy stripes, posts and till bake into a few meshes (shelves bake when they open).
	MeshMerge.merge(self)
	return self


## Striped shade cloth over the customer side of the market, low and narrow so shoppers stay visible.
func _build_canopy() -> void:
	var red := StandardMaterial3D.new()
	red.albedo_color = Color(0.86, 0.33, 0.26)
	var cream := StandardMaterial3D.new()
	cream.albedo_color = Color(0.98, 0.93, 0.82)
	var z0 := 3.9
	var z1 := till_z - 1.0
	var stripes := 12
	var w := (z0 - z1) / stripes
	for i in stripes:
		var cloth := _box(Vector3(0.9, 0.06, w), Vector3(0.95 * side, 2.35, z0 - w * (i + 0.5)), red if i % 2 == 0 else cream, self)
		cloth.rotation_degrees.z = -14 * side
	for z in [z0, (z0 + z1) * 0.5, z1]:
		_box(Vector3(0.12, 2.45, 0.12), Vector3(0.55 * side, 1.22, z), _wood_dark, self)


func _sign(root: Node3D, product: String) -> void:
	var l := Label3D.new()
	l.font = Fx.font()
	l.text = "%sS  %s" % [product.to_upper(), Game.fmt(Game.price_of(product))]
	l.font_size = 44
	l.outline_size = 12
	l.modulate = Color(1, 0.97, 0.88)
	l.outline_modulate = Color(0.3, 0.18, 0.08)
	l.pixel_size = 0.006
	l.rotation_degrees = Vector3(-55, 0, 0)
	# Mirrored markets push the sign toward the player side so the canopy does not cover it.
	l.position = Vector3(-0.2 if side > 0.0 else 0.6, 1.9, 0.9)
	root.add_child(l)
	# Product icon on the price tag, left of the text (job 2, Models.ICONS 128 px).
	var tex := Models.shop_icon(product)
	var icon: Sprite3D = null
	if tex:
		icon = Sprite3D.new()
		icon.texture = tex
		icon.pixel_size = 0.0036
		icon.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		l.add_child(icon)
		_place_sign_icon(l, icon)
	Game.upgraded.connect(func(id: String, _lv: int) -> void:
		if id == "prices" or id == "r%d_fame" % region:
			l.text = "%sS  %s" % [product.to_upper(), Game.fmt(Game.price_of(product))]
			if icon:
				_place_sign_icon(l, icon))


## Icon just left of the sign text, vertically centred on it.
func _place_sign_icon(l: Label3D, icon: Sprite3D) -> void:
	var w := l.font.get_string_size(l.text, HORIZONTAL_ALIGNMENT_LEFT, -1, l.font_size).x * l.pixel_size
	icon.position = Vector3(-w * 0.5 - 0.3, 0.0, 0.0)


func _box(size: Vector3, pos: Vector3, mat: Material, parent: Node3D) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = pos
	parent.add_child(mi)
	return mi


func _blocker(size: Vector3, pos: Vector3, parent: Node3D) -> void:
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = size
	col.shape = bs
	col.position = pos
	sb.add_child(col)
	parent.add_child(sb)


func _build_till() -> void:
	var root := Node3D.new()
	root.position = Vector3(SHELF_X, 0, till_z)
	add_child(root)
	_box(Vector3(1.3, 0.9, 1.6), Vector3(0, 0.45, 0), _wood_mat, root)
	_box(Vector3(1.45, 0.08, 1.75), Vector3(0, 0.92, 0), _wood_dark, root)
	var chest: Node3D = load("res://assets/models/survival/chest.glb").instantiate()
	chest.scale = Vector3.ONE * 2.2
	chest.position = Vector3(0, 0.96, 0.3)
	chest.rotation_degrees.y = 90
	root.add_child(chest)
	_blocker(Vector3(1.3, 1.5, 1.6), Vector3(0, 0.75, 0), root)
	coins = ItemStack.new().setup("coin", 400, 3, 3)
	coins.position = Vector3(SHELF_X + (PLAYER_SIDE - 0.2) * side, 0, till_z)
	add_child(coins)
	coin_zone = Zone.new().setup(Zone.Kind.CUSTOM, null, Vector2(2.0, 2.2), "CASH", Color(1.0, 0.85, 0.3))
	coin_zone.position = coins.position
	coin_zone.interval = 0.0
	coin_zone.on_carrier = _collect
	add_child(coin_zone)


func add_shelf(product: String, z: float) -> void:
	var root := Node3D.new()
	root.position = Vector3(SHELF_X, 0, z)
	add_child(root)
	_box(Vector3(1.2, 0.55, 2.0), Vector3(0, 0.275, 0), _wood_mat, root)
	_box(Vector3(1.3, 0.06, 2.1), Vector3(0, 0.58, 0), _wood_dark, root)
	_blocker(Vector3(1.2, 1.5, 2.0), Vector3(0, 0.75, 0), root)
	_sign(root, product)
	var st := ItemStack.new().setup(product, 30, 1, 2, "shelf:" + product)
	st.position = Vector3(0, 0.62, 0)
	root.add_child(st)
	var zone := Zone.new().setup(
		Zone.Kind.DROP, st, Vector2(2.0, 2.2), product.to_upper() + "S", Color(1, 1, 1)
	)
	zone.position = Vector3(PLAYER_SIDE * side, 0, 0)
	root.add_child(zone)
	shelves[product] = {"root": root, "stack": st, "zone": zone, "z": z}
	queues[product] = []
	root.visible = false


func open_shelf(product: String, animate: bool) -> void:
	var s: Dictionary = shelves[product]
	var root: Node3D = s.root
	root.visible = true
	MeshMerge.merge(root)
	if animate:
		root.scale = Vector3.ONE * 0.05
		var tw := create_tween()
		tw.tween_property(root, "scale", Vector3.ONE, 0.6).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func is_open(product: String) -> bool:
	return shelves.has(product) and (shelves[product].root as Node3D).visible


func shelf(product: String) -> ItemStack:
	return shelves[product].stack


func shelf_zone(product: String) -> Zone:
	return shelves[product].zone


func shelf_spot(product: String, idx: int) -> Vector3:
	var z: float = shelves[product].z
	return to_global(Vector3(SHELF_X + (CUSTOMER_SIDE + idx * 0.9) * side, 0, z + idx * 0.25))


func till_spot(idx: int) -> Vector3:
	return to_global(Vector3(SHELF_X + (CUSTOMER_SIDE + idx * 0.9) * side, 0, till_z - idx * 0.2))


func join_queue(q: String, c: Node) -> void:
	(queues[q] as Array).append(c)


func leave_queue(q: String, c: Node) -> void:
	(queues[q] as Array).erase(c)


func queue_index(q: String, c: Node) -> int:
	return maxi((queues[q] as Array).find(c), 0)


func pay(c: Node3D, amount: int) -> void:
	coin_value += amount
	Sfx.play("pay", -6.0)
	var n := clampi(amount / 2, 1, 6)
	for i in n:
		if coins.is_full():
			break
		var it := Items.make("coin")
		get_tree().current_scene.add_child(it)
		it.global_position = c.global_position + Vector3(0, 1.2, 0)
		coins.push(it)
	Fx.float_text(get_tree().current_scene, c.global_position + Vector3(0, 2.3, 0), "+" + Game.fmt(amount), Color(1.0, 0.9, 0.35))


func _collect(carrier: Node, _delta: float) -> bool:
	if not carrier.get("is_player") or coin_value <= 0:
		return false
	_take_coins(carrier as Node3D)
	return true


func _take_coins(to: Node3D, by_cashier: bool = false) -> void:
	var value := coin_value
	coin_value = 0
	var shown := 0
	while not coins.is_empty():
		var it := coins.pop()
		if shown < 16:
			Fx.fly_to_and_free(it, to, 0.02 * shown)
			shown += 1
		else:
			it.queue_free()
	Sfx.play("coins", -2.0)
	Game.add_money(value, region)
	if by_cashier and region_node:
		region_node.record(value)
	Fx.float_text(get_tree().current_scene, to.global_position + Vector3(0, 2.6, 0), "+" + Game.fmt(value), Color(1.0, 0.85, 0.2), 1.3)


func hire_cashier(animate: bool) -> void:
	has_cashier = true
	cashier = Walker.new()
	cashier.init_walker("character-female-e")
	cashier.position = Vector3(SHELF_X - 0.2 * side, 0, till_z - 1.4)
	add_child(cashier)
	cashier.model.rotation.y = PI * 0.5 * side
	if animate:
		Fx.pop_in(cashier)


func _process(delta: float) -> void:
	if has_cashier:
		cashier.animate()
		_cashier_timer -= delta
		if _cashier_timer <= 0.0 and coin_value > 0:
			_cashier_timer = 1.2
			_take_coins(Game.player, true)
	_spawn_timer -= delta
	if _spawn_timer <= 0.0:
		# More stock waiting on the counters brings more shoppers, so counters never clog.
		var stock := 0
		for p in shelves:
			if is_open(p):
				stock += shelf(p).count()
		var rush := 1.0 + clampf(stock / 12.0, 0.0, 2.5)
		var sign := 1.7 if sign_unlock != "" and Game.is_unlocked(sign_unlock) else 1.0
		_spawn_timer = randf_range(0.9, 1.7) / (rush * sign * (1.0 + 0.1 * Game.level("prices")) * Game.fame_mult(region))
		_try_spawn()


func _try_spawn() -> void:
	var options: Array = []
	for p in shelves:
		if not is_open(p):
			continue
		if (queues[p] as Array).size() >= 7:
			continue
		var w := 3 if not shelf(p).is_empty() else 1
		for i in w:
			options.append(p)
	if options.is_empty():
		return
	var total := 0
	for q in queues:
		total += (queues[q] as Array).size()
	if total >= customer_cap:
		return
	var prod: String = options[randi() % options.size()]
	var big := shelf(prod).count() >= 12
	var n := randi_range(2, 5) if prod == "plank" else randi_range(1, 3)
	if big:
		n += randi_range(1, 3)
	var spawn := to_global(Vector3(road_x, 0, 7.0 + randf() * 3.0))
	if spawn_local != Vector3.INF:
		spawn = to_global(spawn_local + Vector3(0, 0, randf() * 2.0))
	var entry := to_global(Vector3((CUSTOMER_SIDE + 3.0) * side, 0, shelves[prod].z + 1.5))
	var exit_pt := to_global(Vector3(road_x, 0, till_z - 16.0))
	if exit_local != Vector3.INF:
		exit_pt = to_global(exit_local)
	var c := Customer.new().setup(self, prod, n, spawn, entry, exit_pt, lane_via)
	get_parent().add_child(c)
