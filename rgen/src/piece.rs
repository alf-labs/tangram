use std::fmt;
use std::fmt::Formatter;
use crate::coord::RelYRG;

/// All possible colors for a board cell.
#[derive(Debug, Copy, Clone, PartialEq, Eq)]
#[repr(u8)]
pub enum Colors {
    Red = b'R',
    Yellow = b'Y',
    Orange = b'O',
    Black = b'B',
    White = b'W',
    // Special marker for a cell not filled yet in a board
    Empty = b'E',
    // Special marker for an out-of-bounds board cell
    Invalid = b'!',
}

impl fmt::Display for Colors {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        let c = char::from(*self as u8);
        write!(f, "{}", c)
    }
}

#[derive(Debug)]
pub struct Shape {
    cells: Vec<RelYRG>,
}

/// The static definition for one piece: name, color, shape. Symmetry creates multiple pieces.
#[derive(Debug)]
pub struct Piece {
    pub name: String,
    pub color: Colors,
    pub max_rot: i32,
    shape: Shape,
}

impl Piece {
    pub fn new(name: String, color: Colors, max_rot: i32, cells: Vec<RelYRG>) -> Piece {
        Piece { name, color, max_rot, shape : Shape { cells } }
    }
}

// ~~
