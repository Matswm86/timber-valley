class_name Walker
extends Node3D

## Base for computer-controlled people: walks in straight lines between points.

var is_player := false
var model: CharacterModel
var stack: ItemStack
var velocity: Vector3 = Vector3.ZERO
var chopping_until: float = 0.0
var walk_speed: float = 3.0
var cap: int = 6


func init_walker(model_name: String) -> void:
	model = CharacterModel.new().setup(model_name)
	add_child(model)
	stack = ItemStack.new().setup("", 999, 1, 1)
	stack.position = Vector3(0, 0.62, 0.42)
	stack.fly_time = 0.22
	model.add_child(stack)


func capacity() -> int:
	return cap


## Steps toward target; returns true once there.
func step_to(target: Vector3, delta: float, stop_dist: float = 0.15) -> bool:
	var d := target - global_position
	d.y = 0
	var dist := d.length()
	if dist <= stop_dist:
		velocity = Vector3.ZERO
		return true
	var v := d / dist * walk_speed
	velocity = velocity.lerp(v, 1.0 - exp(-10.0 * delta))
	var step := velocity * delta
	if step.length() > dist:
		step = d
	global_position += step
	if velocity.length() > 0.2:
		model.rotation.y = lerp_angle(model.rotation.y, atan2(velocity.x, velocity.z), 1.0 - exp(-12.0 * delta))
	return false


func face(dir: Vector3, delta: float) -> void:
	if Vector2(dir.x, dir.z).length() > 0.01:
		model.rotation.y = lerp_angle(model.rotation.y, atan2(dir.x, dir.z), 1.0 - exp(-10.0 * delta))


func animate() -> void:
	var now := Time.get_ticks_msec() / 1000.0
	model.update_state(velocity.length() / maxf(walk_speed, 0.1), not stack.is_empty(), now < chopping_until)
