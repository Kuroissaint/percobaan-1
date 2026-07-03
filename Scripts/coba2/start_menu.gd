extends Control

# Menyimpan jalur (path) scene ke dalam konstanta agar rapi dan bebas typo
const SCENE_GAMEPLAY = "res://Scenes/gameplay.tscn"
const SCENE_SETTING  = "res://Scenes/Setting/Setting.tscn"

func _ready() -> void:
	# Memastikan mouse muncul saat berada di menu utama
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

	var start_btn = get_node("Option panel/VBoxContainer/StartButton") 
	var setting_btn = get_node("Option panel/VBoxContainer/SettingButton")
	var exit_btn = get_node("Option panel/VBoxContainer/ExitButton")
	
	# Sambungkan sinyal 'pressed' ke fungsi yang ada di bawah
	start_btn.pressed.connect(_on_start_button_pressed)
	setting_btn.pressed.connect(_on_setting_button_pressed)
	exit_btn.pressed.connect(_on_exit_button_pressed)
	# -----------------------------------------------------

# Fungsi untuk tombol Start/Play
#func _on_start_button_pressed() -> void:
	#if ResourceLoader.exists(SCENE_GAMEPLAY):
		#get_tree().change_scene_to_file(SCENE_GAMEPLAY)
	#else:
		#push_error("Gagal memuat: Scene gameplay tidak ditemukan di " + SCENE_GAMEPLAY)

# Fungsi untuk tombol Start/Play
func _on_start_button_pressed() -> void:
	# Memunculkan pesan di konsol untuk ngetes klik
	print("YES! TOMBOL START BERHASIL DIKLIK!") 
	
	# Memaksa pindah scene
	get_tree().change_scene_to_file("res://Scenes/gameplay.tscn")
	
# Fungsi untuk tombol Setting
func _on_setting_button_pressed() -> void:
	if ResourceLoader.exists(SCENE_SETTING):
		get_tree().change_scene_to_file(SCENE_SETTING)
	else:
		push_error("Gagal memuat: Scene setting tidak ditemukan di " + SCENE_SETTING)

# Fungsi untuk tombol Exit/Quit
func _on_exit_button_pressed() -> void:
	get_tree().quit()
