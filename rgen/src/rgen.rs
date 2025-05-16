use crate::board::Board;
use crate::coord::Coords;
use crate::permutations::Permutations;
use crate::pieces::Pieces;
use crate::solutions::BoardSolution;
use std::ops::RangeInclusive;
use std::string::String;
use std::sync::mpsc::Sender;
use std::thread;
use std::thread::ThreadId;
use std::time::Instant;

// Send a log about every 2 seconds. Keep it a power of 2. Use a lower value for debug builds.
#[cfg(debug_assertions)]
const PROGRESS_MOD: i32 = 64;
#[cfg(not(debug_assertions))]
const PROGRESS_MOD: i32 = 1024;


#[derive(Clone)]
pub struct RGenResult {
    pub tid: ThreadId,
    pub progress: String,
    pub result: String,
}

impl RGenResult {
    fn new_result(board: &Board, sol: &BoardSolution) -> RGenResult {
        RGenResult {
            tid: thread::current().id(),
            progress: String::new(),
            result: format!("@@ [{}] SIG {} {} # {:?}", board.perm_index, board, sol, thread::current().id()),
        }
    }

    fn new_progress(log: String) -> RGenResult {
        RGenResult {
            tid: thread::current().id(),
            progress: log,
            result: String::new(),
        }
    }
}


pub struct RGen<'a> {
    pieces: &'a Pieces,
    coords: &'a Coords,
    sender: &'a Sender<RGenResult>,
}

impl RGen<'_> {
    pub fn new<'a>(pieces: &'a Pieces,
                   coords: &'a Coords,
                   sender: &'a Sender<RGenResult>) -> RGen<'a> {
        RGen {
            pieces,
            coords,
            sender,
        }
    }

    pub fn run(&mut self,
               piece_selector: i32,
               perm_range: &RangeInclusive<i32>,
               gen_index: i32,
               gen_modulo: i32) {
        let pmin = *perm_range.start();
        let pmax = *perm_range.end();
        let start_ts = Instant::now();
        let mut spd = 0.0;
        let mut perm_count = 0;

        for permutations in self.pieces.iter(piece_selector) {
            let index = permutations.index;
            if index < pmin {
                continue
            } else if index > pmax {
                break
            }
            if gen_modulo > 1 {
                if index % gen_modulo != gen_index {
                    continue;
                }
            }

            if perm_count % PROGRESS_MOD == 0 {
                self.sender.send(RGenResult::new_progress(
                    format!("@@ perm {0}, {1:.2} pps, img CNT, {2}", index, spd, permutations)
                )).expect("Failed to send progress");
            }

            let empty_board = Board::new(permutations.index, self.coords);
            self.place_pieces(empty_board, permutations, BoardSolution::new());

            perm_count += 1;
            let now_ts = Instant::now();
            let sec = now_ts.duration_since(start_ts).as_secs_f64();
            spd = if sec <= 0.0 { 0.0 } else { (perm_count as f64) / sec };
        }
    }

    fn emit_solution(&mut self, new_board: &Board, new_sol: &BoardSolution) {
        self.sender.send(RGenResult::new_result(new_board, new_sol)).expect("Failed to send solution");
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

        for yrg in shape.positions.iter() {

            let result = board.place_piece(shape, color, yrg);
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
                        self.place_pieces(new_board, rest.clone(), new_sol);
                    }
                }
            }
        }
    }
}


// ~~
