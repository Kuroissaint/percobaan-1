extends CharacterBody2D

var drag_offset: Vector2 = Vector2()
var dragging: bool = false

func start_drag():
	drag_offset = position - get_viewport().get_mouse_position()
	dragging = true

func stop_drag():
	dragging = false

func _input(event):
	if event is InputEventMouseButton \
			and event.button_index == MOUSE_BUTTON_LEFT \
			and not event.is_pressed():
		stop_drag()

	elif event is InputEventMouseMotion:
		if dragging:
			position = get_viewport().get_mouse_position() + drag_offset

func _physics_process(delta):
	if dragging:
		move_and_slide()
