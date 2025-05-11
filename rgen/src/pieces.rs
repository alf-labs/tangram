use crate::coord::RelYRG;
use crate::rel_yrg;

pub struct Piece {
    name: String,
    color: char,
    max_rot: i32,
    count: i32,
    cells: Vec<RelYRG>,
}

pub struct Pieces {
    a: u64,
    p: Vec<Piece>,
}

impl Pieces {
    pub fn new() -> Pieces {
        let mut p: Vec<Piece> = Vec::new();

        p.push( Piece {
            name: "HR".to_string(),
            color: 'R',
            max_rot: 0,
            count: 1,
            cells: vec![
                rel_yrg!(0, 0, 0),
                rel_yrg!(0, 0, 1),
                rel_yrg!(0, 1, 0),
                rel_yrg!(1, 1, 1),
                rel_yrg!(1, 1, 0),
                rel_yrg!(1, 0, 1),
            ],
        });

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
