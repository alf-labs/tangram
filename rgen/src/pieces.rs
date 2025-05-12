use crate::coord::RelYRG;
use crate::rel_yrg;

#[derive(Debug, Copy, Clone, PartialEq, Eq)]
#[repr(u8)]
pub enum Colors {
    Red = b'R',
    Yellow = b'Y',
    Orange = b'O',
    Black = b'B',
    White = b'W',
}

pub struct Shape {
    cells: Vec<RelYRG>,
}

pub struct Piece {
    name: String,
    color: Colors,
    max_rot: i32,
    shape: Shape,
}

pub struct Pieces {
    a: u64,
    p: Vec<Piece>,
}

impl Piece {
    pub fn new(name: String, color: Colors, max_rot: i32, cells: Vec<RelYRG>) -> Piece {
        Piece { name, color, max_rot, shape : Shape { cells } }
    }
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


        Pieces { a: 0, p }
    }
}

impl Iterator for Pieces {
    type Item = u64;

    fn next(&mut self) -> Option<Self::Item> {
        self.a += 1;
        Some(self.a)
    }
}

// ~~
