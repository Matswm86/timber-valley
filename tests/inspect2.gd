extends SceneTree


func _init() -> void:
	var s: Node = load("res://assets/models/chars/character-male-a.glb").instantiate()
	_dump(s, 0)
	var ap: AnimationPlayer = s.find_children("*", "AnimationPlayer", true, false)[0]
	for n in ["idle", "walk", "holding-both", "attack-melee-right", "pick-up", "interact-right"]:
		var a := ap.get_animation(n)
		print(n, " len=", a.length, " loop=", a.loop_mode, " tracks=", a.get_track_count())
		for t in a.get_track_count():
			print("   ", a.track_get_path(t), " type=", a.track_get_type(t))
	quit()


func _dump(n: Node, d: int) -> void:
	var extra := ""
	if n is Skeleton3D:
		for i in (n as Skeleton3D).get_bone_count():
			extra += (n as Skeleton3D).get_bone_name(i) + ","
	print("  ".repeat(d), n.name, " <", n.get_class(), "> ", extra)
	for c in n.get_children():
		_dump(c, d + 1)
