use std::sync::{Arc, Mutex};
use crate::gen::Gen;
use crate::pieces::Pieces;

mod pieces;
mod gen;
mod coord;

fn main() {
    println!("Hello, world!");
    
    let pieces = Pieces::new();
    let pieces_ptr = Arc::new(Mutex::new(pieces));
    
    let mut gen1 = Gen::new(pieces_ptr.clone());
    let mut gen2 = Gen::new(pieces_ptr.clone());
    
    gen1.do_stuff();
    gen2.do_stuff();
    
}
