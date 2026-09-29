extends Node3D

## Dev-only: renders every glb in PREVIEW_DIR side by side and prints animation names.


func _ready() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	sky.sky_material = ProceduralSkyMaterial.new()
	env.sky = sky
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, -30, 0)
	sun.shadow_enabled = true
	add_child(sun)
	var dir := OS.get_environment("PREVIEW_DIR")
	var x := 0.0
	for f in DirAccess.get_files_at(dir):
		if not f.ends_with(".glb"):
			continue
		var s: Node3D = load(dir + "/" + f).instantiate()
		add_child(s)
		var box := Items.aabb_of(s, Transform3D.IDENTITY)
		var k := 1.8 / maxf(box.size.y, 0.01)
		s.scale = Vector3.ONE * k
		s.position = Vector3(x - box.get_center().x * k, -box.position.y * k, 0)
		x += maxf(box.size.x * k, 1.2) + 0.6
		var aps := s.find_children("*", "AnimationPlayer", true, false)
		var names := []
		if not aps.is_empty():
			names = (aps[0] as AnimationPlayer).get_animation_list()
			for n in names:
				if "idle" in n.to_lower():
					(aps[0] as AnimationPlayer).play(n)
					break
		print(f, " size=", box.size.snappedf(0.01), " anims=", names)
	var cam := Camera3D.new()
	add_child(cam)
	cam.position = Vector3(x * 0.5, 2.4, x * 0.55 + 2.0)
	cam.look_at(Vector3(x * 0.5, 0.9, 0))
	for i in 20:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_jpg(OS.get_environment("CAPTURE_DIR") + "/preview.jpg")
	get_tree().quit()
