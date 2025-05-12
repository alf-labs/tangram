use std::collections::HashMap;
use std::sync::Mutex;
use once_cell::sync::Lazy;

pub const N: i8 = 6;
pub const N2: i8 = N/2;

pub struct AbsYRG {
    pub y: i8,
    pub r: i8,
    pub g: i8,
}

#[macro_export]
macro_rules! abs_yrg {
    ($y:expr, $r:expr, $g:expr) => {
        AbsYRG { y: $y as i8, r: $r as i8, g: $g as i8 }
    };
}

pub struct RelYRG {
    pub y: i8,
    pub r: i8,
    pub g: i8,
}

#[macro_export]
macro_rules! rel_yrg {
    ($y:expr, $r:expr, $g:expr) => {
        RelYRG { y: $y as i8, r: $r as i8, g: $g as i8 }
    };
}

impl AbsYRG {
    pub fn new(y: i8, r: i8, g: i8) -> AbsYRG {
        AbsYRG { y, r, g }
    }

    pub fn to_rel(&self) -> RelYRG {
        RelYRG { y: self.y - N2, r: self.r - N2, g: self.g }
    }
}

impl RelYRG {
    pub fn new(y: i8, r: i8, g: i8) -> RelYRG {
        RelYRG { y, r, g }
    }

    pub fn to_abs(&self) -> AbsYRG {
        AbsYRG { y: self.y + N2, r: self.r + N2, g: self.g }
    }
}


pub static VALID_YRG: &'static [AbsYRG] = &[
                                          abs_yrg!(0, 0, 0), abs_yrg!(0, 0, 1), abs_yrg!(0, 1, 0), abs_yrg!(0, 1, 1), abs_yrg!(0, 2, 0), abs_yrg!(0, 2, 1), abs_yrg!(0, 3, 0),
                       abs_yrg!(1, 0, 0), abs_yrg!(1, 0, 1), abs_yrg!(1, 1, 0), abs_yrg!(1, 1, 1), abs_yrg!(1, 2, 0), abs_yrg!(1, 2, 1), abs_yrg!(1, 3, 0), abs_yrg!(1, 3, 1), abs_yrg!(1, 4, 0),
    abs_yrg!(2, 0, 0), abs_yrg!(2, 0, 1), abs_yrg!(2, 1, 0), abs_yrg!(2, 1, 1), abs_yrg!(2, 2, 0), abs_yrg!(2, 2, 1), abs_yrg!(2, 3, 0), abs_yrg!(2, 3, 1), abs_yrg!(2, 4, 0), abs_yrg!(2, 4, 1), abs_yrg!(2, 5, 0),
    abs_yrg!(3, 0, 1), abs_yrg!(3, 1, 0), abs_yrg!(3, 1, 1), abs_yrg!(3, 2, 0), abs_yrg!(3, 2, 1), abs_yrg!(3, 3, 0), abs_yrg!(3, 3, 1), abs_yrg!(3, 4, 0), abs_yrg!(3, 4, 1), abs_yrg!(3, 5, 0), abs_yrg!(3, 5, 1),
                       abs_yrg!(4, 1, 1), abs_yrg!(4, 2, 0), abs_yrg!(4, 2, 1), abs_yrg!(4, 3, 0), abs_yrg!(4, 3, 1), abs_yrg!(4, 4, 0), abs_yrg!(4, 4, 1), abs_yrg!(4, 5, 0), abs_yrg!(4, 5, 1),
                                          abs_yrg!(5, 2, 1), abs_yrg!(5, 3, 0), abs_yrg!(5, 3, 1), abs_yrg!(5, 4, 0), abs_yrg!(5, 4, 1), abs_yrg!(5, 5, 0), abs_yrg!(5, 5, 1),
];

// We can rotate the puzzle cells 60 degrees clockwise by mapping any cell from ROT_60_CCW_SRC (source) to VALID_YRG (destination).
// Example: SRC[0](0,2,1) --> That means that cell (0,2,1) becomes cell (0,0,0) because VALID_YRG[0] = (0,0,0).
pub static ROT_60_CCW_SRC: &'static [AbsYRG] = &[
                                      abs_yrg!(0, 2, 1), abs_yrg!(0, 3, 0), abs_yrg!(1, 3, 1), abs_yrg!(1, 4, 0), abs_yrg!(2, 4, 1), abs_yrg!(2, 5, 0), abs_yrg!(3, 5, 1),
                   abs_yrg!(0, 1, 1), abs_yrg!(0, 2, 0), abs_yrg!(1, 2, 1), abs_yrg!(1, 3, 0), abs_yrg!(2, 3, 1), abs_yrg!(2, 4, 0), abs_yrg!(3, 4, 1), abs_yrg!(3, 5, 0), abs_yrg!(4, 5, 1),
abs_yrg!(0, 0, 1), abs_yrg!(0, 1, 0), abs_yrg!(1, 1, 1), abs_yrg!(1, 2, 0), abs_yrg!(2, 2, 1), abs_yrg!(2, 3, 0), abs_yrg!(3, 3, 1), abs_yrg!(3, 4, 0), abs_yrg!(4, 4, 1), abs_yrg!(4, 5, 0), abs_yrg!(5, 5, 1),
abs_yrg!(0, 0, 0), abs_yrg!(1, 0, 1), abs_yrg!(1, 1, 0), abs_yrg!(2, 1, 1), abs_yrg!(2, 2, 0), abs_yrg!(3, 2, 1), abs_yrg!(3, 3, 0), abs_yrg!(4, 3, 1), abs_yrg!(4, 4, 0), abs_yrg!(5, 4, 1), abs_yrg!(5, 5, 0),
                   abs_yrg!(1, 0, 0), abs_yrg!(2, 0, 1), abs_yrg!(2, 1, 0), abs_yrg!(3, 1, 1), abs_yrg!(3, 2, 0), abs_yrg!(4, 2, 1), abs_yrg!(4, 3, 0), abs_yrg!(5, 3, 1), abs_yrg!(5, 4, 0),
                                      abs_yrg!(2, 0, 0), abs_yrg!(3, 0, 1), abs_yrg!(3, 1, 0), abs_yrg!(4, 1, 1), abs_yrg!(4, 2, 0), abs_yrg!(5, 2, 1), abs_yrg!(5, 3, 0),
];

static mut VALID_YRG_TO_IDX: Option<HashMap<AbsYRG, i32>> = None;

// static GLOBAL_DATA: Lazy<Mutex<HashMap<i32, String>>> = Lazy::new(|| {
//     let mut m = HashMap::new();
//     m.insert(13, "Spica".to_string());
//     m.insert(74, "Hoyten".to_string());
//     Mutex::new(m)
// });





static HASHMAP: Lazy<HashMap<u32, &'static str>> = Lazy::new(|| {
    let mut m = HashMap::new();
    m.insert(0, "foo");
    m.insert(1, "bar");
    m.insert(2, "baz");
    m
});

// ~~
