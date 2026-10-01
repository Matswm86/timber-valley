class_name Customer
extends Walker

## Shopper: walks in from the road, buys from one counter, pays at the till, walks home.

enum State { ENTER, SHELF, TO_TILL, TILL, LEAVE }

const LOOKS := [
	"character-female-a", "character-female-b", "character-female-c", "character-female-d",
	"character-female-f", "character-male-a", "character-male-b", "character-male-c",
	"character-male-d", "character-male-f",
]

var shop: Node
var product: String
var want: int = 1
var state: State = State.ENTER
var entry: Vector3
var exit_point: Vector3
## Optional lane waypoint walked through on the way in and on the way out.
var via: Vector3 = Vector3.INF
var _via_done: bool = false
var _timer: float = 0.0
var _bubble: Label3D


func setup(s: Node, prod: String, n: int, spawn: Vector3, entry_pt: Vector3, exit_pt: Vector3, lane_via: Vector3 = Vector3.INF) -> Customer:
	via = lane_via
	_via_done = via == Vector3.INF
	shop = s
	product = prod
	want = n
	entry = entry_pt
	exit_point = exit_pt
	init_walker(LOOKS[randi() % LOOKS.size()])
	walk_speed = randf_range(2.6, 3.2)
	position = spawn
	_bubble = Label3D.new()
	_bubble.font = Fx.font()
	_bubble.font_size = 44
	_bubble.outline_size = 12
	_bubble.pixel_size = 0.006
	_bubble.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	# Above the 1.8 m KayKit heads (was 2.0 for the 1.5 m Kenney figures).
	_bubble.position = Vector3(0, 2.3, 0)
	_bubble.modulate = Color(1, 1, 1)
	_bubble.outline_modulate = Color(0.15, 0.2, 0.1)
	_bubble.text = "%d %s%s" % [want, product, "s" if want > 1 else ""]
	_bubble.visible = false
	add_child(_bubble)
	return self


func _process(delta: float) -> void:
	match state:
		State.ENTER:
			if not _via_done:
				if step_to(via, delta, 0.5):
					_via_done = true
			elif step_to(entry, delta, 0.3):
				state = State.SHELF
				shop.join_queue(product, self)
		State.SHELF:
			var idx: int = shop.queue_index(product, self)
			var spot: Vector3 = shop.shelf_spot(product, idx)
			if step_to(spot, delta):
				face(Vector3(-shop.side, 0, 0), delta)
				if idx == 0:
					_bubble.visible = stack.count() < want
					_timer -= delta
					if _timer <= 0.0:
						var shelf: ItemStack = shop.shelf(product)
						if not shelf.is_empty():
							shelf.transfer_to(stack)
							Sfx.play("place", -12.0)
							_timer = 0.16
					if stack.count() >= want:
						_bubble.visible = false
						shop.leave_queue(product, self)
						shop.join_queue("till", self)
						state = State.TO_TILL
		State.TO_TILL, State.TILL:
			var idx: int = shop.queue_index("till", self)
			var spot: Vector3 = shop.till_spot(idx)
			if step_to(spot, delta):
				face(Vector3(-shop.side, 0, 0), delta)
				if idx == 0:
					if state != State.TILL:
						state = State.TILL
						_timer = 0.2
					_timer -= delta
					if _timer <= 0.0:
						shop.pay(self, Game.price_of(product) * stack.count())
						shop.leave_queue("till", self)
						state = State.LEAVE
						_via_done = via == Vector3.INF
		State.LEAVE:
			if not _via_done:
				if step_to(via, delta, 0.5):
					_via_done = true
			elif step_to(exit_point, delta, 0.4):
				queue_free()
	animate()
