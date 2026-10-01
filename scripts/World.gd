class_name World
extends Node3D

## Builds the valley: lighting, ground, river, forests, buildings, unlock pads and the camera.

const ROAD_X := 17.0
const GROUND_SHADER := preload("res://scripts/ground.gdshader")
const WATER_SHADER := preload("res://scripts/water.gdshader")
const ROOF_SHADER := preload("res://scripts/roof.gdshader")
const IMPOSTER_SHADER := preload("res://scripts/imposter.gdshader")
const RIVER_X := -27.0
const RIVER_HALF := 3.2
## Scenery MultiMeshes are split into square chunks of this size (m) so off-screen ones cull.
const CHUNK_SIZE := 16.0
## Chunks further than this from the camera are hidden (m).
const CHUNK_VIS_END := 60.0

## Pads live in Balance.UNLOCKS (kept here as an alias for older callers).
const UNLOCKS := Balance.UNLOCKS
## Border-forest imposter atlas: kind order = border_trees_atlas.json, cell = kind_index * 4 + facing.
const IMPOSTER_KINDS := [
	"tree_pineTallA_detailed", "tree_pineTallB_detailed", "tree_pineTallC_detailed", "tree_pineTallD_detailed",
	"tree_pineRoundA", "tree_pineRoundC", "tree_default_dark", "tree_default", "tree_detailed", "tree_oak",
	"tree_fat", "tree_pineDefaultB", "tree_birchA", "tree_birchB", "tree_birchC",
]
## false = the old chunked _far meshes (fallback).
const USE_IMPOSTERS := true
## Birch Bend layout (world coords, GDD 9.2; nudged off paths where noted).
const V2_GROVE1 := Vector3(-55, 0, -2)
const V2_GROVE2 := Vector3(-55, 0, 6)
const V2_GROVE_NORTH := Vector3(-62, 0, -31)
const V2_GROVE_WEST := Vector3(-71, 0, -20)
const V2_MARKET := Vector3(-40, 0, 6)
const V2_LATHE := Vector3(-45, 0, -6)
const V2_PRESS := Vector3(-45, 0, -18)
const V2_PRESS2 := Vector3(-45, 0, -28)
const V2_BOATSHOP := Vector3(-41.5, 0, -38)
const V2_BARGE := Vector3(-33, 0, -36)
const V2_OFFICE := Vector3(-34, 0, 10.2)
const V2_BOATHOUSE := Vector3(-68, 0, 6)
## Flume: hopper (the DROP square) and the water route to the lathe input pile.
const V2_CHUTE := Vector3(-60.7, 0, -24)
const V2_FLUME_PTS := [Vector3(-60.7, 0, -24), Vector3(-51.5, 0, -24), Vector3(-51.5, 0, -6), Vector3(-48.0, 0, -6)]
## Opening in the river walls for the bridge (z range).
const BRIDGE_Z := -6.0
const BRIDGE_HALF := 1.3
## Offline earnings coin pile next to the Valley 1 office.
const OFFLINE_PILE := Vector3(-0.6, 0, 11.0)

var rng := RandomNumberGenerator.new()
var shop: Shop
var machines: Dictionary = {}
var forests: Dictionary = {"a": [], "pine": [], "birch": [], "birch_north": [], "birch_west": []}
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
## Valleys by id. Everything a valley owns is a child of its Region (sleep/wake, GDD 10).
var regions: Dictionary = {}
var r1: Region
var r2: Region
## Per-valley ground: {"mat": ShaderMaterial, "paths": [], "plazas": []}. paths/plazas above = Valley 1's.
var grounds: Dictionary = {}
## Future belts, flume and buildings in Birch Bend: kept clear of grass and rocks.
var _reserved_lines: Array = []
var _reserved_rects: Array = []
## Valley 2 content uses its own seed so Valley 1's layout does not shift with V2 progress.
var rng2 := RandomNumberGenerator.new()
var shop2: Shop
var office2_zone: Zone
var flume_chute: ItemStack
var flume_zone: Zone
var _belt_lp: Conveyor
var _gate_body: StaticBody3D
var _gate_prop: Node3D
var _offline_zone: Zone
var _offline_pile: ItemStack
var _offline_label: Label3D
var _cur_region: int = 1
## Camera offset from the focus point (GDD 10: unchanged at (0, 8.4, 6.6)).
var cam_offset: Vector3 = Vector3(0, 8.4, 6.6)
var _chip_timer: float = 0.0


func _ready() -> void:
	Game.world = self
	rng.seed = 20260929
	rng2.seed = 20261001
	_environment()
	_make_regions()
	_ground()
	_river()
	_road()
	_base_paths()
	_reserve_v2()
	_border_forest()
	_build_forest("a", Vector3(-9, 0, 1.0), 3, 2, 2.5, "broad")
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
	_scatter_deco_v2()
	_update_ground_uniforms()
	_bounds()
	_palisades()
	_palisades_v2()
	_build_offline_pile()
	_update_regions(0.0, true)
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
	env.ambient_light_energy = 0.9
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
	env.adjustment_saturation = 1.1
	env.adjustment_contrast = 1.06
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52, -38, 0)
	sun.light_color = Color(1.0, 0.93, 0.8)
	sun.light_energy = 1.45
	sun.shadow_enabled = true
	sun.shadow_blur = 2.0
	sun.shadow_bias = 0.04
	sun.shadow_normal_bias = 1.2
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_2_SPLITS
	sun.directional_shadow_max_distance = 30.0
	sun.directional_shadow_blend_splits = true
	sun.shadow_opacity = 0.85
	add_child(sun)


func _make_regions() -> void:
	for rid in Balance.REGIONS:
		var r := Region.new().setup(int(rid))
		add_child(r)
		regions[int(rid)] = r
	r1 = regions[1]
	r2 = regions[2]


