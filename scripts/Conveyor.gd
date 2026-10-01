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
## Valley this belt belongs to (its Sharp Saws level speeds it up).
var region: int = 1
## Flume look: a water trough instead of a belt, fixed speed, logs bob on the water.
var flume: bool = false
var bob_m: float = 0.0
var bob_hz: float = 0.0
var _clock: float = 0.0
## Optional second route (a split): items alternate between dest and dest2.
var dest2: ItemStack
var points2: PackedVector3Array
var _length2: float = 0.0
var _flip: bool = false
var _riding: Array = []
var _timer: float = 0.0
var _length: float = 0.0
var _height: float = HEIGHT
## item type -> MultiMeshInstance3D drawing the items riding the belt (their nodes are hidden).
var _rider_mm: Dictionary = {}


func setup(src: ItemStack, dst: ItemStack, pts: PackedVector3Array) -> Conveyor:
	source = src
	dest = dst
	points = pts
	for i in range(1, pts.size()):
		_length += pts[i - 1].distance_to(pts[i])
		if not flume:
			_build_segment(pts[i - 1], pts[i])
	if not flume and pts.size() >= 2:
		_build_end(pts[1], pts[0])
		_build_end(pts[-2], pts[-1])
	# Belt, rails, legs and end rollers bake into one mesh per material for the whole belt, and
	# the valley's StaticBatch merges those across all its belts.
	MeshMerge.merge(self)
	StaticBatch.register(self)
	return self


## Log flume: water speed and spacing from Balance.FLUME; the trough models are built by World.
func setup_flume(src: ItemStack, dst: ItemStack, pts: PackedVector3Array, height: float) -> Conveyor:
	flume = true
	speed = float(Balance.FLUME.speed)
	interval = float(Balance.FLUME.spacing)
	bob_m = float(Balance.FLUME.bob_m)
	bob_hz = float(Balance.FLUME.bob_hz)
	_height = height
	return setup(src, dst, pts)


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
	# Rails and legs are the v3 modular pieces (ASSETS_LEFTOVER.md 2.1): the 1 m rail piece
	# stretches along Z, and one leg pair stands at every station.
	var rails: Node3D = load(Models.path("belt_rails")).instantiate()
	rails.scale = Vector3(1, 1, len + 0.8)
	seg.add_child(rails)
	var n := int(len / 1.6) + 1
	for i in n + 1:
		var z := -len * 0.5 + len * float(i) / maxf(n, 1)
		var lg: Node3D = load(Models.path("belt_legs")).instantiate()
		lg.position = Vector3(0, 0, z)
		seg.add_child(lg)


## End roller just past `end`, on the line from `from`: hides the square belt end at a pile.
func _build_end(from: Vector3, end: Vector3) -> void:
	var dir := (end - from).normalized()
	var cap: Node3D = load(Models.path("belt_end")).instantiate()
	cap.transform = Transform3D(Basis.looking_at(end - from, Vector3.UP), end + dir * 0.4)
	add_child(cap)


func _point_at(dist: float) -> Vector3:
	var d := dist
	for i in range(1, points.size()):
		var l := points[i - 1].distance_to(points[i])
		if d <= l:
			return points[i - 1].lerp(points[i], d / l) + Vector3(0, _height, 0)
		d -= l
	return points[-1] + Vector3(0, _height, 0)


## Adds a second route. full_pts is the whole path to dst2; segments from index build_from on are built.
func add_split(dst2: ItemStack, full_pts: PackedVector3Array, build_from: int) -> void:
	dest2 = dst2
	points2 = full_pts
	_length2 = 0.0
	for i in range(1, full_pts.size()):
		_length2 += full_pts[i - 1].distance_to(full_pts[i])
		if i > build_from:
			_build_segment(full_pts[i - 1], full_pts[i])
	if full_pts.size() >= 2:
		_build_end(full_pts[-2], full_pts[-1])
	MeshMerge.merge(self)
	StaticBatch.register(self)


func _room(route: int) -> int:
	var dst: ItemStack = dest if route == 0 else dest2
	var n := 0
	for r in _riding:
		if int(r.r) == route:
			n += 1
	return dst.capacity - dst.count() - n


func _point_on(route: int, dist: float) -> Vector3:
	if route == 0:
		return _point_at(dist)
	var keep := points
	points = points2
	var out := _point_at(dist)
	points = keep
	return out


func _speed_mult() -> float:
	return 1.0 if flume else Game.machine_speed(region)


func _process(delta: float) -> void:
	_clock += delta
	_timer -= delta
	var route := 0
	if dest2 != null:
		route = 1 if _flip else 0
		if _room(route) <= 0:
			route = 1 - route
	if _timer <= 0.0 and not source.is_empty() and _room(route) > 0:
		_flip = not _flip
		_timer = interval / _speed_mult()
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
		it.visible = false
		_riding.append({"node": it, "d": -0.6, "r": route})
	for r in _riding.duplicate():
		var it: Node3D = r.node
		r.d += speed * _speed_mult() * delta
		var rt := int(r.r)
		if r.d < 0.0:
			it.global_position = it.global_position.lerp(to_global(_point_on(rt, 0.0)), 0.3)
			continue
		if r.d >= (_length if rt == 0 else _length2):
			_riding.erase(r)
			it.visible = true
			(dest if rt == 0 else dest2).push(it)
			continue
		it.global_position = to_global(_point_on(rt, r.d))
		if flume:
			it.global_position.y += sin(_clock * TAU * bob_hz + r.d * 2.0) * bob_m
	_draw_riders()


## Riding items are drawn by one MultiMesh per item type, rebuilt each frame from the hidden nodes.
func _draw_riders() -> void:
	var by_type := {}
	for r in _riding:
		var it: Node3D = r.node
		var t := str(it.get_meta("item"))
		if not by_type.has(t):
			by_type[t] = []
		(by_type[t] as Array).append(it.transform)
	for t in _rider_mm:
		if not by_type.has(t):
			(_rider_mm[t] as MultiMeshInstance3D).multimesh.instance_count = 0
	for t in by_type:
		var list: Array = by_type[t]
		var mmi: MultiMeshInstance3D = _rider_mm.get(t)
		if mmi == null:
			mmi = MultiMeshInstance3D.new()
			var mm := MultiMesh.new()
			mm.transform_format = MultiMesh.TRANSFORM_3D
			mm.mesh = Items.mesh_of(t)
			mmi.multimesh = mm
			mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if Items.casts_shadow(t) else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			add_child(mmi)
			ShadowCull.track(mmi)
			_rider_mm[t] = mmi
		var m := mmi.multimesh
		if m.instance_count != list.size():
			m.instance_count = list.size()
		for i in list.size():
			m.set_instance_transform(i, list[i])
