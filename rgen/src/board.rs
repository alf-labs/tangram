use std::fmt;
use std::fmt::Formatter;
use itertools::Itertools;
use crate::coord::{AbsYRG, Coords, N};
use crate::piece::Colors;

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

#[derive(Debug, Copy, Clone, PartialEq, Eq)]
pub struct Board {
    colors: [Colors; BOARD_SIZE],
    perm_index: i32,
    // TBD solution: Option<Solution>
    // TBD g0free, g1free
}

impl Board {
    pub fn new() -> Board {
        Board {
            colors: [Colors::Invalid; BOARD_SIZE],
            perm_index: 0,
        }
    }

    pub fn init_cells(&mut self, coords: &Coords) {
        for yrg in coords.valid_yrg.iter() {
            self.set_color(yrg, Colors::Empty);
        }
    }

    fn valid(&self, yrg: &AbsYRG) -> bool {
        // It is expected this may get called with invalid YRG values.
        let idx: i8 = yrg_to_idx!(yrg);
        idx >= 0 && idx < BOARD_SIZE as i8 && self.colors[idx as usize] != Colors::Invalid
    }

    fn occupied(&self, yrg: &AbsYRG) -> bool {
        // It is expected this may get called with invalid YRG values.
        let idx: i8 = yrg_to_idx!(yrg);
        if idx >= 0 && idx < BOARD_SIZE as i8 {
            let c = self.colors[idx as usize];
            c != Colors::Invalid && c != Colors::Empty
        } else {
            false
        }
    }

    fn get_color(&self, yrg: &AbsYRG) -> Colors {
        // Callers should validate YRG is valid before calling this. No checks here.
        let idx: i8 = yrg_to_idx!(yrg);
        self.colors[idx as usize]
    }

    fn set_color(&mut self, yrg: &AbsYRG, c: Colors) {
        // Callers should validate YRG is valid before calling this. No checks here.
        let idx: i8 = yrg_to_idx!(yrg);
        self.colors[idx as usize] = c;
        // TBD update g_free
    }
}

impl fmt::Display for Board {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.colors.iter().join(""))
    }
}

// ~~
