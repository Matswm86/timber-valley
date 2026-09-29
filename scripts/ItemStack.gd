class_name ItemStack
extends Node3D

## A neat pile of items (logs, planks, coins...). Items fly into place in an arc.

signal changed(count: int)

var item_type: String = ""
var capacity: int = 40
var cols: int = 2
var rows: int = 2
var persist_id: String = ""
var fly_time: float = 0.28
var items: Array[Node3D] = []


func setup(type: String, cap: int, c: int, r: int, pid: String = "") -> ItemStack:
	item_type = type
	capacity = cap
	cols = c
	rows = r
	persist_id = pid
	return self


func _ready() -> void:
	if persist_id != "":
		Game.register_pile(persist_id, self)
		var n := mini(Game.saved_pile_count(persist_id), capacity)
		for i in n:
			var it := Items.make(item_type)
			add_child(it)
			items.append(it)
			it.transform = slot_transform(i, item_type)
		if n > 0:
			changed.emit(items.size())


func count() -> int:
	return items.size()


func is_empty() -> bool:
	return items.is_empty()


func is_full() -> bool:
	return items.size() >= capacity


func top_type() -> String:
	if items.is_empty():
		return ""
	return str(items[-1].get_meta("item"))


func can_accept(type: String) -> bool:
	if items.size() >= capacity:
		return false
	if item_type != "":
		return type == item_type
	return items.is_empty() or top_type() == type


func slot_transform(i: int, type: String) -> Transform3D:
	var d: Dictionary = Items.def(type)
	var per_layer := cols * rows
	var layer := i / per_layer
	var r := i % per_layer
	var cx := r % cols
	var cz := r / cols
	var cell: Vector2 = d.cell
	var pos := Vector3(
		(cx - (cols - 1) * 0.5) * cell.x, layer * float(d.layer), (cz - (rows - 1) * 0.5) * cell.y
	)
	var yaw := sin(i * 12.9898) * 0.06
	if type == "coin":
		yaw = i * 0.7
	return Transform3D(Basis(Vector3.UP, yaw), pos)


func height() -> float:
	if items.is_empty():
		return 0.0
	var d: Dictionary = Items.def(top_type())
	return (items.size() - 1) / (cols * rows) * float(d.layer) + float(d.layer)


func push(item: Node3D, animate: bool = true) -> void:
	var type := str(item.get_meta("item"))
	if item.has_meta("tw"):
		var old: Tween = item.get_meta("tw")
		if old and old.is_valid():
			old.kill()
		item.scale = Vector3.ONE
	var gxf := item.global_transform if item.is_inside_tree() else global_transform
	if item.get_parent():
		item.get_parent().remove_child(item)
	add_child(item)
	item.global_transform = gxf
	item.transform.basis = item.transform.basis.orthonormalized()
	items.append(item)
	var target := slot_transform(items.size() - 1, type)
	changed.emit(items.size())
	if not animate:
		item.transform = target
		return
	var start := item.position
	var start_basis := item.transform.basis
	var mid := (start + target.origin) * 0.5 + Vector3.UP * (1.2 + start.distance_to(target.origin) * 0.25)
	var tw := item.create_tween()
	item.set_meta("tw", tw)
	tw.tween_method(
		func(t: float) -> void:
			var a := start.lerp(mid, t)
			var b := mid.lerp(target.origin, t)
			item.position = a.lerp(b, t)
			item.transform.basis = start_basis.slerp(target.basis, t),
		0.0, 1.0, fly_time
	).set_trans(Tween.TRANS_SINE)
	tw.tween_property(item, "scale", Vector3(1.15, 0.85, 1.15), 0.05)
	tw.tween_property(item, "scale", Vector3.ONE, 0.08)


func pop() -> Node3D:
	if items.is_empty():
		return null
	var it: Node3D = items.pop_back()
	changed.emit(items.size())
	return it


func transfer_to(other: ItemStack) -> bool:
	if items.is_empty() or not other.can_accept(top_type()):
		return false
	other.push(pop())
	return true


func take_and_free() -> String:
	var it := pop()
	if it == null:
		return ""
	var t := str(it.get_meta("item"))
	it.queue_free()
	return t


func top_global() -> Vector3:
	return global_transform * Vector3(0, height(), 0)
