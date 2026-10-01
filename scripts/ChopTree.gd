class_name ChopTree
extends Node3D

## A tree you chop by standing next to it. Falls, gives logs, regrows from a sapling.

const MODELS := [
	"tree_pineTallA_detailed", "tree_pineTallC_detailed", "tree_pineRoundA", "tree_pineRoundB",
	"tree_pineDefaultA", "tree_pineTallD_detailed",
]
const BROADLEAF := ["tree_default", "tree_oak", "tree_detailed", "tree_fat"]

## Tree kind from Balance.TREES ("broad", "pine", "birch", ...).
var kind: String = "broad"
## Item the tree drops ("log" in Valley 1, "birch_log" in Birch Bend).
var log_type: String = "log"
var logs_given: int = 3
var hits_needed: int = 3
var regrow_time: float = 7.0
var hp: int = 3
var grown: bool = true
var reserved_by: Node = null
var zone: Zone
var _tree: Node3D
var _stump: Node3D
var _progress: Dictionary = {}
var _chips: CPUParticles3D
var _leaves: CPUParticles3D


func setup(tree_kind: String, rng: RandomNumberGenerator) -> ChopTree:
	kind = tree_kind
	var d: Dictionary = Balance.TREES[kind]
	log_type = str(d.log)
	logs_given = int(d.logs)
	hits_needed = int(d.hits)
	regrow_time = float(d.regrow)
	hp = hits_needed
	var paths: Array = []
	if kind == "birch":
		paths = Models.PATHS.birch_trees
	else:
		for m in (MODELS if kind == "pine" else BROADLEAF):
			paths.append("res://assets/models_v3/nature/%s.glb" % m)
	var mpath: String = paths[rng.randi() % paths.size()]
	_tree = Node3D.new()
	var inst: Node3D = load(mpath).instantiate()
	var s := rng.randf_range(2.3, 2.8) * (1.15 if kind == "pine" else 1.0) * float(d.scale)
	inst.scale = Vector3.ONE * s
	inst.rotation.y = rng.randf() * TAU
	_tree.add_child(inst)
	add_child(_tree)
	_stump = Models.make("birch_stump" if kind == "birch" else "default_stump")
	_stump.scale = Vector3.ONE * 2.2
	_stump.visible = false
	add_child(_stump)
	for mi in _stump.find_children("*", "MeshInstance3D", true, false):
		ShadowCull.track(mi as GeometryInstance3D)
	var body := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var cyl := CylinderShape3D.new()
	cyl.radius = 0.22
	cyl.height = 2.0
	col.shape = cyl
	col.position.y = 1.0
	body.add_child(col)
	add_child(body)
	zone = Zone.new().setup(Zone.Kind.CUSTOM, null, Vector2(2.3, 2.3), "")
	zone.marker.visible = false
	zone.interval = 0.0
	zone.on_carrier = _on_carrier
	add_child(zone)
	_chips = _make_particles(Color(0.85, 0.66, 0.42), 0.09, 14)
	_leaves = _make_particles(Color(0.64, 0.82, 0.34) if kind == "birch" else Color(0.36, 0.62, 0.3), 0.12, 10)
	_leaves.position.y = 2.2
	_leaves.gravity = Vector3(0, -2.5, 0)
	return self


func _make_particles(c: Color, size: float, amount: int) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	# Chips and leaves are a few cm: no shadow pass draw.
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	p.emitting = false
	p.one_shot = true
	p.amount = amount
	p.lifetime = 0.8
	p.explosiveness = 0.95
	p.direction = Vector3(0, 1, 0)
	p.spread = 70.0
	p.initial_velocity_min = 2.0
	p.initial_velocity_max = 4.5
	p.gravity = Vector3(0, -12, 0)
	p.scale_amount_min = 0.6
	p.scale_amount_max = 1.2
	var m := BoxMesh.new()
	m.size = Vector3.ONE * size
	var mat := StandardMaterial3D.new()
	mat.albedo_color = c
	m.material = mat
	p.mesh = m
	p.position.y = 0.8
	add_child(p)
	return p


