extends Control

# Menyimpan jalur (path) scene ke dalam konstanta agar rapi dan bebas typo
const SCENE_GAMEPLAY = "res://Scenes/gameplay.tscn"
const SCENE_SETTING  = "res://Scenes/Setting/Setting.tscn"

func _ready() -> void:
	# Memastikan mouse muncul saat berada di menu utama
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

	# --- BAGIAN BARU: MENYAMBUNGKAN TOMBOL LEWAT KODE ---
	# Ambil referensi tombol. 
	# PENTING: Ganti tulisan di dalam tanda kutip dengan jalur (path) yang sesuai di panel Scene kamu.
	var start_btn = get_node("Option panel/VBoxContainer/StartButton") 
	var setting_btn = get_node("Option panel/VBoxContainer/SettingButton")
	var exit_btn = get_node("Option panel/VBoxContainer/ExitButton")
	
	# Sambungkan sinyal 'pressed' ke fungsi yang ada di bawah
	start_btn.pressed.connect(_on_start_button_pressed)
	setting_btn.pressed.connect(_on_setting_button_pressed)
	exit_btn.pressed.connect(_on_exit_button_pressed)
	# -----------------------------------------------------

# Fungsi untuk tombol Start/Play
func _on_start_button_pressed() -> void:
	# 1. Ambil referensi node AnimatedSprite2D pintu
	var pintu = get_node("Door Menu/buka_pintu")
	
	# 2. Mainkan animasinya!
	pintu.play("buka_pintu")
	
	# 3. Minta Godot untuk menunda jalannya kode sampai animasi selesai
	await pintu.animation_finished
	
	# 4. Setelah pintunya terbuka penuh (animasi selesai), baru pindah scene!
	if ResourceLoader.exists(SCENE_GAMEPLAY):
		get_tree().change_scene_to_file(SCENE_GAMEPLAY)
	else:
		push_error("Gagal memuat: Scene gameplay tidak ditemukan di " + SCENE_GAMEPLAY)
		
# Fungsi untuk tombol Setting
func _on_setting_button_pressed() -> void:
	if ResourceLoader.exists(SCENE_SETTING):
		get_tree().change_scene_to_file(SCENE_SETTING)
	else:
		push_error("Gagal memuat: Scene setting tidak ditemukan di " + SCENE_SETTING)

# Fungsi untuk tombol Exit/Quit
func _on_exit_button_pressed() -> void:
	get_tree().quit()
