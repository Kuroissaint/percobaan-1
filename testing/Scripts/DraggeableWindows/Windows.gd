extends Node2D

var paper_stack = []

var paper_scene = preload("res://scenes/DraggeableWindows/Paper.tscn")

func _ready():
	# Register papers already placed in the scene into the stack
	for child in get_children():
		if child is CharacterBody2D:
			paper_stack.append(child)
	_refresh_z_order()

func add_paper(paper):
	add_child(paper)
	paper_stack.append(paper)
	_refresh_z_order()

func push_paper_to_top(paper):
	paper_stack.erase(paper)
	paper_stack.append(paper)
	_refresh_z_order()

func _refresh_z_order():
	for i in range(paper_stack.size()):
		paper_stack[i].z_index = i
