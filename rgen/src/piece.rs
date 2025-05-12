use crate::coord::RelYRG;

#[derive(Debug, Copy, Clone, PartialEq, Eq)]
#[repr(u8)]
pub enum Colors {
    Red = b'R',
    Yellow = b'Y',
    Orange = b'O',
    Black = b'B',
    White = b'W',
}

pub struct Shape {
    cells: Vec<RelYRG>,
}

pub struct Piece {
    name: String,
    color: Colors,
    max_rot: i32,
    shape: Shape,
}

impl Piece {
    pub fn new(name: String, color: Colors, max_rot: i32, cells: Vec<RelYRG>) -> Piece {
        Piece { name, color, max_rot, shape : Shape { cells } }
    }
}

// ~~
