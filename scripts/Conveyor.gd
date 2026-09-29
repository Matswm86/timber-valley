class_name Conveyor
extends Node3D

## A belt that carries items from one pile to another on its own.

const BELT_SHADER := preload("res://scripts/belt.gdshader")
const HEIGHT := 0.55

var source: ItemStack
var dest: ItemStack
var points: PackedVector3Array
var speed: float = 2.2
var interval: float = 0.7
var _riding: Array = []
var _timer: float = 0.0
var _length: float = 0.0


func setup(src: ItemStack, dst: ItemStack, pts: PackedVector3Array) -> Conveyor:
	source = src
	dest = dst
	points = pts
	for i in range(1, pts.size()):
		_length += pts[i - 1].distance_to(pts[i])
		_build_segment(pts[i - 1], pts[i])
	return self


func _build_segment(a: Vector3, b: Vector3) -> void:
	var seg := Node3D.new()
	var len := a.distance_to(b)
	seg.transform = Transform3D(Basis.looking_at(b - a, Vector3.UP), (a + b) * 0.5)
	add_child(seg)
	var belt := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(0.8, 0.12, len + 0.8)
	belt.mesh = bm
	var mat := ShaderMaterial.new()
	mat.shader = BELT_SHADER
	mat.set_shader_parameter("length", len + 0.8)
	mat.set_shader_parameter("speed", speed)
	belt.material_override = mat
	belt.position.y = HEIGHT - 0.06
	seg.add_child(belt)
	var rail_mat := StandardMaterial3D.new()
	rail_mat.albedo_color = Color(0.95, 0.68, 0.18)
	rail_mat.roughness = 0.5
	for side in [-0.45, 0.45]:
		var rail := MeshInstance3D.new()
		var rm := BoxMesh.new()
		rm.size = Vector3(0.1, 0.2, len + 0.8)
		rail.mesh = rm
		rail.material_override = rail_mat
		rail.position = Vector3(side, HEIGHT, 0)
		seg.add_child(rail)
	var leg_mat := StandardMaterial3D.new()
	leg_mat.albedo_color = Color(0.3, 0.33, 0.35)
	leg_mat.metallic = 0.6
	leg_mat.roughness = 0.4
	var n := int(len / 1.6) + 1
	for i in n + 1:
		var z := -len * 0.5 + len * float(i) / maxf(n, 1)
		for side in [-0.35, 0.35]:
			var leg := MeshInstance3D.new()
			var lm := BoxMesh.new()
			lm.size = Vector3(0.08, HEIGHT - 0.1, 0.08)
			leg.mesh = lm
			leg.material_override = leg_mat
			leg.position = Vector3(side, (HEIGHT - 0.1) * 0.5, z)
			seg.add_child(leg)


func _point_at(dist: float) -> Vector3:
	var d := dist
	for i in range(1, points.size()):
		var l := points[i - 1].distance_to(points[i])
		if d <= l:
			return points[i - 1].lerp(points[i], d / l) + Vector3(0, HEIGHT, 0)
		d -= l
	return points[-1] + Vector3(0, HEIGHT, 0)


func _process(delta: float) -> void:
	_timer -= delta
	var room := dest.capacity - dest.count() - _riding.size()
	if _timer <= 0.0 and not source.is_empty() and room > 0:
		_timer = interval / Game.machine_speed()
		var it := source.pop()
		if it.has_meta("tw"):
			var old: Tween = it.get_meta("tw")
			if old and old.is_valid():
				old.kill()
		var gxf := it.global_transform
		it.get_parent().remove_child(it)
		add_child(it)
		it.global_transform = gxf
		it.scale = Vector3.ONE
		_riding.append({"node": it, "d": -0.6})
	for r in _riding.duplicate():
		var it: Node3D = r.node
		r.d += speed * Game.machine_speed() * delta
		if r.d < 0.0:
			it.global_position = it.global_position.lerp(to_global(_point_at(0.0)), 0.3)
			continue
		if r.d >= _length:
			_riding.erase(r)
			dest.push(it)
			continue
		it.global_position = to_global(_point_at(r.d))
