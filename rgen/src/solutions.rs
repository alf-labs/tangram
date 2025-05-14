use itertools::Itertools;
use std::fmt;
use std::fmt::Formatter;
use crate::abs_yrg;
use crate::coord::AbsYRG;
use crate::permutations::Permutation;
use crate::pieces::MAX_PERM_SIZE;

/// A solution for a single piece: piece name + rotation + its location on the board.
#[derive(Copy, Clone, PartialEq, Eq)]
pub struct Solution {
    pub key: [char; 2],
    pub angle: i32,
    pub yrg: AbsYRG,
}

impl Solution {
    pub fn new() -> Solution {
        Solution {
            key: ['-'; 2],
            angle: 0,
            yrg: abs_yrg!(0, 0, 0),
        }
    }
}

impl fmt::Display for Solution {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}{}@{}:{}", self.key[0], self.key[1], self.angle, self.yrg)
    }
}


/// A set of solutions (all pieces/rotations/locations) in a specific order.
#[derive(Copy, Clone, PartialEq, Eq)]
pub struct Solutions {
    pub sol: [Solution; MAX_PERM_SIZE],
    pub size: usize,
}

impl Solutions {
    pub fn new() -> Solutions {
        Solutions {
            sol: [Solution::new(); MAX_PERM_SIZE],
            size: 0,
        }
    }

    pub fn append(&self, permutation: &Permutation, yrg: &AbsYRG) -> Solutions {
        // Caller should check we have room for append first.
        let mut new_sol = self.clone();
        new_sol.sol[new_sol.size] = Solution {
            key: permutation.key,
            angle: permutation.angle,
            yrg: yrg.clone(),
        };
        new_sol.size += 1;
        new_sol
    }
}

impl fmt::Display for Solutions {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.sol.iter().join(","))
    }
}

// ~~
