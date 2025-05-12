
#[macro_export]
macro_rules! abs_yrg {
    ($y:expr, $r:expr, $g:expr) => {
        AbsYRG { y: $y as i8, r: $r as i8, g: $g as i8 }
    };
}

#[macro_export]
macro_rules! rel_yrg {
    ($y:expr, $r:expr, $g:expr) => {
        RelYRG { y: $y as i8, r: $r as i8, g: $g as i8 }
    };
}
