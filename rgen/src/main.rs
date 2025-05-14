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
            let rgen = RGen::new(&pieces, &coord);
            rgen.run(piece)
        }
    }

    // let mut gen1 = RGen::new(pieces_ptr.clone());
    // let mut gen2 = RGen::new(pieces_ptr.clone());
    //
    // gen1.do_stuff();
    // gen2.do_stuff();

    // let start = Instant::now();
    // let mut i = 0;
    // for item in pieces.iter() {
    //     // println!("{}", item);
    //     i += 1;
    //     if i % 16384 == 0 {
    //         let now = Instant::now();
    //         let duration = now.duration_since(start);
    //         let sec = duration.as_secs_f64();
    //         let fps: f64 = if sec <= 0.0 { 0.0 } else { (i as f64) / sec };
    //
    //         print!("{0:.2} fps : {1}           \r", fps, item)
    //     }
    //     // if i == 10 {
    //     //     break;
    //     // }
    // }
    // println!("Number of permutations: {}", i);
}