## One ground plane and material per valley (the shader holds 32 paths and 24 plazas each).
## Valley 1 covers x > river centre, Birch Bend x < river centre; the river hides the seam.
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
	var planes := {1: [RIVER_X, 80.0], 2: [-110.0, RIVER_X]}
	for rid in planes:
		var mat := ShaderMaterial.new()
		mat.shader = GROUND_SHADER
		mat.set_shader_parameter("noise_tex", _noise_tex)
		mat.set_shader_parameter("detail_tex", detail)
		mat.set_shader_parameter("river_x", RIVER_X)
		mat.set_shader_parameter("river_half", RIVER_HALF)
		mat.set_shader_parameter("grass_tex", load(Models.GROUND[rid]))
		mat.set_shader_parameter("dirt_tex", load(Models.GROUND["dirt"]))
		var mi := MeshInstance3D.new()
		var pm := PlaneMesh.new()
		var x0: float = planes[rid][0]
		var x1: float = planes[rid][1]
		pm.size = Vector2(x1 - x0, 170)
		pm.subdivide_width = 2
		pm.subdivide_depth = 2
		mi.mesh = pm
		mi.material_override = mat
		mi.position = Vector3((x0 + x1) * 0.5, 0, -15)
		add_child(mi)
		grounds[rid] = {"mat": mat, "paths": [], "plazas": []}
	ground_mat = grounds[1].mat
	paths = grounds[1].paths
	plazas = grounds[1].plazas
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
	mi.position = Vector3(ROAD_X, 0.03, -15)
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)
	var line_mat := StandardMaterial3D.new()
	line_mat.albedo_color = Color(0.95, 0.9, 0.7)
	for i in 40:
		var dash := MeshInstance3D.new()
		var dm := PlaneMesh.new()
		dm.size = Vector2(0.14, 1.4)
		dash.mesh = dm
		dash.material_override = line_mat
		dash.position = Vector3(ROAD_X, 0.05, 60 - i * 4.0)
		dash.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
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
	var bank_e := RIVER_X + RIVER_HALF + 0.3
	var bank_w := RIVER_X - RIVER_HALF - 0.3
	var z0 := BRIDGE_Z - BRIDGE_HALF
	var z1 := BRIDGE_Z + BRIDGE_HALF
	# Both river banks are walls except at the bridge; the corridor walls keep you on the bridge.
	for x in [bank_e, bank_w]:
		_wall(Vector2(x, 70), Vector2(x, z1))
		_wall(Vector2(x, z0), Vector2(x, -100))
	_wall(Vector2(bank_w, z0 - 0.1), Vector2(bank_e, z0 - 0.1))
	_wall(Vector2(bank_w, z1 + 0.1), Vector2(bank_e, z1 + 0.1))
	_wall(Vector2(ROAD_X + 2.2, 70), Vector2(ROAD_X + 2.2, -100))
	_wall(Vector2(-80, 15.5), Vector2(40, 15.5))
	_wall(Vector2(-80, -47), Vector2(40, -47))
	_wall(Vector2(-79.3, 20), Vector2(-79.3, -50))
	# Closed gate in the Valley 1 bank until the River Bridge is bought.
	if not Game.is_unlocked("r2_bridge"):
		_gate_body = _wall(Vector2(bank_e, z0), Vector2(bank_e, z1))


func _wall(a: Vector2, b: Vector2) -> StaticBody3D:
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(maxf(absf(b.x - a.x), 1.0), 2, maxf(absf(b.y - a.y), 1.0))
	col.shape = bs
	sb.position = Vector3((a.x + b.x) * 0.5, 1, (a.y + b.y) * 0.5)
	sb.add_child(col)
	add_child(sb)
	return sb


func _update_ground_uniforms() -> void:
	for rid in grounds:
		var g: Dictionary = grounds[rid]
		var mat: ShaderMaterial = g.mat
		var ps: Array[Vector4] = []
		var ws: Array[float] = []
		for p in g.paths:
			ps.append(p[0])
			ws.append(p[1])
		while ps.size() < 32:
			ps.append(Vector4.ZERO)
			ws.append(-10.0)
		mat.set_shader_parameter("paths", ps)
		mat.set_shader_parameter("path_widths", PackedFloat32Array(ws))
		mat.set_shader_parameter("path_count", mini(g.paths.size(), 32))
		var pl: Array[Vector4] = []
		for p in g.plazas:
			pl.append(p)
		while pl.size() < 24:
			pl.append(Vector4(9999, 9999, 0, 0))
		mat.set_shader_parameter("plazas", pl)
		mat.set_shader_parameter("plaza_count", mini(g.plazas.size(), 24))


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


func _multimesh(path: String, xforms: Array, shadows: bool = true, parent: Node3D = null) -> void:
	if xforms.is_empty():
		return
	var mm_info := _first_mesh(path)
	if mm_info.is_empty():
		return
	# Godot culls a MultiMesh only as a whole, so bucket instances into CHUNK_SIZE squares.
	var chunks := {}
	for x in xforms:
		var xf: Transform3D = x
		var key := Vector2i(floori(xf.origin.x / CHUNK_SIZE), floori(xf.origin.z / CHUNK_SIZE))
		if not chunks.has(key):
			chunks[key] = []
		(chunks[key] as Array).append(xf)
	var mesh: Mesh = mm_info[0]
	var local: Transform3D = mm_info[1]
	var mesh_aabb := mesh.get_aabb()
	for key in chunks:
		var list: Array = chunks[key]
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.mesh = mesh
		mm.instance_count = list.size()
		var box := AABB()
		for i in list.size():
			var t: Transform3D = (list[i] as Transform3D) * local
			mm.set_instance_transform(i, t)
			var b := t * mesh_aabb
			box = b if i == 0 else box.merge(b)
		mm.custom_aabb = box
		var mmi := MultiMeshInstance3D.new()
		mmi.multimesh = mm
		mmi.visibility_range_end = CHUNK_VIS_END
		mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if shadows else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		(parent if parent else self).add_child(mmi)


func _busy(p: Vector2, margin: float) -> bool:
	var lines: Array = _reserved_lines.duplicate()
	var rects: Array = _reserved_rects.duplicate()
	for rid in grounds:
		lines.append_array(grounds[rid].paths)
		rects.append_array(grounds[rid].plazas)
	for pa in lines:
		var s: Vector4 = pa[0]
		var a := Vector2(s.x, s.y)
		var b := Vector2(s.z, s.w)
		var ab := b - a
		var t := clampf((p - a).dot(ab) / maxf(ab.length_squared(), 0.0001), 0.0, 1.0)
		if p.distance_to(a + ab * t) < float(pa[1]) + margin:
			return true
	for pl in rects:
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
	var birches := ["tree_birchA", "tree_birchB", "tree_birchC"]
	var buckets := {}
	for k in kinds + birches:
		buckets[k] = []
	# Outer edges of the two-valley map plus the strip inside Valley 1's west palisade.
	var areas := [
		Rect2(-101, 18, 161, 16),
		Rect2(-101, -66, 161, 18),
		Rect2(-101, -48, 21, 66),
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
			# Keep the way to the River Bridge open.
			if p.x > RIVER_X and p.x < -15.0 and absf(p.y - BRIDGE_Z) < 3.4:
				continue
			var k: String = kinds[rng.randi() % kinds.size()]
			# Birch Bend's edges are half birch.
			if p.x < RIVER_X and rng.randf() < 0.5:
				k = birches[rng.randi() % birches.size()]
			var s := rng.randf_range(2.4, 3.6)
			var xf := Transform3D(Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3.ONE * s), Vector3(p.x, 0, p.y))
			(buckets[k] as Array).append(xf)
	if USE_IMPOSTERS:
		_imposters(buckets)
		return
	for k in buckets:
		var dir := "birch" if k.begins_with("tree_birch") else "nature"
		_multimesh("res://assets/models_v3/%s/%s_far.glb" % [dir, k], buckets[k])


