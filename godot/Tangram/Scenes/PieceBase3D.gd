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

var center := Vector2.ZERO
var default_pos := Vector3.ZERO
var isSelected := false
var isDragging := false

func _ready() -> void:
    var mesh = _findMesh()
    if mesh != null:
        var meshPos = mesh.position if mesh != null else Vector3.ZERO
        var meshCenter = _getMeshCenter(mesh)
        center = Vector2(meshPos.x, meshPos.z)
        center += Vector2(meshCenter.x, meshCenter.z)
        var center3 = Vector3(center.x, 0, center.y)
        print("@@ Ready ", self.get_class(), " ", key, "x", variants, ", offset by center=", center)
        for child in get_children():
            if child is Node3D:
                child.position -= center3
        center = Vector2.ZERO
    print("@@ Ready ", self.get_class(), " ", key, "x", variants, ", center=", center)

func centerOn(pos: Vector3) -> void:
    var p = pos + Vector3(-center.x, Y_DEFAULT, -center.y)
    default_pos = p
    position = p
    print("@@ Center ", self.get_class(),  " ", key, "x", variants, ", to=", p)

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

func onDragging(target_x: float, target_z: float) -> void:
    if not isSelected:
        return
    isDragging = true
    position.x = target_x - center.x
    position.z = target_z - center.y

func onDragEnded() -> void:
    isDragging = false

func _findMesh() -> MeshInstance3D:
    for child in get_children():
        if child is MeshInstance3D:
            return child
    return null

func _getMeshCenter(mesh: MeshInstance3D) -> Vector3:
    if mesh == null:
        return Vector3.ZERO
    print("@@ Mesh: ", mesh, " at ", mesh.position)
    var aabb = mesh.get_aabb()
    print("@@ Mesh AABB: ", aabb)
    print("@@ Mesh AABB pos: ", aabb.position)
    print("@@ Mesh AABB size: ", aabb.size)
    return aabb.position + aabb.size / 2

# ~~
