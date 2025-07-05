class_name RelYRG

var y: int
var r: int
var g: int

func _init(y_: int, r_: int, g_: int) -> void:
    y = y_
    r = r_
    g = g_

func to_abs() -> AbsYRG:
    const N2 = BoardData.N2
    return AbsYRG.new(y + N2, r + N2, g)

# ~~
