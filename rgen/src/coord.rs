use std::collections::HashMap;
use std::fmt;
use std::fmt::Formatter;
use crate::abs_yrg;
use crate::solutions::Solution;

pub const N: i8 = 6;
pub const N2: i8 = N/2;

/// An absolute YRG coordinate: Y/R in range [0...N-1], G in range [0,1].
#[derive(Debug, Copy, Clone, PartialEq, Eq, Hash)]
pub struct AbsYRG {
    pub y: i8,
    pub r: i8,
    pub g: i8,
}

/// A center-relative YRG coordinate: Y/R in range [-N/2...N/2-1], G in range [0,1].
#[derive(Debug, Copy, Clone, PartialEq, Eq, Hash)]
pub struct RelYRG {
    pub y: i8,
    pub r: i8,
    pub g: i8,
}

impl fmt::Display for AbsYRG {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}x{}x{}", self.y, self.r, self.g)
    }
}

impl AbsYRG {
    pub fn new(y: i8, r: i8, g: i8) -> AbsYRG {
        AbsYRG { y, r, g }
    }

    pub fn to_rel(&self) -> RelYRG {
        RelYRG { y: self.y - N2, r: self.r - N2, g: self.g }
    }
}

impl RelYRG {
    pub fn new(y: i8, r: i8, g: i8) -> RelYRG {
        RelYRG { y, r, g }
    }

    pub fn to_abs(&self) -> AbsYRG {
        AbsYRG { y: self.y + N2, r: self.r + N2, g: self.g }
    }

    pub fn offset_by(&self, offset: &AbsYRG) -> AbsYRG {
        AbsYRG { y: self.y + offset.y, r: self.r + offset.r, g: self.g }
    }
}

/// Static YRG coordinates helpers: valid YRG coordinates, rotation lookup table.
pub struct Coords {
    pub valid_yrg: Vec<AbsYRG>,
    valid_yrg_to_idx: HashMap<AbsYRG, usize>,
    rot60ccw_src: Vec<AbsYRG>,
    rot60ccw_src_to_idx: HashMap<AbsYRG, usize>,
}

