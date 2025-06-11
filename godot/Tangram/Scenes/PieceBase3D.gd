class_name PieceBase3D
extends Node3D

# Represents an instance of a piece, with its 3D representation
# and all the board data.

@export var key: String
@export var variants = 1
@export var cell_width := 1.0
@export var cell_height := 1.0

const ANGLE = 60
const UNIT_HEIGHT = 0.8660
const Y_SELECTED = 1.0
const Y_DEFAULT  = 0.0
const EVENT_DRAG_FACTOR = 1/50.0

var default_pos := Vector3.ZERO
var isSelected := false
var isDragging := false

func _ready() -> void:
    print("@@ Ready ", self.get_class(), " ", key, " ", variants)

func center_on(pos: Vector3) -> void:
    var p = Vector3(pos)
    p += Vector3(-cell_width / 2, Y_DEFAULT, -cell_height * UNIT_HEIGHT / 2)
    default_pos = p
    position = p

func setSelected(selected_: bool) -> void:
    if isSelected == selected_:
        return
    isSelected = selected_
    var target_y = Y_SELECTED if isSelected else Y_DEFAULT
    # Tween the movement
    const tween_dur = 0.25
    var tw = create_tween()
    tw.tween_property(self, "position:y", target_y, tween_dur)

func onDragging(event_x: float, event_y: float) -> void:
    if not isSelected:
        return
    isDragging = true
    position.x -= event_x * EVENT_DRAG_FACTOR
    position.z -= event_y * EVENT_DRAG_FACTOR

func onDragEnded() -> void:
    isDragging = true
    # TEMPRORARY
    # Tween back to default position
    const tween_dur = 0.25
    var tw = create_tween()
    tw.tween_property(self, "position:x", default_pos.x, tween_dur)
    tw.tween_property(self, "position:z", default_pos.z, tween_dur)
