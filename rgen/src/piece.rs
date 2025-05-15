use std::collections::HashMap;
use std::fmt;
use std::fmt::Formatter;
use itertools::Itertools;
use crate::board::Board;
use crate::coord::{AbsYRG, Coords, RelYRG, N};
use crate::{abs_yrg, rel_yrg};

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
    pub positions: Vec<AbsYRG>,
}

impl Shape {

    pub fn new(cells: Vec<RelYRG>) -> Shape {
        Shape { cells, positions: vec![] }
    }

    /// Recompute the shape such that the first cell always has Y=0/R=0.
    /// The G coordinates are untouched.
    pub fn recenter(&self) -> Shape {
        let y_offset = self.cells[0].y;
        let r_offset = self.cells[0].r;

        let mut new_cells = Vec::new();
        for src in self.cells.iter() {
            let dst = rel_yrg!(src.y - y_offset, src.r - r_offset, src.g);
            new_cells.push(dst);
        }

        // This shape does not have its valid positions computed yet.
        Shape::new(new_cells)
    }

    /// Rotates the shape by 60 degrees CCW.
    pub fn rotate_60_ccw(&self, coords: &Coords) -> Shape {
        let mut rot_cells = Vec::new();
        for src in self.cells.iter() {
            let dst = coords.rot_60_ccw_yrg(src);
            rot_cells.push(dst);
        }

        // This shape does not have its valid positions computed yet.
        Shape::new(rot_cells)
    }

    /// Precomputes all the positions where this shape can fit on a board.
    /// This is a fairly expensive operation so we don't do it automatically
    /// in the new() method. It needs to be invoked once the shape is rotated
    /// and centered.
    pub fn precompute_positions(&self, coords: &Coords) -> Shape {
        let board = Board::new(0, &coords);
        let mut positions = Vec::new();

        for y in 0..N {
            for r in 0..N {
                for g in 0..=1i8 {
                    let yrg = abs_yrg!(y, r, g);
                    let result = board.place_piece(self, Colors::Black, &yrg);
                    match result {
                        None => {}
                        Some(_) => {
                            positions.push(yrg);
                        }
                    }
                }
            }
        }

        Shape { cells: self.cells.clone(), positions }
    }
}

impl fmt::Display for Shape {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.cells.iter().join(","))
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
        map.insert(0, Shape::new(cells));
        Piece { key, color, max_rot, shapes: map }
    }

    /// Precompute shapes for each possible rotation, as well as all valid positions
    /// for the rotated shape on the board.
    pub fn precompute_shapes(&mut self, coords: &Coords) {
        let mut shape = self.shapes.get(&0).unwrap().clone();
        self.shapes.insert(0, shape.recenter().precompute_positions(coords));

        if self.max_rot > 0 {

            for angle in (60..=self.max_rot).step_by(60) {
                let new_shape = shape.rotate_60_ccw(coords);
                self.shapes.insert(angle, new_shape.recenter().precompute_positions(coords));
                shape = new_shape;
            }
        }
    }

    pub fn shape(&self, angle: i32) -> &Shape {
        self.shapes.get(&angle).unwrap()
    }
}



#[cfg(test)]
mod tests {
    use crate::rel_yrg;
    use super::*;

