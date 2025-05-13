use itertools::Itertools;
use std::fmt;
use std::fmt::Formatter;

#[derive(Clone, PartialEq, Eq)]
pub struct Permutation {
    pub key: String,
    pub angle: i32,
}

impl fmt::Display for Permutation {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}@{}", self.key, self.angle)
    }
}


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


// ~~
