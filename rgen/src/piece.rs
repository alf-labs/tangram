use std::collections::HashMap;
use std::fmt;
use std::fmt::Formatter;
use crate::coord::{Coords, RelYRG};

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
    Empty = b'e',
    // Special marker for an out-of-bounds board cell
    Invalid = b'.',
}

impl fmt::Display for Colors {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        let c = char::from(*self as u8);
        write!(f, "{}", c)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Shape {
    pub cells: Vec<RelYRG>,
}

impl Shape {
    pub fn rotate_60_ccw(&self, coords: &Coords) -> Shape {
        let mut rot_cells = Vec::new();
        for src in self.cells.iter() {
            let dst = coords.rot_60_ccw_yrg(src);
            rot_cells.push(dst);
        }

        Shape { cells: rot_cells }
    }
}


/// The type of a piece key/name is a 2-character ASCII.
pub type PieceKey = [char; 2];


/// The static definition for one piece: name, color, shape. Symmetry creates multiple pieces.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Piece {
    pub key: PieceKey,
    pub color: Colors,
    pub max_rot: i32,
    shapes: HashMap<i32, Shape>,
}

impl Piece {
    //noinspection RsSelfConvention
    pub fn to_key(name: &str) -> PieceKey {
        let mut char_iter = name.chars();
        [char_iter.next().unwrap(), char_iter.next().unwrap()]
    }

    pub fn new(key: PieceKey, color: Colors, max_rot: i32, cells: Vec<RelYRG>) -> Piece {
        let mut map = HashMap::new();
        map.insert(0, Shape { cells });
        Piece { key, color, max_rot, shapes: map }
    }

    pub fn init_rotations(&mut self, coords: &Coords) {
        if self.max_rot > 0 {
            let mut shape = self.shapes.get(&0).unwrap().clone();

            for angle in (60..=self.max_rot).step_by(60) {
                let new_shape = shape.rotate_60_ccw(coords);
                self.shapes.insert(angle, new_shape.clone());
                shape = new_shape;
            }
        }
    }

    pub fn shape(&self, angle: i32) -> &Shape {
        self.shapes.get(&angle).unwrap()
    }
}

// ~~
