class_name Hud
extends CanvasLayer

## Screen overlay: money counter, hints, toasts, upgrade shop, menu, finish screen and joystick.

const CREAM := Color(1.0, 0.97, 0.9)
const INK := Color(0.2, 0.15, 0.1)
const GREEN := Color(0.33, 0.66, 0.34)
const GOLD := Color(1.0, 0.78, 0.22)

var font: Font
var money_label: Label
var money_pill: PanelContainer
var hint: Label
var hint_pill: PanelContainer
var toast_label: Label
var toast_pill: PanelContainer
var upgrades_panel: PanelContainer
var upgrade_rows: Dictionary = {}
var menu_panel: PanelContainer
var finish_panel: PanelContainer
var sound_btn: Button
var joy_base: Control
var joy_knob: Control
var _shown_money: float = 0.0
var _touch_index: int = -1
var _joy_origin: Vector2
var _toast_tween: Tween
const JOY_RADIUS := 110.0


func _ready() -> void:
	Game.hud = self
	font = Fx.font()
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	_build_top(root)
	_build_joystick(root)
	_build_upgrades(root)
	_build_menu(root)
	_build_finish(root)
	_shown_money = Game.money
	Game.money_changed.connect(_on_money)
	Game.upgraded.connect(func(_i: String, _l: int) -> void: _refresh_upgrades())
	_update_money_text()


func _style(bg: Color, radius: int, pad: int = 18) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.set_corner_radius_all(radius)
	sb.content_margin_left = pad + 8
	sb.content_margin_right = pad + 8
	sb.content_margin_top = pad
	sb.content_margin_bottom = pad
	sb.shadow_color = Color(0, 0, 0, 0.18)
	sb.shadow_size = 8
	sb.shadow_offset = Vector2(0, 4)
	return sb


func _label(text: String, size: int, color: Color = INK) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	return l


func _button(text: String, bg: Color, size: int = 40) -> Button:
	var b := Button.new()
	b.text = text
	b.add_theme_font_override("font", font)
	b.add_theme_font_size_override("font_size", size)
	b.add_theme_color_override("font_color", Color.WHITE)
	b.add_theme_color_override("font_hover_color", Color.WHITE)
	b.add_theme_color_override("font_pressed_color", Color.WHITE)
	b.add_theme_color_override("font_disabled_color", Color(1, 1, 1, 0.6))
	var n := _style(bg, 26, 12)
	b.add_theme_stylebox_override("normal", n)
	b.add_theme_stylebox_override("hover", _style(bg.lightened(0.08), 26, 12))
	b.add_theme_stylebox_override("pressed", _style(bg.darkened(0.12), 26, 12))
	b.add_theme_stylebox_override("disabled", _style(Color(0.62, 0.6, 0.56), 26, 12))
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	b.pressed.connect(func() -> void: Sfx.play("click", -6.0))
	return b


func _build_top(root: Control) -> void:
	var top := VBoxContainer.new()
	top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top.offset_top = 70
	top.alignment = BoxContainer.ALIGNMENT_BEGIN
	top.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top.add_theme_constant_override("separation", 16)
	root.add_child(top)
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top.add_child(row)
	money_pill = PanelContainer.new()
	money_pill.add_theme_stylebox_override("panel", _style(CREAM, 40, 12))
	money_pill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(money_pill)
	var mrow := HBoxContainer.new()
	mrow.add_theme_constant_override("separation", 14)
	money_pill.add_child(mrow)
	var coin := CoinIcon.new()
	coin.custom_minimum_size = Vector2(58, 58)
	mrow.add_child(coin)
	money_label = _label("$0", 58)
	mrow.add_child(money_label)
	hint_pill = PanelContainer.new()
	hint_pill.add_theme_stylebox_override("panel", _style(Color(0.1, 0.12, 0.08, 0.6), 30, 10))
	hint_pill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hint_pill.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	top.add_child(hint_pill)
	hint = _label("", 40, Color.WHITE)
	hint_pill.add_child(hint)
	hint_pill.visible = false
	toast_pill = PanelContainer.new()
	toast_pill.add_theme_stylebox_override("panel", _style(GREEN, 34, 14))
	toast_pill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	toast_pill.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	top.add_child(toast_pill)
	toast_label = _label("", 46, Color.WHITE)
	toast_pill.add_child(toast_label)
	toast_pill.modulate.a = 0.0
	var menu_btn := _button("Menu", Color(0.25, 0.3, 0.22, 0.85), 34)
	menu_btn.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	menu_btn.offset_left = -190
	menu_btn.offset_top = 70
	menu_btn.offset_right = -30
	menu_btn.offset_bottom = 150
	menu_btn.pressed.connect(func() -> void: menu_panel.visible = not menu_panel.visible)
	root.add_child(menu_btn)


