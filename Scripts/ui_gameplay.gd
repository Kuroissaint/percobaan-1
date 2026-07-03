extends Node

# ---------------------------------------------------------------------------
# Node references — resolved via unique_name_in_owner (%NodeName)
# ---------------------------------------------------------------------------

@onready var score_label: Label             = %ScoreLabel
@onready var state_label: Label             = %StateLabel
@onready var character_sprite: TextureRect  = %CharacterSprite
@onready var customer_species_label: Label  = %CustomerSpeciesLabel
@onready var customer_desc_label: Label     = %CustomerDescLabel
@onready var order_icon: TextureRect        = %OrderIcon
@onready var order_label: Label             = %OrderLabel
@onready var feedback_panel: PanelContainer = %FeedbackPanel
@onready var feedback_label: Label          = %FeedbackLabel
@onready var menu_grid: GridContainer       = %MenuGrid
@onready var selected_label: Label          = %SelectedLabel
@onready var serve_button: Button           = %ServeButton
@onready var skip_button: Button            = %SkipButton

# ---------------------------------------------------------------------------
# Internal state
# ---------------------------------------------------------------------------

var _game_manager: Node        = null
var _selected_food_id: String  = ""
var _awaiting_result: bool     = false

const FOOD_ICONS: Dictionary = {
	"tacos":             "res://Assets/Foods/tacos.png",
	"ramen":             "res://Assets/Foods/ramen.png",
	"hamburger_steak":   "res://Assets/Foods/hamburger_steak.png",
	"fire":              "res://Assets/Foods/fire.png",
	"cake":              "res://Assets/Foods/cake.png",
	"holy_water":        "res://Assets/Foods/Water.png",
	"english_breakfast": "res://Assets/Foods/English Breakfast.png",
	"katsudon":          "res://Assets/Foods/katsudon.png",
	"soda":              "res://Assets/Foods/Soda.png",
}

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

func _ready() -> void:
	_game_manager = get_node("../GameManager")

	_game_manager.customer_changed.connect(_on_customer_changed)
	_game_manager.order_result.connect(_on_order_result)
	_game_manager.score_changed.connect(_on_score_changed)
	_game_manager.waiting_for_order.connect(_on_waiting_for_order)

	serve_button.pressed.connect(_on_serve_pressed)
	skip_button.pressed.connect(_on_skip_pressed)

	feedback_panel.hide()
	_update_score(0)
	_set_serving_enabled(false)
	_set_state_text("Waiting for customer...")

# ---------------------------------------------------------------------------
# GameManager signal handlers
# ---------------------------------------------------------------------------

func _on_customer_changed(customer: Dictionary) -> void:
	_selected_food_id = ""
	_awaiting_result  = false
	feedback_panel.hide()
	_set_serving_enabled(false)

	var species_data: Dictionary = customer.get("species_data", {})
	var species_id: String = str(customer.get("species", "temp")).to_lower()
	
	customer_species_label.text = species_data.get("display_name", customer.get("species", "???"))
	customer_desc_label.text    = species_data.get("description", "")

	var order: Dictionary = customer.get("order", {})
	order_label.text = order.get("display_name", "???")
	_update_order_icon(order.get("id", ""))

	var dynamic_path = "res://Assets/Character/" + species_id + "/" + species_id + "_neutral.png"
	var fallback_path = "res://Assets/Character/temp/marisa.png"
	
	if ResourceLoader.exists(dynamic_path):
		character_sprite.texture = load(dynamic_path)
	else:
		character_sprite.texture = load(fallback_path)

	selected_label.text = "Selected: —"
	_build_menu()
	_set_state_text("Customer is talking...")


func _on_waiting_for_order() -> void:
	_set_serving_enabled(true)
	_set_state_text("Choose a dish and press Serve!")


func _on_order_result(correct: bool, _food_id: String, reason: String) -> void:
	_awaiting_result = false
	_set_serving_enabled(false)

	feedback_label.text = ("✓  %s" if correct else "✗  %s") % reason

	var style := StyleBoxFlat.new()
	style.corner_radius_top_left     = 8
	style.corner_radius_top_right    = 8
	style.corner_radius_bottom_left  = 8
	style.corner_radius_bottom_right = 8
	style.content_margin_left        = 8.0
	style.content_margin_right       = 8.0
	style.content_margin_top         = 6.0
	style.content_margin_bottom      = 6.0
	style.bg_color = Color(0.18, 0.55, 0.18, 0.92) if correct else Color(0.65, 0.15, 0.15, 0.92)
	feedback_panel.add_theme_stylebox_override("panel", style)
	feedback_panel.show()

	_set_state_text("Next customer incoming...")


func _on_score_changed(new_score: int) -> void:
	_update_score(new_score)

# ---------------------------------------------------------------------------
# Button handlers
# ---------------------------------------------------------------------------

func _on_serve_pressed() -> void:
	if _selected_food_id.is_empty() or _awaiting_result:
		return
	_awaiting_result = true
	_set_serving_enabled(false)
	_game_manager.serve_food(_selected_food_id)


func _on_skip_pressed() -> void:
	if _awaiting_result:
		return
	_awaiting_result = true
	_set_serving_enabled(false)
	_set_state_text("Skipping customer...")
	_game_manager.next_customer()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

func _update_score(value: int) -> void:
	score_label.text = "Score: %d" % value


func _set_state_text(text: String) -> void:
	state_label.text = text


func _update_order_icon(food_id: String) -> void:
	if FOOD_ICONS.has(food_id):
		var icon_path = FOOD_ICONS[food_id]
		if ResourceLoader.exists(icon_path):
			order_icon.texture = load(icon_path)
			order_icon.show()
			return
	
	order_icon.texture = null
	order_icon.hide()


func _build_menu() -> void:
	for child in menu_grid.get_children():
		child.queue_free()

	var foods: Array = _game_manager.foods_db.get("foods", [])
	for food in foods:
		var btn := Button.new()
		btn.text                   = food.get("display_name", food.get("id", "?"))
		btn.custom_minimum_size    = Vector2(130, 40)
		btn.size_flags_horizontal  = Control.SIZE_SHRINK_CENTER
		btn.focus_mode             = Control.FOCUS_NONE
		btn.autowrap_mode          = TextServer.AUTOWRAP_WORD

		var food_id: String = food.get("id", "")
		
		if FOOD_ICONS.has(food_id):
			var icon_path = FOOD_ICONS[food_id]
			if ResourceLoader.exists(icon_path):
				btn.icon = load(icon_path)
				btn.expand_icon = true
				btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
				btn.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP

		btn.pressed.connect(func(): _select_food(food_id, btn.text))
		menu_grid.add_child(btn)


func _select_food(food_id: String, display_name: String) -> void:
	_selected_food_id   = food_id
	selected_label.text = "Selected: %s" % display_name


func _set_serving_enabled(enabled: bool) -> void:
	serve_button.disabled = not enabled
	skip_button.disabled  = not enabled
	for child in menu_grid.get_children():
		if child is Button:
			child.disabled = not enabled