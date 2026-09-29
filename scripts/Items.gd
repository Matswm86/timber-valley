class_name Items
extends RefCounted

## Item catalogue: how each carried item looks and how tall it stacks.

const DEFS := {
	"log": {"proc": "log", "path": "", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.31, "cell": Vector2(1.05, 0.36)},
	"plank": {"proc": "plank", "path": "", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.11, "cell": Vector2(1.0, 0.4)},
	"chair": {"path": "res://assets/models/furniture/chair.glb", "scale": 1.9, "rot": Vector3(0, 180, 0), "layer": 0.36, "cell": Vector2(0.5, 0.5)},
	"table": {"path": "res://assets/models/furniture/table.glb", "scale": 1.05, "rot": Vector3(0, 0, 0), "layer": 0.36, "cell": Vector2(0.95, 0.55)},
	"bookcase": {"path": "res://assets/models/furniture/bookcaseClosed.glb", "scale": 1.25, "rot": Vector3(-90, 0, 0), "layer": 0.34, "cell": Vector2(0.6, 1.15)},
	"coin": {"path": "", "scale": 1.0, "rot": Vector3.ZERO, "layer": 0.075, "cell": Vector2(0.36, 0.36)},
}

static var _cache: Dictionary = {}
static var _coin_mesh: Mesh
static var _coin_mat: StandardMaterial3D


static func def(type: String) -> Dictionary:
	return DEFS[type]


static func make(type: String) -> Node3D:
	var root := Node3D.new()
	root.name = type
	root.set_meta("item", type)
	var d: Dictionary = DEFS[type]
	if d.has("proc"):
		root.add_child(_procedural(str(d.proc)))
		return root
	if type == "coin":
		var mi := MeshInstance3D.new()
		mi.mesh = _coin()
		mi.material_override = _coin_mat
		mi.position.y = 0.035
		root.add_child(mi)
		return root
	var info: Dictionary = _load(type)
	root.add_child(_build(info.scene, d))
	(root.get_child(0) as Node3D).position = info.offset
	return root


static func _procedural(kind: String) -> Node3D:
	var n := Node3D.new()
	match kind:
		"log":
			Shapes.log_node(n, 0.16, 0.95, Vector3(0, 0.16, 0), Vector3(0, 0, 90))
		"plank":
			var mi := Shapes.box_node(n, Vector3(0.95, 0.1, 0.34), Vector3(0, 0.05, 0), Shapes.wood(Color(0.96, 0.76, 0.48), 9.0), 0.03)
			mi.name = "plank"
	return n


static func _build(scene: PackedScene, d: Dictionary) -> Node3D:
	var inst: Node3D = scene.instantiate()
	var pivot := Node3D.new()
	pivot.rotation_degrees = d.rot
	pivot.add_child(inst)
	inst.scale = Vector3.ONE * float(d.scale)
	return pivot


static func _load(type: String) -> Dictionary:
	if _cache.has(type):
		return _cache[type]
	var scene: PackedScene = load(DEFS[type].path)
	var tmp := _build(scene, DEFS[type])
	var box := aabb_of(tmp, Transform3D.IDENTITY)
	tmp.free()
	var c := box.get_center()
	var info := {"scene": scene, "offset": Vector3(-c.x, -box.position.y, -c.z)}
	_cache[type] = info
	return info


static func _coin() -> Mesh:
	if _coin_mesh == null:
		var m := CylinderMesh.new()
		m.top_radius = 0.15
		m.bottom_radius = 0.15
		m.height = 0.07
		m.radial_segments = 20
		_coin_mesh = m
		_coin_mat = StandardMaterial3D.new()
		_coin_mat.albedo_color = Color(1.0, 0.78, 0.2)
		_coin_mat.metallic = 0.75
		_coin_mat.roughness = 0.3
		_coin_mat.emission_enabled = true
		_coin_mat.emission = Color(0.35, 0.22, 0.0)
	return _coin_mesh


static func aabb_of(n: Node, xf: Transform3D) -> AABB:
	var out := AABB()
	var first := true
	if n is Node3D:
		xf = xf * (n as Node3D).transform
	if n is MeshInstance3D:
		out = xf * (n as MeshInstance3D).get_aabb()
		first = false
	for c in n.get_children():
		var a := aabb_of(c, xf)
		if a.size != Vector3.ZERO:
			out = a if first else out.merge(a)
			first = false
	return out
