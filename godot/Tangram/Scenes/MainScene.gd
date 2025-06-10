extends Node3D

@onready var cam3d = $Camera3D

const NUM_PIECES = 12
const RADIUS_PIECES = 5.5
const MIN_DRAG_DELAY_MS = 250
const RAY_LENGTH = 1000.0
const PI_2 = PI / 2   # 90 degrees in radians
var staticCamDistance := 0.0
var camAngleX := 0.0
var camAngleY := 0.0
var pieces = {}

func _ready() -> void:
    # Grab the initial camera setup in the scene to reuse it later.
    staticCamDistance = cam3d.position.distance_to(Vector3(0, 0, 0))
    camAngleX = atan2(cam3d.position.z, cam3d.position.x)
    camAngleY = atan2(cam3d.position.y, cam3d.position.z)
    print("@@ START Camera: ", cam3d.position, " > ", rad_to_deg(camAngleX), " x ", rad_to_deg(camAngleY))
    _updateCamera()
    _initPieces()

func _initPieces() -> void:
    var scene_ = get_tree().current_scene
    var vec = Vector3(RADIUS_PIECES, 0, 0)
    vec = vec.rotated(Vector3.UP, PI_2)
    var angleInc = -PI * 2 / NUM_PIECES

    var _add_piece = func(name: String, vec: Vector3) -> Vector3:
        var p = get_node(name) as PieceBase3D
        pieces[name] = p
        p.center_on(vec)
        print("@@ name ", name, ", vec ", vec)
        return vec.rotated(Vector3.UP, angleInc)
    vec = _add_piece.call("PieceHR", vec)
    vec = _add_piece.call("PieceVB", vec)
    vec = _add_piece.call("PieceTY1", vec)
    vec = _add_piece.call("PieceJ1", vec)
    vec = _add_piece.call("PieceTY2", vec)
    vec = _add_piece.call("PieceL1", vec)
    vec = _add_piece.call("PieceTW", vec)
    vec = _add_piece.call("PieceP1", vec)
    vec = _add_piece.call("PieceTO", vec)
    vec = _add_piece.call("PieceW1", vec)
    vec = _add_piece.call("PieceI1", vec)

var mousePendingEvent = null
var mouseRayResult = null
var mouseMotion = false
var mousePressedMS = 0
func _input(event: InputEvent) -> void:
    #print("TOUCH: ", event)
    if event is InputEventScreenTouch:
        if event.pressed:
            mouseMotion = false
            mouseRayResult = null
            mousePendingEvent = event
            mousePressedMS = Time.get_ticks_msec()
            print("@@ INPUT PENDING: ", mousePendingEvent)
            # NExt: Process raycast for selection in _physics_process
        elif mouseRayResult and not mouseMotion:
            # TBD process result of raycast for selection
            print("@@ RAY RESULT: ", mouseRayResult)
            mouseRayResult = null
    elif event is InputEventScreenDrag:
        #print("DRAG: ", event)
        var delayMS = Time.get_ticks_msec() - mousePressedMS
        if delayMS > MIN_DRAG_DELAY_MS: # prevent very short click mvt from being a drag
            mouseMotion = true
            _clearSelection()
            camAngleX -= event.relative.x / 200
            camAngleY = max(-PI_2 + 0.01, min(PI_2 - 0.01, camAngleY + event.relative.y / 200))
            _updateCamera()
            #print("@@ MOVED Camera: ", cam3d.position, " > ", rad_to_deg(camAngleX), " x ", rad_to_deg(camAngleY))

func _physics_process(delta: float) -> void:
    if mousePendingEvent:
        var event = mousePendingEvent
        mousePendingEvent = null
        var space_state = get_world_3d().direct_space_state
        var from = cam3d.project_ray_origin(event.position)
        var to = from + cam3d.project_ray_normal(event.position) * RAY_LENGTH
        var query = PhysicsRayQueryParameters3D.create(from, to)
        mouseRayResult = space_state.intersect_ray(query)
        print("@@ PHYSICS RAY RESULT: ", mouseRayResult)

func _clearSelection():
    # TBD
    pass

func _updateCamera():
    var vec = Vector3(staticCamDistance, 0, 0)
    vec = vec.rotated(Vector3.BACK, camAngleY)
    vec = vec.rotated(Vector3.UP, camAngleX)
    cam3d.position = vec
    cam3d.look_at(Vector3.ZERO)
