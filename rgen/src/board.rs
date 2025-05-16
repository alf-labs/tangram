use crate::coord::{AbsYRG, Coords, N};
use crate::piece::{Colors, Shape};
use itertools::Itertools;
use regex::Regex;
use std::fmt;
use std::fmt::Formatter;

pub const BOARD_SIZE: usize = (2 * N * N) as usize;

// Converts an AbsYRG to a BOARD_SIZE index.
// Note: caller could give an invalid AbsYRG with negative y/r coords
// thus here we return an i8 and code needs to check 0..SIZE before
// converting to usize.
macro_rules! yrg_to_idx {
    ($abs_yrg:expr) => {
        2 * N * $abs_yrg.y + 2 * $abs_yrg.r + $abs_yrg.g
    }
}

/// A board contains a model of all "colors" associated with each board physical cell.
#[derive(Copy, Clone, PartialEq, Eq)]
pub struct Board {
    colors: [Colors; BOARD_SIZE],
    pub perm_index: i32,
    // TBD solution: Option<Solution>
    // TBD g0free, g1free
}

impl Board {
    pub fn new(perm_index: i32, coords: &Coords) -> Board {
        let mut board = Board {
            colors: [Colors::Invalid; BOARD_SIZE],
            perm_index,
        };
        for yrg in coords.valid_yrg.iter() {
            board.set_color(yrg, Colors::Empty);
        }

        board
    }

    pub fn valid(&self, yrg: &AbsYRG) -> bool {
        // It is expected this may get called with invalid YRG values.
        let idx: i8 = yrg_to_idx!(yrg);
        idx >= 0 && idx < BOARD_SIZE as i8 && self.colors[idx as usize] != Colors::Invalid
    }

    pub fn occupied(&self, yrg: &AbsYRG) -> bool {
        // It is expected this may get called with invalid YRG values.
        let idx: i8 = yrg_to_idx!(yrg);
        if idx >= 0 && idx < BOARD_SIZE as i8 {
            let c = self.colors[idx as usize];
            c != Colors::Invalid && c != Colors::Empty
        } else {
            false
        }
    }

    #[allow(dead_code)]
    pub fn get_color(&self, yrg: &AbsYRG) -> Colors {
        // Callers should validate YRG is valid before calling this. No checks here.
        let idx: i8 = yrg_to_idx!(yrg);
        self.colors[idx as usize]
    }

    pub fn set_color(&mut self, yrg: &AbsYRG, c: Colors) {
        // Callers should validate YRG is valid before calling this. No checks here.
        let idx: i8 = yrg_to_idx!(yrg);
        self.colors[idx as usize] = c;
        // TBD update g_free
    }

    pub fn place_piece(&self, shape: &Shape, color: Colors, offset: &AbsYRG) -> Option<Board> {
        // Cells with G=0 and G=1 are not compatible. The piece must be properly aligned.
        if offset.g != shape.cells[0].g {
            return None;
        }

        // Micro-optimization: only clone the board once we have at least one new color to add.
        // Not sure if there's a better way to write this. This only provides a modest 2~3%
        // increase in pps.
        let mut new_board : Option<Board> = None;

        for cell in shape.cells.iter() {
            let yrg = cell.offset_by(offset);

            if !self.valid(&yrg) {
                return None;
            }
            if self.occupied(&yrg) {
                return None;
            }

            match &mut new_board {
                None => {
                    new_board = Some(self.clone());
                    let board = new_board.as_mut().unwrap();
                    board.set_color(&yrg, color);
                }
                Some(board) => {
                    board.set_color(&yrg, color);
                }
            };
        }

        match &new_board {
            None => {}
            Some(board  ) => {
                // The piece fits at the desired location.
                // Now validate that we are not leaving 1-single empty cells around.
                for yrg in shape.adjacents.iter() {
                    let abs = yrg.offset_by(offset);
                    if board.valid(&abs) {
                        if !board.occupied(&abs) {
                            if board.surrounded(&abs) {
                                return None;
                            }
                        }
                    }
                }
            }
        };

        new_board
    }

