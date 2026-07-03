class_name GenerateCustomer

static func generate(species_db, foods):
	var customer = {}

	# pick random species
	var species_keys = species_db.keys()
	var random_species_key = species_keys[randi() % species_keys.size()]

	var species_data = species_db[random_species_key]

	# pick random food
	var food_keys = foods["foods"]
	var random_food = food_keys[randi() % food_keys.size()]

	# optional: random permits (for now simple)
	var permits = []

	# example chance system
	if randf() < 0.3:
		permits.append("large_predator_permit")

	if randf() < 0.2:
		permits.append("holy_substance_consumption_license")

	# build customer object
	customer["species"] = random_species_key
	customer["species_data"] = species_data
	customer["order"] = random_food
	customer["permits"] = permits

	return customer
