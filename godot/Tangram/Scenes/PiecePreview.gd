class_name PiecePreview
extends SubViewportContainer

@onready var viewport: SubViewport = $SubViewport
@onready var camera: Camera3D = $SubViewport/Camera3D
var _piece: PieceBase3D

func setPiece(piece: PieceBase3D) -> void:
    if piece == _piece:
        return
    if _piece != null:
        _piece.queue_free()
        _piece = null

    if piece == null:
        return
    _piece = piece.duplicate() as PieceBase3D
    _piece.currentVariant = piece.currentVariant
    viewport.add_child(_piece)
    _piece.centerOn(Vector3.ZERO)
    camera.look_at(_piece.position, Vector3.UP)

func selectVariant(variant: int) -> void:
    if _piece != null:
        _piece.selectVariant(variant)

func _process(delta: float) -> void:
    if _piece == null:
        return
    _piece.rotation.y += 0.5 * delta
    if _piece.rotation.y > TAU:
        _piece.rotation.y -= TAU

# ~~
