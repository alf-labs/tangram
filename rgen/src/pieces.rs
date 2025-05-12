use indexmap::IndexMap;
use crate::coord::RelYRG;
use crate::piece::{Colors, Piece};
use crate::rel_yrg;

pub struct Permutation {
    key: String,
    angle: u16,
}

pub type Permutations = Vec<Permutation>;

pub struct Pieces {
    pieces: IndexMap<String, Piece>,
}

struct PiecesIter {
    level: usize,
    rot: i32,
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
            0,
            vec![
                rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0),
            ],
        ));

        for i in 1..=2 {
            p.push(Piece::new(
                "TY".to_string(),
                Colors::Yellow,
                0,
                vec![
                    rel_yrg!(0, 0, 0), rel_yrg!(0, 0, 1), rel_yrg!(0, 1, 0),
                ],
            ));
        }

        let mut p_map = IndexMap::new();
        for item in p {
            p_map.insert(item.name.clone(), item);
        }

        Pieces { pieces: p_map }
    }

    // pub fn iter(&self) -> PiecesIter {
    //
    // }
}


// ~~
