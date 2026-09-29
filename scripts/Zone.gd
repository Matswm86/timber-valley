class_name Zone
extends Node3D

## A marked square on the ground. Carriers standing on it drop, pick up, or trigger something.

enum Kind { DROP, PICK, CUSTOM }

const MARKER_SHADER := preload("res://scripts/zone_marker.gdshader")

var kind: Kind = Kind.CUSTOM
var stack: ItemStack
var half: Vector2 = Vector2(1.1, 1.1)
var interval: float = 0.06
var player_only: bool = false
var on_carrier: Callable
var on_enter: Callable
var on_exit: Callable
var marker: MeshInstance3D
var label: Label3D
var _timers: Dictionary = {}
var _inside: Dictionary = {}
var _mat: ShaderMaterial


func setup(k: Kind, s: ItemStack, size: Vector2, text: String, color: Color = Color.WHITE) -> Zone:
	kind = k
	stack = s
	half = size * 0.5
	marker = MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = size
	marker.mesh = pm
	_mat = ShaderMaterial.new()
	_mat.shader = MARKER_SHADER
	_mat.set_shader_parameter("color", color)
	_mat.set_shader_parameter("size", size)
	marker.material_override = _mat
	marker.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	marker.position.y = 0.03
	add_child(marker)
	if text != "":
		label = Label3D.new()
		label.text = text
		label.font = Fx.font()
		label.font_size = 56
		label.outline_size = 20
		label.modulate = Color(1, 1, 1, 1)
		label.outline_modulate = Color(0.32, 0.2, 0.1, 1.0)
		label.pixel_size = 0.0095
		label.rotation_degrees = Vector3(-90, 0, 0)
		label.position = Vector3(0, 0.05, size.y * 0.5 + 0.4)
		label.double_sided = false
		add_child(label)
	add_to_group("zones")
	return self


func set_progress(p: float) -> void:
	_mat.set_shader_parameter("progress", p)


func set_highlight(on: bool) -> void:
	_mat.set_shader_parameter("active", 1.0 if on else 0.0)


func contains(p: Vector3) -> bool:
	var l := global_transform.affine_inverse() * p
	return absf(l.x) <= half.x + 0.25 and absf(l.z) <= half.y + 0.25


## Called every physics frame for a carrier standing inside. Returns true if something moved.
func tick(carrier: Node, delta: float) -> bool:
	var id := carrier.get_instance_id()
	if not _inside.has(id):
		_inside[id] = true
		if carrier.get("is_player") and on_enter.is_valid():
			on_enter.call(carrier)
	var t: float = _timers.get(id, 0.0) - delta
	if t > 0.0:
		_timers[id] = t
		return false
	var moved := false
	match kind:
		Kind.DROP:
			var back: ItemStack = carrier.stack
			if not back.is_empty() and stack.can_accept(back.top_type()):
				back.transfer_to(stack)
				Sfx.play("wood", -8.0, 1.1)
				moved = true
		Kind.PICK:
			var back: ItemStack = carrier.stack
			if not stack.is_empty() and back.count() < carrier.capacity() and back.can_accept(stack.top_type()):
				stack.transfer_to(back)
				Sfx.play("place", -8.0)
				moved = true
		Kind.CUSTOM:
			if on_carrier.is_valid():
				moved = on_carrier.call(carrier, delta)
	_timers[id] = interval if moved else 0.0
	return moved


func left(carrier: Node) -> void:
	var id := carrier.get_instance_id()
	if _inside.has(id):
		_inside.erase(id)
		_timers.erase(id)
		if carrier.get("is_player") and on_exit.is_valid():
			on_exit.call(carrier)
