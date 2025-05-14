use crate::board::Board;
use crate::coord::{AbsYRG, Coords};
use crate::permutations::Permutations;
use crate::piece::{Colors, Shape};
use crate::pieces::Pieces;

pub struct RGen<'a> {
    pieces: &'a Pieces,
    coords: &'a Coords,
    // TBD: a callback (lambda) that receives a Board+Solution
}

impl RGen<'_> {
    pub fn new<'a>(pieces: &'a Pieces, coords: &'a Coords) -> RGen<'a> {
        RGen {
            pieces,
            coords,
        }
    }

    pub(crate) fn run(&self, piece_selector: &i32) {
        for permutations in self.pieces.iter(*piece_selector) {
            let empty_board = Board::new(permutations.index);
            self.place_pieces(empty_board, permutations);
        }
    }

    fn place_pieces(&self, board: Board, permutations: Permutations, /* solutions */) {
        let split = permutations.split_first();
        if split.is_none() {
            return;
        }
        let (first, rest) = split.unwrap();

        let piece = self.pieces.get(&*first.key).unwrap();
        let shape = piece.shape(first.angle);
        let color = piece.color;


        for yrg in self.coords.valid_yrg.iter() {
            // TBD: place piece "first" in board at offset yrg
            // match place piece option<new board>:
            // none --> continue
            // ok -->
            //   accumulate solution
            //   if rest is empty, record solution in board and emit
            //   else recurse place_piece(new board, rest, new solutions)
            let result = self.place_piece(&board, shape, color, yrg);
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
            new_board.set_color(&yrg, color);
        }

        Some(new_board)
    }
}
