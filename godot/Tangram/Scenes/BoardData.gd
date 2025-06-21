class_name BoardData

const N = 6
const N2 = 3

const VALID_YRG = [
    [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 0],
    [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [1, 3, 0], [1, 3, 1], [1, 4, 0],
    [2, 0, 0], [2, 0, 1], [2, 1, 0], [2, 1, 1], [2, 2, 0], [2, 2, 1], [2, 3, 0], [2, 3, 1], [2, 4, 0], [2, 4, 1], [2, 5, 0],
    [3, 0, 1], [3, 1, 0], [3, 1, 1], [3, 2, 0], [3, 2, 1], [3, 3, 0], [3, 3, 1], [3, 4, 0], [3, 4, 1], [3, 5, 0], [3, 5, 1],
    [4, 1, 1], [4, 2, 0], [4, 2, 1], [4, 3, 0], [4, 3, 1], [4, 4, 0], [4, 4, 1], [4, 5, 0], [4, 5, 1],
    [5, 2, 1], [5, 3, 0], [5, 3, 1], [5, 4, 0], [5, 4, 1], [5, 5, 0], [5, 5, 1],
];


var board : Array[BoardCell] = [];
var unitY : Vector3;
var unitR : Vector3;

func _init() -> void:
    unitR = Vector3(1, 0, 0)
    unitY = Vector3(cos(PI / 3 * 2), sin(PI / 3 * 2), 0)

    for yrg in VALID_YRG:
        var abs_ = AbsYRG.new(yrg[0], yrg[1], yrg[2])
        var pos = pointYR(abs_.y, abs_.r)
        var cell = BoardCell.new(abs_, pos)
        board.append(cell)

func pointYR(y: int, r: int) -> Vector3:
    return y * unitY + r * unitR
