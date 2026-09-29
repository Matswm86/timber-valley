class_name World
extends Node3D

## Builds the valley: lighting, ground, river, forests, buildings, unlock pads and the camera.

const ROAD_X := 17.0
const GROUND_SHADER := preload("res://scripts/ground.gdshader")
const WATER_SHADER := preload("res://scripts/water.gdshader")
const ROOF_SHADER := preload("res://scripts/roof.gdshader")
const RIVER_X := -27.0
const RIVER_HALF := 3.2

# Every purchasable step. Pads show once all "req" ids are owned.
const UNLOCKS := [
	{"id": "trees2", "cost": 10, "req": [], "title": "More Trees", "pad": Vector3(-9, 0, 5.8)},
	{"id": "office", "cost": 25, "req": [], "title": "Upgrade Office", "pad": Vector3(-3.5, 0, 10.5)},
	{"id": "jack1", "cost": 50, "req": ["trees2"], "title": "Hire a Lumberjack", "pad": Vector3(-4.6, 0, 2.5)},
	{"id": "hauler1", "cost": 70, "req": ["jack1"], "title": "Hire a Plank Carrier", "pad": Vector3(5.0, 0, -0.5)},
	{"id": "carpentry", "cost": 120, "req": ["hauler1"], "title": "Carpentry: Chairs", "pad": Vector3(2, 0, -13)},
	{"id": "hauler3", "cost": 160, "req": ["carpentry"], "title": "Hire a Chair Carrier", "pad": Vector3(6.5, 0, -8.5)},
	{"id": "pine", "cost": 180, "req": ["carpentry"], "title": "Pine Forest", "pad": Vector3(-9.5, 0, -10.5)},
	{"id": "cashier", "cost": 220, "req": ["carpentry"], "title": "Hire a Cashier", "pad": Vector3(7.0, 0, -3.8)},
	{"id": "sawmill2", "cost": 260, "req": ["pine"], "title": "Second Sawmill", "pad": Vector3(-3, 0, -24)},
	{"id": "jack2", "cost": 300, "req": ["sawmill2"], "title": "Hire a Lumberjack", "pad": Vector3(-8.0, 0, -20.5)},
	{"id": "hauler2", "cost": 320, "req": ["sawmill2"], "title": "Hire a Carrier: Sawmill to Carpentry", "pad": Vector3(0.6, 0, -18.8)},
	{"id": "cnc", "cost": 600, "req": ["hauler2"], "title": "CNC Workshop: Tables", "pad": Vector3(9, 0, -24)},
	{"id": "conveyor1", "cost": 700, "req": ["cnc"], "title": "Conveyor Belt", "pad": Vector3(3.0, 0, -20.2)},
	{"id": "hauler4", "cost": 750, "req": ["cnc"], "title": "Hire a Table Carrier", "pad": Vector3(13.0, 0, -19.5)},
	{"id": "factory", "cost": 1200, "req": ["conveyor1"], "title": "Robot Furniture Factory", "pad": Vector3(0, 0, -36)},
	{"id": "jack3", "cost": 900, "req": ["factory"], "title": "North Forest + 2 Lumberjacks", "pad": Vector3(-8.5, 0, -29.0)},
	{"id": "dock", "cost": 1500, "req": ["factory"], "title": "Truck Loading Dock", "pad": Vector3(13.5, 0, -36)},
	{"id": "conveyor2", "cost": 1300, "req": ["dock"], "title": "Factory Conveyor", "pad": Vector3(8.0, 0, -41.0)},
	{"id": "roadsign", "cost": 200, "req": ["carpentry"], "title": "Road Sign: More Shoppers", "pad": Vector3(13.0, 0, 9.5)},
	{"id": "belt_planks", "cost": 350, "req": ["cashier"], "title": "Conveyor: Sawmill to Market", "pad": Vector3(3.2, 0, 9.6)},
	{"id": "belt_saw2", "cost": 500, "req": ["hauler2"], "title": "Conveyor: Sawmill 2 to Carpentry", "pad": Vector3(-2.6, 0, -18.4)},
	{"id": "belt_chairs", "cost": 650, "req": ["hauler3", "belt_planks"], "title": "Conveyor: Chairs to Market", "pad": Vector3(8.0, 0, -8.0)},
	{"id": "megasaw", "cost": 2500, "req": ["factory"], "title": "MEGA Sawmill", "pad": Vector3(11.0, 0, -13.5)},
	{"id": "belt_mega", "cost": 1000, "req": ["megasaw"], "title": "Conveyor: Mega Sawmill to CNC", "pad": Vector3(9.5, 0, -18.4)},
	{"id": "lodge", "cost": 6000, "req": ["conveyor2", "jack3", "belt_mega"], "title": "Build the Grand Lodge", "pad": Vector3(-12, 0, -39)},
]

var rng := RandomNumberGenerator.new()
var shop: Shop
var machines: Dictionary = {}
var forests: Dictionary = {"a": [], "pine": []}
var pads: Dictionary = {}
var ground_mat: ShaderMaterial
var paths: Array = []
var plazas: Array = []
var camera: Camera3D
var player: Player
var guide: MeshInstance3D
var office_zone: Zone
var _cam_pos: Vector3
var _loading: bool = true
var _noise_tex: NoiseTexture2D


func _ready() -> void:
	Game.world = self
	rng.seed = 20260929
	_environment()
	_ground()
	_river()
	_road()
	_base_paths()
	_border_forest()
	_build_forest("a", Vector3(-9, 0, 1.0), 3, 2, 2.5, "broad", 3)
	_build_sawmill1()
	_build_shop()
	player = Player.new()
	player.position = Vector3(0, 0, 4)
	add_child(player)
	_camera()
	_guide_arrow()
	for u in UNLOCKS:
		if Game.is_unlocked(u.id):
			_apply_unlock(u.id, false)
	_refresh_pads()
	_scatter_deco()
	_update_ground_uniforms()
	_bounds()
	_palisades()
	Game.unlocked.connect(_on_unlocked)
	_loading = false


# ---------------------------------------------------------------- environment