    /// Checks whether all valid surrounding cells are occupied.
    fn surrounded(&self, abs_yrg: &AbsYRG) -> bool {
        let mut num_occupied = 0;
        let mut num_cells = 0;

        for adj in Coords::compute_adjacents(&abs_yrg.to_rel()) {
            let abs_adj = adj.to_abs();
            if self.valid(&abs_adj) {
                num_cells += 1;
                if self.occupied(&abs_adj) {
                    num_occupied += 1;
                }
            }
        }

        // All valid surrounding cells are occupied.
        num_occupied == num_cells
    }
}

impl fmt::Display for Board {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}",
               self.colors
                   .iter()
                   .filter(|&c| *c != Colors::Invalid)
                   .join(""))
    }
}

impl fmt::Debug for Board {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        let repr = self.colors
            .iter()
            .join("");

        let dots = Regex::new(r"\.+").unwrap();
        let result = dots.replace_all(&*repr, ".");

        write!(f, "{}", result)
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::abs_yrg;
    use crate::pieces::Pieces;

    #[test]
    fn test_board_display_empty() {
        let coord = Coords::new();
        let b = Board::new(42, &coord);

        // The Display format only shows each cell color.
        assert_eq!(format!("{}", b), "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee");

        // The Debug format also adds line boundaries.
        assert_eq!(format!("{:?}", b), "eeeeeee.eeeeeeeee.eeeeeeeeeee.eeeeeeeeeee.eeeeeeeee.eeeeeee");
    }

    #[test]
    fn test_place_piece_single() {
        let coords = Coords::new();
        let pieces = Pieces::new(&coords);

        let empty = Board::new(42, &coords);

        let piece = pieces.by_str("VB").unwrap();
        let mut shape = piece.shape(0);

        // The VB piece at its default rotation can only fit on the top line in 2 spots,
        // at 100 and 110. It's out of bounds anywhere on the first row, and at 120, 130, and 140.
        // It cannot fit on any starting position G=1 as it's oriented for G=0.

        let mut invalid = empty.place_piece(shape, piece.color, &abs_yrg!(0, 0, 0));
        assert_eq!(invalid, None);

        let mut result = empty.place_piece(shape, piece.color, &abs_yrg!(1, 0, 0)).unwrap();
        assert_eq!(format!("{:?}", result), "BBBBeee.BBeeeeeee.eeeeeeeeeee.eeeeeeeeeee.eeeeeeeee.eeeeeee");

        invalid = empty.place_piece(shape, piece.color, &abs_yrg!(1, 0, 1));
        assert_eq!(invalid, None);

        result = empty.place_piece(shape, piece.color, &abs_yrg!(1, 1, 0)).unwrap();
        assert_eq!(format!("{:?}", result), "eeBBBBe.eeBBeeeee.eeeeeeeeeee.eeeeeeeeeee.eeeeeeeee.eeeeeee");

        invalid = empty.place_piece(shape, piece.color, &abs_yrg!(1, 1, 1));
        assert_eq!(invalid, None);

        invalid = empty.place_piece(shape, piece.color, &abs_yrg!(1, 2, 0));
        assert_eq!(invalid, None);

        invalid = empty.place_piece(shape, piece.color, &abs_yrg!(1, 2, 1));
        assert_eq!(invalid, None);

        invalid = empty.place_piece(shape, piece.color, &abs_yrg!(1, 3, 0));
        assert_eq!(invalid, None);

        // Now try again with the VB piece rotated by 300 degrees.
        // This time it can only fit on cells with G=1, at locations 001 and 011,
        // it's out of bounds at 021.

        shape = piece.shape(300);

        invalid = empty.place_piece(shape, piece.color, &abs_yrg!(0, 0, 0));
        assert_eq!(invalid, None);

        result = empty.place_piece(shape, piece.color, &abs_yrg!(0, 0, 1)).unwrap();
        assert_eq!(format!("{:?}", result), "eBBBBee.eeeeeBBee.eeeeeeeeeee.eeeeeeeeeee.eeeeeeeee.eeeeeee");

        invalid = empty.place_piece(shape, piece.color, &abs_yrg!(0, 1, 0));
        assert_eq!(invalid, None);

        result = empty.place_piece(shape, piece.color, &abs_yrg!(0, 1, 1)).unwrap();
        assert_eq!(format!("{:?}", result), "eeeBBBB.eeeeeeeBB.eeeeeeeeeee.eeeeeeeeeee.eeeeeeeee.eeeeeee");

        invalid = empty.place_piece(shape, piece.color, &abs_yrg!(0, 2, 0));
        assert_eq!(invalid, None);


        invalid = empty.place_piece(shape, piece.color, &abs_yrg!(0, 2, 1));
        assert_eq!(invalid, None);

        invalid = empty.place_piece(shape, piece.color, &abs_yrg!(0, 3, 0));
        assert_eq!(invalid, None);
    }