impl Coords {
    pub fn new() -> Coords {
        let valid_yrg = vec![
                                      abs_yrg!(0, 0, 0), abs_yrg!(0, 0, 1), abs_yrg!(0, 1, 0), abs_yrg!(0, 1, 1), abs_yrg!(0, 2, 0), abs_yrg!(0, 2, 1), abs_yrg!(0, 3, 0),
                   abs_yrg!(1, 0, 0), abs_yrg!(1, 0, 1), abs_yrg!(1, 1, 0), abs_yrg!(1, 1, 1), abs_yrg!(1, 2, 0), abs_yrg!(1, 2, 1), abs_yrg!(1, 3, 0), abs_yrg!(1, 3, 1), abs_yrg!(1, 4, 0),
abs_yrg!(2, 0, 0), abs_yrg!(2, 0, 1), abs_yrg!(2, 1, 0), abs_yrg!(2, 1, 1), abs_yrg!(2, 2, 0), abs_yrg!(2, 2, 1), abs_yrg!(2, 3, 0), abs_yrg!(2, 3, 1), abs_yrg!(2, 4, 0), abs_yrg!(2, 4, 1), abs_yrg!(2, 5, 0),
abs_yrg!(3, 0, 1), abs_yrg!(3, 1, 0), abs_yrg!(3, 1, 1), abs_yrg!(3, 2, 0), abs_yrg!(3, 2, 1), abs_yrg!(3, 3, 0), abs_yrg!(3, 3, 1), abs_yrg!(3, 4, 0), abs_yrg!(3, 4, 1), abs_yrg!(3, 5, 0), abs_yrg!(3, 5, 1),
                   abs_yrg!(4, 1, 1), abs_yrg!(4, 2, 0), abs_yrg!(4, 2, 1), abs_yrg!(4, 3, 0), abs_yrg!(4, 3, 1), abs_yrg!(4, 4, 0), abs_yrg!(4, 4, 1), abs_yrg!(4, 5, 0), abs_yrg!(4, 5, 1),
                                      abs_yrg!(5, 2, 1), abs_yrg!(5, 3, 0), abs_yrg!(5, 3, 1), abs_yrg!(5, 4, 0), abs_yrg!(5, 4, 1), abs_yrg!(5, 5, 0), abs_yrg!(5, 5, 1),
        ];

        let mut valid_idx = HashMap::new();
        for (index, yrg) in valid_yrg.iter().enumerate() {
            valid_idx.insert(yrg.clone(), index);
        }

        // We can rotate the puzzle cells 60 degrees clockwise by mapping any cell from ROT_60_CCW_SRC (source) to VALID_YRG (destination).
        // Example: SRC[0](0,2,1) --> That means that cell (0,2,1) becomes cell (0,0,0) because VALID_YRG[0] = (0,0,0).
        let rot60ccw_src = vec![
                                      abs_yrg!(0, 2, 1), abs_yrg!(0, 3, 0), abs_yrg!(1, 3, 1), abs_yrg!(1, 4, 0), abs_yrg!(2, 4, 1), abs_yrg!(2, 5, 0), abs_yrg!(3, 5, 1),
                   abs_yrg!(0, 1, 1), abs_yrg!(0, 2, 0), abs_yrg!(1, 2, 1), abs_yrg!(1, 3, 0), abs_yrg!(2, 3, 1), abs_yrg!(2, 4, 0), abs_yrg!(3, 4, 1), abs_yrg!(3, 5, 0), abs_yrg!(4, 5, 1),
abs_yrg!(0, 0, 1), abs_yrg!(0, 1, 0), abs_yrg!(1, 1, 1), abs_yrg!(1, 2, 0), abs_yrg!(2, 2, 1), abs_yrg!(2, 3, 0), abs_yrg!(3, 3, 1), abs_yrg!(3, 4, 0), abs_yrg!(4, 4, 1), abs_yrg!(4, 5, 0), abs_yrg!(5, 5, 1),
abs_yrg!(0, 0, 0), abs_yrg!(1, 0, 1), abs_yrg!(1, 1, 0), abs_yrg!(2, 1, 1), abs_yrg!(2, 2, 0), abs_yrg!(3, 2, 1), abs_yrg!(3, 3, 0), abs_yrg!(4, 3, 1), abs_yrg!(4, 4, 0), abs_yrg!(5, 4, 1), abs_yrg!(5, 5, 0),
                   abs_yrg!(1, 0, 0), abs_yrg!(2, 0, 1), abs_yrg!(2, 1, 0), abs_yrg!(3, 1, 1), abs_yrg!(3, 2, 0), abs_yrg!(4, 2, 1), abs_yrg!(4, 3, 0), abs_yrg!(5, 3, 1), abs_yrg!(5, 4, 0),
                                      abs_yrg!(2, 0, 0), abs_yrg!(3, 0, 1), abs_yrg!(3, 1, 0), abs_yrg!(4, 1, 1), abs_yrg!(4, 2, 0), abs_yrg!(5, 2, 1), abs_yrg!(5, 3, 0),
        ];

        let mut rot60_idx = HashMap::new();
        for (index, yrg) in rot60ccw_src.iter().enumerate() {
            rot60_idx.insert(yrg.clone(), index);
        }

        Coords {
            valid_yrg,
            valid_yrg_to_idx: valid_idx,
            rot60ccw_src,
            rot60ccw_src_to_idx: rot60_idx,
        }
    }

    pub fn rot_60_ccw_yrg(&self, yrg: &RelYRG) -> RelYRG {
        let abs = yrg.to_abs();
        let index = self.rot60ccw_src_to_idx.get(&abs).unwrap();
        let yrg_dst = self.valid_yrg[*index];
        yrg_dst.to_rel()
    }
}

// ~~
