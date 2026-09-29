extends Node3D

## Dev-only: renders the app icon (lumberjack with logs next to a pine) to CAPTURE_DIR/icon.png.


func _ready() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.background_color = Color(0.55, 0.78, 0.45)
	var sky := Sky.new()
	sky.sky_material = ProceduralSkyMaterial.new()
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 1.0
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, -30, 0)
	sun.light_energy = 1.4
	sun.shadow_enabled = true
	add_child(sun)
	var ground := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(30, 30)
	ground.mesh = pm
	var gm := StandardMaterial3D.new()
	gm.albedo_color = Color(0.5, 0.74, 0.32)
	ground.material_override = gm
	add_child(ground)
	for p in [[Vector3(-1.2, 0, -1.0), "tree_pineTallC_detailed", 2.6], [Vector3(1.5, 0, -1.8), "tree_pineRoundA", 2.4], [Vector3(-2.4, 0, 0.6), "tree_oak", 2.2]]:
		var t: Node3D = load("res://assets/models/nature/%s.glb" % p[1]).instantiate()
		t.position = p[0]
		t.scale = Vector3.ONE * p[2]
		add_child(t)
	var stump: Node3D = load("res://assets/models/nature/stump_roundDetailed.glb").instantiate()
	stump.position = Vector3(1.2, 0, 0.6)
	stump.scale = Vector3.ONE * 2.2
	add_child(stump)
	var ch := CharacterModel.new().setup("character-male-e")
	ch.position = Vector3(0.2, 0, 0.8)
	ch.rotation_degrees.y = 75
	add_child(ch)
	var st := ItemStack.new().setup("", 99, 1, 1)
	st.position = Vector3(0, 0.62, 0.42)
	ch.add_child(st)
	for i in 5:
		st.push(Items.make("log"), false)
	ch.update_state(0.0, true, false)
	var cam := Camera3D.new()
	cam.fov = 36
	add_child(cam)
	cam.position = Vector3(0.8, 7.4, 5.6)
	cam.look_at(Vector3(0.1, 1.2, 0.2))
	cam.current = true
	for i in 30:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(OS.get_environment("CAPTURE_DIR") + "/icon_raw.png")
	get_tree().quit()
