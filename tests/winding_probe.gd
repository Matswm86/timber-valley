extends SceneTree

## Dev-only: compares triangle winding of Shapes.rounded_box against Godot's own BoxMesh.

func _tally(arrays: Array, label: String) -> void:
	var v: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var n: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
	var idx: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
	var count := idx.size() if idx.size() > 0 else v.size()
	var agree := 0
	var disagree := 0
	for t in range(0, count, 3):
		var ia := idx[t] if idx.size() > 0 else t
		var ib := idx[t + 1] if idx.size() > 0 else t + 1
		var ic := idx[t + 2] if idx.size() > 0 else t + 2
		var g := (v[ib] - v[ia]).cross(v[ic] - v[ia])
		if g.length() < 1e-9:
			continue
		if g.dot(n[ia] + n[ib] + n[ic]) > 0.0:
			agree += 1
		else:
			disagree += 1
	print("%s: cross(b-a,c-a) along normal=%d, against normal=%d" % [label, agree, disagree])


func _init() -> void:
	var bm := BoxMesh.new()
	bm.size = Vector3(2.4, 0.1, 2.4)
	_tally(bm.surface_get_arrays(0), "BoxMesh (Godot reference)")
	var shapes: GDScript = load("res://scripts/Shapes.gd")
	var rb: ArrayMesh = shapes.rounded_box(Vector3(2.4, 0.1, 2.4), 0.25)
	_tally(rb.surface_get_arrays(0), "Shapes.rounded_box")
	quit()
