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

var center := Vector2.ZERO
var default_pos := Vector3.ZERO
var isSelected := false
var isDragging := false

func _ready() -> void:
    print("@@ Ready ", self.get_class(), " ", key, " ", variants)
    center = Vector2(cell_width / 2, cell_height * UNIT_HEIGHT / 2)

func center_on(pos: Vector3) -> void:
    var p = Vector3(pos)
    p += Vector3(-center.x, Y_DEFAULT, -center.y)
    default_pos = p
    position = p

func setSelected(selected_: bool, endFunc: Callable) -> void:
    if isSelected == selected_:
        endFunc.call()
        return
    isSelected = selected_
    var target_y = Y_SELECTED if isSelected else Y_DEFAULT
    var target_x = default_pos.x
    var target_z = default_pos.z
    if selected_:
        # If the piece is outside of the board, we tween into the center
        # otherwise we leave it where it is.
        if target_x * target_x + target_z * target_z > 3.5 * 3.5:
            target_x = -center.x
            target_z = -center.y
    # Tween the movement
    const tween_dur = 0.25
    var tw = create_tween()
    tw.tween_property(self, "position:y", target_y, tween_dur)
    tw.parallel().tween_property(self, "position:x", target_x, tween_dur)
    tw.parallel().tween_property(self, "position:z", target_z, tween_dur)
    if endFunc != null:
        tw.tween_callback(endFunc)

func onDragging(event_x: float, event_y: float) -> void:
    if not isSelected:
        return
    isDragging = true
    position.x -= event_x * EVENT_DRAG_FACTOR
    position.z -= event_y * EVENT_DRAG_FACTOR

func onDragEnded() -> void:
    isDragging = false