## Camera-facing cards from one atlas (ASSETS_M1.md section 5): one MultiMesh per 16 m chunk,
## no Y rotation (the four facings give the variety), no shadows.
func _imposters(buckets: Dictionary) -> void:
	var w := 256.0 / 140.0
	var bottom := -(256.0 - 246.0) / 256.0 * w
	var tilt := Basis(Vector3.RIGHT, deg_to_rad(-52.0))
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var corners := [
		[Vector3(-w * 0.5, bottom + w, 0), Vector2(0, 0)], [Vector3(w * 0.5, bottom + w, 0), Vector2(1, 0)],
		[Vector3(w * 0.5, bottom, 0), Vector2(1, 1)], [Vector3(-w * 0.5, bottom, 0), Vector2(0, 1)],
	]
	for i in [0, 1, 2, 0, 2, 3]:
		st.set_normal(Vector3.UP)
		st.set_uv(corners[i][1])
		st.add_vertex(tilt * (corners[i][0] as Vector3))
	var card := st.commit()
	var mat := ShaderMaterial.new()
	mat.shader = IMPOSTER_SHADER
	mat.set_shader_parameter("atlas", load(Models.IMPOSTER_ATLAS))
	var chunks := {}
	for k in buckets:
		var base: int = IMPOSTER_KINDS.find(k) * 4
		for x in buckets[k]:
			var xf: Transform3D = x
			# Drop the random yaw: cards must face the camera. Keep the scale.
			var sc := xf.basis.get_scale().x
			var key := Vector2i(floori(xf.origin.x / CHUNK_SIZE), floori(xf.origin.z / CHUNK_SIZE))
			if not chunks.has(key):
				chunks[key] = []
			(chunks[key] as Array).append([Transform3D(Basis().scaled(Vector3.ONE * sc), xf.origin), base + rng.randi() % 4])
	var aabb := card.get_aabb()
	for key in chunks:
		var list: Array = chunks[key]
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_custom_data = true
		mm.mesh = card
		mm.instance_count = list.size()
		var box := AABB()
		for i in list.size():
			var t: Transform3D = list[i][0]
			mm.set_instance_transform(i, t)
			mm.set_instance_custom_data(i, Color(float(list[i][1]) / 255.0, 0, 0, 0))
			var b := t * aabb
			box = b if i == 0 else box.merge(b)
		mm.custom_aabb = box
		var mmi := MultiMeshInstance3D.new()
		mmi.multimesh = mm
		mmi.material_override = mat
		mmi.visibility_range_end = CHUNK_VIS_END
		mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(mmi)


func _scatter_deco() -> void:
	var sets := [
		["grass", 260, 2.4, false], ["grass_large", 160, 2.4, false], ["grass_leafs", 110, 2.6, false],
		["flower_redA", 110, 2.6, false], ["flower_yellowA", 120, 2.6, false], ["flower_yellowB", 60, 2.4, false],
		["flower_redC", 50, 2.4, false], ["plant_bush", 110, 2.8, true], ["plant_bushDetailed", 90, 2.6, true],
		["rock_smallA", 40, 2.2, false], ["rock_smallC", 40, 2.2, false], ["mushroom_redGroup", 25, 2.2, false],
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
		_multimesh("res://assets/models_v3/nature/%s.glb" % s[0], list, s[3])
	# Tall rocks and reeds on the river banks.
	var rocks := []
	for i in 26:
		var z := rng.randf_range(-60, 20)
		var side := -1.0 if rng.randf() < 0.5 else 1.0
		var x := RIVER_X + side * (RIVER_HALF + rng.randf_range(0.2, 0.9))
		rocks.append(Transform3D(Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3.ONE * rng.randf_range(1.6, 2.6)), Vector3(x, -0.05, z)))
	_multimesh("res://assets/models_v3/nature/rock_smallD.glb", rocks, false)
	# A few props around the starting yard.
	_model("res://assets/models_v3/nature/log_stackLarge.glb", Vector3(-3.6, 0, -6.8), 2.2, 10, r1)
	_model("res://assets/models_v3/survival/barrel.glb", Vector3(3.8, 0, -6.4), 2.4, 0, r1)
	_model("res://assets/models_v3/survival/box-large.glb", Vector3(4.6, 0, -6.6), 2.2, 20, r1)
	_model("res://assets/models_v3/survival/signpost.glb", Vector3(1.4, 0, 6.0), 2.6, -20, r1)
	_model("res://assets/models_v3/nature/campfire_logs.glb", Vector3(-4.5, 0, 12.5), 3.0, 0, r1)
	for i in 6:
		_model("res://assets/models_v3/nature/fence_simple.glb", Vector3(-12.5 + i * 2.0, 0, 13.5), 2.0, 0, r1)


func _build_forest(key: String, center: Vector3, cols: int, rows: int, spacing: float, kind: String, animate: bool = false, region: int = 1) -> void:
	var g := rng if region == 1 else rng2
	for r in rows:
		for c in cols:
			var p := center + Vector3((c - (cols - 1) * 0.5) * spacing, 0, (r - (rows - 1) * 0.5) * spacing)
			p += Vector3(g.randf_range(-0.35, 0.35), 0, g.randf_range(-0.35, 0.35))
			var t := ChopTree.new().setup(kind, g)
			t.position = p
			(regions[region] as Region).add_child(t)
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
	r1.add_child(m)


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
		[Vector2(-23.2, 15.3), Vector2(-23.2, BRIDGE_Z + BRIDGE_HALF)],
		[Vector2(-23.2, BRIDGE_Z - BRIDGE_HALF), Vector2(-23.2, -46.6)],
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
	r1.add_child(mmi)
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(0.4, 2, 11)
	col.shape = bs
	sb.position = Vector3(-13.3, 1, 4)
	sb.add_child(col)
	r1.add_child(sb)


func _build_shop() -> void:
	shop = Shop.new().setup()
	shop.position = Vector3(10, 0, 4)
	shop.road_x = ROAD_X - 10.0
	shop.region_node = r1
	shop.add_shelf("plank", 2.6)
	shop.add_shelf("chair", 0.0)
	shop.add_shelf("table", -2.6)
	r1.add_child(shop)
	shop.open_shelf("plank", false)


func _spawn_lumberjack(look: String, forest: Array, m: Machine, home: Vector3, animate: bool) -> void:
	_spawn_jack_to(look, forest, m.input, m.in_zone.global_position, home, animate, 1)


