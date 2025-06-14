class_name ActionButton
extends TextureButton

func _draw() -> void:
    match get_draw_mode():
        DrawMode.DRAW_PRESSED:
            if not disabled:
                modulate = Color.YELLOW
        DrawMode.DRAW_HOVER:
            if not disabled:
                modulate = Color.LIGHT_CYAN
        _:
            modulate = Color.WHITE if not disabled else Color.GRAY

# ~~
