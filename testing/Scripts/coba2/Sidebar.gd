extends PanelContainer

@onready var main_menu = $MarginContainer/Menu
@onready var menu_parent = $MarginContainer/Menu/MarginContainer
@onready var tool_menu = $MarginContainer/Menu/MarginContainer/toolMenu
#@onready var material_menu = $MarginContainer/Menu/MarginContainer

func _ready():
	main_menu.visible = false
	
func _set_menu(menu):
	var wasClosed = menu.visible == false
	
	_close_all_menus()
	
	main_menu.visible = wasClosed
	menu.visible = wasClosed
	

func _close_all_menus():
	for menu in menu_parent.get_children():
		menu.visible = false

func _on_open_tab_menu_pressed() -> void:
	_set_menu(tool_menu)