## Lumberjack that delivers to any pile (a machine input or the flume chute).
func _spawn_jack_to(look: String, forest: Array, dst: ItemStack, dst_pos: Vector3, home: Vector3, animate: bool, region: int) -> void:
	var w := Worker.new().as_lumberjack(look, forest, dst, dst_pos, home)
	w.region = region
	(regions[region] as Region).add_child(w)
	if animate:
		Fx.pop_in(w)


func _spawn_hauler(look: String, src: ItemStack, src_zone: Zone, dst: ItemStack, dst_zone: Zone, animate: bool, region: int = 1) -> void:
	var w := Worker.new().as_hauler(look, src, src_zone.global_position, dst, dst_zone.global_position)
	w.region = region
	(regions[region] as Region).add_child(w)
	if animate:
		Fx.pop_in(w)


func _apply_unlock(id: String, animate: bool) -> void:
	if id.begins_with("r2_"):
		_apply_unlock_r2(id, animate)
		if not _loading:
			_update_ground_uniforms()
		return
	match id:
		"trees2":
			_build_forest("a", Vector3(-9, 0, 6.2), 3, 2, 2.5, "broad", animate)
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
			_build_forest("pine", Vector3(-13.5, 0, -15), 4, 3, 2.6, "pine", animate)
			paths.append([Vector4(0, -12, -9, -14), 0.7])
		"cashier":
			shop.hire_cashier(animate)
		"sawmill2":
			var m := _machine("sawmill2", Vector3(-3, 0, -24), "log", "plank", 1, 2, 0.8)
			_dress_sawmill(m, Color(0.3, 0.75, 0.3))
			r1.add_child(m)
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
			r1.add_child(c)
			if animate:
				Fx.pop_in(c, 0.6)
		"hauler4":
			_spawn_hauler("character-female-b", machines.cnc.output, machines.cnc.out_zone, shop.shelf("table"), shop.shelf_zone("table"), animate)
		"factory":
			_build_factory(animate)
		"jack3":
			forests["north"] = []
			_build_forest("north", Vector3(-13.5, 0, -31), 4, 2, 2.6, "pine", animate)
			_spawn_lumberjack("character-male-a", forests.north, machines.factory, Vector3(-8, 0, -30), animate)
			_spawn_lumberjack("character-female-a", forests.north, machines.factory, Vector3(-8, 0, -32), animate)
		"dock":
			var d := TruckDock.new().setup("bookcase", ROAD_X)
			d.region_node = r1
			d.position = Vector3(13.5, 0, -36)
			r1.add_child(d)
			machines["dock"] = d
			plazas.append(Vector4(13.5, -36, 2.6, 3.0))
			paths.append([Vector4(3, -36, 12, -36), 0.8])
			if animate:
				Fx.pop_in(d, 0.6)
		"conveyor2":
			var d: TruckDock = machines.dock
			var c := Conveyor.new().setup(machines.factory.output, d.pile, PackedVector3Array([
				Vector3(3.9, 0, -37.8), Vector3(14.4, 0, -37.8), Vector3(14.4, 0, -36.6)]))
			r1.add_child(c)
			if animate:
				Fx.pop_in(c, 0.6)
		"roadsign":
			var sg := Node3D.new()
			sg.position = Vector3(15.0, 0, 10.5)
			r1.add_child(sg)
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
			r1.add_child(ms)
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


func _belt(src: ItemStack, dst: ItemStack, pts: Array, animate: bool, region: int = 1) -> Conveyor:
	var c := Conveyor.new()
	c.region = region
	c.setup(src, dst, PackedVector3Array(pts))
	(regions[region] as Region).add_child(c)
	if animate:
		Fx.pop_in(c, 0.6)
	return c


func _build_office(animate: bool) -> void:
	var root := Node3D.new()
	root.position = Vector3(-3.5, 0, 12.5)
	r1.add_child(root)
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
	r1.add_child(office_zone)
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
	r1.add_child(m)
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
	r1.add_child(m)
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
	r1.add_child(m)
	plazas.append(Vector4(0, -36, 5.6, 2.6))
	if animate:
		Fx.pop_in(m, 0.8)


func _build_lodge(animate: bool) -> void:
	var root := Node3D.new()
	root.position = Vector3(-12, 0, -39)
	r1.add_child(root)
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
		var big: bool = id in Balance.BIG_PADS
		var pad := UnlockPad.new().setup(id, u.cost, u.title, Vector2(3.2, 3.2) if big else Vector2(2.4, 2.4))
		pad.position = u.pad
		_pad_region(id).add_child(pad)
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
	# Landmarks no longer end the game: they show the "Valley complete" card (GDD 6, rule 2).
	if Balance.LANDMARKS.has(id):
		var where: Vector3 = Vector3(-12, 0, -39) if id == "lodge" else V2_BOATHOUSE
		if id == "lodge":
			Game.finished = true
		Game.save_game()
		for i in 6:
			get_tree().create_timer(0.3 * i).timeout.connect(func() -> void:
				Fx.confetti(self, where + Vector3(randf_range(-4, 4), 5, randf_range(-3, 3))))
		if Game.hud:
			var next := "The River Bridge to Birch Bend is ready to build." if id == "lodge" else "Your crews keep working in both valleys, even while you are away."
			Game.hud.show_valley_card(int(Balance.LANDMARKS[id]), next)


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
	camera.global_position = _cam_pos + cam_offset
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
	var v2_tutorial := _cur_region == 2 and not Game.is_unlocked("r2_jack1")
	if cheapest and Game.money >= cheapest.cost - cheapest.paid_amount:
		return [cheapest.global_position, "Buy %s!" % cheapest.title if (tutorial or v2_tutorial) else ""]
	if v2_tutorial:
		return _goal_v2(p)
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


func _nearest_tree(p: Vector3, key: String = "a") -> ChopTree:
	var best: ChopTree = null
	var bd := INF
	for t in forests[key]:
		var tree: ChopTree = t
		if tree.is_ready():
			var d := tree.global_position.distance_squared_to(p)
			if d < bd:
				bd = d
				best = tree
	return best


func _process(delta: float) -> void:
	_place_camera(1.0 - exp(-6.0 * delta))
	_update_regions(delta, false)
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


# ---------------------------------------------------------------- valleys: sleep/wake, chip

