extends Node3D

@onready var cam3d = $Camera3D
@onready var rootControl = $RootControl

const PI_2 = PI / 2
const RAD_90_DEG = PI_2   # 90 degrees in radians
const NUM_PIECES = 11
const RADIUS_PIECES = 5.5
const MIN_DRAG_DELAY_MS = 125
const RAY_LENGTH = 1000.0
const MAX_ANGLE_Y = RAD_90_DEG - 0.01
const START_ANGLE_Y = RAD_90_DEG / 2
const CAM_LOOK_AT = Vector3(0, -5, 0)
const CAM_LOOK_AT_ZERO_ANGLE_Y = (PI_2 / 90 * 20)
const CAM_SELECTED_FOV = 35.0
const EVENT_DRAG_FACTOR = 1/200.0

enum SelectionMode { Board, PieceIn, Piece, PieceOut }
var selectionMode : SelectionMode = SelectionMode.Board

var staticCamDistance := 0.0
var staticCamFov := 0.0
var camAngleX := 0.0
var camAngleY := 0.0
var camAngleYBoardMode := 0.0
var pieces = {}
var selectedPiece : PieceBase3D = null


func _ready() -> void:
    rootControl.visible = false
    # Grab the initial camera setup in the scene to reuse it later.
    staticCamDistance = cam3d.position.distance_to(Vector3(0, 0, 0))
    staticCamFov = cam3d.fov
    # Option 1: Start with the camera matching the Godot scene
    # camAngleX = atan2(cam3d.position.z, cam3d.position.x)
    # camAngleY = atan2(cam3d.position.y, cam3d.position.z)
    # Option 2: Start with a top-view camera
    camAngleX = RAD_90_DEG
    camAngleY = RAD_90_DEG
    print("@@ START Camera: ", cam3d.position, " > ", rad_to_deg(camAngleX), " x ", rad_to_deg(camAngleY), " fov ", cam3d.fov)
    _updateCamera()
    _tweenCamera(START_ANGLE_Y, staticCamFov)
    _initPieces()

func _initPieces() -> void:
    var vec := Vector3(RADIUS_PIECES, 0, 0)
    vec = vec.rotated(Vector3.UP, RAD_90_DEG)
    const angleInc = -PI * 2 / NUM_PIECES
    const delay_dur = 0.10
    const tween_dur = 0.50
    const y_offset = 10.0
    var delay := 0.0

    var _add_piece = func(name_: String, vec_: Vector3, delay_: float) -> Vector3:
        var p = get_node(name_) as PieceBase3D
        pieces[name_] = p
        p.center_on(vec_)
        # print("@@ name_ ", name_, ", vec_ ", vec_)
        # Tween Y to create a drop effect
        var tw = p.create_tween()
        tw.tween_interval(delay_)
        var y_end = p.position.y
        var y_start = y_end + y_offset
        p.position.y = y_start
        tw.tween_property(p, "position:y", y_end, tween_dur)
        # Optional: we could interpolate the alpha of the material w/ something like this:
        # tw.tween_property(p, "mesh.material.albedo_color.a", 1, tween_dur)
        return vec_.rotated(Vector3.UP, angleInc)

    vec = _add_piece.call("PieceHR", vec, delay)
    delay += delay_dur
    vec = _add_piece.call("PieceVB", vec, delay)
    delay += delay_dur
    vec = _add_piece.call("PieceTO", vec, delay)
    delay += delay_dur
    vec = _add_piece.call("PieceJ1", vec, delay)
    delay += delay_dur
    vec = _add_piece.call("PieceTW", vec, delay)
    delay += delay_dur
    vec = _add_piece.call("PieceL1", vec, delay)
    delay += delay_dur
    vec = _add_piece.call("PieceTY1", vec, delay)
    delay += delay_dur
    vec = _add_piece.call("PieceP1", vec, delay)
    delay += delay_dur
    vec = _add_piece.call("PieceTY2", vec, delay)
    delay += delay_dur
    vec = _add_piece.call("PieceI1", vec, delay)
    delay += delay_dur
    vec = _add_piece.call("PieceW1", vec, delay)

func _tweenCamera(target_angle_y: float, target_fov: float) -> void:
    # Twin the camera from current angle Y to max Y after all pieces drop.
    const tween_dur = 0.50
    const delay = 0 # NUM_PIECES * 0.10
    var tc = create_tween()
    tc.tween_interval(delay)
    var _cam_tween = func(y):
        camAngleY = y
        _updateCamera()
    tc.tween_method(_cam_tween, camAngleY, target_angle_y, tween_dur)
    tc.parallel().tween_property(cam3d, "fov", target_fov, tween_dur)


