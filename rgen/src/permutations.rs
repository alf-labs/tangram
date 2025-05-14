use itertools::Itertools;
use std::fmt;
use std::fmt::Formatter;
use crate::piece::PieceKey;

/// A permutation for a single piece: piece name + rotation.
#[derive(Copy, Clone, PartialEq, Eq)]
pub struct Permutation {
    pub key: PieceKey,
    pub angle: i32,
}

impl Permutation {
    pub fn new(key: PieceKey, angle: i32) -> Permutation {
        Permutation { key, angle }
    }
}

impl fmt::Display for Permutation {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}{}@{}", self.key[0], self.key[1], self.angle)
    }
}


/// A set of permutation (all pieces and their specific rotations) in a specific order.
#[derive(Clone, PartialEq, Eq)]
pub struct Permutations {
    pub perms: Vec<Permutation>,
    pub index: i32,
}

impl fmt::Display for Permutations {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.index, self.perms.iter().join(","))
    }
}

impl Permutations {
    pub fn is_empty(&self) -> bool {
        self.perms.is_empty()
    }

    pub fn split_first(&self) -> Option<(Permutation, Permutations)> {
        if self.perms.is_empty() {
            None
        } else {
            let first = self.perms.get(0).unwrap();
            Some((
                first.clone(),
                Permutations {
                    perms: self.perms[1..].to_vec(),
                    index: self.index,
                }
                ))
        }
    }
}


// ~~
