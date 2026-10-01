extends Node

## Dev-only flicker probe. Frames each unlock pad / zone at a few camera distances and renders
## 16 frames per spot while the whole World slides by sub-centimetre steps. The view is identical
## every frame, so any pixel that changes on the pad is a depth (z-fight) or shadow-map artifact.
## PROBE_VARIANT: laptop (project defaults), phone (2048 atlas, soft quality 2 like .mobile),
## phone_noshadow (phone + sun shadows off). Run under Xvfb with CAPTURE_DIR set.

var out_dir: String = OS.get_environment("CAPTURE_DIR")
var variant: String = OS.get_environment("PROBE_VARIANT")
var world: World


func _ready() -> void:
	if FileAccess.file_exists(Game.SAVE_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(Game.SAVE_PATH))
	Game.money = 0
	Game.unlocked_ids.clear()
	Game.pile_counts.clear()
	var main: Node = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	world = main.get_node("World")
	await _frames(20)
	if variant.begins_with("phone"):
		RenderingServer.directional_shadow_atlas_set_size(2048, true)
		RenderingServer.directional_soft_shadow_filter_set_quality(RenderingServer.SHADOW_QUALITY_SOFT_LOW)
	var sun: DirectionalLight3D = world.find_children("*", "DirectionalLight3D", false, false)[0]
	if variant == "phone_noshadow":
		sun.shadow_enabled = false
	if variant.ends_with("noground"):
		for c in world.get_children():
			if c is MeshInstance3D and (c as MeshInstance3D).material_override == world.ground_mat:
				c.visible = false
	if variant.ends_with("subdiv"):
		for c in world.get_children():
			if c is MeshInstance3D and (c as MeshInstance3D).material_override == world.ground_mat:
				var pm: PlaneMesh = (c as MeshInstance3D).mesh
				pm.subdivide_width = int(OS.get_environment("PROBE_SUB"))
				pm.subdivide_depth = int(OS.get_environment("PROBE_SUB"))
	world.set_process(false)
	world.player.global_position = Vector3(0, 0, -44)
	var targets := {
		"trees2": (world.pads["trees2"] as Node3D).position,
		"office": (world.pads["office"] as Node3D).position,
		"cash": world.shop.coin_zone.global_position,
	}
	for k in targets:
		var pad_pos: Vector3 = targets[k]
		for d in [["near", Vector3(0, 0, 3.0)], ["mid", Vector3.ZERO], ["far", Vector3(0, 0, -9.0)]]:
			await _probe("%s_%s" % [k, d[0]], pad_pos, pad_pos + (d[1] as Vector3))
	get_tree().quit()


func _probe(tag: String, pad: Vector3, look: Vector3) -> void:
	var cam := world.camera
	cam.position = look + Vector3(0, 8.4, 6.6)
	cam.look_at(world.to_global(look + Vector3(0, 0.6, 0)), Vector3.UP)
	for i in 16:
		world.position = Vector3(i * 0.013, 0, i * 0.007)
		cam.position = look + Vector3(0, 8.4, 6.6)
		await _frames(2)
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var c := cam.unproject_position(world.to_global(pad))
		var sz := img.get_size()
		var r := Rect2i(int(c.x) - 170, int(c.y) - 150, 340, 300).intersection(Rect2i(Vector2i.ZERO, sz))
		img.get_region(r).save_png("%s/%s_%s_%02d.png" % [out_dir, variant, tag, i])
		if i == 0:
			img.save_jpg("%s/full_%s_%s.jpg" % [out_dir, variant, tag], 0.85)
	world.position = Vector3.ZERO


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame
