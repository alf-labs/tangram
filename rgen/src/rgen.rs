use crate::board::Board;
use crate::coord::{AbsYRG, Coords};
use crate::permutations::Permutations;
use crate::piece::{Colors, Shape};
use crate::pieces::Pieces;
use crate::solutions::Solutions;
use std::fs::{File, OpenOptions};
use std::time::Instant;
use std::io::Write;

pub struct RGen<'a> {
    pieces: &'a Pieces,
    coords: &'a Coords,
    output_file: File,
    output_count: i32,
}

impl RGen<'_> {
    pub fn new<'a>(pieces: &'a Pieces, coords: &'a Coords) -> RGen<'a> {
        let file = OpenOptions::new()
            .append(true)
            .create(true)
            .open("rgen_output.txt").expect("Could not open output file");
        RGen {
            pieces,
            coords,
            output_file: file,
            output_count: 0,
        }
    }

    pub fn run(&mut self, piece_selector: &i32) {
        let start_ts = Instant::now();
        let mut spd = 0.0;
        let mut perm_count = 0;

        for permutations in self.pieces.iter(*piece_selector) {
            let index = permutations.index;
            println!("@@ perm {0}, {1:.2} pps, img {2}, {3}",
                index, spd, self.output_count, permutations);

            let empty_board = Board::new(permutations.index, self.coords);
            self.place_pieces(empty_board, permutations, Solutions::new());

            perm_count += 1;
            let now_ts = Instant::now();
            let sec = now_ts.duration_since(start_ts).as_secs_f64();
            spd = if sec <= 0.0 { 0.0 } else { (perm_count as f64) / sec };
        }
    }

    fn emit_solution(&mut self, new_board: &Board, new_sol: &Solutions) {
        let mut file = &self.output_file;
        writeln!(file, "@@ [{}] SIG {} {}", new_board.perm_index, new_board, new_sol)
            .expect("Failed to write to output file");
        file.sync_all()
            .expect("Failed to sync output file");
        self.output_count += 1;
    }

    fn place_pieces(&mut self,
                    board: Board,
                    permutations: Permutations,
                    solutions: Solutions) {
        let split = permutations.split_first();
        if split.is_none() {
            return;
        }
        let (first, rest) = split.unwrap();

        let piece = self.pieces.by_key(&first.key).unwrap();
        let shape = piece.shape(first.angle);
        let color = piece.color;
        let first_g = shape.cells[0].g;

        for yrg in self.coords.valid_yrg.iter() {
            // We can only place a piece on a cell that has the same G coordinate
            // as the first cell in the shape.
            if yrg.g != first_g {
                continue;
            }

            // TBD: place piece "first" in board at offset yrg
            // match place piece option<new board>:
            // none --> continue
            // ok -->
            //   accumulate solution
            //   if rest is empty, record solution in board and emit
            //   else recurse place_piece(new board, rest, new solutions)
            let result = self.place_piece(&board, shape, color, yrg);
            match result {
                None => {
                    continue;
                }
                Some(new_board) => {
                    let new_sol = solutions.append(&first, yrg);
                    if rest.is_empty() {
                        self.emit_solution(&new_board, &new_sol);
                        return;
                    } else {
                        // Place next piece
                        self.place_pieces(new_board, rest, new_sol);
                        return;
                    }
                }
            }
        }
    }

    fn place_piece(&self, board: &Board, shape: &Shape, color: Colors, offset: &AbsYRG) -> Option<Board> {
        let mut new_board = board.clone();

        for cell in shape.cells.iter() {
            let yrg = cell.offset_by(offset);

            if !new_board.valid(&yrg) {
                return None;
            }
            if new_board.occupied(&yrg) {
                return None;
            }
            // TBD: optimize by only cloning board here
            new_board.set_color(&yrg, color);
        }

        Some(new_board)
    }
}