func _environment() -> void:
	var env := Environment.new()
	var sky := Sky.new()
	var sm := ProceduralSkyMaterial.new()
	sm.sky_top_color = Color(0.32, 0.62, 0.95)
	sm.sky_horizon_color = Color(0.82, 0.9, 0.95)
	sm.ground_horizon_color = Color(0.78, 0.86, 0.9)
	sm.ground_bottom_color = Color(0.4, 0.5, 0.4)
	sm.sun_angle_max = 30.0
	sky.sky_material = sm
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.75
	env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	env.tonemap_exposure = 0.92
	env.tonemap_white = 6.0
	env.glow_enabled = true
	env.glow_intensity = 0.2
	env.glow_bloom = 0.0
	env.glow_hdr_threshold = 1.6
	env.fog_enabled = true
	env.fog_light_color = Color(0.75, 0.84, 0.9)
	env.fog_density = 0.0025
	env.fog_sky_affect = 0.2
	env.adjustment_enabled = true
	env.adjustment_saturation = 1.22
	env.adjustment_contrast = 1.06
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52, -38, 0)
	sun.light_color = Color(1.0, 0.93, 0.8)
	sun.light_energy = 1.45
	sun.shadow_enabled = true
	sun.shadow_blur = 1.5
	sun.shadow_bias = 0.04
	sun.shadow_normal_bias = 1.2
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_2_SPLITS
	sun.directional_shadow_max_distance = 42.0
	sun.directional_shadow_blend_splits = true
	sun.shadow_opacity = 0.85
	add_child(sun)
	# Cool fill light from the opposite side keeps shadowed faces readable.
	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-35, 150, 0)
	fill.light_color = Color(0.7, 0.8, 1.0)
	fill.light_energy = 0.35
	fill.shadow_enabled = false
	add_child(fill)


func _ground() -> void:
	_noise_tex = NoiseTexture2D.new()
	_noise_tex.seamless = true
	_noise_tex.width = 256
	_noise_tex.height = 256
	var fn := FastNoiseLite.new()
	fn.frequency = 0.02
	fn.fractal_octaves = 3
	_noise_tex.noise = fn
	var detail := NoiseTexture2D.new()
	detail.seamless = true
	detail.width = 256
	detail.height = 256
	var fn2 := FastNoiseLite.new()
	fn2.frequency = 0.12
	fn2.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	detail.noise = fn2
	ground_mat = ShaderMaterial.new()
	ground_mat.shader = GROUND_SHADER
	ground_mat.set_shader_parameter("noise_tex", _noise_tex)
	ground_mat.set_shader_parameter("detail_tex", detail)
	ground_mat.set_shader_parameter("river_x", RIVER_X)
	ground_mat.set_shader_parameter("river_half", RIVER_HALF)
	ground_mat.set_shader_parameter("grass_a", Color(0.27, 0.54, 0.14))
	ground_mat.set_shader_parameter("grass_b", Color(0.38, 0.63, 0.17))
	ground_mat.set_shader_parameter("dirt", Color(0.86, 0.72, 0.5))
	ground_mat.set_shader_parameter("dirt_dark", Color(0.78, 0.63, 0.42))
	var mi := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(160, 170)
	pm.subdivide_width = 2
	pm.subdivide_depth = 2
	mi.mesh = pm
	mi.material_override = ground_mat
	mi.position = Vector3(0, 0, -15)
	add_child(mi)
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	col.shape = WorldBoundaryShape3D.new()
	sb.add_child(col)
	add_child(sb)


func _river() -> void:
	var mi := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(RIVER_HALF * 2.0 + 1.0, 170)
	pm.subdivide_depth = 60
	mi.mesh = pm
	var mat := ShaderMaterial.new()
	mat.shader = WATER_SHADER
	mat.set_shader_parameter("noise_tex", _noise_tex)
	mi.material_override = mat
	mi.position = Vector3(RIVER_X, 0.06, -15)
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)
	# A little wooden bridge and some reeds along the bank.
	for z in [-6.0]:
		for i in 5:
			var b := _model("res://assets/models/nature/bridge_wood.glb", Vector3(RIVER_X - 3.2 + i * 1.6, 0, z), 1.6, 90)
			b.name = "bridge"


func _road() -> void:
	var mi := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(3.6, 170)
	mi.mesh = pm
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.5, 0.49, 0.46)
	mat.roughness = 0.95
	mi.material_override = mat
	mi.position = Vector3(ROAD_X, 0.02, -15)
	add_child(mi)
	var line_mat := StandardMaterial3D.new()
	line_mat.albedo_color = Color(0.95, 0.9, 0.7)
	for i in 40:
		var dash := MeshInstance3D.new()
		var dm := PlaneMesh.new()
		dm.size = Vector2(0.14, 1.4)
		dash.mesh = dm
		dash.material_override = line_mat
		dash.position = Vector3(ROAD_X, 0.03, 60 - i * 4.0)
		add_child(dash)
	paths.append([Vector4(ROAD_X, 70, ROAD_X, -100), 2.6])


func _base_paths() -> void:
	paths.append([Vector4(0, 12, 0, -44), 1.0])
	paths.append([Vector4(-9, 1, 0, -1.5), 0.8])
	paths.append([Vector4(2.5, -3.5, 8.5, 3), 0.8])
	paths.append([Vector4(8.5, -1.2, ROAD_X, -1.2), 0.9])
	plazas.append(Vector4(0, -4, 4.8, 2.2))
	plazas.append(Vector4(10.5, 2.5, 3.2, 5.6))


func _bounds() -> void:
	var walls := [
		[Vector3(RIVER_X + RIVER_HALF + 0.3, 1, -15), Vector3(1, 2, 170)],
		[Vector3(ROAD_X + 2.2, 1, -15), Vector3(1, 2, 170)],
		[Vector3(0, 1, 15.5), Vector3(80, 2, 1)],
		[Vector3(0, 1, -47), Vector3(80, 2, 1)],
	]
	for w in walls:
		var sb := StaticBody3D.new()
		var col := CollisionShape3D.new()
		var bs := BoxShape3D.new()
		bs.size = w[1]
		col.shape = bs
		sb.position = w[0]
		sb.add_child(col)
		add_child(sb)


func _update_ground_uniforms() -> void:
	var ps: Array[Vector4] = []
	var ws: Array[float] = []
	for p in paths:
		ps.append(p[0])
		ws.append(p[1])
	while ps.size() < 32:
		ps.append(Vector4.ZERO)
		ws.append(-10.0)
	ground_mat.set_shader_parameter("paths", ps)
	ground_mat.set_shader_parameter("path_widths", PackedFloat32Array(ws))
	ground_mat.set_shader_parameter("path_count", mini(paths.size(), 32))
	var pl: Array[Vector4] = []
	for p in plazas:
		pl.append(p)
	while pl.size() < 24:
		pl.append(Vector4(9999, 9999, 0, 0))
	ground_mat.set_shader_parameter("plazas", pl)
	ground_mat.set_shader_parameter("plaza_count", mini(plazas.size(), 24))


# ---------------------------------------------------------------- helpers

func _model(path: String, pos: Vector3, scl: float, rot_y: float = 0.0, parent: Node3D = null) -> Node3D:
	var inst: Node3D = load(path).instantiate()
	inst.position = pos
	inst.scale = Vector3.ONE * scl
	inst.rotation_degrees.y = rot_y
	(parent if parent else self).add_child(inst)
	return inst


