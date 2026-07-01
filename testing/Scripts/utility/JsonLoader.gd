class_name JsonLoader

static func load_json(path: String):
	var file = FileAccess.open(path, FileAccess.READ)
	if file == null:
		return null

	var text = file.get_as_text()
	file.close()

	return JSON.parse_string(text)