    //noinspection DuplicatedCode
    #[test]
    fn test_piece_i1_rotation() {
        let coord = Coords::new();

        let mut p = Piece::new(
            Piece::to_key("i1"),
            Colors::Red,
            120,
            vec![
                rel_yrg!(0, -1, 0), rel_yrg!(0, -1, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1),
            ],
        );

        p.precompute_shapes(&coord);

        // Python gen validation:
        // @@ ROT i1@0 ([(0, -1, 0), (0, -1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1)], [3, 3])
        // @@ ROT i1@60 ([(1, 0, 1), (0, 0, 0), (0, 0, 1), (-1, 0, 0), (-1, 0, 1), (-2, 0, 0)], [3, 3])
        // @@ ROT i1@120 ([(0, 1, 0), (0, 0, 1), (-1, 0, 0), (-1, -1, 1), (-2, -1, 0), (-2, -2, 1)], [3, 3])
        // Note that the new versions always start on (0,0,0) or (0,0,1).

        let mut s = p.shape(0);
        assert_eq!(format!("{}", s), "0.0.0,0.0.1,0.1.0,0.1.1,0.2.0,0.2.1");
        assert_eq!(s.positions, vec![
            abs_yrg!(0, 0, 0),
            abs_yrg!(1, 0, 0), abs_yrg!(1, 1, 0),
            abs_yrg!(2, 0, 0), abs_yrg!(2, 1, 0), abs_yrg!(2, 2, 0),
            abs_yrg!(3, 1, 0), abs_yrg!(3, 2, 0), abs_yrg!(3, 3, 0),
                               abs_yrg!(4, 2, 0), abs_yrg!(4, 3, 0),
                                                  abs_yrg!(5, 3, 0),
        ]);

        s = p.shape(60);
        assert_eq!(format!("{}", s), "0.0.1,-1.0.0,-1.0.1,-2.0.0,-2.0.1,-3.0.0");
        assert_eq!(s.positions.len(), 1+2+3+3+2+1);

        s = p.shape(120);
        assert_eq!(format!("{}", s), "0.0.0,0.-1.1,-1.-1.0,-1.-2.1,-2.-2.0,-2.-3.1");
        assert_eq!(s.positions.len(), 1+2+3+3+2+1);
    }

    //noinspection DuplicatedCode
    #[test]
    fn test_piece_vb_rotation() {
        let coord = Coords::new();

        let mut p = Piece::new(
            Piece::to_key("VB"),
            Colors::Black,
            300,
            vec![
                rel_yrg!(1, 0, 0), rel_yrg!(1, 0, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1),
            ],
        );

        p.precompute_shapes(&coord);

        // Python gen validation:
        // @@ ROT VB@0 ([(1, 0, 0), (1, 0, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1)], [3, 3])
        // @@ ROT VB@60 ([(1, 1, 1), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (-1, 0, 1), (-2, 0, 0)], [3, 3])
        // @@ ROT VB@120 ([(-1, 1, 0), (-1, 0, 1), (-1, 0, 0), (-1, -1, 1), (-2, -1, 0), (-2, -2, 1)], [3, 3])
        // @@ ROT VB@180 ([(-2, -1, 1), (-2, -1, 0), (-1, -1, 1), (-1, -1, 0), (-1, -2, 1), (-1, -2, 0)], [3, 3])
        // @@ ROT VB@240 ([(-2, -2, 0), (-1, -2, 1), (-1, -1, 0), (0, -1, 1), (0, -1, 0), (1, -1, 1)], [3, 3])
        // @@ ROT VB@300 ([(0, -2, 1), (0, -1, 0), (0, -1, 1), (0, 0, 0), (1, 0, 1), (1, 1, 0)], [3, 3])
        // Note that the new versions always start on (0,0,0) or (0,0,1).

        let mut s = p.shape(0);
        assert_eq!(format!("{}", s), "0.0.0,0.0.1,-1.0.0,-1.0.1,-1.1.0,-1.1.1");

        s = p.shape(60);
        assert_eq!(format!("{}", s), "0.0.1,-1.0.0,-1.-1.1,-2.-1.0,-2.-1.1,-3.-1.0");

        s = p.shape(120);
        assert_eq!(format!("{}", s), "0.0.0,0.-1.1,0.-1.0,0.-2.1,-1.-2.0,-1.-3.1");

        s = p.shape(180);
        assert_eq!(format!("{}", s), "0.0.1,0.0.0,1.0.1,1.0.0,1.-1.1,1.-1.0");

        s = p.shape(240);
        assert_eq!(format!("{}", s), "0.0.0,1.0.1,1.1.0,2.1.1,2.1.0,3.1.1");

        s = p.shape(300);
        assert_eq!(format!("{}", s), "0.0.1,0.1.0,0.1.1,0.2.0,1.2.1,1.3.0");
    }
}

// ~~
