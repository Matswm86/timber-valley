class_name Worker
extends Walker

## Hired help. Lumberjacks chop a forest and deliver logs; haulers move items between two spots.

enum Job { LUMBERJACK, HAULER }

var job: Job
var trees: Array = []
var source: ItemStack
var source_pos: Vector3
var dest: ItemStack
var dest_pos: Vector3
var home: Vector3
var _target_tree: ChopTree
var _delivering: bool = false
var _timer: float = 0.0
var _wait: float = 0.0


func as_lumberjack(look: String, forest: Array, d: ItemStack, d_pos: Vector3, home_pos: Vector3) -> Worker:
	job = Job.LUMBERJACK
	trees = forest
	dest = d
	dest_pos = d_pos
	home = home_pos
	init_walker(look)
	position = home_pos
	return self


func as_hauler(look: String, s: ItemStack, s_pos: Vector3, d: ItemStack, d_pos: Vector3) -> Worker:
	job = Job.HAULER
	source = s
	source_pos = s_pos
	dest = d
	dest_pos = d_pos
	home = s_pos
	init_walker(look)
	position = s_pos + Vector3(0.5, 0, 0.8)
	return self


func _process(delta: float) -> void:
	walk_speed = Game.worker_speed()
	cap = Game.worker_capacity()
	if job == Job.LUMBERJACK:
		_lumberjack(delta)
	else:
		_hauler(delta)
	animate()


func _deliver(delta: float) -> void:
	if step_to(dest_pos, delta, 0.3):
		_timer -= delta
		if _timer <= 0.0:
			_timer = 0.09
			if not stack.transfer_to(dest):
				if stack.is_empty():
					_delivering = false
			else:
				Sfx.play("wood", -16.0)
			if stack.is_empty():
				_delivering = false


func _lumberjack(delta: float) -> void:
	if _delivering:
		_deliver(delta)
		return
	if stack.count() >= cap:
		_release_tree()
		_delivering = true
		return
	if _target_tree == null or not _target_tree.is_ready():
		_release_tree()
		_target_tree = _find_tree()
		if _target_tree == null:
			if not stack.is_empty():
				_delivering = true
			else:
				step_to(home, delta, 0.3)
			return
		_target_tree.reserved_by = self
	var tp := _target_tree.global_position
	var to_me := global_position - tp
	to_me.y = 0
	var stand := tp + (to_me.normalized() if to_me.length() > 0.01 else Vector3.BACK) * 0.9
	if step_to(stand, delta, 0.2):
		face(tp - global_position, delta)
		_target_tree._on_carrier(self, delta)


func _find_tree() -> ChopTree:
	var best: ChopTree = null
	var best_d := INF
	for t in trees:
		var tree: ChopTree = t
		if not tree.is_visible_in_tree() or not tree.is_ready():
			continue
		if tree.reserved_by != null and tree.reserved_by != self and is_instance_valid(tree.reserved_by):
			continue
		var d := tree.global_position.distance_squared_to(global_position)
		if d < best_d:
			best_d = d
			best = tree
	return best


func _release_tree() -> void:
	if _target_tree != null and _target_tree.reserved_by == self:
		_target_tree.reserved_by = null
	_target_tree = null


func _hauler(delta: float) -> void:
	if _delivering:
		_deliver(delta)
		return
	if step_to(source_pos, delta, 0.3):
		_timer -= delta
		if _timer > 0.0:
			return
		_timer = 0.09
		if stack.count() < cap and not source.is_empty() and stack.can_accept(source.top_type()):
			source.transfer_to(stack)
			Sfx.play("place", -16.0)
			_wait = 0.0
		else:
			_wait += 0.09
		# Head off when full, or when holding something and the pile has been empty a moment.
		if stack.count() >= cap or (not stack.is_empty() and _wait > 1.2):
			_delivering = true
			_wait = 0.0