func _mat(c: Color, rough: float = 0.8, metal: float = 0.0) -> StandardMaterial3D:
	return Shapes.mat(c, rough, metal)


func _box(parent: Node3D, size: Vector3, pos: Vector3, mat: Material, rot: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var r := clampf(minf(size.x, minf(size.y, size.z)) * 0.3, 0.02, 0.12)
	return Shapes.box_node(parent, size, pos, mat, r, rot)


## Open wooden shed: floor, four posts and a pitched roof.
func _shed(parent: Node3D, w: float, d: float, h: float, roof: Color) -> void:
	var wood := Shapes.wood(Color(0.86, 0.62, 0.38))
	var dark := Shapes.wood(Color(0.55, 0.36, 0.22))
	_box(parent, Vector3(w, 0.2, d), Vector3(0, 0.1, 0), wood)
	for sx in [-1, 1]:
		for sz in [-1, 1]:
			Shapes.log_node(parent, 0.13, h, Vector3(sx * (w * 0.5 - 0.2), h * 0.5, sz * (d * 0.5 - 0.2)), Vector3.ZERO)
	_box(parent, Vector3(w + 0.2, 0.2, 0.24), Vector3(0, h, -d * 0.5 + 0.2), dark)
	_box(parent, Vector3(w + 0.2, 0.2, 0.24), Vector3(0, h, d * 0.5 - 0.2), dark)
	# Lean-to roof over the back half so the machine stays visible from the camera.
	var rm := ShaderMaterial.new()
	rm.shader = ROOF_SHADER
	rm.set_shader_parameter("base", roof)
	var slope := 18.0
	var depth := d * 0.62 + 0.4
	var panel := depth / cos(deg_to_rad(slope))
	var rise := depth * tan(deg_to_rad(slope))
	var zc := -d * 0.5 - 0.4 + depth * 0.5
	_box(parent, Vector3(w + 0.7, 0.16, panel), Vector3(0, h + rise * 0.5 + 0.1, zc), rm, Vector3(-slope, 0, 0))
	_box(parent, Vector3(w + 0.8, 0.2, 0.22), Vector3(0, h + 0.1, zc + depth * 0.5), _mat(roof.darkened(0.25)))
	_box(parent, Vector3(w + 0.2, rise + 0.2, 0.18), Vector3(0, h + rise * 0.5, -d * 0.5 + 0.2), _mat(Color(0.6, 0.42, 0.26)))


func _first_mesh(path: String) -> Array:
	var inst: Node3D = load(path).instantiate()
	var mis := inst.find_children("*", "MeshInstance3D", true, false)
	var out := []
	if not mis.is_empty():
		var mi: MeshInstance3D = mis[0]
		var xf := Transform3D.IDENTITY
		var n: Node = mi
		while n != inst and n is Node3D:
			xf = (n as Node3D).transform * xf
			n = n.get_parent()
		out = [mi.mesh, xf]
	inst.free()
	return out


func _multimesh(path: String, xforms: Array, shadows: bool = true) -> void:
	if xforms.is_empty():
		return
	var mm_info := _first_mesh(path)
	if mm_info.is_empty():
		return
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = mm_info[0]
	mm.instance_count = xforms.size()
	for i in xforms.size():
		mm.set_instance_transform(i, (xforms[i] as Transform3D) * (mm_info[1] as Transform3D))
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if shadows else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mmi)


func _busy(p: Vector2, margin: float) -> bool:
	for pa in paths:
		var s: Vector4 = pa[0]
		var a := Vector2(s.x, s.y)
		var b := Vector2(s.z, s.w)
		var ab := b - a
		var t := clampf((p - a).dot(ab) / maxf(ab.length_squared(), 0.0001), 0.0, 1.0)
		if p.distance_to(a + ab * t) < float(pa[1]) + margin:
			return true
	for pl in plazas:
		var v: Vector4 = pl
		if absf(p.x - v.x) < v.z + margin + 0.6 and absf(p.y - v.y) < v.w + margin + 0.6:
			return true
	for u in UNLOCKS:
		var pp: Vector3 = u.pad
		if Vector2(pp.x, pp.z).distance_to(p) < 3.2 + margin:
			return true
	if absf(p.x - RIVER_X) < RIVER_HALF + 0.8:
		return true
	for key in forests:
		for t in forests[key]:
			var tp: Vector3 = (t as Node3D).position
			if Vector2(tp.x, tp.z).distance_to(p) < 1.3 + margin:
				return true
	return false


# ---------------------------------------------------------------- scenery

func _border_forest() -> void:
	var kinds := [
		"tree_pineTallA_detailed", "tree_pineTallB_detailed", "tree_pineTallC_detailed",
		"tree_pineTallD_detailed", "tree_pineRoundA", "tree_pineRoundC", "tree_default_dark",
		"tree_default", "tree_detailed", "tree_oak", "tree_fat", "tree_pineDefaultB",
	]
	var buckets := {}
	for k in kinds:
		buckets[k] = []
	var areas := [
		Rect2(-60, 18, 120, 16),
		Rect2(-60, -66, 120, 18),
		Rect2(RIVER_X - 26, -66, 22, 98),
		Rect2(ROAD_X + 3.2, -66, 30, 98),
		Rect2(RIVER_X + RIVER_HALF + 0.8, -50, 5.0, 66),
	]
	for r in areas:
		var rect: Rect2 = r
		var n := int(rect.get_area() / 3.2)
		for i in n:
			var p := Vector2(rng.randf_range(rect.position.x, rect.end.x), rng.randf_range(rect.position.y, rect.end.y))
			if absf(p.x - RIVER_X) < RIVER_HALF + 1.0:
				continue
			if absf(p.x - ROAD_X) < 3.0:
				continue
			var k: String = kinds[rng.randi() % kinds.size()]
			var s := rng.randf_range(2.4, 3.6)
			var xf := Transform3D(Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3.ONE * s), Vector3(p.x, 0, p.y))
			(buckets[k] as Array).append(xf)
	for k in kinds:
		_multimesh("res://assets/models/nature/%s.glb" % k, buckets[k])