## Wake/sleep rules (GDD 10): awake inside rect + 24 m, asleep beyond rect + 30 m, at most 2 awake.
func _update_regions(delta: float, force: bool) -> void:
	var focus := _cam_pos
	var want: Array = []
	for rid in regions:
		var r: Region = regions[rid]
		var d := r.distance_outside(focus)
		var on := d <= Balance.WAKE_MARGIN if (force or not r.awake) else d <= Balance.SLEEP_MARGIN
		if on:
			want.append(r)
	want.sort_custom(func(a: Region, b: Region) -> bool: return a.center().distance_to(focus) < b.center().distance_to(focus))
	want = want.slice(0, Balance.MAX_AWAKE)
	for rid in regions:
		var r: Region = regions[rid]
		r.set_awake(r in want)
		r.tick(delta)
	var cur := _cur_region
	for rid in regions:
		if (regions[rid] as Region).contains_point(player.global_position):
			cur = rid
	if cur != _cur_region:
		_cur_region = cur
		if cur == 2 and float(Game.stats(2).get("time", 0.0)) <= 0.0 and Game.hud:
			Game.hud.toast("Valley 2: Birch Bend")
	var st := Game.stats(_cur_region)
	st["time"] = float(st.get("time", 0.0)) + delta
	_chip_timer -= delta
	if _chip_timer <= 0.0 and Game.hud:
		_chip_timer = 0.5
		Game.hud.set_valley(_valley_chip())


func region_of_unlock(id: String) -> int:
	return 2 if id.begins_with("r2_") else 1


func _valley_chip() -> String:
	var r: Region = regions[_cur_region]
	var own := 0
	var total := 0
	for u in UNLOCKS:
		if region_of_unlock(u.id) == _cur_region:
			total += 1
			if Game.is_unlocked(u.id):
				own += 1
	return "%s %d/%d" % [r.title, own, total]


func current_region() -> int:
	return _cur_region


# ---------------------------------------------------------------- offline earnings

## Offline income waits as a coin pile next to the Valley 1 office; walk over it to collect.
func _build_offline_pile() -> void:
	if Game.offline_pending <= 0:
		return
	_offline_pile = ItemStack.new().setup("coin", 60, 3, 3)
	_offline_pile.position = OFFLINE_PILE
	r1.add_child(_offline_pile)
	for i in clampi(Game.offline_pending / 50, 6, 45):
		_offline_pile.push(Items.make("coin"), false)
	_offline_label = Label3D.new()
	_offline_label.font = Fx.font()
	_offline_label.text = "%s\nwhile away" % Game.fmt(Game.offline_pending)
	_offline_label.font_size = 52
	_offline_label.outline_size = 14
	_offline_label.modulate = Color(1.0, 0.9, 0.35)
	_offline_label.outline_modulate = Color(0.25, 0.15, 0.0, 0.9)
	_offline_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_offline_label.pixel_size = 0.006
	_offline_label.position = OFFLINE_PILE + Vector3(0, 1.7, 0)
	r1.add_child(_offline_label)
	_offline_zone = Zone.new().setup(Zone.Kind.CUSTOM, null, Vector2(2.0, 2.0), "OFFLINE", Color(1.0, 0.85, 0.3))
	_offline_zone.position = OFFLINE_PILE
	_offline_zone.interval = 0.0
	_offline_zone.on_carrier = _collect_offline
	r1.add_child(_offline_zone)


func _collect_offline(carrier: Node, _delta: float) -> bool:
	if not carrier.get("is_player") or Game.offline_pending <= 0:
		return false
	var v := Game.collect_offline()
	var i := 0
	while not _offline_pile.is_empty():
		Fx.fly_to_and_free(_offline_pile.pop(), carrier as Node3D, 0.02 * i)
		i += 1
	Sfx.play("coins", -2.0)
	Fx.float_text(get_tree().current_scene, (carrier as Node3D).global_position + Vector3(0, 2.6, 0), "+" + Game.fmt(v), Color(1.0, 0.85, 0.2), 1.3)
	_offline_zone.queue_free()
	_offline_label.queue_free()
	return true


# ---------------------------------------------------------------- Birch Bend (Valley 2)

const V2_BELT_LP := [Vector3(-42.3, 0, -7.4), Vector3(-42.3, 0, -11.5), Vector3(-49.6, 0, -11.5), Vector3(-49.6, 0, -17.8), Vector3(-48.9, 0, -17.8)]
## The second press hangs off the same belt: shared up to index 3, then on to press 2.
const V2_BELT_LP2 := [Vector3(-42.3, 0, -7.4), Vector3(-42.3, 0, -11.5), Vector3(-49.6, 0, -11.5), Vector3(-49.6, 0, -17.8), Vector3(-49.6, 0, -27.8), Vector3(-48.9, 0, -27.8)]
const V2_BELT_P1B := [Vector3(-41.0, 0, -17.8), Vector3(-40.0, 0, -17.8), Vector3(-40.0, 0, -34.4), Vector3(-44.2, 0, -34.4), Vector3(-44.2, 0, -36.3)]
const V2_BELT_P2B := [Vector3(-42.3, 0, -29.4), Vector3(-42.3, 0, -32.6), Vector3(-45.6, 0, -32.6), Vector3(-45.6, 0, -36.3)]
const V2_BELT_BB := [Vector3(-38.1, 0, -39.4), Vector3(-38.1, 0, -40.2), Vector3(-32.4, 0, -40.2), Vector3(-32.4, 0, -38.4)]


func _pad_region(id: String) -> Region:
	return r2 if id.begins_with("r2_") and id != "r2_bridge" else r1


func _path2(a: Vector2, b: Vector2, w: float) -> void:
	(grounds[2].paths as Array).append([Vector4(a.x, a.y, b.x, b.y), w])


func _plaza2(c: Vector2, half: Vector2) -> void:
	(grounds[2].plazas as Array).append(Vector4(c.x, c.y, half.x, half.y))


