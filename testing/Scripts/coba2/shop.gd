extends Control

const GAME_WINDOW_SCENE := preload("res://scripts/game_window.tscn")

@onready var windows_layer: Control = $WindowsLayer

var _window_count: int = 0


func open_info_window(window_title: String, body_text: String) -> void:
	var win: GameWindow = GAME_WINDOW_SCENE.instantiate()
	windows_layer.add_child(win)
	win.setup(window_title)
	win.position = Vector2(40, 40) + Vector2(_window_count * 30, _window_count * 30)
	_window_count += 1

	var label := Label.new()
	label.text = body_text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD
	win.content.add_child(label)