func _scatter_deco() -> void:
	var sets := [
		["grass", 260, 2.4, false], ["grass_large", 160, 2.4, false], ["grass_leafs", 110, 2.6, false],
		["flower_redA", 110, 2.6, false], ["flower_yellowA", 120, 2.6, false], ["flower_yellowB", 60, 2.4, false],
		["flower_redC", 50, 2.4, false], ["plant_bush", 110, 2.8, true], ["plant_bushDetailed", 90, 2.6, true],
		["rock_smallA", 40, 2.2, true], ["rock_smallC", 40, 2.2, true], ["mushroom_redGroup", 25, 2.2, false],
		["mushroom_tanGroup", 20, 2.2, false], ["rock_largeA", 10, 2.4, true],
	]
	var area := Rect2(RIVER_X - 10, -50, (ROAD_X + 12) - (RIVER_X - 10), 68)
	for s in sets:
		var list := []
		var tries: int = s[1] * 3
		while list.size() < int(s[1]) and tries > 0:
			tries -= 1
			var p := Vector2(rng.randf_range(area.position.x, area.end.x), rng.randf_range(area.position.y, area.end.y))
			if absf(p.x - ROAD_X) < 2.4:
				continue
			if _busy(p, 0.6):
				continue
			var sc: float = s[2] * rng.randf_range(0.75, 1.3)
			list.append(Transform3D(Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3.ONE * sc), Vector3(p.x, 0, p.y)))
		_multimesh("res://assets/models/nature/%s.glb" % s[0], list, s[3])
	# Tall rocks and reeds on the river banks.
	var rocks := []
	for i in 26:
		var z := rng.randf_range(-60, 20)
		var side := -1.0 if rng.randf() < 0.5 else 1.0
		var x := RIVER_X + side * (RIVER_HALF + rng.randf_range(0.2, 0.9))
		rocks.append(Transform3D(Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3.ONE * rng.randf_range(1.6, 2.6)), Vector3(x, -0.05, z)))
	_multimesh("res://assets/models/nature/rock_smallD.glb", rocks)
	# A few props around the starting yard.
	_model("res://assets/models/nature/log_stackLarge.glb", Vector3(-3.6, 0, -6.8), 2.2, 10)
	_model("res://assets/models/survival/barrel.glb", Vector3(3.8, 0, -6.4), 2.4)
	_model("res://assets/models/survival/box-large.glb", Vector3(4.6, 0, -6.6), 2.2, 20)
	_model("res://assets/models/survival/signpost.glb", Vector3(1.4, 0, 6.0), 2.6, -20)
	_model("res://assets/models/nature/campfire_logs.glb", Vector3(-4.5, 0, 12.5), 3.0)
	for i in 6:
		_model("res://assets/models/nature/fence_simple.glb", Vector3(-12.5 + i * 2.0, 0, 13.5), 2.0)


func _build_forest(key: String, center: Vector3, cols: int, rows: int, spacing: float, kind: String, logs: int, animate: bool = false) -> void:
	for r in rows:
		for c in cols:
			var p := center + Vector3((c - (cols - 1) * 0.5) * spacing, 0, (r - (rows - 1) * 0.5) * spacing)
			p += Vector3(rng.randf_range(-0.35, 0.35), 0, rng.randf_range(-0.35, 0.35))
			var t := ChopTree.new().setup(kind, logs, rng)
			t.position = p
			if kind == "pine":
				t.regrow_time = 8.0
			add_child(t)
			(forests[key] as Array).append(t)
			if animate:
				Fx.pop_in(t, 0.5 + 0.05 * (r * cols + c))


# ---------------------------------------------------------------- buildings

func _machine(id: String, pos: Vector3, i_t: String, o_t: String, i_n: int, o_n: int, t: float) -> Machine:
	var m := Machine.new().setup(id, i_t, o_t, i_n, o_n, t)
	m.position = pos
	machines[id] = m
	return m


func _build_sawmill1() -> void:
	var m := _machine("sawmill1", Vector3(0, 0, -4), "log", "plank", 1, 2, 1.0)
	_dress_sawmill(m, Color(1.0, 0.45, 0.12))
	add_child(m)


func _dress_sawmill(m: Machine, frame: Color) -> void:
	m.input.position.x = -3.4
	m.in_zone.position.x = -3.4
	m.output.position.x = 3.4
	m.out_zone.position.x = 3.4
	var bed := Shapes.mat(Color(0.2, 0.5, 0.86), 0.45)
	var yellow := Shapes.mat(Color(1.0, 0.76, 0.18), 0.45)
	var steel := Shapes.mat(Color(0.55, 0.58, 0.62), 0.4, 0.6)
	_box(m.body, Vector3(4.4, 0.5, 1.15), Vector3(0, 0.25, 0.2), bed)
	for z in [-0.42, 0.82]:
		_box(m.body, Vector3(4.5, 0.14, 0.12), Vector3(0, 0.56, z), yellow)
	var belt := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(0.8, 0.05, 4.3)
	belt.mesh = bm
	var bmat := ShaderMaterial.new()
	bmat.shader = Conveyor.BELT_SHADER
	bmat.set_shader_parameter("length", 4.3)
	bmat.set_shader_parameter("speed", -1.0)
	belt.material_override = bmat
	belt.position = Vector3(0, 0.52, 0.2)
	belt.rotation_degrees.y = 90
	m.body.add_child(belt)
	for x in [-1.8, 1.8]:
		for z in [-0.35, 0.75]:
			_box(m.body, Vector3(0.14, 0.2, 0.14), Vector3(x, 0.05, z), steel)
	# Stand for the saw motor behind the belt, then the saw itself across the belt.
	# Frame over the belt holding an upright chainsaw that rips logs into planks.
	var fc := Shapes.mat(frame, 0.45)
	for x in [-0.75, 0.75]:
		_box(m.body, Vector3(0.24, 2.7, 0.3), Vector3(x, 1.35, -0.45), fc)
	_box(m.body, Vector3(1.8, 0.3, 0.34), Vector3(0, 2.7, -0.45), fc)
	_box(m.body, Vector3(1.9, 0.08, 0.4), Vector3(0, 2.88, -0.45), yellow)
	var saw := ChainSaw.new()
	saw.bar_len = 1.55
	saw.setup(m, frame)
	saw.rotation_degrees = Vector3(90, 90, 0)
	saw.position = Vector3(0, 1.28, 0.2)
	m.body.add_child(saw)
	# Warning stripes and a little control box.
	_box(m.body, Vector3(0.35, 0.5, 0.3), Vector3(1.4, 0.8, -0.75), yellow)
	_box(m.body, Vector3(0.22, 0.16, 0.05), Vector3(1.4, 0.92, -0.58), Shapes.mat(Color(0.15, 0.8, 0.35), 0.3))
	var logs := Node3D.new()
	logs.position = Vector3(-1.2, 0, -1.25)
	m.body.add_child(logs)
	for k in 3:
		Shapes.log_node(logs, 0.17, 1.3, Vector3(0, 0.17, k * 0.36 - 0.36), Vector3(0, 0, 90))
	Shapes.log_node(logs, 0.17, 1.3, Vector3(0, 0.47, -0.18), Vector3(0, 0, 90))
	Shapes.log_node(logs, 0.17, 1.3, Vector3(0, 0.47, 0.18), Vector3(0, 0, 90))
	m.mouth_in = Vector3(-2.0, 0.55, 0.2)
	m.mouth_out = Vector3(1.9, 0.55, 0.2)
	m.cut_point = Vector3(0, 0.55, 0.2)
	m.add_dust(Vector3(0.1, 0.75, 0.3), Color(0.98, 0.78, 0.45))
	m.dust.amount = 48
	m.dust.initial_velocity_min = 2.5
	m.dust.initial_velocity_max = 5.0
	m.dust.direction = Vector3(0.6, 1, 0.3)
	m.dust.spread = 50
	m.dust.gravity = Vector3(0, -9, 0)
	m.dust.lifetime = 1.0
	(m.dust.mesh as BoxMesh).size = Vector3(0.09, 0.04, 0.05)
	m.add_blocker(Vector3(4.4, 1.2, 1.3), Vector3(0, 0, 0.2))


