extends Control

@export var panel_width: float = 220.0
@export var open_margin: float = 16.0
@export var slide_duration: float = 0.25

@onready var race_label: Label = $Panel/RaceLabel
@onready var allergy_label: Label = $Panel/AllergyLabel

var _is_open: bool = false
var _closed_x: float
var _open_x: float


func _ready() -> void:
	size.x = panel_width
	_closed_x = get_viewport_rect().size.x
	_open_x = get_viewport_rect().size.x - panel_width - open_margin
	position.x = _closed_x

	DialogueManager.customer_info_changed.connect(_on_customer_info_changed)
	DialogueManager.dialogue_ended.connect(_on_dialogue_ended)


func _on_customer_info_changed(race: String, allergies: Array[String]) -> void:
	race_label.text = "Ras: %s" % race
	if allergies.is_empty():
		allergy_label.text = "Alergi: tidak ada"
	else:
		allergy_label.text = "Alergi: %s" % ", ".join(allergies)


func _on_dialogue_ended() -> void:
	_close()


func toggle() -> void:
	if not DialogueManager.is_active:
		return

	if _is_open:
		_close()
	else:
		_open()


func _open() -> void:
	_is_open = true
	var tween := create_tween()
	tween.tween_property(self, "position:x", _open_x, slide_duration).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)


func _close() -> void:
	_is_open = false
	var tween := create_tween()
	tween.tween_property(self, "position:x", _closed_x, slide_duration).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)
