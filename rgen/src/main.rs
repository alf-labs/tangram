use std::sync::{Arc, Mutex};
use std::time::Instant;
use crate::rgen::RGen;
use crate::pieces::Pieces;

mod macros;
mod coord;
mod piece;
mod pieces;
mod rgen;

fn main() {
    println!("Hello, world!");

    let pieces = Pieces::new();
    // let pieces_ptr = Arc::new(Mutex::new(pieces));

    // let mut gen1 = RGen::new(pieces_ptr.clone());
    // let mut gen2 = RGen::new(pieces_ptr.clone());
    //
    // gen1.do_stuff();
    // gen2.do_stuff();

    let start = Instant::now();
    let mut i = 0;
    for item in pieces.iter() {
        // println!("{}", item);
        i += 1;
        if i % 16384 == 0 {
            let now = Instant::now();
            let duration = now.duration_since(start);
            let sec = duration.as_secs_f64();
            let fps: f64 = if sec <= 0.0 { 0.0 } else { (i as f64) / sec };

            print!("{0:.2} fps : {1}           \r", fps, item)
        }
        // if i == 10 {
        //     break;
        // }
    }
    println!("Number of permutations: {}", i);
}