## Log palisade fences: rows of upright logs around the valley and behind the first forest.
func _palisades() -> void:
	var lines := [
		[Vector2(-23.2, 15.3), Vector2(14.8, 15.3)],
		[Vector2(-23.2, -46.6), Vector2(14.8, -46.6)],
		[Vector2(-23.2, 15.3), Vector2(-23.2, -46.6)],
		[Vector2(-13.3, -1.5), Vector2(-13.3, 9.5)],
	]
	var xforms := []
	for ln in lines:
		var a: Vector2 = ln[0]
		var b: Vector2 = ln[1]
		var n := int(a.distance_to(b) / 0.31)
		for k in n + 1:
			var p := a.lerp(b, float(k) / maxf(n, 1))
			var hgt := rng.randf_range(0.95, 1.3)
			var basis := Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3(1, hgt, 1))
			basis = Basis(Vector3(rng.randf_range(-1, 1), 0, rng.randf_range(-1, 1)).normalized(), rng.randf_range(0, 0.04)) * basis
			xforms.append(Transform3D(basis, Vector3(p.x, hgt * 0.5, p.y)))
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = Shapes.log_mesh(0.16, 1.0)
	mm.instance_count = xforms.size()
	for k in xforms.size():
		mm.set_instance_transform(k, xforms[k])
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	mmi.material_override = Shapes.log_material(0.16)
	add_child(mmi)
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(0.4, 2, 11)
	col.shape = bs
	sb.position = Vector3(-13.3, 1, 4)
	sb.add_child(col)
	add_child(sb)


func _build_shop() -> void:
	shop = Shop.new().setup()
	shop.position = Vector3(10, 0, 4)
	shop.road_x = ROAD_X - 10.0
	shop.add_shelf("plank", 2.6)
	shop.add_shelf("chair", 0.0)
	shop.add_shelf("table", -2.6)
	add_child(shop)
	shop.open_shelf("plank", false)


func _spawn_lumberjack(look: String, forest: Array, m: Machine, home: Vector3, animate: bool) -> void:
	var w := Worker.new().as_lumberjack(look, forest, m.input, m.in_zone.global_position, home)
	add_child(w)
	if animate:
		Fx.pop_in(w)


func _spawn_hauler(look: String, src: ItemStack, src_zone: Zone, dst: ItemStack, dst_zone: Zone, animate: bool) -> void:
	var w := Worker.new().as_hauler(look, src, src_zone.global_position, dst, dst_zone.global_position)
	add_child(w)
	if animate:
		Fx.pop_in(w)


func _apply_unlock(id: String, animate: bool) -> void:
	match id:
		"trees2":
			_build_forest("a", Vector3(-9, 0, 6.2), 3, 2, 2.5, "broad", 3, animate)
		"office":
			_build_office(animate)
		"jack1":
			_spawn_lumberjack("character-male-c", forests.a, machines.sawmill1, Vector3(-5, 0, 3), animate)
		"hauler1":
			_spawn_hauler("character-female-d", machines.sawmill1.output, machines.sawmill1.out_zone, shop.shelf("plank"), shop.shelf_zone("plank"), animate)
		"carpentry":
			_build_carpentry(animate)
			shop.open_shelf("chair", animate)
		"hauler3":
			_spawn_hauler("character-male-b", machines.carpentry.output, machines.carpentry.out_zone, shop.shelf("chair"), shop.shelf_zone("chair"), animate)
		"pine":
			_build_forest("pine", Vector3(-13.5, 0, -15), 4, 3, 2.6, "pine", 4, animate)
			paths.append([Vector4(0, -12, -9, -14), 0.7])
		"cashier":
			shop.hire_cashier(animate)
		"sawmill2":
			var m := _machine("sawmill2", Vector3(-3, 0, -24), "log", "plank", 1, 2, 0.8)
			_dress_sawmill(m, Color(0.3, 0.75, 0.3))
			add_child(m)
			plazas.append(Vector4(-3, -24, 4.8, 2.2))
			if animate:
				Fx.pop_in(m, 0.7)
		"jack2":
			_spawn_lumberjack("character-male-d", forests.pine, machines.sawmill2, Vector3(-8, 0, -20), animate)
		"hauler2":
			_spawn_hauler("character-female-c", machines.sawmill2.output, machines.sawmill2.out_zone, machines.carpentry.input, machines.carpentry.in_zone, animate)
		"cnc":
			_build_cnc(animate)
			shop.open_shelf("table", animate)
		"conveyor1":
			var c := Conveyor.new().setup(machines.sawmill2.output, machines.cnc.input, PackedVector3Array([
				Vector3(0.4, 0, -25.6), Vector3(6.0, 0, -25.6), Vector3(6.0, 0, -24.4)]))
			add_child(c)
			if animate:
				Fx.pop_in(c, 0.6)
		"hauler4":
			_spawn_hauler("character-female-b", machines.cnc.output, machines.cnc.out_zone, shop.shelf("table"), shop.shelf_zone("table"), animate)
		"factory":
			_build_factory(animate)
		"jack3":
			forests["north"] = []
			_build_forest("north", Vector3(-13.5, 0, -31), 4, 2, 2.6, "pine", 4, animate)
			_spawn_lumberjack("character-male-a", forests.north, machines.factory, Vector3(-8, 0, -30), animate)
			_spawn_lumberjack("character-female-a", forests.north, machines.factory, Vector3(-8, 0, -32), animate)
		"dock":
			var d := TruckDock.new().setup("bookcase", ROAD_X)
			d.position = Vector3(13.5, 0, -36)
			add_child(d)
			machines["dock"] = d
			plazas.append(Vector4(13.5, -36, 2.6, 3.0))
			paths.append([Vector4(3, -36, 12, -36), 0.8])
			if animate:
				Fx.pop_in(d, 0.6)
		"conveyor2":
			var d: TruckDock = machines.dock
			var c := Conveyor.new().setup(machines.factory.output, d.pile, PackedVector3Array([
				Vector3(3.9, 0, -37.8), Vector3(14.4, 0, -37.8), Vector3(14.4, 0, -36.6)]))
			add_child(c)
			if animate:
				Fx.pop_in(c, 0.6)
		"roadsign":
			var sg := Node3D.new()
			sg.position = Vector3(15.0, 0, 10.5)
			add_child(sg)
			for x in [-0.9, 0.9]:
				Shapes.log_node(sg, 0.12, 2.6, Vector3(x, 1.3, 0), Vector3.ZERO)
			_box(sg, Vector3(2.4, 1.1, 0.14), Vector3(0, 2.1, 0), Shapes.wood(Color(0.9, 0.66, 0.4)))
			var lbl := Label3D.new()
			lbl.font = Fx.font()
			lbl.text = "TIMBER\nVALLEY"
			lbl.font_size = 64
			lbl.outline_size = 14
			lbl.modulate = Color(1, 0.96, 0.85)
			lbl.outline_modulate = Color(0.35, 0.2, 0.08)
			lbl.pixel_size = 0.006
			lbl.position = Vector3(0, 2.1, 0.09)
			sg.add_child(lbl)
			if animate:
				Fx.pop_in(sg, 0.6)
		"belt_planks":
			_belt(machines.sawmill1.output, shop.shelf("plank"), [Vector3(4.8, 0, -3.8), Vector3(4.8, 0, 6.6), Vector3(9.1, 0, 6.6)], animate)
		"belt_saw2":
			_belt(machines.sawmill2.output, machines.carpentry.input, [Vector3(0.4, 0, -22.3), Vector3(0.4, 0, -15.2), Vector3(-0.7, 0, -15.2), Vector3(-0.7, 0, -14.2)], animate)
		"belt_chairs":
			_belt(machines.carpentry.output, shop.shelf("chair"), [Vector3(5.9, 0, -12.8), Vector3(5.9, 0, 4.0), Vector3(9.1, 0, 4.0)], animate)
		"megasaw":
			var ms := MegaSaw.new().setup()
			ms.position = Vector3(10.2, 0, -13.2)
			add_child(ms)
			machines["megasaw"] = ms
			plazas.append(Vector4(11.0, -12.6, 5.0, 2.8))
			if animate:
				Fx.pop_in(ms, 0.9)
		"belt_mega":
			var ms: MegaSaw = machines.megasaw
			_belt(ms.output, machines.cnc.input, [Vector3(15.1, 0, -12.9), Vector3(15.1, 0, -27.4), Vector3(6.9, 0, -27.4), Vector3(6.9, 0, -24.7)], animate)
		"lodge":
			_build_lodge(animate)
	if not _loading:
		_update_ground_uniforms()


