use crate::pieces::Pieces;
use clap::Parser;
use std::ops::RangeInclusive;
use crate::coord::Coords;
use crate::rgen::RGen;

mod macros;
mod coord;
mod permutations;
mod solutions;
mod piece;
mod pieces;
mod board;
mod rgen;

#[derive(Parser, Debug)]
enum Cli {
    Dump {
        #[arg(short, long, default_value_t = -1,
        help = "Piece selector. Default: use all pieces.")]
        piece: i32,

        #[arg(long, default_value_t = 0,
            help = "Min permutation index to print.")]
        min_perm: i32,

        #[arg(long, default_value_t = i32::MAX,
        help = "Max permutation index to print.")]
        max_perm: i32,

        #[arg(long,
        help = "Print everything (very verbose).")]
        print_all: bool,
    },
    Gen {
        #[arg(short, long, default_value_t = -1,
        help = "Piece selector. Default: use all pieces.")]
        piece: i32,
    }
}

fn main() {
    println!("Hello, world!");

    let cli = Cli::parse();

    let coord = Coords::new();
    let pieces = Pieces::new(&coord);

    match &cli {
        Cli::Dump { piece, min_perm, max_perm, print_all  } => {
            let range = RangeInclusive::new(*min_perm, *max_perm);
            pieces.dump(piece, range, *print_all)
        },
        Cli::Gen { piece } => {
            let mut rgen = RGen::new(&pieces, &coord);
            rgen.run(piece)
        }
    }
}

// ~~
