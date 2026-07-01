extends Button
class_name NPCBase

@export var npc_name: String = "NPC"
@export var dialogue_resource: DialogueResource
@export var race: String = "Human"
@export var allergies: Array[String] = []

func _ready() -> void:
	pressed.connect(interact)

func interact() -> void:
	DialogueManager.show_dialogue_balloon(dialogue_resource, "start", [self])