func _build_joystick(root: Control) -> void:
	joy_base = JoyCircle.new()
	(joy_base as JoyCircle).radius = JOY_RADIUS
	(joy_base as JoyCircle).fill = Color(1, 1, 1, 0.18)
	(joy_base as JoyCircle).ring = Color(1, 1, 1, 0.55)
	joy_base.mouse_filter = Control.MOUSE_FILTER_IGNORE
	joy_base.visible = false
	root.add_child(joy_base)
	joy_knob = JoyCircle.new()
	(joy_knob as JoyCircle).radius = 48
	(joy_knob as JoyCircle).fill = Color(1, 1, 1, 0.85)
	(joy_knob as JoyCircle).ring = Color(1, 1, 1, 0.0)
	joy_knob.mouse_filter = Control.MOUSE_FILTER_IGNORE
	joy_knob.visible = false
	root.add_child(joy_knob)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		var t := event as InputEventScreenTouch
		if t.pressed and _touch_index == -1:
			_touch_index = t.index
			_joy_origin = t.position
			joy_base.position = _joy_origin
			joy_knob.position = _joy_origin
			joy_base.visible = true
			joy_knob.visible = true
		elif not t.pressed and t.index == _touch_index:
			_touch_index = -1
			joy_base.visible = false
			joy_knob.visible = false
			if Game.player:
				Game.player.input_vector = Vector2.ZERO
	elif event is InputEventScreenDrag:
		var d := event as InputEventScreenDrag
		if d.index != _touch_index:
			return
		var off := d.position - _joy_origin
		if off.length() > JOY_RADIUS * 1.4:
			_joy_origin = d.position - off.normalized() * JOY_RADIUS * 1.4
			joy_base.position = _joy_origin
			off = d.position - _joy_origin
		var v := off.limit_length(JOY_RADIUS)
		joy_knob.position = _joy_origin + v
		if Game.player:
			var raw := v / JOY_RADIUS
			Game.player.input_vector = raw.normalized() * smoothstep(0.1, 0.55, raw.length()) if raw.length() > 0.08 else Vector2.ZERO


func _panel_base(root: Control) -> PanelContainer:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", _style(CREAM, 42, 26))
	p.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	p.anchor_left = 0.04
	p.anchor_right = 0.96
	p.anchor_top = 1.0
	p.anchor_bottom = 1.0
	p.grow_vertical = Control.GROW_DIRECTION_BEGIN
	p.offset_bottom = -60
	p.visible = false
	root.add_child(p)
	return p


func _build_upgrades(root: Control) -> void:
	upgrades_panel = _panel_base(root)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 14)
	upgrades_panel.add_child(v)
	var title := _label("Upgrades", 56)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(title)
	for id in Game.UPGRADES:
		var d: Dictionary = Game.UPGRADES[id]
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 16)
		v.add_child(row)
		var texts := VBoxContainer.new()
		texts.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		texts.add_theme_constant_override("separation", 0)
		row.add_child(texts)
		texts.add_child(_label(d.name, 40))
		var sub := _label(d.desc, 28, Color(0.42, 0.36, 0.3))
		texts.add_child(sub)
		var pips := _label("", 30, GREEN)
		texts.add_child(pips)
		var btn := _button("$0", GREEN, 36)
		btn.custom_minimum_size = Vector2(230, 96)
		btn.pressed.connect(func() -> void:
			if Game.buy_upgrade(id):
				Sfx.play("upgrade", -3.0)
			_refresh_upgrades())
		row.add_child(btn)
		upgrade_rows[id] = {"btn": btn, "pips": pips}
	Game.money_changed.connect(func(_v: int, _d: int) -> void:
		if upgrades_panel.visible:
			_refresh_upgrades())


func _refresh_upgrades() -> void:
	for id in upgrade_rows:
		var r: Dictionary = upgrade_rows[id]
		var lvl := Game.level(id)
		var mx: int = Game.UPGRADES[id].max
		(r.pips as Label).text = "●".repeat(lvl) + "○".repeat(mx - lvl)
		var btn: Button = r.btn
		if not Game.can_upgrade(id):
			btn.text = "MAX"
			btn.disabled = true
		else:
			var c := Game.upgrade_cost(id)
			btn.text = "$%d" % c
			btn.disabled = Game.money < c


func open_upgrades() -> void:
	_refresh_upgrades()
	Sfx.play("open", -4.0)
	upgrades_panel.visible = true
	upgrades_panel.pivot_offset = upgrades_panel.size * Vector2(0.5, 1.0)
	upgrades_panel.scale = Vector2(0.9, 0.9)
	create_tween().tween_property(upgrades_panel, "scale", Vector2.ONE, 0.18).set_trans(Tween.TRANS_BACK)