func _belt(src: ItemStack, dst: ItemStack, pts: Array, animate: bool) -> void:
	var c := Conveyor.new().setup(src, dst, PackedVector3Array(pts))
	add_child(c)
	if animate:
		Fx.pop_in(c, 0.6)


func _build_office(animate: bool) -> void:
	var root := Node3D.new()
	root.position = Vector3(-3.5, 0, 12.5)
	add_child(root)
	_shed(root, 3.2, 2.4, 2.1, Color(0.3, 0.55, 0.35))
	_model("res://assets/models/survival/workbench.glb", Vector3(-0.6, 0.2, -0.3), 2.6, 0, root)
	_model("res://assets/models/survival/chest.glb", Vector3(0.8, 0.2, -0.4), 2.4, 0, root)
	_model("res://assets/models/survival/signpost-single.glb", Vector3(1.9, 0, 1.3), 2.6, 0, root)
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(3.2, 2, 2.4)
	col.shape = bs
	col.position.y = 1
	sb.add_child(col)
	root.add_child(sb)
	office_zone = Zone.new().setup(Zone.Kind.CUSTOM, null, Vector2(2.4, 2.0), "UPGRADES", Color(0.6, 0.95, 1.0))
	office_zone.position = Vector3(-3.5, 0, 10.0)
	office_zone.on_enter = func(_c: Node) -> void:
		if Game.hud:
			Game.hud.open_upgrades()
	office_zone.on_exit = func(_c: Node) -> void:
		if Game.hud:
			Game.hud.close_upgrades()
	add_child(office_zone)
	plazas.append(Vector4(-3.5, 11.5, 2.4, 2.2))
	if animate:
		Fx.pop_in(root, 0.6)


func _build_carpentry(animate: bool) -> void:
	var m := _machine("carpentry", Vector3(2, 0, -13), "plank", "chair", 2, 1, 1.4)
	_shed(m.body, 3.6, 2.6, 2.3, Color(0.35, 0.55, 0.3))
	m.add_model("res://assets/models/survival/workbench.glb", Vector3(-0.7, 0.2, 0.1), 3.2)
	m.add_model("res://assets/models/survival/workbench-grind.glb", Vector3(0.8, 0.2, 0.2), 3.2)
	m.add_model("res://assets/models/furniture/chair.glb", Vector3(0.9, 0.2, -1.0), 2.2, 30)
	var saw := m.add_saw_blade(Vector3(0.8, 1.05, 0.35), 0.3)
	saw.rotation_degrees.y = 90
	m.mouth_in = Vector3(-0.8, 1.1, 0.2)
	m.mouth_out = Vector3(1.0, 1.0, 0.2)
	m.add_dust(Vector3(0, 1.1, 0.3), Color(0.9, 0.75, 0.5))
	m.add_blocker(Vector3(3.6, 2.2, 2.6))
	add_child(m)
	plazas.append(Vector4(2, -13, 4.3, 2.0))
	if animate:
		Fx.pop_in(m, 0.7)


func _build_cnc(animate: bool) -> void:
	var m := _machine("cnc", Vector3(9, 0, -24), "plank", "table", 3, 1, 1.6)
	_box(m.body, Vector3(3.8, 0.2, 2.8), Vector3(0, 0.1, 0), _mat(Color(0.55, 0.57, 0.58), 0.7))
	m.add_model("res://assets/models/factory/machine-window.glb", Vector3(0, 0.2, 0), 1.7, 90)
	m.add_model("res://assets/models/factory/screen-small.glb", Vector3(-1.2, 0.2, -1.0), 1.3)
	var cog := m.add_model("res://assets/models/factory/cog-a.glb", Vector3(0, 2.45, 0), 0.9)
	cog.rotation_degrees.x = 0
	m.spinners.append(cog)
	m.add_model("res://assets/models/factory/lever-single.glb", Vector3(1.3, 0.2, -0.9), 1.4)
	m.mouth_in = Vector3(-1.1, 1.0, 0)
	m.mouth_out = Vector3(1.1, 0.8, 0)
	m.add_dust(Vector3(0, 1.4, 0.8), Color(0.95, 0.85, 0.65))
	m.add_blocker(Vector3(3.0, 2.2, 2.6))
	add_child(m)
	plazas.append(Vector4(9, -24, 4.3, 2.0))
	paths.append([Vector4(0, -24, 9, -24), 0.7])
	if animate:
		Fx.pop_in(m, 0.7)


