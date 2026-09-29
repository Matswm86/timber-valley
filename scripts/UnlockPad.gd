class_name UnlockPad
extends Node3D

## Stand here to pay for the next building. Coins drain from your wallet into the pad.

signal paid(id: String)

var id: String
var cost: int
var paid_amount: int = 0
var title: String
var zone: Zone
var _price: Label3D
var _arrow: MeshInstance3D
var _t: float = 0.0


func setup(pad_id: String, price: int, text: String, size: Vector2 = Vector2(2.6, 2.6)) -> UnlockPad:
	id = pad_id
	cost = price
	title = text
	name = "Pad_" + pad_id
	zone = Zone.new().setup(Zone.Kind.CUSTOM, null, size, "", Color(1.0, 0.82, 0.25))
	zone.interval = 0.0
	zone.on_carrier = _on_carrier
	add_child(zone)
	var t := Label3D.new()
	t.text = text
	t.font = Fx.font()
	t.font_size = 52
	t.outline_size = 14
	t.outline_modulate = Color(0.12, 0.1, 0.04, 0.8)
	t.pixel_size = 0.0085
	t.rotation_degrees = Vector3(-60, 0, 0)
	t.position = Vector3(0, 0.35, -size.y * 0.5 - 0.1)
	t.width = 700
	t.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(t)
	_price = Label3D.new()
	_price.font = Fx.font()
	_price.font_size = 72
	_price.outline_size = 16
	_price.modulate = Color(1.0, 0.88, 0.3)
	_price.outline_modulate = Color(0.25, 0.15, 0.0, 0.9)
	_price.pixel_size = 0.009
	_price.rotation_degrees = Vector3(-90, 0, 0)
	_price.position = Vector3(0, 0.06, 0)
	add_child(_price)
	_arrow = MeshInstance3D.new()
	var cm := CylinderMesh.new()
	cm.top_radius = 0.28
	cm.bottom_radius = 0.0
	cm.height = 0.55
	cm.radial_segments = 4
	_arrow.mesh = cm
	var am := StandardMaterial3D.new()
	am.albedo_color = Color(1.0, 0.8, 0.2)
	am.emission_enabled = true
	am.emission = Color(0.6, 0.4, 0.0)
	_arrow.material_override = am
	add_child(_arrow)
	_refresh()
	return self


func _refresh() -> void:
	_price.text = "$%d" % (cost - paid_amount)
	zone.set_progress(float(paid_amount) / float(cost))


func _process(delta: float) -> void:
	_t += delta
	var affordable := Game.money > 0 and Game.money + paid_amount >= cost
	_arrow.visible = affordable
	_arrow.position = Vector3(0, 2.1 + sin(_t * 4.0) * 0.18, 0)
	_arrow.rotation.y = _t * 1.5
	zone.set_highlight(affordable)


func _on_carrier(carrier: Node, delta: float) -> bool:
	if not carrier.get("is_player") or Game.money <= 0:
		return false
	var chunk := maxi(1, int(ceil(cost / 45.0)))
	chunk = mini(chunk, mini(Game.money, cost - paid_amount))
	if chunk <= 0:
		return false
	Game.spend(chunk)
	paid_amount += chunk
	if randf() < 0.5:
		var c := Items.make("coin")
		get_tree().current_scene.add_child(c)
		c.global_position = (carrier as Node3D).global_position + Vector3(0, 1.4, 0)
		var tw := c.create_tween()
		tw.tween_property(c, "global_position", global_position + Vector3(0, 0.1, 0), 0.22).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
		tw.tween_callback(c.queue_free)
		Sfx.play("coin", -10.0, 1.0 + float(paid_amount) / cost * 0.6, 0.06)
	_refresh()
	if paid_amount >= cost:
		set_process(false)
		zone.remove_from_group("zones")
		Sfx.play("unlock", -2.0)
		Fx.confetti(get_tree().current_scene, global_position + Vector3(0, 0.5, 0))
		var tw := create_tween()
		tw.tween_property(self, "scale", Vector3.ONE * 0.01, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
		tw.tween_callback(queue_free)
		paid.emit(id)
	return true
