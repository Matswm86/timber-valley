class_name TruckDock
extends Node3D

## Loading dock by the road. A truck pulls in, loads finished goods, and pays on the way out.

enum State { AWAY, ARRIVING, LOADING, LEAVING }

var pile: ItemStack
var zone: Zone
var product: String
var road_x: float
var truck: Node3D
var bed: ItemStack
var state: State = State.AWAY
var _timer: float = 2.0
var _wait: float = 0.0
var _stop: Vector3
var _start: Vector3
var _end: Vector3


func setup(prod: String, road_x_global: float) -> TruckDock:
	name = "TruckDock"
	product = prod
	road_x = road_x_global
	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_color = Color(0.62, 0.6, 0.56)
	floor_mat.roughness = 0.9
	var slab := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(4.2, 0.18, 5.0)
	slab.mesh = bm
	slab.material_override = floor_mat
	slab.position = Vector3(0.6, 0.09, 0)
	add_child(slab)
	for z in [-2.3, 2.3]:
		var post: Node3D = load("res://assets/models/factory/structure-yellow-tall.glb").instantiate()
		post.scale = Vector3.ONE * 1.4
		post.position = Vector3(2.4, 0, z)
		add_child(post)
	pile = ItemStack.new().setup(product, 24, 2, 3, "dock:" + product)
	pile.position = Vector3(0.9, 0.18, 0)
	add_child(pile)
	zone = Zone.new().setup(Zone.Kind.DROP, pile, Vector2(2.4, 3.0), "EXPORT " + product.to_upper() + "S", Color(0.7, 1.0, 0.8))
	zone.position = Vector3(-1.6, 0, 0)
	add_child(zone)
	truck = Node3D.new()
	var model: Node3D = load("res://assets/models/car/truck-flat.glb").instantiate()
	model.scale = Vector3.ONE * 1.7
	truck.add_child(model)
	bed = ItemStack.new().setup(product, 8, 2, 2)
	bed.position = Vector3(0, 1.25, -0.9)
	truck.add_child(bed)
	return self


func _ready() -> void:
	get_parent().add_child.call_deferred(truck)
	_stop = Vector3(road_x, 0, global_position.z)
	_start = Vector3(road_x, 0, global_position.z + 45.0)
	_end = Vector3(road_x, 0, global_position.z - 45.0)
	truck.visible = false


func _process(delta: float) -> void:
	if not truck.is_inside_tree():
		return
	match state:
		State.AWAY:
			_timer -= delta
			if _timer <= 0.0:
				state = State.ARRIVING
				truck.visible = true
				truck.global_position = _start
				truck.rotation.y = PI
		State.ARRIVING:
			truck.global_position = truck.global_position.move_toward(_stop, 9.0 * delta * _ease(_stop))
			if truck.global_position.distance_to(_stop) < 0.05:
				state = State.LOADING
				_wait = 0.0
				_timer = 0.0
		State.LOADING:
			_timer -= delta
			_wait += delta
			if _timer <= 0.0 and not pile.is_empty() and not bed.is_full():
				_timer = 0.18
				pile.transfer_to(bed)
				Sfx.play("wood", -10.0)
			var ready := bed.is_full() or (not bed.is_empty() and pile.is_empty() and _wait > 4.0)
			if ready:
				state = State.LEAVING
				Sfx.play("bell", -6.0)
		State.LEAVING:
			truck.global_position = truck.global_position.move_toward(_end, 10.0 * delta)
			if truck.global_position.distance_to(_end) < 0.1:
				var value := 0
				while not bed.is_empty():
					value += Game.price_of(bed.take_and_free())
				Game.add_money(value)
				Sfx.play("coins", -4.0)
				if Game.hud:
					Game.hud.toast("Truck delivered: +$%d" % value)
				state = State.AWAY
				truck.visible = false
				_timer = 5.0


func _ease(target: Vector3) -> float:
	return clampf(truck.global_position.distance_to(target) / 6.0, 0.15, 1.0)