## Keeps grass and rocks off where Birch Bend's belts, flume, groves and buildings will stand.
func _reserve_v2() -> void:
	for line in [V2_FLUME_PTS, V2_BELT_LP, V2_BELT_LP2, V2_BELT_P1B, V2_BELT_P2B, V2_BELT_BB]:
		for i in range(1, line.size()):
			var a: Vector3 = line[i - 1]
			var b: Vector3 = line[i]
			_reserved_lines.append([Vector4(a.x, a.z, b.x, b.z), 0.8])
	_reserved_lines.append([Vector4(-80, 14.6, -44.5, 14.2), 1.0])
	_reserved_lines.append([Vector4(RIVER_X - RIVER_HALF, BRIDGE_Z, -41, BRIDGE_Z), 1.0])
	# Valley 1 side: the path from the main road to the bridge appears with the bridge.
	_reserved_lines.append([Vector4(RIVER_X + RIVER_HALF, BRIDGE_Z, 0, BRIDGE_Z), 1.2])
	_reserved_lines.append([Vector4(-40, -1, -40, -38), 0.9])
	for g in [[V2_GROVE1, 3, 3], [V2_GROVE2, 3, 2], [V2_GROVE_NORTH, 4, 3], [V2_GROVE_WEST, 3, 4]]:
		var c: Vector3 = g[0]
		_reserved_rects.append(Vector4(c.x, c.z, int(g[1]) * 1.3 + 0.4, int(g[2]) * 1.3 + 0.4))
	for m in [V2_LATHE, V2_PRESS, V2_PRESS2]:
		_reserved_rects.append(Vector4(m.x, m.z, 4.2, 1.8))
	_reserved_rects.append(Vector4(V2_MARKET.x - 0.5, V2_MARKET.z - 1.5, 3.4, 5.8))
	_reserved_rects.append(Vector4(V2_OFFICE.x, V2_OFFICE.z + 1.0, 2.4, 3.4))
	_reserved_rects.append(Vector4(V2_BOATHOUSE.x, V2_BOATHOUSE.z + 1.5, 3.6, 5.8))
	_reserved_rects.append(Vector4(V2_BOATSHOP.x, V2_BOATSHOP.z, 5.0, 2.0))
	_reserved_rects.append(Vector4(V2_BARGE.x - 0.6, V2_BARGE.z, 3.0, 2.8))
	_reserved_rects.append(Vector4(V2_CHUTE.x, V2_CHUTE.z + 0.8, 1.8, 2.0))


func _apply_unlock_r2(id: String, animate: bool) -> void:
	match id:
		"r2_bridge":
			_open_bridge(animate)
			_build_forest("birch", V2_GROVE1, 3, 3, 2.6, "birch", animate, 2)
			paths.append([Vector4(RIVER_X + RIVER_HALF, BRIDGE_Z, 0, BRIDGE_Z), 0.9])
			_path2(Vector2(RIVER_X - RIVER_HALF, BRIDGE_Z), Vector2(-41, BRIDGE_Z), 1.0)
		"r2_lathe":
			_build_lathe(animate)
			_build_shop2(animate)
		"r2_grove2":
			_build_forest("birch", V2_GROVE2, 3, 2, 2.6, "birch", animate, 2)
		"r2_office":
			_build_office2(animate)
		"r2_jack1":
			var lathe: Machine = machines.lathe
			_spawn_jack_to("character-male-a", forests.birch, lathe.input, lathe.in_zone.global_position, Vector3(-50, 0, 2), animate, 2)
		"r2_hauler1":
			var lathe: Machine = machines.lathe
			_spawn_hauler("character-female-b", lathe.output, lathe.out_zone, shop2.shelf("veneer"), shop2.shelf_zone("veneer"), animate, 2)
		"r2_flume":
			_build_flume(animate)
			_build_forest("birch_north", V2_GROVE_NORTH, 4, 3, 2.6, "birch", animate, 2)
		"r2_cashier":
			shop2.hire_cashier(animate)
		"r2_press":
			_build_press("press", V2_PRESS, animate)
			shop2.open_shelf("plywood", animate)
			_path2(Vector2(-40, -6), Vector2(-40, -18), 0.8)
		"r2_jack2":
			for k in 2:
				_spawn_jack_to(["character-male-d", "character-female-a"][k], forests.birch_north, flume_chute, flume_zone.global_position, Vector3(-57, 0, -25 - k * 2), animate, 2)
		"r2_belt_lp":
			_belt_lp = _belt(machines.lathe.output, machines.press.input, V2_BELT_LP, animate, 2)
		"r2_hauler2":
			var press: Machine = machines.press
			_spawn_hauler("character-female-c", press.output, press.out_zone, shop2.shelf("plywood"), shop2.shelf_zone("plywood"), animate, 2)
		"r2_press2":
			_build_press("press2", V2_PRESS2, animate)
			_path2(Vector2(-40, -18), Vector2(-40, -28), 0.8)
			# The lathe belt splits 50/50 between the two presses.
			if _belt_lp:
				_belt_lp.add_split(machines.press2.input, PackedVector3Array(V2_BELT_LP2), 3)
		"r2_boatshop":
			_build_boatshop(animate)
			_path2(Vector2(-40, -28), Vector2(-40, -35.5), 0.8)
		"r2_barge":
			var d := TruckDock.new().setup("canoe", RIVER_X, "barge", 2)
			d.position = V2_BARGE
			d.region_node = r2
			r2.add_child(d)
			machines["barge"] = d
			_plaza2(Vector2(V2_BARGE.x - 1.2, V2_BARGE.z), Vector2(2.0, 2.6))
			if animate:
				Fx.pop_in(d, 0.6)
		"r2_belt_pb":
			_belt(machines.press.output, machines.boatshop.input, V2_BELT_P1B, animate, 2)
			_belt(machines.press2.output, machines.boatshop.input, V2_BELT_P2B, animate, 2)
		"r2_belt_bb":
			var dock: TruckDock = machines.barge
			_belt(machines.boatshop.output, dock.pile, V2_BELT_BB, animate, 2)
		"r2_jack3":
			_build_forest("birch_west", V2_GROVE_WEST, 3, 4, 2.6, "birch", animate, 2)
			var lathe: Machine = machines.lathe
			var dst: ItemStack = flume_chute if flume_chute else lathe.input
			var dst_pos: Vector3 = flume_zone.global_position if flume_zone else lathe.in_zone.global_position
			for k in 2:
				_spawn_jack_to(["character-male-c", "character-female-d"][k], forests.birch_west, dst, dst_pos, Vector3(-67, 0, -13 - k * 1.5), animate, 2)
			_model(Models.path("log_stack_birch"), Vector3(-65.5, 0, -12.0), 2.4, -15, r2)
		"r2_boathouse":
			_build_boathouse(animate)


func _open_bridge(animate: bool) -> void:
	if _gate_body:
		_gate_body.queue_free()
		_gate_body = null
	if _gate_prop:
		var gp := _gate_prop
		_gate_prop = null
		if animate:
			var tw := gp.create_tween()
			tw.tween_property(gp, "scale", Vector3.ONE * 0.01, 0.8).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
			tw.tween_callback(gp.queue_free)
		else:
			gp.queue_free()


func _machine2(id: String, recipe: String, pos: Vector3) -> Machine:
	var r: Array = Balance.MACHINES[recipe]
	var m := Machine.new().setup(id, str(r[0]), str(r[4]), int(r[1]), int(r[5]), float(r[6]), 2, int(Balance.MACHINE_OUT_CAP.get(recipe, 48)))
	m.position = pos
	machines[id] = m
	return m


