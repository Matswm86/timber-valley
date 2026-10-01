class_name MegaSaw
extends Node3D

## Big late-game machine: a crane drops a giant log on a conveyor bed and a huge chainsaw
## slices it into planks. Logs arrive by themselves, so it only needs room in its output pile.

const LOG_R := 0.85
const LOG_LEN := 4.6
const SAW_X := 1.6

var output: ItemStack
var out_zone: Zone
var body: Node3D
var _busy: bool = true
var _log: MeshInstance3D
var _t: float = 0.0
var _batch: float = 0.0
var _dropping: bool = false
var _chips: CPUParticles3D
var _crane_hook: Node3D


func setup() -> MegaSaw:
	name = "MegaSaw"
	body = Node3D.new()
	add_child(body)
	var blue := Shapes.mat(Color(0.2, 0.5, 0.88), 0.45)
	var yellow := Shapes.mat(Color(1.0, 0.76, 0.18), 0.45)
	var red := Shapes.mat(Color(0.9, 0.28, 0.2), 0.45)
	var steel := Shapes.mat(Color(0.55, 0.58, 0.62), 0.4, 0.6)
	Shapes.box_node(body, Vector3(8.4, 0.8, 2.6), Vector3(-0.6, 0.4, 0), blue, 0.12)
	for z in [-1.25, 1.25]:
		Shapes.box_node(body, Vector3(8.5, 0.2, 0.2), Vector3(-0.6, 0.85, z), yellow, 0.06)
	var belt := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(2.2, 0.06, 8.2)
	belt.mesh = bm
	var bmat := ShaderMaterial.new()
	bmat.shader = Conveyor.BELT_SHADER
	bmat.set_shader_parameter("length", 8.2)
	bmat.set_shader_parameter("speed", -0.5)
	belt.material_override = bmat
	belt.position = Vector3(-0.6, 0.82, 0)
	belt.rotation_degrees.y = 90
	body.add_child(belt)
	# Gantry over the belt carrying an upright giant chainsaw.
	# One pillar behind the belt with a cantilever arm, so the camera sees the blade.
	Shapes.box_node(body, Vector3(0.6, 4.8, 0.6), Vector3(SAW_X, 2.4, -1.8), red, 0.14)
	Shapes.box_node(body, Vector3(0.7, 0.6, 2.4), Vector3(SAW_X, 4.5, -0.7), red, 0.14)
	Shapes.box_node(body, Vector3(0.8, 0.12, 2.5), Vector3(SAW_X, 4.86, -0.7), yellow, 0.05)
	var saw := ChainSaw.new()
	saw.bar_len = 3.2
	saw.bar_h = 0.8
	saw.setup(null, Color(1.0, 0.45, 0.12))
	saw.rotation_degrees = Vector3(90, 90, 0)
	saw.position = Vector3(SAW_X, 2.35, 0)
	saw.always_on = true
	body.add_child(saw)
	# Crane that brings in the next log.
	var crane: Node3D = load("res://assets/models/factory/crane.glb").instantiate()
	crane.scale = Vector3.ONE * 1.5
	crane.position = Vector3(-4.2, 0, -2.2)
	crane.rotation_degrees.y = 90
	body.add_child(crane)
	_crane_hook = Node3D.new()
	body.add_child(_crane_hook)
	Shapes.box_node(_crane_hook, Vector3(0.12, 3.0, 0.12), Vector3(0, 1.5, 0), steel, 0.04)
	_crane_hook.visible = false
	# Sawdust mound under the blade.
	var mound := MeshInstance3D.new()
	var sm := SphereMesh.new()
	sm.radius = 1.1
	sm.height = 0.9
	mound.mesh = sm
	mound.material_override = Shapes.mat(Color(0.98, 0.84, 0.58), 0.95)
	mound.position = Vector3(SAW_X + 0.9, 0.0, 1.9)
	mound.scale = Vector3(1.2, 0.6, 0.8)
	body.add_child(mound)
	_log = Shapes.log_node(body, LOG_R, LOG_LEN, Vector3.ZERO, Vector3(0, 0, 90), Shapes.log_material(LOG_R))
	_place_log(0.0)
	# Bed, rails, belt, gantry, crane and mound bake into a few meshes; the log and hook move.
	MeshMerge.merge(body, [_log, _crane_hook])
	_chips = CPUParticles3D.new()
	_chips.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_chips.amount = 70
	_chips.lifetime = 1.2
	_chips.direction = Vector3(0.7, 1, 0.5)
	_chips.spread = 45
	_chips.initial_velocity_min = 3
	_chips.initial_velocity_max = 7
	_chips.gravity = Vector3(0, -10, 0)
	_chips.scale_amount_min = 0.8
	_chips.scale_amount_max = 1.6
	var cm := BoxMesh.new()
	cm.size = Vector3(0.12, 0.05, 0.06)
	cm.material = Shapes.mat(Color(0.98, 0.78, 0.45))
	_chips.mesh = cm
	_chips.position = Vector3(SAW_X + 0.2, 1.8, 0.4)
	add_child(_chips)
	output = ItemStack.new().setup("plank", 60, 2, 3, "megasaw:out")
	output.position = Vector3(SAW_X + 3.3, 0, 0.3)
	add_child(output)
	out_zone = Zone.new().setup(Zone.Kind.PICK, output, Vector2(2.4, 2.8), "PLANKS", Color(1.0, 0.95, 0.7))
	out_zone.position = output.position
	add_child(out_zone)
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(8.4, 2.5, 3.6)
	col.shape = bs
	col.position = Vector3(-0.6, 1.25, 0)
	sb.add_child(col)
	add_child(sb)
	return self


## t = 0 fresh log, 1 = fully cut. The log's right end stays at the saw while it shortens.
func _place_log(t: float) -> void:
	var length := LOG_LEN * (1.0 - t * 0.92)
	_log.scale = Vector3(1, length / LOG_LEN, 1)
	_log.position = Vector3(SAW_X - length * 0.5 + 0.2, 0.84 + LOG_R, 0)


func _process(delta: float) -> void:
	var room := output.count() + 2 <= output.capacity
	_chips.emitting = room and not _dropping
	if _dropping or not room:
		return
	var speed := Game.machine_speed()
	_t += delta * speed / 14.0
	_batch += delta * speed
	if _batch >= 0.7:
		_batch = 0.0
		for i in 2:
			var it := Items.make("plank")
			add_child(it)
			it.position = Vector3(SAW_X + 0.6, 1.2 + i * 0.12, 0.3)
			output.push(it)
		Sfx.play("machine", -12.0, 0.8, 0.2)
	if _t >= 1.0:
		_t = 0.0
		_drop_new_log()
	else:
		_place_log(_t)


func _drop_new_log() -> void:
	_dropping = true
	_crane_hook.visible = true
	_place_log(0.0)
	var rest := _log.position
	_log.position = rest + Vector3(-1.5, 6.0, -2.5)
	_crane_hook.position = _log.position + Vector3(0, LOG_R, 0)
	var tw := create_tween()
	tw.tween_property(_log, "position", rest + Vector3(0, 0.4, 0), 1.4).set_trans(Tween.TRANS_SINE)
	tw.parallel().tween_property(_crane_hook, "position", rest + Vector3(0, LOG_R + 0.4, 0), 1.4).set_trans(Tween.TRANS_SINE)
	tw.tween_property(_log, "position", rest, 0.2).set_trans(Tween.TRANS_BOUNCE)
	tw.tween_callback(func() -> void:
		Sfx.play("tree_fall", -6.0, 0.8)
		_crane_hook.visible = false
		_dropping = false)
