class_name BoardCell

enum Colors { Invalid, Empty, White, Orange, Yellow, Red, Black }

var yrg: AbsYRG
var color: Colors = Colors.Invalid
var pos: Vector3 = Vector3.ZERO

func _init(yrg_ : AbsYRG, pos_: Vector3) -> void:
    yrg = yrg_
    pos = pos_


# ~~