func _build_lathe(animate: bool) -> void:
	var m := _machine2("lathe", "lathe", V2_LATHE)
	m.add_model(Models.path("lathe"), Vector3.ZERO, 1.0)
	# The birch log spins around X: the pivot turns local Z onto world X.
	var pivot := Node3D.new()
	pivot.position = Vector3(0, 0.98, 0)
	pivot.rotation_degrees.y = 90
	m.body.add_child(pivot)
	var lg := Models.make("lathe_log")
	lg.rotation_degrees.y = -90
	pivot.add_child(lg)
	m.spinners.append(pivot)
	m.mouth_in = Vector3(-1.2, 1.0, 0)
	m.mouth_out = Vector3(0.6, 0.9, 0.78)
	m.add_dust(Vector3(0, 1.1, 0.5), Color(0.96, 0.9, 0.75))
	m.add_blocker(Vector3(3.0, 1.6, 1.95))
	r2.add_child(m)
	_plaza2(Vector2(V2_LATHE.x, V2_LATHE.z), Vector2(4.8, 2.2))
	_model(Models.path("log_stack_birch"), V2_LATHE + Vector3(-1.4, 0, -2.4), 2.2, 10, r2)
	if animate:
		Fx.pop_in(m, 0.7)


func _build_press(id: String, pos: Vector3, animate: bool) -> void:
	var m := _machine2(id, "press", pos)
	m.add_model(Models.path("press"), Vector3.ZERO, 1.0)
	m.plates.append(m.add_model(Models.path("press_plate"), Vector3(0, 1.35, 0), 1.0))
	m.mouth_in = Vector3(-0.9, 0.8, 0)
	m.mouth_out = Vector3(0.9, 0.75, 0)
	m.add_blocker(Vector3(2.2, 3.2, 1.67))
	r2.add_child(m)
	_plaza2(Vector2(pos.x, pos.z), Vector2(4.8, 2.2))
	if animate:
		Fx.pop_in(m, 0.7)


func _build_boatshop(animate: bool) -> void:
	var m := _machine2("boatshop", "boatshop", V2_BOATSHOP)
	m.input.position.x = -3.4
	m.in_zone.position.x = -3.4
	m.output.position.x = 3.4
	m.out_zone.position.x = 3.4
	m.add_model(Models.path("boatshop"), Vector3.ZERO, 1.0)
	m.mouth_in = Vector3(-1.6, 0.9, 0.6)
	m.mouth_out = Vector3(1.6, 0.9, 0.6)
	m.add_dust(Vector3(0, 1.2, 0.6), Color(0.95, 0.85, 0.65))
	m.add_blocker(Vector3(4.5, 2.8, 3.0))
	r2.add_child(m)
	_plaza2(Vector2(V2_BOATSHOP.x, V2_BOATSHOP.z), Vector2(5.6, 2.4))
	if animate:
		Fx.pop_in(m, 0.8)


func _build_shop2(animate: bool) -> void:
	# Mirrored market: the player serves from the east, shoppers walk in along a lane from the west.
	shop2 = Shop.new().setup(2, -1.0)
	shop2.position = V2_MARKET
	# Lane along z 14.5, south of the boathouse jetty (it reaches z 12.6).
	shop2.spawn_local = Vector3(-79.5, 0, 13.6) - V2_MARKET
	shop2.exit_local = Vector3(-79.5, 0, 14.6) - V2_MARKET
	shop2.lane_via = Vector3(-44.5, 0, 14.2)
	shop2.sign_unlock = ""
	shop2.region_node = r2
	shop2.add_shelf("veneer", 2.6)
	shop2.add_shelf("plywood", 0.0)
	r2.add_child(shop2)
	shop2.open_shelf("veneer", animate)
	_plaza2(Vector2(V2_MARKET.x + 0.5, V2_MARKET.z - 1.5), Vector2(3.2, 5.6))
	_path2(Vector2(-80, 14.6), Vector2(-44.5, 14.2), 0.9)
	_path2(Vector2(-40, -1), Vector2(-40, -6), 0.8)


func _build_office2(animate: bool) -> void:
	var root := Node3D.new()
	root.position = V2_OFFICE
	r2.add_child(root)
	root.add_child(Models.make("riverside_office"))
	var lbl := Label3D.new()
	lbl.font = Fx.font()
	lbl.text = "OFFICE"
	lbl.font_size = 56
	lbl.outline_size = 12
	lbl.modulate = Color(0.25, 0.16, 0.08)
	lbl.outline_modulate = Color(1, 0.95, 0.75)
	lbl.pixel_size = 0.006
	lbl.position = Vector3(0, 2.05, 1.40)
	root.add_child(lbl)
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(3.9, 3.0, 3.3)
	col.shape = bs
	col.position = Vector3(0, 1.5, -0.2)
	sb.add_child(col)
	root.add_child(sb)
	office2_zone = Zone.new().setup(Zone.Kind.CUSTOM, null, Vector2(2.4, 2.0), "UPGRADES", Color(0.6, 0.95, 1.0))
	office2_zone.position = V2_OFFICE + Vector3(0, 0, 3.2)
	office2_zone.on_enter = func(_c: Node) -> void:
		if Game.hud:
			Game.hud.open_upgrades(2)
	office2_zone.on_exit = func(_c: Node) -> void:
		if Game.hud:
			Game.hud.close_upgrades()
	r2.add_child(office2_zone)
	_plaza2(Vector2(V2_OFFICE.x, V2_OFFICE.z + 2.6), Vector2(2.2, 1.6))
	_path2(Vector2(-38.3, 1.0), Vector2(-34, 12.6), 0.7)
	if animate:
		Fx.pop_in(root, 0.6)


## Log flume: chute by the North Grove, water trough to the lathe input (GDD 7.6 A).
func _build_flume(animate: bool) -> void:
	var root := Node3D.new()
	root.name = "Flume"
	r2.add_child(root)
	var chute := Models.make("flume_chute")
	chute.position = V2_CHUTE + Vector3(0.7, 0, 0)
	root.add_child(chute)
	var xf := []
	for x in [-58.0, -56.0, -54.0, -52.0]:
		xf.append(Transform3D(Basis(), Vector3(x, 0, -24)))
	var along_z := Basis(Vector3.UP, deg_to_rad(-90))
	for i in 9:
		xf.append(Transform3D(along_z, Vector3(-51.5, 0, -23.5 + i * 2.0)))
	xf.append(Transform3D(Basis(), Vector3(-50.7, 0, -6)))
	_multimesh(Models.path("flume_straight"), xf, true, root)
	var end := Models.make("flume_end")
	end.position = Vector3(-48.7, 0, -6)
	root.add_child(end)
	flume_chute = ItemStack.new().setup("birch_log", 16, 2, 2, "flume:in")
	flume_chute.position = V2_CHUTE + Vector3(0, 0.75, 0)
	r2.add_child(flume_chute)
	flume_zone = Zone.new().setup(Zone.Kind.DROP, flume_chute, Vector2(2.2, 2.0), "FLUME", Color(1, 1, 1))
	flume_zone.position = V2_CHUTE + Vector3(0, 0, 1.9)
	r2.add_child(flume_zone)
	var c := Conveyor.new()
	c.region = 2
	c.setup_flume(flume_chute, (machines.lathe as Machine).input, PackedVector3Array(V2_FLUME_PTS), 0.95)
	root.add_child(c)
	_plaza2(Vector2(V2_CHUTE.x, V2_CHUTE.z + 1.4), Vector2(1.6, 1.8))
	if animate:
		Fx.pop_in(root, 0.7)


