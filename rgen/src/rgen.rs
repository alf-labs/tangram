use crate::board::Board;
use crate::coord::{AbsYRG, Coords};
use crate::permutations::Permutations;
use crate::piece::{Colors, Shape};
use crate::pieces::Pieces;
use crate::solutions::BoardSolution;
use std::fs::{File, OpenOptions};
use std::time::Instant;
use std::io::Write;
use std::ops::RangeInclusive;

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

        for yrg in self.coords.valid_yrg.iter() {
            // We can only place a piece on a cell that has the same G coordinate
            // as the first cell in the shape.
            if yrg.g != first_g {
                println!("@@ IN piece {}:{} KO {} -- rest {}", first, yrg, first_g, rest); // DEBUG
                continue;
            }
            println!("@@ IN piece {}:{} ok {} -- rest {}", first, yrg, first_g, rest); // DEBUG

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

    fn place_piece(&self, board: &Board, shape: &Shape, color: Colors, offset: &AbsYRG) -> Option<Board> {
        let mut new_board = board.clone();

        for cell in shape.cells.iter() {
            let yrg = cell.offset_by(offset);

            if !new_board.valid(&yrg) {
                println!("@@ -- not valid yrg rel {} + abs {} = {}", cell, offset, yrg); // DEBUG
                return None;
            }
            if new_board.occupied(&yrg) {
                println!("@@ -- occupied yrg {} -> {}", yrg, new_board.get_color(&yrg)); // DEBUG
                return None;
            }
            // TBD: optimize by only cloning board here
            new_board.set_color(&yrg, color);
        }

        Some(new_board)
    }
}



#[cfg(test)]
mod tests {
    use crate::abs_yrg;
    use super::*;

    #[test]
    fn test_place_piece() {
        let coords = Coords::new();
        let pieces = Pieces::new(&coords);
        let rgen = RGen::new(
            &pieces,
            &coords,
            None);

        // Simulate this permutation:
        // HR@0:2x4x0 i1@0:2x1x0 W1@0:0x0x0 P1@0:4x3x1 VB@300:0x3x0 J1@0:1x1x1
        // L2@0:3x2x1 TO@180:4x2x0 TW@0:5x4x0 TY@240:5x4x0 TY@300:4x2x0

        let empty_board = Board::new(156954, &coords);

        // HR@0:2x4x0
        let mut piece = pieces.by_str("HR").unwrap();
        let mut shape = piece.shape(0);
        let mut result = rgen.place_piece(&empty_board, shape, piece.color, &abs_yrg!(2, 4, 0)).unwrap();
        assert_eq!(format!("{}", result), "eeeeeeeeeeeeeeeeeeeeeeeeRRReeeeeeeeRRReeeeeeeeeeeeeeee");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // i1@0:2x1x0
        piece = pieces.by_str("i1").unwrap();
        shape = piece.shape(0);
        result = rgen.place_piece(&result, shape, piece.color, &abs_yrg!(2, 1, 0)).unwrap();
        assert_eq!(format!("{}", result), "eeeeeeeeeeeeeeeeRRRRRReeRRReeeeeeeeRRReeeeeeeeeeeeeeee");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // W1@0:0x0x0
        piece = pieces.by_str("W1").unwrap();
        shape = piece.shape(0);
        result = rgen.place_piece(&result, shape, piece.color, &abs_yrg!(0, 0, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBeeeeBBBeeeeeeRRRRRReeRRReeeeeeeeRRReeeeeeeeeeeeeeee");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // P1@0:4x3x1
        piece = pieces.by_str("P1").unwrap();
        shape = piece.shape(0);
        result = rgen.place_piece(&result, shape, piece.color, &abs_yrg!(4, 3, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBeeeeBBBeeeeeeRRRRRReeRRReeeeeeeeRRReeeeRRRRReeeeeeR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // VB@300:0x3x0
        piece = pieces.by_str("VB").unwrap();
        shape = piece.shape(300);
        result = rgen.place_piece(&result, shape, piece.color, &abs_yrg!(0, 3, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBeeeeBBRRRRRReeRRReeeeeeeeRRReeeeRRRRReeeeeeR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // J1@0:1x1x1
        piece = pieces.by_str("J1").unwrap();
        shape = piece.shape(0);
        result = rgen.place_piece(&result, shape, piece.color, &abs_yrg!(1, 1, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBOOOOBBRRRRRROORRReeeeeeeeRRReeeeRRRRReeeeeeR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // L2@0:3x2x1
        piece = pieces.by_str("L2").unwrap();
        shape = piece.shape(0);
        result = rgen.place_piece(&result, shape, piece.color, &abs_yrg!(3, 2, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBOOOOBBRRRRRROORRReeeYYYYYRRReeYeRRRRReeeeeeR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // TW@0:5x4x0
        piece = pieces.by_str("TW").unwrap();
        shape = piece.shape(0);
        result = rgen.place_piece(&result, shape, piece.color, &abs_yrg!(5, 4, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBOOOOBBRRRRRROORRReeeYYYYYRRReeYeRRRRReeeWWWR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // TO@180:4x2x0
        piece = pieces.by_str("TO").unwrap();
        shape = piece.shape(180);
        result = rgen.place_piece(&result, shape, piece.color, &abs_yrg!(4, 2, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRReeYeRRRRReeeWWWR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // TY@240:5x4x0
        piece = pieces.by_str("TY").unwrap();
        shape = piece.shape(240);
        result = rgen.place_piece(&result, shape, piece.color, &abs_yrg!(5, 4, 0)).unwrap();
        assert_eq!(format!("{}", result), "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRReeYYRRRRReYYWWWR");
        assert_board_overlaps(result,     "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");

        // TY@300:4x2x0
        piece = pieces.by_str("TY").unwrap();
        shape = piece.shape(300);
        let finalb = rgen.place_piece(&result, shape, piece.color, &abs_yrg!(4, 2, 0)).unwrap();
        assert_eq!(format!("{}", finalb), "BBBBBBBBBBOOOOBBRRRRRROORRROOOYYYYYRRRYYYYRRRRRYYYWWWR");
    }

    fn assert_board_overlaps(board: Board, expected: &str) {
        let actual = &format!("{}", board)[..];
        assert_eq!(actual.len(), expected.len());
        for (a, e) in actual.chars().zip(expected.chars()) {
            if a != 'e' {
                assert_eq!(a, e);
            }
        }
    }
}

// ~~
