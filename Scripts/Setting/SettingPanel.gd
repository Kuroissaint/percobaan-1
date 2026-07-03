extends Control

@onready var master_slider: HSlider = $Panel/MasterRow/MasterSlider
@onready var music_slider: HSlider = $Panel/MusicRow/MusicSlider
@onready var sfx_slider: HSlider = $Panel/SFXRow/SFXSlider
@onready var close_button: Button = $Panel/CloseButton

var _master_bus: int
var _music_bus: int
var _sfx_bus: int

func _ready() -> void:
	_master_bus = AudioServer.get_bus_index("Master")
	_music_bus = AudioServer.get_bus_index("Music")
	_sfx_bus = AudioServer.get_bus_index("SFX")
	
	# TAMBAHKAN INI UNTUK MENGECEK:
	print("Index Master: ", _master_bus)
	print("Index Music: ", _music_bus)
	print("Index SFX: ", _sfx_bus)

	for slider in [master_slider, music_slider, sfx_slider]:
		slider.min_value = 0
		slider.max_value = 100
		slider.step = 1

	_load_settings()

	master_slider.value_changed.connect(func(v): _apply_volume(_master_bus, v))
	music_slider.value_changed.connect(func(v): _apply_volume(_music_bus, v))
	sfx_slider.value_changed.connect(func(v): _apply_volume(_sfx_bus, v))
	
	# PENTING: _save_settings() dipindahkan ke sini, hanya jalan saat tombol di-klik
	close_button.pressed.connect(func(): 
		_save_settings() 
		hide()
	)

func _apply_volume(bus_idx: int, value: float) -> void:
	# TAMBAHKAN BARIS INI UNTUK TES:
	print("Mengubah Bus Index: ", bus_idx, " menjadi Volume: ", value)
	if value <= 0.0:
		AudioServer.set_bus_mute(bus_idx, true)
	else:
		AudioServer.set_bus_mute(bus_idx, false)
		# Pembagian 100.0 diubah jadi float agar presisi
		AudioServer.set_bus_volume_db(bus_idx, linear_to_db(value / 100.0))
	
	# _save_settings() DIHAPUS dari sini agar tidak spam tulis file ke disk

func _load_settings() -> void:
	var config := ConfigFile.new()
	var err := config.load("user://settings.cfg")

	if err == OK:
		master_slider.value = config.get_value("audio", "master", 100.0)
		music_slider.value = config.get_value("audio", "music", 100.0)
		sfx_slider.value = config.get_value("audio", "sfx", 100.0)
	else:
		master_slider.value = 100.0
		music_slider.value = 100.0
		sfx_slider.value = 100.0

	_apply_volume(_master_bus, master_slider.value)
	_apply_volume(_music_bus, music_slider.value)
	_apply_volume(_sfx_bus, sfx_slider.value)

func _save_settings() -> void:
	var config := ConfigFile.new()
	config.set_value("audio", "master", master_slider.value)
	config.set_value("audio", "music", music_slider.value)
	config.set_value("audio", "sfx", sfx_slider.value)
	config.save("user://settings.cfg")
	print("Pengaturan audio berhasil disimpan!") # Untuk debugging


func _on_close_button_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/StartMenu.tscn")
