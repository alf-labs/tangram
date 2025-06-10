class_name PieceBase3D
extends Node3D

# Represents an instance of a piece, with its 3D representation
# and all the board data.

@export var key: String
@export var variants = 1
@export var cell_width := 1.0
@export var cell_height := 1.0

const ANGLE = 60
const UNIT_Y = 0.8660

func _ready() -> void:
    print("@@ Ready ", self.get_class(), " ", key, " ", variants)

func center_on(pos: Vector3) -> void:
    var p = Vector3(pos)
    p += Vector3(-cell_width / 2, 0, -cell_height * UNIT_Y / 2)
    position = p