## Inside a valley the tree model is drawn by the valley's TreeBatch (one draw per model).
func _enter_tree() -> void:
	var batch := TreeBatch.find_for(self)
	for mi in _tree.find_children("*", "MeshInstance3D", true, false):
		if batch:
			batch.add(mi as MeshInstance3D)
		else:
			ShadowCull.track(mi as GeometryInstance3D)


func _exit_tree() -> void:
	var batch := TreeBatch.find_for(self)
	if batch:
		for mi in _tree.find_children("*", "MeshInstance3D", true, false):
			batch.remove(mi as MeshInstance3D)


func is_ready() -> bool:
	return grown and hp > 0


func _on_carrier(carrier: Node, delta: float) -> bool:
	if not is_ready():
		return false
	var back: ItemStack = carrier.stack
	if back.count() >= carrier.capacity() or not back.can_accept(log_type):
		return false
	if reserved_by != null and reserved_by != carrier and is_instance_valid(reserved_by):
		return false
	var id := carrier.get_instance_id()
	var chop_t: float = Game.chop_time() * (1.6 if not carrier.get("is_player") else 1.0)
	carrier.chopping_until = Time.get_ticks_msec() / 1000.0 + 0.25
	_face(carrier)
	var t: float = _progress.get(id, chop_t * 0.6) + delta
	if t < chop_t:
		_progress[id] = t
		return false
	_progress[id] = 0.0
	_hit(carrier)
	return true


func _face(carrier: Node) -> void:
	var m: Node3D = carrier.model
	var d := global_position - (carrier as Node3D).global_position
	if Vector2(d.x, d.z).length() > 0.1 and (carrier as Node3D).get("velocity") != null:
		var v: Vector3 = carrier.velocity
		if Vector2(v.x, v.z).length() < 0.5:
			m.rotation.y = lerp_angle(m.rotation.y, atan2(d.x, d.z), 0.5)


func _hit(carrier: Node) -> void:
	hp -= 1
	Sfx.play("chop", -4.0, randf_range(0.95, 1.1))
	_chips.restart()
	_chips.emitting = true
	if hp > 0:
		_leaves.restart()
		_leaves.emitting = true
		var tw := create_tween()
		var ax := randf_range(-1, 1)
		tw.tween_property(_tree, "rotation", Vector3(0.09 * ax, 0, 0.09), 0.06)
		tw.tween_property(_tree, "rotation", Vector3(-0.05 * ax, 0, -0.05), 0.1)
		tw.tween_property(_tree, "rotation", Vector3.ZERO, 0.15).set_trans(Tween.TRANS_ELASTIC)
		return
	_fall(carrier)


func _fall(carrier: Node) -> void:
	grown = false
	reserved_by = null
	Sfx.play("tree_fall", -3.0)
	var away := global_position - (carrier as Node3D).global_position
	away.y = 0
	if away.length() < 0.01:
		away = Vector3.RIGHT
	away = away.normalized()
	var axis := Vector3.UP.cross(away).normalized()
	_stump.visible = true
	_stump.scale = Vector3.ONE * 2.2
	var tw := create_tween()
	tw.tween_method(
		func(a: float) -> void: _tree.basis = Basis(axis, a), 0.0, PI * 0.5, 0.45
	).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.tween_property(_tree, "scale", Vector3.ONE * 0.01, 0.2)
	tw.tween_callback(func() -> void: _tree.visible = false)
	# Logs burst out of the tree and fly onto the carrier's stack.
	var back: ItemStack = carrier.stack
	var n := mini(logs_given, carrier.capacity() - back.count())
	for i in n:
		var it := Items.make(log_type)
		get_tree().current_scene.add_child(it)
		it.global_position = global_position + away * (1.0 + i * 0.5) + Vector3.UP * 0.4
		it.rotation.y = randf() * TAU
		back.push(it)
	get_tree().create_timer(regrow_time).timeout.connect(_regrow)


func _regrow() -> void:
	_tree.visible = true
	_tree.basis = Basis()
	_tree.scale = Vector3.ONE * 0.05
	hp = hits_needed
	var tw := create_tween()
	tw.tween_property(_tree, "scale", Vector3.ONE, 1.4).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	tw.parallel().tween_property(_stump, "scale", Vector3.ONE * 0.01, 0.4)
	tw.tween_callback(func() -> void:
		_stump.visible = false
		grown = true)
