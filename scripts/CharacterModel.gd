class_name CharacterModel
extends Node3D

## Kenney mini-character with walk/idle/carry/chop animations and an axe on the right hand.

const SCALE := 2.0

var anim: AnimationPlayer
var skeleton: Skeleton3D
var axe: Node3D
var _current: String = ""
var _chop_until: float = 0.0


func setup(model_name: String) -> CharacterModel:
	var scene: PackedScene = load("res://assets/models/chars/%s.glb" % model_name)
	var inst: Node3D = scene.instantiate()
	inst.scale = Vector3.ONE * SCALE
	add_child(inst)
	anim = inst.find_children("*", "AnimationPlayer", true, false)[0]
	skeleton = inst.find_children("*", "Skeleton3D", true, false)[0]
	_build_anims()
	var att := BoneAttachment3D.new()
	skeleton.add_child(att)
	att.bone_name = "arm-right"
	axe = load("res://assets/models/survival/tool-axe.glb").instantiate()
	axe.scale = Vector3.ONE * 1.3
	axe.rotation_degrees = Vector3(90, 0, 0)
	axe.position = Vector3(-0.02, -0.12, 0.06)
	att.add_child(axe)
	axe.visible = false
	_play("idle")
	return self


func set_axe_model(upgraded: bool) -> void:
	var path := "res://assets/models/survival/tool-axe%s.glb" % ("-upgraded" if upgraded else "")
	var parent := axe.get_parent()
	var xf := axe.transform
	var vis := axe.visible
	axe.queue_free()
	axe = load(path).instantiate()
	axe.transform = xf
	axe.visible = vis
	parent.add_child(axe)


func _build_anims() -> void:
	var lib: AnimationLibrary = anim.get_animation_library("")
	for n in ["idle", "walk", "sprint"]:
		if lib.has_animation(n):
			lib.get_animation(n).loop_mode = Animation.LOOP_LINEAR
	lib.add_animation("carry-walk", _compose("walk", "holding-both", ["arm-left", "arm-right"]))
	lib.add_animation("carry-idle", _compose("idle", "holding-both", ["arm-left", "arm-right"]))
	lib.add_animation(
		"chop-walk", _compose("walk", "attack-melee-right", ["arm-left", "arm-right", "torso"])
	)
	lib.get_animation("chop-walk").loop_mode = Animation.LOOP_NONE
	var chop: Animation = lib.get_animation("attack-melee-right")
	chop.loop_mode = Animation.LOOP_NONE


func _compose(base: String, overlay: String, bones: Array) -> Animation:
	var a: Animation = anim.get_animation(base).duplicate(true)
	var o: Animation = anim.get_animation(overlay)
	for bone in bones:
		for t in range(a.get_track_count() - 1, -1, -1):
			if str(a.track_get_path(t)).ends_with(":" + bone):
				a.remove_track(t)
		for t in o.get_track_count():
			if str(o.track_get_path(t)).ends_with(":" + bone):
				o.copy_track(t, a)
	# A one-frame pose overlay (holding) must hold its key across the base loop.
	a.loop_mode = Animation.LOOP_LINEAR
	return a


func _play(n: String, speed: float = 1.0) -> void:
	if _current == n:
		anim.speed_scale = speed
		return
	_current = n
	anim.play(n, 0.12)
	anim.speed_scale = speed


## moving: speed 0..1, carrying: has items, chopping: swinging the axe.
func update_state(move_speed: float, carrying: bool, chopping: bool) -> void:
	var now := Time.get_ticks_msec() / 1000.0
	if chopping:
		axe.visible = true
		if now >= _chop_until:
			_current = ""
			var n := "chop-walk" if move_speed > 0.1 else "attack-melee-right"
			_play(n, 1.5)
			_chop_until = now + anim.get_animation(n).length / 1.5
		return
	if now < _chop_until:
		return
	axe.visible = false
	if move_speed > 0.1:
		_play("carry-walk" if carrying else "walk", clampf(move_speed * 1.25, 0.7, 1.6))
	else:
		_play("carry-idle" if carrying else "idle")
