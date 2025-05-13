use std::cell::{RefCell, RefMut};
use std::fmt;
use std::fmt::Formatter;
use indexmap::IndexMap;
use itertools::Itertools;
use crate::coord::RelYRG;
use crate::piece::{Colors, Piece};
use crate::rel_yrg;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Permutation {
    key: String,
    angle: i32,
}

impl fmt::Display for Permutation {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{}@{}", self.key, self.angle)
    }
}


#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Permutations {
    perms: Vec<Permutation>,
    index: i32,
}

impl fmt::Display for Permutations {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.index, self.perms.iter().join(","))
    }
}


#[derive(Debug)]
pub struct Pieces {
    pieces: IndexMap<String, Piece>,
}

impl Pieces {
    pub fn new() -> Pieces {
        let mut p: Vec<Piece> = Vec::new();

        p.push( Piece::new(
            "HR".to_string(),
            Colors::Red,
            0,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(1, 1, 1), rel_yrg!(1, 1, 0), rel_yrg!(1, 0, 1),
            ],
        ));

        p.push( Piece::new(
            "i1".to_string(),
            Colors::Red,
            120,
            vec![
                rel_yrg!(0, -1, 0), rel_yrg!(0, -1, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1),
            ],
        ));

        p.push( Piece::new(
            "i2".to_string(),
            Colors::Red,
            120,
            vec![
                rel_yrg!(0, -1, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0),
            ],
        ));

        p.push( Piece::new(
            "W1".to_string(),
            Colors::Black,
            300,
            vec![
                rel_yrg!(1, 1, 0), rel_yrg!(1, 0, 1), rel_yrg!(1, 0, 0), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0),
            ],
        ));

        p.push( Piece::new(
            "W2".to_string(),
            Colors::Black,
            300,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(1, 2, 0), rel_yrg!(1, 1, 1), rel_yrg!(1, 1, 0),
            ],
        ));

        p.push( Piece::new(
            "P1".to_string(),
            Colors::Red,
            300,
            vec![
                rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0), rel_yrg!(0, 2, 1), rel_yrg!(1, 2, 1),
            ],
        ));

        p.push( Piece::new(
            "P2".to_string(),
            Colors::Red,
            300,
            vec![
                rel_yrg!(1, 1, 1), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0), rel_yrg!(0, 2, 1),
            ],
        ));

        p.push( Piece::new(
            "VB".to_string(),
            Colors::Black,
            300,
            vec![
                rel_yrg!(1, 0, 0), rel_yrg!(1, 0, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1),
            ],
        ));

        p.push( Piece::new(
            "J1".to_string(),
            Colors::Orange,
            300,
            vec![
                rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0), rel_yrg!(1, 2, 1), rel_yrg!(1, 2, 0),
            ],
        ));

        p.push( Piece::new(
            "J2".to_string(),
            Colors::Orange,
            300,
            vec![
                rel_yrg!(1, 1, 0), rel_yrg!(1, 0, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1),
            ],
        ));

        p.push( Piece::new(
            "L1".to_string(),
            Colors::Yellow,
            300,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0), rel_yrg!(1, 2, 1),
            ],
        ));

        p.push( Piece::new(
            "L2".to_string(),
            Colors::Yellow,
            300,
            vec![
                rel_yrg!(1, 0, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0),
            ],
        ));

        p.push( Piece::new(
            "TW".to_string(),
            Colors::White,
            0,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0),
            ],
        ));

        p.push( Piece::new(
            "TO".to_string(),
            Colors::Orange,
            300,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0),
            ],
        ));

        p.push(Piece::new(
            "TY".to_string(),
            Colors::Yellow,
            300,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0),
            ],
        ));

        let mut p_map = IndexMap::new();
        for item in p {
            p_map.insert(item.name.clone(), item);
        }

        Pieces { pieces: p_map }
    }

    pub fn iter(&self) -> PiecesIteratorState {
        PiecesIteratorState::new(self)
    }
}

#[derive(Debug)]
pub struct PiecesIteratorState<'a> {
    state: Vec< RefCell<PieceIteratorState<'a>> >,
    index: i32,
    done: bool,
}

impl PiecesIteratorState<'_> {
    fn new(pieces: &Pieces) -> PiecesIteratorState {
        let mut state = Vec::new();

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.pieces.get("HR").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.pieces.get("i1").unwrap(),
                        pieces.pieces.get("i2").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.pieces.get("W1").unwrap(),
                        pieces.pieces.get("W2").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.pieces.get("P1").unwrap(),
                        pieces.pieces.get("P2").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.pieces.get("VB").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.pieces.get("J1").unwrap(),
                        pieces.pieces.get("J2").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.pieces.get("L1").unwrap(),
                        pieces.pieces.get("L2").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.pieces.get("TW").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.pieces.get("TO").unwrap(),
                    ])));

        for i in 1..=2 {
            state.push(
                RefCell::new(
                    PieceIteratorState::new(
                        vec![
                            pieces.pieces.get("TY").unwrap(),
                        ])));
        }

        PiecesIteratorState {
            state,
            index: 0,
            done: false
        }
    }
}

impl<'a> Iterator for PiecesIteratorState<'a> {
    type Item = Permutations;

    fn next(&mut self) -> Option<Self::Item> {
        if self.done {
            return None;
        }

        let mut perms = Vec::new();

        for item in self.state.iter() {
            let s = item.borrow();
            perms.push( s.current() );
        }

        let result = Some( Permutations {
            perms,
            index: self.index,
        });

        // Compute the _next_ state.
        // This works like an odometer: increment the lower value first,
        // and each times it wraps around, "carry" an increment to the next
        // value up. If the last value "carries", then the entire odometer
        // reached the end of its count and we're done.
        // Implementation detail: some pieces like HR or TW have only one state and
        // thus they "carry" at every single iteration.
        self.index += 1;
        let mut carry = false;
        for item in self.state.iter().rev() {
            // Obtain a mutable borrow of the RefCell's content
            let mut s = item.try_borrow_mut().unwrap();
            carry = s.inc();
            if !carry {
                break;
            }
        }
        if carry {
            self.done = true;
        }

        result
    }
}

#[derive(Debug)]
struct PieceIteratorState<'a> {
    pieces: Vec<&'a Piece>,
    max_rot: i32,
    p_index: usize,
    r_index: i32,
}

impl PieceIteratorState<'_> {
    fn new(p: Vec<&Piece>) -> PieceIteratorState {
        let rot = p[0].max_rot;
        PieceIteratorState {
            pieces: p,
            max_rot: rot,
            p_index: 0,
            r_index: 0,
        }
    }

    fn current(&self) -> Permutation {
        let p = self.pieces[self.p_index];
        Permutation {
            key: p.name.clone(),
            angle: self.r_index,
        }
    }

    fn inc(&mut self) -> bool {
        /// Returns true if wraps around.
        if self.r_index < self.max_rot {
            self.r_index += 60;
        } else if self.p_index < self.pieces.len() - 1 {
            self.p_index += 1;
            self.r_index = 0;
        } else {
            // Wrap around
            self.p_index = 0;
            self.r_index = 0;
            return true;
        }
        false
    }
}




// ~~