func _build_factory(animate: bool) -> void:
	var m := _machine("factory", Vector3(0, 0, -36), "log", "bookcase", 3, 1, 1.8)
	m.input.position = Vector3(-3.6, 0, 0.3)
	m.in_zone.position = m.input.position
	m.output.position = Vector3(3.6, 0, 0.3)
	m.out_zone.position = m.output.position
	_box(m.body, Vector3(5.4, 0.22, 3.6), Vector3(0, 0.11, 0), _mat(Color(0.6, 0.6, 0.6), 0.8))
	m.add_model("res://assets/models/factory/machine-fortified.glb", Vector3(-1.1, 0.22, -0.4), 1.9, 90)
	m.add_model("res://assets/models/factory/machine.glb", Vector3(1.3, 0.22, -0.4), 1.9, 90)
	m.add_model("res://assets/models/factory/hopper-square.glb", Vector3(-2.3, 0.22, -0.6), 1.2)
	var arm1 := m.add_model("res://assets/models/factory/robot-arm-a.glb", Vector3(-2.3, 0.22, 1.2), 0.9)
	var arm2 := m.add_model("res://assets/models/factory/robot-arm-b.glb", Vector3(2.4, 0.22, 1.2), 0.9)
	m.arms.append(arm1)
	m.arms.append(arm2)
	var chimney := m.add_model("res://assets/models/factory/structure-yellow-tall.glb", Vector3(-1.9, 0.22, -1.5), 1.6)
	chimney.name = "chimney"
	m.add_smoke(Vector3(-1.9, 3.6, -1.5))
	m.mouth_in = Vector3(-2.2, 1.4, -0.4)
	m.mouth_out = Vector3(2.2, 0.9, 0.4)
	m.add_blocker(Vector3(5.0, 2.4, 3.2))
	add_child(m)
	plazas.append(Vector4(0, -36, 5.6, 2.6))
	if animate:
		Fx.pop_in(m, 0.8)


func _build_lodge(animate: bool) -> void:
	var root := Node3D.new()
	root.position = Vector3(-12, 0, -39)
	add_child(root)
	var log_mat := _mat(Color(0.62, 0.4, 0.24), 0.85)
	var end_mat := _mat(Color(0.86, 0.68, 0.45), 0.8)
	var w := 7.0
	var d := 5.0
	var h := 3.2
	var r := 0.22
	var rows := int(h / (r * 1.8))
	for i in rows:
		var y := r + i * r * 1.8
		for side in [-1, 1]:
			var lg := MeshInstance3D.new()
			var cm := CylinderMesh.new()
			cm.top_radius = r
			cm.bottom_radius = r
			cm.height = w + 0.5
			cm.radial_segments = 10
			lg.mesh = cm
			lg.material_override = log_mat
			lg.rotation_degrees.z = 90
			lg.position = Vector3(0, y, side * d * 0.5)
			root.add_child(lg)
			var lg2 := MeshInstance3D.new()
			var cm2 := cm.duplicate() as CylinderMesh
			cm2.height = d + 0.5
			lg2.mesh = cm2
			lg2.material_override = log_mat
			lg2.rotation_degrees.x = 90
			lg2.position = Vector3(side * w * 0.5, y + r * 0.9, 0)
			root.add_child(lg2)
	for sx in [-1, 1]:
		for sz in [-1, 1]:
			var cap := MeshInstance3D.new()
			var cyl := CylinderMesh.new()
			cyl.top_radius = r * 1.05
			cyl.bottom_radius = r * 1.05
			cyl.height = h + 0.3
			cap.mesh = cyl
			cap.material_override = end_mat
			cap.position = Vector3(sx * w * 0.5, (h + 0.3) * 0.5, sz * d * 0.5)
			root.add_child(cap)
	var roof := ShaderMaterial.new()
	roof.shader = ROOF_SHADER
	roof.set_shader_parameter("base", Color(0.62, 0.24, 0.18))
	var slope := 32.0
	var half_d := d * 0.5 + 0.7
	var panel := half_d / cos(deg_to_rad(slope))
	var rise := half_d * tan(deg_to_rad(slope))
	_box(root, Vector3(w + 1.2, 0.25, panel), Vector3(0, h + rise * 0.5 + 0.1, -half_d * 0.5), roof, Vector3(slope, 0, 0))
	_box(root, Vector3(w + 1.2, 0.25, panel), Vector3(0, h + rise * 0.5 + 0.1, half_d * 0.5), roof, Vector3(-slope, 0, 0))
	_box(root, Vector3(w - 0.2, rise, 0.3), Vector3(0, h + rise * 0.35, d * 0.5 - 0.2), log_mat)
	_box(root, Vector3(w - 0.2, rise, 0.3), Vector3(0, h + rise * 0.35, -d * 0.5 + 0.2), log_mat)
	_box(root, Vector3(0.9, 2.6, 0.9), Vector3(2.2, h + rise * 0.8, -0.8), _mat(Color(0.55, 0.53, 0.5), 0.9))
	var glow := StandardMaterial3D.new()
	glow.albedo_color = Color(1.0, 0.85, 0.5)
	glow.emission_enabled = true
	glow.emission = Color(1.0, 0.7, 0.3)
	glow.emission_energy_multiplier = 1.6
	for x in [-2.4, 2.4]:
		_box(root, Vector3(1.0, 0.9, 0.1), Vector3(x, 1.7, d * 0.5 + r + 0.02), glow)
	_box(root, Vector3(1.1, 2.0, 0.12), Vector3(0, 1.0, d * 0.5 + r + 0.02), _mat(Color(0.4, 0.25, 0.15)))
	_box(root, Vector3(w + 1.6, 0.25, 1.8), Vector3(0, 0.12, d * 0.5 + 1.1), _mat(Color(0.7, 0.5, 0.3)))
	_model("res://assets/models/furniture/bench.glb", Vector3(-2.6, 0.25, d * 0.5 + 1.2), 2.4, 0, root)
	_model("res://assets/models/furniture/loungeChair.glb", Vector3(2.0, 0.25, d * 0.5 + 0.8), 2.2, 180, root)
	var smoke := CPUParticles3D.new()
	root.add_child(smoke)
	smoke.position = Vector3(2.2, h + rise + 1.5, -0.8)
	smoke.amount = 10
	smoke.lifetime = 3.5
	smoke.direction = Vector3(0.2, 1, 0)
	smoke.initial_velocity_min = 0.6
	smoke.initial_velocity_max = 1.0
	smoke.gravity = Vector3(0.3, 0.1, 0)
	var sm := SphereMesh.new()
	sm.radius = 0.3
	sm.height = 0.6
	var smat := StandardMaterial3D.new()
	smat.albedo_color = Color(0.9, 0.9, 0.9, 0.5)
	smat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	sm.material = smat
	smoke.mesh = sm
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(w + 0.4, 4, d + 0.4)
	col.shape = bs
	col.position.y = 2
	sb.add_child(col)
	root.add_child(sb)
	plazas.append(Vector4(-12, -37.5, 5.0, 4.0))
	if animate:
		Fx.pop_in(root, 1.0)


