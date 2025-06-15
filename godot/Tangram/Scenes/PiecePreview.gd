class_name PiecePreview
extends SubViewportContainer

@onready var viewport: SubViewport = $SubViewport
@onready var camera: Camera3D = $SubViewport/Camera3D
var piece: PieceBase3D

func setPiece(piece_: PieceBase3D) -> void:
    if piece_ == piece:
        return
    if piece != null:
        piece.queue_free()
        piece = null

    if piece_ == null:
        return
    piece = piece_.duplicate() as PieceBase3D
    # piece.position = Vector3.ZERO
    viewport.add_child(piece)
    piece.centerOn(Vector3.ZERO)
    camera.look_at(piece.position, Vector3.UP)

func _process(delta: float) -> void:
    if piece == null:
        return
    piece.rotate_y(0.5 * delta)

# ~~
