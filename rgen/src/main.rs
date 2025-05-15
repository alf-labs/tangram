use crate::pieces::Pieces;
use clap::{Parser, Subcommand};
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

#[derive(Parser)]
struct Cli {
    #[arg(short, long, default_value_t = -1,
        help = "Piece selector. Default: use all pieces.")]
    piece: i32,

    #[arg(long, default_value_t = 0,
        help = "Min permutation index to print.")]
    min_perm: i32,

    #[arg(long, default_value_t = i32::MAX,
        help = "Max permutation index to print.")]
    max_perm: i32,

    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    Dump {

        #[arg(long,
        help = "Print everything (very verbose).")]
        print_all: bool,
    },
    Gen {
    }
}

fn main() {
    println!("Hello, world!");

    let cli = Cli::parse();
    let range = RangeInclusive::new(cli.min_perm, cli.max_perm);

    let coord = Coords::new();
    let pieces = Pieces::new(&coord);

    match &cli.command {
        Some( Commands::Dump { print_all  } ) => {
            pieces.dump(&cli.piece, range, *print_all)
        },
        Some( Commands::Gen { } ) => {
            let mut rgen = RGen::new(
                &pieces,
                &coord,
                Some("rgen_output.txt"));
            rgen.run(&cli.piece, range)
        },
        &None => {}
    }
}

// ~~