    #[test]
    fn test_place_piece_gap() {
        let coords = Coords::new();
        let pieces = Pieces::new(&coords);

        // One of the heuristics is to detect whether placing a piece creates a gap of
        // one cell that will be impossible to fill later.

        let empty = Board::new(42, &coords);

        // HR@0:0x0x0
        let mut piece = pieces.by_str("HR").unwrap();
        let mut shape = piece.shape(0);
        let board = empty.place_piece(shape, piece.color, &abs_yrg!(0, 0, 0)).unwrap();
        assert_eq!(format!("{:?}", board), "RRReeee.eRRReeeee.eeeeeeeeeee.eeeeeeeeeee.eeeeeeeee.eeeeeee");

        piece = pieces.by_str("TW").unwrap();
        shape = piece.shape(0);
        let invalid = board.place_piece(shape, piece.color, &abs_yrg!(0, 2, 0));
        assert_eq!(invalid, None);
        // The board would look like this: "RRReWWW.eRRReeeee.eeeeeeeeeee.eeeeeeeeeee.eeeeeeeee.eeeeeee"
    }

    #[test]
    fn test_place_piece_all_permutations() {
        let coords = Coords::new();
        let pieces = Pieces::new(&coords);

        // Simulate this Python gen permutation:
        // HR@0:2x4x0 i1@0:2x1x0 W1@0:0x0x0 P1@0:4x3x1 VB@300:0x3x0 J1@0:1x1x1
        // L2@0:3x2x1 TO@180:4x2x0 TW@0:5x4x0 TY@240:5x4x0 TY@300:4x2x0
        //
        // Note that the coordinates are slightly different in rgen because each piece shape
        // is recentered to start on a (0,0) relative cell.

        let empty = Board::new(156954, &coords);

        // HR@0:2x4x0
        let mut piece = pieces.by_str("HR").unwrap();
        let mut shape = piece.shape(0);
        assert!(shape.positions.contains(&abs_yrg!(2, 4, 0)));
        let mut result = empty.place_piece(shape, piece.color, &abs_yrg!(2, 4, 0)).unwrap();
        assert_eq!(format!("{:?}", result), "eeeeeee.eeeeeeeee.eeeeeeeeRRR.eeeeeeeeRRR.eeeeeeeee.eeeeeee");
        assert_board_overlaps(result,       "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.YYYYRRRRR.YYYWWWR");

        // i1@0:2x1x0
        piece = pieces.by_str("i1").unwrap();
        shape = piece.shape(0);
        assert!(shape.positions.contains(&abs_yrg!(2, 0, 0)));
        result = result.place_piece(shape, piece.color, &abs_yrg!(2, 0, 0)).unwrap();
        assert_eq!(format!("{:?}", result), "eeeeeee.eeeeeeeee.RRRRRReeRRR.eeeeeeeeRRR.eeeeeeeee.eeeeeee");
        assert_board_overlaps(result,       "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.YYYYRRRRR.YYYWWWR");

        // W1@0:0x0x0
        piece = pieces.by_str("W1").unwrap();
        shape = piece.shape(0);
        assert!(shape.positions.contains(&abs_yrg!(1, 1, 0)));
        result = result.place_piece(shape, piece.color, &abs_yrg!(1, 1, 0)).unwrap();
        assert_eq!(format!("{:?}", result), "BBBeeee.BBBeeeeee.RRRRRReeRRR.eeeeeeeeRRR.eeeeeeeee.eeeeeee");
        assert_board_overlaps(result,       "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.YYYYRRRRR.YYYWWWR");

        // P1@0:4x3x1
        piece = pieces.by_str("P1").unwrap();
        shape = piece.shape(0);
        assert!(shape.positions.contains(&abs_yrg!(4, 3, 1)));
        result = result.place_piece(shape, piece.color, &abs_yrg!(4, 3, 1)).unwrap();
        assert_eq!(format!("{:?}", result), "BBBeeee.BBBeeeeee.RRRRRReeRRR.eeeeeeeeRRR.eeeeRRRRR.eeeeeeR");
        assert_board_overlaps(result,       "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.YYYYRRRRR.YYYWWWR");

        // VB@300:0x3x0
        piece = pieces.by_str("VB").unwrap();
        shape = piece.shape(300);
        assert!(shape.positions.contains(&abs_yrg!(0, 1, 1)));
        result = result.place_piece(shape, piece.color, &abs_yrg!(0, 1, 1)).unwrap();
        assert_eq!(format!("{:?}", result), "BBBBBBB.BBBeeeeBB.RRRRRReeRRR.eeeeeeeeRRR.eeeeRRRRR.eeeeeeR");
        assert_board_overlaps(result,       "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.YYYYRRRRR.YYYWWWR");

        // J1@0:1x1x1
        piece = pieces.by_str("J1").unwrap();
        shape = piece.shape(0);
        assert!(shape.positions.contains(&abs_yrg!(1, 1, 1)));
        result = result.place_piece(shape, piece.color, &abs_yrg!(1, 1, 1)).unwrap();
        assert_eq!(format!("{:?}", result), "BBBBBBB.BBBOOOOBB.RRRRRROORRR.eeeeeeeeRRR.eeeeRRRRR.eeeeeeR");
        assert_board_overlaps(result,       "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.YYYYRRRRR.YYYWWWR");

        // L2@0:3x2x1
        piece = pieces.by_str("L2").unwrap();
        shape = piece.shape(0);
        assert!(shape.positions.contains(&abs_yrg!(4, 2, 1)));
        result = result.place_piece(shape, piece.color, &abs_yrg!(4, 2, 1)).unwrap();
        assert_eq!(format!("{:?}", result), "BBBBBBB.BBBOOOOBB.RRRRRROORRR.eeeYYYYYRRR.eeYeRRRRR.eeeeeeR");
        assert_board_overlaps(result,       "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.YYYYRRRRR.YYYWWWR");

        // TW@0:5x4x0
        piece = pieces.by_str("TW").unwrap();
        shape = piece.shape(0);
        assert!(shape.positions.contains(&abs_yrg!(5, 4, 0)));
        result = result.place_piece(shape, piece.color, &abs_yrg!(5, 4, 0)).unwrap();
        assert_eq!(format!("{:?}", result), "BBBBBBB.BBBOOOOBB.RRRRRROORRR.eeeYYYYYRRR.eeYeRRRRR.eeeWWWR");
        assert_board_overlaps(result,       "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.YYYYRRRRR.YYYWWWR");

        // TO@180:4x2x0
        piece = pieces.by_str("TO").unwrap();
        shape = piece.shape(180);
        assert!(shape.positions.contains(&abs_yrg!(3, 1, 1)));
        result = result.place_piece(shape, piece.color, &abs_yrg!(3, 1, 1)).unwrap();
        assert_eq!(format!("{:?}", result), "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.eeYeRRRRR.eeeWWWR");
        assert_board_overlaps(result,       "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.YYYYRRRRR.YYYWWWR");

        // TY@240:5x4x0
        piece = pieces.by_str("TY").unwrap();
        shape = piece.shape(240);
        assert!(shape.positions.contains(&abs_yrg!(4, 3, 0)));
        result = result.place_piece(shape, piece.color, &abs_yrg!(4, 3, 0)).unwrap();
        assert_eq!(format!("{:?}", result), "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.eeYYRRRRR.eYYWWWR");
        assert_board_overlaps(result,       "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.YYYYRRRRR.YYYWWWR");

        // TY@300:4x2x0
        piece = pieces.by_str("TY").unwrap();
        shape = piece.shape(300);
        assert!(shape.positions.contains(&abs_yrg!(4, 1, 1)));
        let finalb = result.place_piece(shape, piece.color, &abs_yrg!(4, 1, 1)).unwrap();
        assert_eq!(format!("{:?}", finalb), "BBBBBBB.BBBOOOOBB.RRRRRROORRR.OOOYYYYYRRR.YYYYRRRRR.YYYWWWR");
    }

    fn assert_board_overlaps(board: Board, expected: &str) {
        let actual = &format!("{:?}", board)[..];
        assert_eq!(actual.len(), expected.len());
        for (a, e) in actual.chars().zip(expected.chars()) {
            if a != 'e' {
                assert_eq!(a, e);
            }
        }
    }
}

// ~~
