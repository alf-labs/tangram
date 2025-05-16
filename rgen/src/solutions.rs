use itertools::Itertools;
use std::fmt;
use std::fmt::Formatter;
use crate::abs_yrg;
use crate::coord::AbsYRG;
use crate::permutations::Permutation;
use crate::pieces::MAX_PERM_SIZE;

/// A solution for a single piece: piece name + rotation + its location on the board.
#[derive(Copy, Clone, PartialEq, Eq)]
pub struct PieceSolution {
    pub key: [char; 2],
    pub angle: i32,
    pub yrg: AbsYRG,
}

impl PieceSolution {
    pub fn new() -> PieceSolution {
        PieceSolution {
            key: ['-'; 2],
            angle: 0,
            yrg: abs_yrg!(0, 0, 0),
        }
    }
}

impl fmt::Display for PieceSolution {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}{}@{}:{}", self.key[0], self.key[1], self.angle, self.yrg)
    }
}


/// A set of piece solutions for the entire board.
#[derive(Copy, Clone, PartialEq, Eq)]
pub struct BoardSolution {
    pub sol: [PieceSolution; MAX_PERM_SIZE],
    pub size: usize,
}

impl BoardSolution {
    pub fn new() -> BoardSolution {
        BoardSolution {
            sol: [PieceSolution::new(); MAX_PERM_SIZE],
            size: 0,
        }
    }

    pub fn append(&self, permutation: &Permutation, yrg: &AbsYRG) -> BoardSolution {
        // Caller should check we have room for append first.
        let mut new_sol = self.clone();
        new_sol.sol[new_sol.size] = PieceSolution {
            key: permutation.key,
            angle: permutation.angle,
            yrg: yrg.clone(),
        };
        new_sol.size += 1;
        new_sol
    }
}

impl fmt::Display for BoardSolution {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.sol.iter().join(","))
    }
}


#[cfg(test)]
mod tests {
    use crate::piece::Piece;
    use super::*;

    #[test]
    fn test_piece_solution_display_empty() {
        let p = PieceSolution::new();
        assert_eq!(format!("{}", p), "--@0:0x0x0");
    }

    #[test]
    fn test_piece_solution_display() {
        let mut p = PieceSolution::new();
        p.key = Piece::to_key("HR");
        p.angle = 300;
        p.yrg = abs_yrg!(3, 2, 1);
        assert_eq!(format!("{}", p), "HR@300:3x2x1");
    }

    #[test]
    fn test_board_solution_display_empty() {
        let b = BoardSolution::new();
        assert_eq!(format!("{}", b),
                   "--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0");
    }

    #[test]
    fn test_board_solution_append() {
        let mut b = BoardSolution::new();
        assert_eq!(b.size, 0);

        b = b.append(
            &Permutation::new(Piece::to_key("HR"), 60),
            &abs_yrg!(3, 2, 1));

        assert_eq!(b.size, 1);
        assert_eq!(format!("{}", b.sol[0]), "HR@60:3x2x1");
        assert_eq!(format!("{}", b),
                   "HR@60:3x2x1,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0,--@0:0x0x0");
    }

}

// ~~
