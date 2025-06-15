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
    piece.currentVariant = piece_.currentVariant
    viewport.add_child(piece)
    piece.centerOn(Vector3.ZERO)
    camera.look_at(piece.position, Vector3.UP)

func selectVariant(variant: int) -> void:
    if piece != null:
        piece.selectVariant(variant)

func _process(delta: float) -> void:
    if piece == null:
        return
    piece.rotation.y += 0.5 * delta
    if piece.rotation.y > TAU:
        piece.rotation.y -= TAU

# ~~
