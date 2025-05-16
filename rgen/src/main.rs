use crate::coord::Coords;
use crate::pieces::Pieces;
use crate::rgen::{RGen, RGenResult};
use clap::{Parser, Subcommand};
use std::fs::OpenOptions;
use std::io::Write;
use std::ops::RangeInclusive;
use std::sync::{mpsc, Arc};
use std::sync::mpsc::{Receiver, Sender};
use std::thread;

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
        // #[arg(long, default_value_t = 0,
        //     help = "Generator core index from 0 to gen-cores-1.")]
        // gen_index: i32,

        #[arg(long, default_value_t = 1,
            help = "Generator number of cores.")]
        gen_cores: i32,

        #[arg(short = 'o', long, value_name = "FILE", default_value = "rgen_output.txt")]
        gen_output: String,
    }
}

fn main() {
    println!("Hello, world!");

    let cli = Cli::parse();
    let range = RangeInclusive::new(cli.min_perm, cli.max_perm);

    match &cli.command {
        Some( Commands::Dump { print_all  } ) => {
            let coords = Coords::new();
            let pieces = Pieces::new(&coords);
            pieces.dump(&cli.piece, range, *print_all)
        },
        Some( Commands::Gen { gen_cores, gen_output } ) => {
            executor(cli.piece, range, *gen_cores, gen_output);
        },
        &None => {}
    }
}

fn executor(piece_selector: i32,
            perm_range: RangeInclusive<i32>,
            gen_cores: i32,
            gen_output: &String) {
    let mut file = OpenOptions::new()
        .append(true)
        .create(true)
        .open(gen_output).expect("Could not open output file");

    let coords = Arc::new( Coords::new() );
    let pieces = Arc::new( Pieces::new(&coords) );

    let (tx, rx): (Sender<RGenResult>, Receiver<RGenResult>) = mpsc::channel();

    // Receiver Thread
    let receiver = thread::spawn(move || {
        let mut sig_count = 0;
        for message in rx {
            if message.result.is_empty() {
                // This is a progress log.
                println!("[{:?}] {}",
                         message.tid,
                         message.progress.replace("CNT", sig_count.to_string().as_str()));
            } else {
                // This is a solution signature
                sig_count += 1;
                writeln!(file, "{}", message.result).expect("Could not write to file");
                file.sync_all().expect("Could not sync file");
            }
        }
    });

    // Producer Threads
    let mut receivers = Vec::new();
    for i in 0..gen_cores {
        let tx_clone = tx.clone();
        let pieces_clone = pieces.clone();
        let coords_clone = coords.clone();
        let range_clone = perm_range.clone();
        let receiver = thread::spawn(move || {
            let mut rgen = RGen::new(
                &pieces_clone,
                &coords_clone,
                &tx_clone);
            rgen.run(piece_selector, &range_clone, i, gen_cores)
        });
        receivers.push(receiver);
    }

    receiver.join().expect("Could not join receiver thread");
    for receiver in receivers {
        receiver.join().expect("Could not join receiver thread");
    }

    println!("Done");
}



// ~~
