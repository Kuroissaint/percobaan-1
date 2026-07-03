extends Area2D

var dragged_paper = null

func _process(delta):
	position = get_global_mouse_position()

	# On click: pick the top paper under the cursor and start dragging it.
	if Input.is_action_just_pressed("mouse_click"):
		var top_paper = _get_top_paper()
		if top_paper != null:
			dragged_paper = top_paper
			dragged_paper.start_drag()
			get_parent().push_paper_to_top(dragged_paper)

	# On release: stop dragging whatever we were holding.
	if Input.is_action_just_released("mouse_click"):
		if dragged_paper != null:
			dragged_paper.stop_drag()
			dragged_paper = null

func _get_top_paper():
	var bodies = get_overlapping_bodies()
	if bodies.is_empty():
		return null

	var top = bodies[0]
	for b in bodies:
		if b.z_index > top.z_index:
			top = b
	return top
