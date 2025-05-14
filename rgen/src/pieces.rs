use crate::coord::{Coords, RelYRG};
use crate::piece::{Colors, Piece, PieceKey};
use crate::rel_yrg;
use indexmap::IndexMap;
use std::cell::RefCell;
use std::ops::RangeInclusive;
use std::time::Instant;
use crate::permutations::{Permutation, Permutations};

/// The max number of pieces in one Permutations or one Solutions array.
pub const MAX_PERM_SIZE : usize = 11;

/// The static definition of all pieces possible (one per symmetry).
#[derive(Debug)]
pub struct Pieces {
    pieces: IndexMap<PieceKey, Piece>,
}

impl Pieces {
    pub fn new(coords: &Coords) -> Pieces {
        let mut p: Vec<Piece> = Vec::new();

        p.push( Piece::new(
            Piece::to_key("HR"),
            Colors::Red,
            0,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(1, 1, 1), rel_yrg!(1, 1, 0), rel_yrg!(1, 0, 1),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("i1"),
            Colors::Red,
            120,
            vec![
                rel_yrg!(0, -1, 0), rel_yrg!(0, -1, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("i2"),
            Colors::Red,
            120,
            vec![
                rel_yrg!(0, -1, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("W1"),
            Colors::Black,
            300,
            vec![
                rel_yrg!(1, 1, 0), rel_yrg!(1, 0, 1), rel_yrg!(1, 0, 0), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("W2"),
            Colors::Black,
            300,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(1, 2, 0), rel_yrg!(1, 1, 1), rel_yrg!(1, 1, 0),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("P1"),
            Colors::Red,
            300,
            vec![
                rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0), rel_yrg!(0, 2, 1), rel_yrg!(1, 2, 1),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("P2"),
            Colors::Red,
            300,
            vec![
                rel_yrg!(1, 1, 1), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0), rel_yrg!(0, 2, 1),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("VB"),
            Colors::Black,
            300,
            vec![
                rel_yrg!(1, 0, 0), rel_yrg!(1, 0, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("J1"),
            Colors::Orange,
            300,
            vec![
                rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0), rel_yrg!(1, 2, 1), rel_yrg!(1, 2, 0),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("J2"),
            Colors::Orange,
            300,
            vec![
                rel_yrg!(1, 1, 0), rel_yrg!(1, 0, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("L1"),
            Colors::Yellow,
            300,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0), rel_yrg!(1, 2, 1),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("L2"),
            Colors::Yellow,
            300,
            vec![
                rel_yrg!(1, 0, 1), rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0), rel_yrg!(0, 1, 1), rel_yrg!(0, 2, 0),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("TW"),
            Colors::White,
            0,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0),
            ],
        ));

        p.push( Piece::new(
            Piece::to_key("TO"),
            Colors::Orange,
            300,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0),
            ],
        ));

        p.push(Piece::new(
            Piece::to_key("TY"),
            Colors::Yellow,
            300,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0),
            ],
        ));

        let mut p_map = IndexMap::new();
        for mut item in p {
            item.init_rotations(coords);
            p_map.insert(item.key, item);
        }

        Pieces { pieces: p_map }
    }
    
    pub fn by_key(&self, key: &PieceKey) -> Option<&Piece> {
        self.pieces.get(key)
    }

    pub fn by_str(&self, key: &str) -> Option<&Piece> {
        let k = Piece::to_key(key);
        self.pieces.get(&k)
    }

    pub fn iter(&self, piece_selector: i32) -> PiecesIteratorState {
        PiecesIteratorState::new(self, piece_selector)
    }

    pub(crate) fn dump(&self,
                       piece_selector: &i32,
                       perm_range: RangeInclusive<i32>,
                       print_all: bool) {
        let pmin = *perm_range.start();
        let pmax = *perm_range.end();
        let start_ts = Instant::now();
        let mut count = 0;
        let mut do_print_all = print_all;
        let mut print_range =true;
        for item in self.iter(*piece_selector) {
            count += 1;
            let index = item.index;
            if index > pmax {
                break
            }
            if pmin > 0 && index == pmin {
                do_print_all = true;
                println!();
            }

            if do_print_all {
                println!("{}", item);
            } else if print_range && count % 16384 == 0 {
                let now = Instant::now();
                let duration = now.duration_since(start_ts);
                let sec = duration.as_secs_f64();
                let pps: f64 = if sec <= 0.0 { 0.0 } else { (count as f64) / sec };
                print!("{0:.2} pps : {1}           \r", pps, item);

            }
        }

        println!("\nNumber of permutations: {}", count);
        let now = Instant::now();
        let duration = now.duration_since(start_ts);
        let sec = duration.as_secs_f64();
        let pps: f64 = if sec <= 0.0 { 0.0 } else { (count as f64) / sec };
        println!("Speed: {0:.2} pps", pps)
    }
}

#[derive(Debug)]
pub struct PiecesIteratorState<'a> {
    state: Vec< RefCell<PieceIteratorState<'a>> >,
    index: i32,
    done: bool,
}

impl PiecesIteratorState<'_> {
    fn new(pieces: &Pieces, piece_selector: i32) -> PiecesIteratorState {
        let mut state = Vec::new();

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.by_str("HR").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.by_str("i1").unwrap(),
                        pieces.by_str("i2").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.by_str("W1").unwrap(),
                        pieces.by_str("W2").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.by_str("P1").unwrap(),
                        pieces.by_str("P2").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.by_str("VB").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.by_str("J1").unwrap(),
                        pieces.by_str("J2").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.by_str("L1").unwrap(),
                        pieces.by_str("L2").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.by_str("TW").unwrap(),
                    ])));

        state.push(
            RefCell::new(
                PieceIteratorState::new(
                    vec![
                        pieces.by_str("TO").unwrap(),
                    ])));

        for i in 1..=2 {
            state.push(
                RefCell::new(
                    PieceIteratorState::new(
                        vec![
                            pieces.by_str("TY").unwrap(),
                        ])));
        }

        if piece_selector >= 0 {
            // Limit the list of pieces to that single index.
            // Swap the desired element to the beginning of the vector then truncate it to length 1.
            if piece_selector > 0 {
                state.swap(piece_selector as usize, 0);
            }
            state.truncate(1);
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

        self.index += 1;

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
            key: p.key,
            angle: self.r_index,
        }
    }

    fn inc(&mut self) -> bool {
        // Returns true if wraps around.
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
