extends Node3D

@onready var cam3d = $Camera3D
const MIN_DRAG_DELAY_MS = 250
var staticCamDistance := 0.0
var camAngleX := 0.0
var camAngleY := 0.0


func _ready() -> void:
    # Grab the initial camera setup in the scene to reuse it later.
    staticCamDistance = cam3d.position.distance_to(Vector3(0, 0, 0))
    camAngleX = atan2(cam3d.position.z, cam3d.position.x)
    camAngleY = atan2(cam3d.position.y, cam3d.position.z)
    print("@@ START Camera: ", cam3d.position, " > ", rad_to_deg(camAngleX), " x ", rad_to_deg(camAngleY))
    _updateCamera()

var mousePendingEvent = null
var mouseRayResult = null
var mouseMotion = false
var mousePressedMS = 0
func _input(event: InputEvent) -> void:
    print("TOUCH: ", event)
    if event is InputEventScreenTouch:
        if event.pressed:
            mouseMotion = false
            mouseRayResult = null
            mousePendingEvent = event
            mousePressedMS = Time.get_ticks_msec()
            # TBD raycast for selection in _physics_process
        elif mouseRayResult and not mouseMotion:
            # TBD process result of raycast for selection
            pass
    elif event is InputEventScreenDrag:
        #print("DRAG: ", event)
        var delayMS = Time.get_ticks_msec() - mousePressedMS
        if delayMS > MIN_DRAG_DELAY_MS: # prevent very short click mvt from being a drag
            mouseMotion = true
            _clearSelection()
            camAngleX -= event.relative.x / 100
            camAngleY += event.relative.y / 100
            _updateCamera()
            #print("@@ MOVED Camera: ", cam3d.position, " > ", rad_to_deg(camAngleX), " x ", rad_to_deg(camAngleY))

func _physics_process(delta: float) -> void:
    if mousePendingEvent:
        pass
        # TBD raycast for selection in _physics_process
        # and store result in mouseRayResult

func _clearSelection():
    # TBD
    pass

func _updateCamera():
    var vec = Vector3(staticCamDistance, 0, 0)
    vec = vec.rotated(Vector3.BACK, camAngleY)
    vec = vec.rotated(Vector3.UP, camAngleX)
    cam3d.position = vec
    cam3d.look_at(Vector3.ZERO)
