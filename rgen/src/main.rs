use std::sync::{Arc, Mutex};
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
    let pieces_ptr = Arc::new(Mutex::new(pieces));

    let mut gen1 = RGen::new(pieces_ptr.clone());
    let mut gen2 = RGen::new(pieces_ptr.clone());

    gen1.do_stuff();
    gen2.do_stuff();

}
