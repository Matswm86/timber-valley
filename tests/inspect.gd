extends SceneTree


func _init() -> void:
	var dir := "res://assets/models/"
	for sub in ["chars", "nature", "survival", "factory", "furniture", "car", "city"]:
		var d := DirAccess.open(dir + sub)
		for f in d.get_files():
			if not f.ends_with(".glb"):
				continue
			var s: Node3D = load(dir + sub + "/" + f).instantiate()
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