var mousePendingEvent = null
var mouseDragging := false
var mouseRaySelected : PieceBase3D = null
var mousePressedMS := 0
func _input(event: InputEvent) -> void:
    #print("TOUCH: ", event)
    if event is InputEventScreenTouch:
        if event.pressed:
            mouseDragging = false
            mouseRaySelected = null
            mousePendingEvent = event
            mousePressedMS = Time.get_ticks_msec()
            # Next: Process raycast for selection in _physics_process
            # then follow up bellow with mouseRaySelected != null
        elif mouseRaySelected and not mouseDragging:
            # This ensure we only select on mouse/touch-up IIF there's no drag motion.
            # This gets called at the end of a piece being dragged too.
            match selectionMode:
                SelectionMode.Board:
                    _select(mouseRaySelected)
                SelectionMode.Piece:
                    if mouseRaySelected.isDragging:
                        # This was a drag, not a click.
                        mouseRaySelected.onDragEnded()
                    else:
                        # This was a click on the selected piece.
                        # print("TOUCH PIECE: ", event)
                        if selectedPiece == mouseRaySelected:
                            _deselect()
                        else:
                            _select(mouseRaySelected)
            # print("@@ RAY RESULT: ", mouseRaySelected)
            mouseRaySelected = null
    elif event is InputEventScreenDrag:
        #print("DRAG: ", event)
        var delayMS = Time.get_ticks_msec() - mousePressedMS
        if delayMS > MIN_DRAG_DELAY_MS: # prevent very short click mvt from being a drag
            match selectionMode:
                SelectionMode.Board:
                    # We're dragging the main camera
                    mouseDragging = true
                    camAngleX -= event.relative.x * EVENT_DRAG_FACTOR
                    camAngleY += event.relative.y * EVENT_DRAG_FACTOR
                    _updateCamera()
                    #print("@@ MOVED Camera: ", cam3d.position, " > ", rad_to_deg(camAngleX), " x ", rad_to_deg(camAngleY))
                SelectionMode.Piece:
                    if mouseRaySelected:
                        # We're dragging that piece
                        print("DRAG PIECE: ", mouseRaySelected, " --> ", event)
                        var intercept := _projectScreenToPlane(event.position, mouseRaySelected.position.y)
                        if intercept != Vector3.ZERO:
                            mouseRaySelected.onDragging(intercept.x, intercept.z)
                    else:
                        # We're dragging the camera while in the "piece selected" mode.
                        # We can rotate but not change the Y angle.
                        mouseDragging = true
                        camAngleX -= event.relative.x * EVENT_DRAG_FACTOR
                        _updateCamera()

func _physics_process(_delta: float) -> void:
    if not mousePendingEvent:
        return
    var event = mousePendingEvent
    mousePendingEvent = null
    var space_state = get_world_3d().direct_space_state
    var from = cam3d.project_ray_origin(event.position)
    var to = from + cam3d.project_ray_normal(event.position) * RAY_LENGTH
    var query = PhysicsRayQueryParameters3D.create(from, to)
    var rayResult = space_state.intersect_ray(query)
    if not rayResult or not "collider" in rayResult:
        return
    mouseRaySelected = null
    var collider = rayResult["collider"]
    # The collider should be a StaticBody3D inside a parent PieceBase3D.
    if not collider is StaticBody3D:
        return
    var parent = collider
    while parent != null and not parent is PieceBase3D:
        parent = parent.get_parent()
    if parent is PieceBase3D:
        mouseRaySelected = parent
        # Next: process the ray result in _input instead of in physics_process.

func _projectScreenToPlane(screenPos: Vector2, planeY: float) -> Vector3:
    # Ray from camera at screen position
    var rayOrigin : Vector3 = cam3d.project_ray_origin(screenPos)
    var rayNormal : Vector3= cam3d.project_ray_normal(screenPos)

    # Horizontal plane at y=1
    var planeOrigin := Vector3(0, planeY, 0)
    var planeNormal := Vector3.UP

    # Plane intersection on the ray line
    # https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
    var denominator : float = planeNormal.dot(rayNormal)
    # No solution if ray is parallel to the plane
    if abs(denominator) < 0.0001:
        return Vector3.ZERO
    var t : float = (planeOrigin  - rayOrigin).dot(planeNormal) / denominator

    # If t is negative, the intersection point is behind the ray origin
    if t < 0:
        return Vector3.ZERO

    # Calculate the intersection point
    var intersect : Vector3 = rayOrigin + rayNormal * t
    return intersect

func _select(piece: PieceBase3D) -> void:
    if selectionMode == SelectionMode.Board:
        camAngleYBoardMode = camAngleY
    selectionMode = SelectionMode.PieceIn
    _showRootControl(true)
    _clearSelection(func() -> void:
        selectedPiece = piece
        piece.setSelected(true, func() -> void:
            selectionMode = SelectionMode.Piece
            # Move camera to top view
            _tweenCamera(RAD_90_DEG, CAM_SELECTED_FOV)
        )
    )

func _deselect() -> void:
    selectionMode = SelectionMode.PieceOut
    _showRootControl(false)
    _clearSelection(func() -> void:
        selectionMode = SelectionMode.Board
        # Move camera back to previous angle
        _tweenCamera(camAngleYBoardMode, staticCamFov)
    )

func _clearSelection(endFunc: Callable):
    if selectedPiece == null:
        endFunc.call()
        return
    var p = selectedPiece
    selectedPiece = null
    p.setSelected(false, endFunc)

func _updateCamera():
    var vec = Vector3(staticCamDistance, 0, 0)
    camAngleY = max(-MAX_ANGLE_Y, min(MAX_ANGLE_Y, camAngleY))
    vec = vec.rotated(Vector3.BACK, camAngleY)
    vec = vec.rotated(Vector3.UP, camAngleX)
    cam3d.position = vec
    var target = CAM_LOOK_AT
    # When the camera gets close to the ground, we look at the origin.
    # Otherwise we look at CAM_LOOK_AT which is offset such that the overall
    # board appears centered in the view.
    if abs(camAngleY) < CAM_LOOK_AT_ZERO_ANGLE_Y:
        target.y *= (camAngleY / CAM_LOOK_AT_ZERO_ANGLE_Y)
    elif camAngleY < 0:
        target.y = -target.y
    cam3d.look_at(target)

func _showRootControl(show: bool) -> void:
    if rootControl.visible == show:
        return
    const tween_dur = 0.25
    var tw = rootControl.create_tween()
    tw.tween_property(rootControl, "modulate:a", 1.0 if show else 0.0, tween_dur)
    tw.tween_callback(func() -> void:
        rootControl.visible = show
    )

# ~~
