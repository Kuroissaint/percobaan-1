extends Node

# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------

## Emitted when a new customer has been generated and is ready to be displayed.
signal customer_changed(customer: Dictionary)

## Emitted when the player serves food and the result is determined.
signal order_result(correct: bool, food_id: String, reason: String)

## Emitted whenever the score changes.
signal score_changed(new_score: int)

## Emitted when dialogue ends and the player may now choose what to serve.
signal waiting_for_order()

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

var foods_db: Dictionary = {}
var species_db: Dictionary = {}
var ingredients_db: Dictionary = {}

var current_customer: Dictionary = {}

var score: int = 0 : set = _set_score

const POINTS_CORRECT : int = 10
const POINTS_WRONG   : int = -5

var _customer_dialogue: DialogueResource = preload("res://dialogues/customer.dialogue")

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

func _ready() -> void:
	_load_game_data()
	# Defer so every other node (UI) has time to connect signals first.
	call_deferred("next_customer")


func _load_game_data() -> void:
	foods_db       = JsonLoader.load_json("res://data/foods.json")
	species_db     = JsonLoader.load_json("res://data/species.json")
	ingredients_db = JsonLoader.load_json("res://data/ingredients.json")

	if foods_db == null or species_db == null or ingredients_db == null:
		push_error("GameManager: failed to load one or more data files.")

# ---------------------------------------------------------------------------
# Customer flow
# ---------------------------------------------------------------------------

## Generate the next customer, show their data in the UI, then start dialogue.
func next_customer() -> void:
	if species_db.is_empty() or foods_db.is_empty():
		push_error("GameManager: data not loaded — cannot generate customer.")
		return

	current_customer = GenerateCustomer.generate(species_db, foods_db)
	emit_signal("customer_changed", current_customer)

	# Wait one frame so UI can react to customer_changed before dialogue opens.
	await get_tree().process_frame
	_start_customer_dialogue()


func _start_customer_dialogue() -> void:
	# Connect one-shot to dialogue_ended so we unlock serving when it closes.
	if not DialogueManager.dialogue_ended.is_connected(_on_dialogue_ended):
		DialogueManager.dialogue_ended.connect(_on_dialogue_ended, CONNECT_ONE_SHOT)

	DialogueManager.show_dialogue_balloon(
		_customer_dialogue,
		"start",
		[self]
	)


func _on_dialogue_ended(_resource: DialogueResource) -> void:
	# Dialogue is over — player can now pick a dish.
	emit_signal("waiting_for_order")

# ---------------------------------------------------------------------------
# Dialogue-exposed properties
# ---------------------------------------------------------------------------

var race: String :
	get:
		return current_customer.get("species_data", {}).get("display_name", "")

var order_name: String :
	get:
		return current_customer.get("order", {}).get("display_name", "")

# ---------------------------------------------------------------------------
# Order serving
# ---------------------------------------------------------------------------

func serve_food(food_id: String) -> void:
	if current_customer.is_empty():
		push_warning("GameManager.serve_food: no active customer.")
		return

	var result := _validate_order(food_id)
	var correct: bool = result["correct"]
	var reason: String  = result["reason"]

	emit_signal("order_result", correct, food_id, reason)

	if correct:
		score += POINTS_CORRECT
	else:
		score += POINTS_WRONG

	await get_tree().create_timer(1.5).timeout
	next_customer()

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

func _validate_order(food_id: String) -> Dictionary:
	var food := _find_food_by_id(food_id)
	if food.is_empty():
		return { "correct": false, "reason": "Unknown food '%s'." % food_id }

	var ordered_id: String = current_customer.get("order", {}).get("id", "")
	if food_id != ordered_id:
		return {
			"correct": false,
			"reason": "Customer ordered '%s', but received '%s'." % [
				current_customer.get("order", {}).get("display_name", ordered_id),
				food.get("display_name", food_id)
			]
		}

	var required_permits: Array = food.get("required_customer_permits", [])
	var customer_permits: Array = current_customer.get("permits", [])
	for permit in required_permits:
		if not permit in customer_permits:
			return {
				"correct": false,
				"reason": "Customer lacks permit: %s." % permit.replace("_", " ")
			}

	var species_data: Dictionary = current_customer.get("species_data", {})
	var forbidden_tags: Array    = species_data.get("forbidden_tags", [])
	var required_tags: Array     = species_data.get("required_tags", [])
	var all_tags                 := _collect_ingredient_tags(food.get("ingredients", []))

	for tag in forbidden_tags:
		if tag in all_tags:
			return {
				"correct": false,
				"reason": "This species cannot eat '%s' ingredients." % tag
			}

	for tag in required_tags:
		if not tag in all_tags:
			return {
				"correct": false,
				"reason": "This species requires '%s' in the meal." % tag
			}

	return { "correct": true, "reason": "Order accepted!" }


func _collect_ingredient_tags(ingredient_keys: Array) -> Array:
	var tags := []
	for key in ingredient_keys:
		var ingredient: Dictionary = ingredients_db.get(key, {})
		for tag in ingredient.get("tags", []):
			if not tag in tags:
				tags.append(tag)
	return tags


func _find_food_by_id(food_id: String) -> Dictionary:
	for food in foods_db.get("foods", []):
		if food.get("id", "") == food_id:
			return food
	return {}

# ---------------------------------------------------------------------------
# Score setter
# ---------------------------------------------------------------------------

func _set_score(value: int) -> void:
	score = value
	emit_signal("score_changed", score)