# ---------------------------------------------------------------- pads + camera

func _refresh_pads() -> void:
	for u in UNLOCKS:
		var id: String = u.id
		if Game.is_unlocked(id) or pads.has(id):
			continue
		var ok := true
		for r in u.req:
			if not Game.is_unlocked(r):
				ok = false
		if not ok:
			continue
		var big: bool = id in ["carpentry", "sawmill2", "cnc", "factory", "dock", "lodge", "office"]
		var pad := UnlockPad.new().setup(id, u.cost, u.title, Vector2(3.2, 3.2) if big else Vector2(2.4, 2.4))
		pad.position = u.pad
		add_child(pad)
		pad.paid.connect(func(pid: String) -> void: Game.unlock(pid))
		pads[id] = pad
		if not _loading:
			Fx.pop_in(pad, 0.5)


func _on_unlocked(id: String) -> void:
	if pads.has(id):
		var pad: UnlockPad = pads[id]
		if is_instance_valid(pad) and not pad.is_queued_for_deletion() and pad.paid_amount < pad.cost:
			pad.queue_free()
		pads.erase(id)
	_apply_unlock(id, true)
	var title := id
	for u in UNLOCKS:
		if u.id == id:
			title = u.title
	if Game.hud:
		Game.hud.toast(title + "!")
	_refresh_pads()
	if id == "lodge":
		Game.finished = true
		Game.save_game()
		for i in 6:
			get_tree().create_timer(0.3 * i).timeout.connect(func() -> void:
				Fx.confetti(self, Vector3(-12 + randf_range(-4, 4), 5, -39 + randf_range(-3, 3))))
		if Game.hud:
			Game.hud.show_finish()


func _camera() -> void:
	camera = Camera3D.new()
	camera.fov = 52.0
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	camera.near = 0.5
	camera.far = 160.0
	add_child(camera)
	_cam_pos = player.global_position
	_place_camera(1.0)
	camera.current = true


func _place_camera(t: float) -> void:
	var vp := get_viewport().get_visible_rect().size
	var portrait := vp.y > vp.x
	camera.keep_aspect = Camera3D.KEEP_WIDTH if portrait else Camera3D.KEEP_HEIGHT
	camera.fov = 45.0 if portrait else 36.0
	_cam_pos = _cam_pos.lerp(player.global_position, t)
	var offset := Vector3(0, 8.4, 6.6)
	camera.global_position = _cam_pos + offset
	camera.look_at(_cam_pos + Vector3(0, 0.6, 0), Vector3.UP)


func _guide_arrow() -> void:
	guide = MeshInstance3D.new()
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var pts := [Vector3(0, 0, -0.55), Vector3(0.38, 0, 0.1), Vector3(0.14, 0, 0.1), Vector3(0.14, 0, 0.45), Vector3(-0.14, 0, 0.45), Vector3(-0.14, 0, 0.1), Vector3(-0.38, 0, 0.1)]
	for tri in [[0, 1, 6], [2, 3, 4], [2, 4, 5]]:
		for i in tri:
			st.set_normal(Vector3.UP)
			st.add_vertex(pts[i])
	guide.mesh = st.commit()
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(1.0, 0.85, 0.25, 0.9)
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	guide.material_override = m
	guide.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(guide)


## Where the guide arrow should point, plus a hint line. Beginners get step-by-step help.
func _goal() -> Array:
	var p := player.global_position
	var back := player.stack
	var saw: Machine = machines.sawmill1
	var tutorial := not Game.is_unlocked("jack1")
	var cheapest: UnlockPad = null
	for id in pads:
		var pad: UnlockPad = pads[id]
		if cheapest == null or pad.cost - pad.paid_amount < cheapest.cost - cheapest.paid_amount:
			cheapest = pad
	if cheapest and Game.money >= cheapest.cost - cheapest.paid_amount:
		return [cheapest.global_position, "Buy %s!" % cheapest.title if tutorial else ""]
	if not tutorial:
		return [null, ""]
	if shop.coin_value > 0 and back.is_empty():
		return [shop.coin_zone.global_position, "Collect your cash"]
	if back.top_type() == "log" and saw.in_zone.contains(p):
		return [saw.in_zone.global_position, "Bring logs to the sawmill"]
	if back.top_type() == "log":
		if back.count() >= player.capacity() or _nearest_tree(p) == null or back.count() >= 6:
			return [saw.in_zone.global_position, "Bring logs to the sawmill"]
		return [_nearest_tree(p).global_position, "Chop trees: just walk up to one"]
	if back.top_type() == "plank":
		if saw.out_zone.contains(p) and not saw.output.is_empty() and back.count() < player.capacity():
			return [saw.out_zone.global_position, "Pick up the planks"]
		return [shop.shelf_zone("plank").global_position, "Put planks on the counter"]
	if saw.output.count() >= 4:
		return [saw.out_zone.global_position, "Pick up the planks"]
	var t := _nearest_tree(p)
	if t:
		return [t.global_position, "Chop trees: just walk up to one"]
	return [null, ""]


func _nearest_tree(p: Vector3) -> ChopTree:
	var best: ChopTree = null
	var bd := INF
	for t in forests.a:
		var tree: ChopTree = t
		if tree.is_ready():
			var d := tree.global_position.distance_squared_to(p)
			if d < bd:
				bd = d
				best = tree
	return best


func _process(delta: float) -> void:
	_place_camera(1.0 - exp(-6.0 * delta))
	var g := _goal()
	var target = g[0]
	if Game.hud:
		Game.hud.set_hint(g[1])
	if target == null:
		guide.visible = false
		return
	var p := player.global_position
	var dir: Vector3 = (target as Vector3) - p
	dir.y = 0
	var dist := dir.length()
	guide.visible = dist > 2.4
	if guide.visible:
		dir /= dist
		guide.global_position = p + dir * 1.35 + Vector3(0, 0.06, 0)
		guide.rotation.y = atan2(-dir.x, -dir.z)
		var s := 1.0 + sin(Time.get_ticks_msec() / 150.0) * 0.08
		guide.scale = Vector3.ONE * s