func _build_boathouse(animate: bool) -> void:
	var root := Node3D.new()
	root.position = V2_BOATHOUSE
	r2.add_child(root)
	root.add_child(Models.make("boathouse"))
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(6.4, 3.0, 8.4)
	col.shape = bs
	col.position.y = 1.5
	sb.add_child(col)
	root.add_child(sb)
	_plaza2(Vector2(V2_BOATHOUSE.x, V2_BOATHOUSE.z + 5.0), Vector2(1.6, 2.0))
	if animate:
		Fx.pop_in(root, 1.0)


## Grass, flowers and rocks across Birch Bend (same density as Valley 1), reeds on the bank,
## lily pads on the river. Scenery stays outside the Region nodes (it culls by chunk).
func _scatter_deco_v2() -> void:
	var sets := [
		["grass", 260, 2.4, false], ["grass_large", 160, 2.4, false], ["grass_leafs", 110, 2.6, false],
		["flower_redA", 110, 2.6, false], ["flower_yellowA", 120, 2.6, false], ["flower_yellowB", 60, 2.4, false],
		["flower_redC", 50, 2.4, false], ["plant_bush", 110, 2.8, true], ["plant_bushDetailed", 90, 2.6, true],
		["rock_smallA", 40, 2.2, false], ["rock_smallC", 40, 2.2, false], ["mushroom_redGroup", 25, 2.2, false],
		["mushroom_tanGroup", 20, 2.2, false], ["rock_largeA", 10, 2.4, true],
	]
	var area := Rect2(-78.5, -46.5, 47.0, 61.5)
	var scale_n := area.get_area() / (66.0 * 68.0)
	for s in sets:
		var list := []
		var want := int(float(s[1]) * scale_n)
		var tries: int = want * 3
		while list.size() < want and tries > 0:
			tries -= 1
			var p := Vector2(rng2.randf_range(area.position.x, area.end.x), rng2.randf_range(area.position.y, area.end.y))
			if _busy(p, 0.6):
				continue
			var sc: float = s[2] * rng2.randf_range(0.75, 1.3)
			list.append(Transform3D(Basis(Vector3.UP, rng2.randf() * TAU).scaled(Vector3.ONE * sc), Vector3(p.x, 0, p.y)))
		_multimesh("res://assets/models_v3/nature/%s.glb" % s[0], list, s[3])
	var reeds := []
	for i in 40:
		var z := rng2.randf_range(-46, 15)
		if absf(z - BRIDGE_Z) < 2.0 or absf(z - V2_BARGE.z) < 3.5:
			continue
		reeds.append(Transform3D(Basis(Vector3.UP, rng2.randf() * TAU).scaled(Vector3.ONE * rng2.randf_range(2.2, 3.0)), Vector3(RIVER_X - RIVER_HALF - rng2.randf_range(-0.2, 0.6), 0, z)))
	_multimesh(Models.path("reeds"), reeds, false)
	var pads_x := []
	for i in 14:
		var z := rng2.randf_range(-60, 15)
		if absf(z - BRIDGE_Z) < 2.0:
			continue
		pads_x.append(Transform3D(Basis(Vector3.UP, rng2.randf() * TAU).scaled(Vector3.ONE * rng2.randf_range(2.0, 2.8)), Vector3(RIVER_X + rng2.randf_range(-2.4, -1.2), 0.09, z)))
	_multimesh(Models.path("lilypads"), pads_x, false)


## Log palisade around Birch Bend (sleeps with the valley), plus the closed gate at the bridge.
func _palisades_v2() -> void:
	var lines := [
		[Vector2(-78.8, 15.3), Vector2(-31.0, 15.3)],
		[Vector2(-78.8, -46.6), Vector2(-31.0, -46.6)],
		[Vector2(-78.8, 15.3), Vector2(-78.8, -46.6)],
	]
	var xforms := []
	for ln in lines:
		var a: Vector2 = ln[0]
		var b: Vector2 = ln[1]
		var n := int(a.distance_to(b) / 0.31)
		for k in n + 1:
			var p := a.lerp(b, float(k) / maxf(n, 1))
			var hgt := rng2.randf_range(0.95, 1.3)
			var basis := Basis(Vector3.UP, rng2.randf() * TAU).scaled(Vector3(1, hgt, 1))
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
	r2.add_child(mmi)
	if not Game.is_unlocked("r2_bridge"):
		_gate_prop = _model(Models.path("gate_fence"), Vector3(RIVER_X + RIVER_HALF + 0.6, 0, BRIDGE_Z), 2.6, 90, r1)


## Birch Bend mini-tutorial until its first lumberjack (GDD 12): chop, feed the lathe, stock the counter.
func _goal_v2(p: Vector3) -> Array:
	var back := player.stack
	if not Game.is_unlocked("r2_lathe"):
		if pads.has("r2_lathe"):
			return [(pads.r2_lathe as Node3D).global_position, "Build the veneer lathe"]
		return [null, ""]
	var lathe: Machine = machines.lathe
	if shop2.coin_value > 0 and back.is_empty():
		return [shop2.coin_zone.global_position, "Collect your cash"]
	if back.top_type() == "birch_log":
		var t := _nearest_tree(p, "birch")
		if lathe.in_zone.contains(p) or back.count() >= player.capacity() or t == null or back.count() >= 8:
			return [lathe.in_zone.global_position, "Feed the veneer lathe"]
		return [t.global_position, "Chop the birch trees"]
	if back.top_type() == "veneer":
		if lathe.out_zone.contains(p) and not lathe.output.is_empty() and back.count() < player.capacity():
			return [lathe.out_zone.global_position, "Pick up the veneer"]
		return [shop2.shelf_zone("veneer").global_position, "Stock the veneer counter"]
	if not back.is_empty():
		return [null, ""]
	if lathe.output.count() >= 6:
		return [lathe.out_zone.global_position, "Pick up the veneer"]
	var t2 := _nearest_tree(p, "birch")
	if t2:
		return [t2.global_position, "Chop the birch trees"]
	return [null, ""]
