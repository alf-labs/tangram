pub struct Pieces {
    a: u64,
}

impl Pieces {
    pub fn new() -> Pieces {
        Pieces { a: 0 }
    }
}

impl Iterator for Pieces {
    type Item = u64;
    
    fn next(&mut self) -> Option<Self::Item> {
        self.a += 1;
        Some(self.a)
    }
}
