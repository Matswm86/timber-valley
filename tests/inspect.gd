extends SceneTree


func _init() -> void:
	var dir := "res://tools/kenney_models/"
	for sub in ["chars", "nature", "survival", "factory", "furniture", "car", "city"]:
		var d := DirAccess.open(dir + sub)
		if d == null:
			continue
		for f in d.get_files():
			if not f.ends_with(".glb"):
				continue
			var s: Node3D = _glb(dir + sub + "/" + f)
			var aabb := _aabb(s, Transform3D.IDENTITY)
			print(sub, "/", f, " size=", aabb.size.snappedf(0.01), " pos=", aabb.position.snappedf(0.01))
			s.free()
	quit()


func _aabb(n: Node, xf: Transform3D) -> AABB:
	var out := AABB()
	var first := true
	if n is Node3D:
		xf = xf * (n as Node3D).transform
	if n is MeshInstance3D:
		out = xf * (n as MeshInstance3D).get_aabb()
		first = false
	for c in n.get_children():
		var a := _aabb(c, xf)
		if a.size != Vector3.ZERO:
			out = a if first else out.merge(a)
			first = false
	return out


## The Kenney models live in the .gdignore'd tools/kenney_models/ (not imported), so read the GLB directly.
func _glb(path: String) -> Node3D:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	if doc.append_from_file(path, state) != OK:
		push_error("cannot read " + path)
		return Node3D.new()
	return doc.generate_scene(state) as Node3D
