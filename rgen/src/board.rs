use std::fmt;
use std::fmt::Formatter;
use itertools::Itertools;
use crate::coord::{AbsYRG, Coords, N};
use crate::piece::{Colors, Shape};

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
#[derive(Debug, Copy, Clone, PartialEq, Eq)]
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
        let mut new_board = self.clone();

        for cell in shape.cells.iter() {
            let yrg = cell.offset_by(offset);

            if !new_board.valid(&yrg) {
                println!("@@ -- not valid yrg rel {} + abs {} = {}", cell, offset, yrg); // DEBUG
                return None;
            }
            if new_board.occupied(&yrg) {
                println!("@@ -- occupied yrg {} -> {}", yrg, new_board.get_color(&yrg)); // DEBUG
                return None;
            }
            // TBD: optimize by only cloning board here
            new_board.set_color(&yrg, color);
        }

        Some(new_board)
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


#[cfg(test)]
mod tests {
    use crate::abs_yrg;
    use crate::pieces::Pieces;
    use super::*;

    #[test]
    fn test_board_display_empty() {
        let coord = Coords::new();
        let b = Board::new(42, &coord);
        assert_eq!(format!("{}", b), "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee");
    }

    #[test]
    fn test_place_piece() {
        let coords = Coords::new();
        let pieces = Pieces::new(&coords);

        // Simulate this permutation:
        // HR@0:2x4x0 i1@0:2x1x0 W1@0:0x0x0 P1@0:4x3x1 VB@300:0x3x0 J1@0:1x1x1
        // L2@0:3x2x1 TO@180:4x2x0 TW@0:5x4x0 TY@240:5x4x0 TY@300:4x2x0

        let empty_board = Board::new(156954, &coords);

        // HR@0:2x4x0
        let mut piece = pieces.by_str("HR").unwrap();
        let mut shape = piece.shape(0);
        let mut result = empty_board.place_piece(shape, piece.color, &abs_yrg!(2, 4, 0)).unwrap();
        assert_eq!(format!("{}", result), "eeeeeeeeeeeeeeeeeeeeeeeeRRReeeeeeeeRRReeeeeeeeeeeeeeee");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // i1@0:2x1x0
        piece = pieces.by_str("i1").unwrap();
        shape = piece.shape(0);
        result = result.place_piece(shape, piece.color, &abs_yrg!(2, 1, 0)).unwrap();
        assert_eq!(format!("{}", result), "eeeeeeeeeeeeeeeeRRRRRReeRRReeeeeeeeRRReeeeeeeeeeeeeeee");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // W1@0:0x0x0
        piece = pieces.by_str("W1").unwrap();
        shape = piece.shape(0);
        result = result.place_piece(shape, piece.color, &abs_yrg!(0, 0, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBeeeeBBBeeeeeeRRRRRReeRRReeeeeeeeRRReeeeeeeeeeeeeeee");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // P1@0:4x3x1
        piece = pieces.by_str("P1").unwrap();
        shape = piece.shape(0);
        result = result.place_piece(shape, piece.color, &abs_yrg!(4, 3, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBeeeeBBBeeeeeeRRRRRReeRRReeeeeeeeRRReeeeRRRRReeeeeeR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // VB@300:0x3x0
        piece = pieces.by_str("VB").unwrap();
        shape = piece.shape(300);
        result = result.place_piece(shape, piece.color, &abs_yrg!(0, 3, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBeeeeBBRRRRRReeRRReeeeeeeeRRReeeeRRRRReeeeeeR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // J1@0:1x1x1
        piece = pieces.by_str("J1").unwrap();
        shape = piece.shape(0);
        result = result.place_piece(shape, piece.color, &abs_yrg!(1, 1, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBOOOOBBRRRRRROORRReeeeeeeeRRReeeeRRRRReeeeeeR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // L2@0:3x2x1
        piece = pieces.by_str("L2").unwrap();
        shape = piece.shape(0);
        result = result.place_piece(shape, piece.color, &abs_yrg!(3, 2, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBOOOOBBRRRRRROORRReeeYYYYYRRReeYeRRRRReeeeeeR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // TW@0:5x4x0
        piece = pieces.by_str("TW").unwrap();
        shape = piece.shape(0);
        result = result.place_piece(shape, piece.color, &abs_yrg!(5, 4, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBOOOOBBRRRRRROORRReeeYYYYYRRReeYeRRRRReeeWWWR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // TO@180:4x2x0
        piece = pieces.by_str("TO").unwrap();
        shape = piece.shape(180);
        result = result.place_piece(shape, piece.color, &abs_yrg!(4, 2, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRReeYeRRRRReeeWWWR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // TY@240:5x4x0
        piece = pieces.by_str("TY").unwrap();
        shape = piece.shape(240);
        result = result.place_piece(shape, piece.color, &abs_yrg!(5, 4, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRReeYYRRRRReYYWWWR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // TY@300:4x2x0
        piece = pieces.by_str("TY").unwrap();
        shape = piece.shape(300);
        let finalb = result.place_piece(shape, piece.color, &abs_yrg!(4, 2, 0)).unwrap();
        assert_eq!(format!("{}", finalb), "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");
    }

    fn assert_board_overlaps(board: Board, expected: &str) {
        let actual = &format!("{}", board)[..];
        assert_eq!(actual.len(), expected.len());
        for (a, e) in actual.chars().zip(expected.chars()) {
            if a != 'e' {
                assert_eq!(a, e);
            }
        }
    }
}

// ~~
