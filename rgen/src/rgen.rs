use std::sync::{Arc, Mutex};
use std::thread;
use crate::pieces;

pub struct RGen {
    p: Arc<Mutex<pieces::Pieces>>,
}

impl RGen {
    pub fn new(p : Arc<Mutex<pieces::Pieces>>) -> RGen {
        RGen { p }
    }
    
    pub fn do_stuff(&mut self) {
        let v = self.next_pieces();
        println!("stuff: thread {:?}, value {}", thread::current().id(), v);
    }

    fn next_pieces(&mut self) -> u64 {
        let mut p = self.p.lock().unwrap();
        // let v = p.next().unwrap();
        // v
        42
    }
}
