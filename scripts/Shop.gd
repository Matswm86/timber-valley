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
var _spawn_timer: float = 0.5
var _cashier_timer: float = 0.0
var _wood_mat: StandardMaterial3D
var _wood_dark: StandardMaterial3D


func setup() -> Shop:
	name = "Shop"
	_wood_mat = StandardMaterial3D.new()
	_wood_mat.albedo_color = Color(0.78, 0.55, 0.34)
	_wood_mat.roughness = 0.8
	_wood_dark = StandardMaterial3D.new()
	_wood_dark.albedo_color = Color(0.52, 0.34, 0.2)
	_wood_dark.roughness = 0.85
	_build_till()
	_build_canopy()
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
		var cloth := _box(Vector3(0.9, 0.06, w), Vector3(0.95, 2.35, z0 - w * (i + 0.5)), red if i % 2 == 0 else cream, self)
		cloth.rotation_degrees.z = -14
	for z in [z0, (z0 + z1) * 0.5, z1]:
		_box(Vector3(0.12, 2.45, 0.12), Vector3(0.55, 1.22, z), _wood_dark, self)


func _sign(root: Node3D, product: String) -> void:
	var l := Label3D.new()
	l.font = Fx.font()
	l.text = "%sS  $%d" % [product.to_upper(), Game.price_of(product)]
	l.font_size = 44
	l.outline_size = 12
	l.modulate = Color(1, 0.97, 0.88)
	l.outline_modulate = Color(0.3, 0.18, 0.08)
	l.pixel_size = 0.006
	l.rotation_degrees = Vector3(-55, 0, 0)
	l.position = Vector3(-0.2, 1.9, 0.9)
	root.add_child(l)
	Game.upgraded.connect(func(id: String, _lv: int) -> void:
		if id == "prices":
			l.text = "%sS  $%d" % [product.to_upper(), Game.price_of(product)])


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
	coins.position = Vector3(SHELF_X + PLAYER_SIDE - 0.2, 0, till_z)
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
	zone.position = Vector3(PLAYER_SIDE, 0, 0)
	root.add_child(zone)
	shelves[product] = {"root": root, "stack": st, "zone": zone, "z": z}
	queues[product] = []
	root.visible = false


func open_shelf(product: String, animate: bool) -> void:
	var s: Dictionary = shelves[product]
	var root: Node3D = s.root
	root.visible = true
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
	return to_global(Vector3(SHELF_X + CUSTOMER_SIDE + idx * 0.9, 0, z + idx * 0.25))


func till_spot(idx: int) -> Vector3:
	return to_global(Vector3(SHELF_X + CUSTOMER_SIDE + idx * 0.9, 0, till_z - idx * 0.2))


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
	Fx.float_text(get_tree().current_scene, c.global_position + Vector3(0, 2.3, 0), "+$%d" % amount, Color(1.0, 0.9, 0.35))


func _collect(carrier: Node, _delta: float) -> bool:
	if not carrier.get("is_player") or coin_value <= 0:
		return false
	_take_coins(carrier as Node3D)
	return true


func _take_coins(to: Node3D) -> void:
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
	Game.add_money(value)
	Fx.float_text(get_tree().current_scene, to.global_position + Vector3(0, 2.6, 0), "+$%d" % value, Color(1.0, 0.85, 0.2), 1.3)


func hire_cashier(animate: bool) -> void:
	has_cashier = true
	cashier = Walker.new()
	cashier.init_walker("character-female-e")
	cashier.position = Vector3(SHELF_X - 0.2, 0, till_z - 1.4)
	add_child(cashier)
	cashier.model.rotation.y = PI * 0.5
	if animate:
		Fx.pop_in(cashier)


func _process(delta: float) -> void:
	if has_cashier:
		cashier.animate()
		_cashier_timer -= delta
		if _cashier_timer <= 0.0 and coin_value > 0:
			_cashier_timer = 1.2
			_take_coins(Game.player)
	_spawn_timer -= delta
	if _spawn_timer <= 0.0:
		_spawn_timer = randf_range(1.2, 2.4) / (1.0 + 0.08 * Game.level("prices"))
		_try_spawn()


func _try_spawn() -> void:
	var options: Array = []
	for p in shelves:
		if not is_open(p):
			continue
		if (queues[p] as Array).size() >= 4:
			continue
		var w := 3 if not shelf(p).is_empty() else 1
		for i in w:
			options.append(p)
	if options.is_empty():
		return
	var total := 0
	for q in queues:
		total += (queues[q] as Array).size()
	if total > 12:
		return
	var prod: String = options[randi() % options.size()]
	var n := randi_range(1, 3) if prod == "plank" else randi_range(1, 2)
	var spawn := to_global(Vector3(road_x, 0, 7.0 + randf() * 3.0))
	var entry := to_global(Vector3(CUSTOMER_SIDE + 3.0, 0, shelves[prod].z + 1.5))
	var exit_pt := to_global(Vector3(road_x, 0, till_z - 16.0))
	var c := Customer.new().setup(self, prod, n, spawn, entry, exit_pt)
	get_parent().add_child(c)
