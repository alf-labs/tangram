use crate::board::Board;
use crate::coord::Coords;
use crate::permutations::Permutations;
use crate::pieces::Pieces;
use crate::solutions::BoardSolution;
use std::fs::{File, OpenOptions};
use std::io::Write;
use std::ops::RangeInclusive;
use std::time::Instant;

pub struct RGen<'a> {
    pieces: &'a Pieces,
    coords: &'a Coords,
    output_file: Option<File>,
    output_count: i32,
}

impl RGen<'_> {
    pub fn new<'a>(pieces: &'a Pieces,
                   coords: &'a Coords,
                   file_path: Option<&str>) -> RGen<'a> {
        let file = match file_path {
            None => { None }
            Some(path) => Option::from({
                OpenOptions::new()
                    .append(true)
                    .create(true)
                    .open(path).expect("Could not open output file")
            })
        };
        RGen {
            pieces,
            coords,
            output_file: file,
            output_count: 0,
        }
    }

    pub fn run(&mut self,
               piece_selector: &i32,
               perm_range: RangeInclusive<i32>) {
        let pmin = *perm_range.start();
        let pmax = *perm_range.end();
        let start_ts = Instant::now();
        let mut spd = 0.0;
        let mut perm_count = 0;

        for permutations in self.pieces.iter(*piece_selector) {
            let index = permutations.index;
            if index < pmin {
                continue
            } else if index > pmax {
                break
            }
            println!("@@ perm {0}, {1:.2} pps, img {2}, {3}",
                index, spd, self.output_count, permutations);

            let empty_board = Board::new(permutations.index, self.coords);
            self.place_pieces(empty_board, permutations, BoardSolution::new());

            perm_count += 1;
            let now_ts = Instant::now();
            let sec = now_ts.duration_since(start_ts).as_secs_f64();
            spd = if sec <= 0.0 { 0.0 } else { (perm_count as f64) / sec };
        }
    }

    fn emit_solution(&mut self, new_board: &Board, new_sol: &BoardSolution) {
        match self.output_file {
            None => {}
            Some(ref mut file) => {
                writeln!(file, "@@ [{}] SIG {} {}", new_board.perm_index, new_board, new_sol)
                    .expect("Failed to write to output file");
                file.sync_all()
                    .expect("Failed to sync output file");
                self.output_count += 1;
            }
        }
    }

    fn place_pieces(&mut self,
                    board: Board,
                    permutations: Permutations,
                    solutions: BoardSolution) {
        let split = permutations.split_first();
        if split.is_none() {
            return;
        }
        let (first, rest) = split.unwrap();

        let piece = self.pieces.by_key(&first.key).unwrap();
        let shape = piece.shape(first.angle);
        let color = piece.color;
        let first_g = shape.cells[0].g;

        for yrg in shape.positions.iter() {
            println!("@@ IN piece {}:{} ok {} -- rest {}", first, yrg, first_g, rest); // DEBUG

            let result = board.place_piece(shape, color, yrg);
            match result {
                None => {
                    continue;
                }
                Some(new_board) => {
                    let new_sol = solutions.append(&first, yrg);
                    println!("@@ -- OUT --> NEW sol {}, rest {}", new_sol, rest); // DEBUG
                    if rest.is_empty() {
                        self.emit_solution(&new_board, &new_sol);
                        return;
                    } else {
                        // Place next piece
                        self.place_pieces(new_board, rest.clone(), new_sol);
                    }
                }
            }
        }
    }
}


// ~~