func close_upgrades() -> void:
	upgrades_panel.visible = false


func _build_menu(root: Control) -> void:
	menu_panel = PanelContainer.new()
	menu_panel.add_theme_stylebox_override("panel", _style(CREAM, 42, 28))
	menu_panel.set_anchors_preset(Control.PRESET_CENTER)
	menu_panel.anchor_left = 0.12
	menu_panel.anchor_right = 0.88
	menu_panel.anchor_top = 0.3
	menu_panel.anchor_bottom = 0.3
	menu_panel.visible = false
	root.add_child(menu_panel)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 22)
	menu_panel.add_child(v)
	var t := _label("Timber Valley", 58)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(t)
	var info := _label("A calm lumber mill. No ads, no timers.\nProgress saves on its own.", 30, Color(0.42, 0.36, 0.3))
	info.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(info)
	sound_btn = _button("", GREEN, 40)
	sound_btn.custom_minimum_size.y = 100
	sound_btn.pressed.connect(func() -> void:
		Game.sound_on = not Game.sound_on
		Sfx.apply_sound_setting()
		_sound_text()
		Game.save_game())
	v.add_child(sound_btn)
	_sound_text()
	var reset := _button("Start over", Color(0.75, 0.38, 0.3), 36)
	reset.custom_minimum_size.y = 90
	var confirm_state := [false]
	reset.pressed.connect(func() -> void:
		if confirm_state[0]:
			Game.reset_game()
		else:
			confirm_state[0] = true
			reset.text = "Tap again to erase your valley")
	v.add_child(reset)
	var close := _button("Back to the valley", Color(0.35, 0.45, 0.3), 40)
	close.custom_minimum_size.y = 100
	close.pressed.connect(func() -> void:
		menu_panel.visible = false
		confirm_state[0] = false
		reset.text = "Start over")
	v.add_child(close)


func _sound_text() -> void:
	sound_btn.text = "Sound: " + ("On" if Game.sound_on else "Off")


func _build_finish(root: Control) -> void:
	finish_panel = PanelContainer.new()
	finish_panel.add_theme_stylebox_override("panel", _style(CREAM, 42, 34))
	finish_panel.set_anchors_preset(Control.PRESET_CENTER)
	finish_panel.anchor_left = 0.08
	finish_panel.anchor_right = 0.92
	finish_panel.anchor_top = 0.28
	finish_panel.anchor_bottom = 0.28
	finish_panel.visible = false
	root.add_child(finish_panel)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 22)
	finish_panel.add_child(v)
	var t := _label("The Grand Lodge is built!", 52, GREEN)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	t.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(t)
	var body := _label("", 34)
	body.name = "Body"
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(body)
	var keep := _button("Keep relaxing", GREEN, 42)
	keep.custom_minimum_size.y = 110
	keep.pressed.connect(func() -> void: finish_panel.visible = false)
	v.add_child(keep)


func show_finish() -> void:
	var body: Label = finish_panel.find_child("Body", true, false)
	body.text = "Timber Valley is complete.\nYou earned $%d in total.\n\nYour workers keep going, so feel free to stay and chop a few trees." % Game.total_earned
	finish_panel.visible = true
	Sfx.play("upgrade", 0.0)


func set_hint(text: String) -> void:
	hint_pill.visible = text != ""
	if hint.text != text:
		hint.text = text


func toast(text: String) -> void:
	toast_label.text = text
	if _toast_tween:
		_toast_tween.kill()
	toast_pill.modulate.a = 0.0
	_toast_tween = create_tween()
	_toast_tween.tween_property(toast_pill, "modulate:a", 1.0, 0.2)
	_toast_tween.tween_interval(2.2)
	_toast_tween.tween_property(toast_pill, "modulate:a", 0.0, 0.5)


func _on_money(_value: int, delta: int) -> void:
	if delta > 0:
		money_pill.pivot_offset = money_pill.size * 0.5
		var tw := create_tween()
		tw.tween_property(money_pill, "scale", Vector2(1.12, 1.12), 0.08)
		tw.tween_property(money_pill, "scale", Vector2.ONE, 0.15)


func _process(delta: float) -> void:
	var target := float(Game.money)
	if absf(_shown_money - target) > 0.5:
		_shown_money = lerpf(_shown_money, target, 1.0 - exp(-10.0 * delta))
	else:
		_shown_money = target
	_update_money_text()


func _update_money_text() -> void:
	money_label.text = "$%d" % int(round(_shown_money))
