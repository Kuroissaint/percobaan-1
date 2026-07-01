extends Control
class_name GameWindow

signal closed

@onready var title_bar: Control = $TitleBar
@onready var title_label: Label = $TitleBar/TitleLabel
@onready var close_button: Button = $TitleBar/CloseButton
@onready var content: VBoxContainer = $Content

var _dragging: bool = false
var _drag_offset: Vector2 = Vector2.ZERO


func _ready() -> void:
	title_bar.mouse_filter = Control.MOUSE_FILTER_STOP
	title_bar.gui_input.connect(_on_title_bar_input)
	close_button.pressed.connect(_on_close_pressed)


func setup(window_title: String) -> void:
	title_label.text = window_title


func _on_title_bar_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			move_to_front()
			_dragging = true
			_drag_offset = get_global_mouse_position() - global_position
		else:
			_dragging = false

	elif event is InputEventMouseMotion and _dragging:
		global_position = get_global_mouse_position() - _drag_offset


func _on_close_pressed() -> void:
	closed.emit()
	queue_free()
