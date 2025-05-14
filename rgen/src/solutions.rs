use itertools::Itertools;
use std::fmt;
use std::fmt::Formatter;
use crate::coord::AbsYRG;

/// A solution for a single piece: piece name + rotation + its location on the board.
#[derive(Clone, PartialEq, Eq)]
pub struct Solution {
    pub key: String,
    pub angle: i32,
    pub yrg: AbsYRG,
}

impl fmt::Display for Solution {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}@{}:{}", self.key, self.angle, self.yrg)
    }
}


/// A set of solutions (all pieces/rotations/locations) in a specific order.
#[derive(Clone, PartialEq, Eq)]
pub struct Solutions {
    pub sol: Vec<Solution>,
}

impl fmt::Display for Solutions {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.sol.iter().join(","))
    }
}

// ~~
