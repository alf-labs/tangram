# Tangram Puzzle: Generate All Possible Solutions
#
# (c) 2025 ralfoide at gmail
#
# Note: run with python -O or -OO to disable __debug__ sections.

import colors
import coord
import cv2
import math
import numpy as np
import os
import time

from coord import Axis, XY, YRG, YRGCoord
from img_proc import Cell
from typing import Generator as TGenerator
from typing import Tuple

N2 = coord.N2
DEBUG_PIECE=-1
DEBUG_SAVE=False

PX_CELL_SIZE = 30
INVALID_CELL = "INVALID"
EMPTY_CELL = "EMPTY"

PIECES = {
    "HR": {
        "color": "Red",
        "cells": [
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 1, 1), (1, 1, 0), (1, 0, 1), ],
        ],
        "rot": 0,
    },
    "i": {
        "color": "Red",
        "name": [ "i1", "i2" ],
        "cells": [
            [ (0, -1, 0), (0, -1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ],
            [ (0, -1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), ],
        ],
        "rot": 120,
    },
    "W": {
        "color": "Black",
        "name": [ "W1", "W2" ],
        "cells": [
            [ (1, 1, 0), (1, 0, 1), (1, 0, 0), (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 2, 0), (1, 1, 1), (1, 1, 0), ],
        ],
    },
    "P": {
        "color": "Red",
        "name": [ "P1", "P2" ],
        "cells": [
            [ (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), (0, 2, 1), (1, 2, 1), ],
            [ (1, 1, 1), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), (0, 2, 1), ],
        ]
    },
    "VB": {
        "color": "Black",
        "cells": [
            [ (1, 0, 0), (1, 0, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ],
        ],
    },
    "J": {
        "color": "Orange",
        "name": [ "J1", "J2" ],
        "cells": [
            [ (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), (1, 2, 1), (1, 2, 0), ],
            [ (1, 1, 0), (1, 0, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ],
        ],
    },
    "L": {
        "color": "Yellow",
        "name": [ "L1", "L2" ],
        "cells": [
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), (1, 2, 1), ],
            [ (1, 0, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), ],
        ],
    },
    "TW": {
        "color": "White",
        "cells": [
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
        ],
        "rot": 0,
    },
    "TO": {
        "color": "Orange",
        "cells": [
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
        ],
    },
    "TY": {
        "color": "Yellow",
        "cells": [
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
        ],
        "count": 2,
    },
}


class Cells:
    def __init__(self):
        self.cells   = None     # list[Cell]
        self.colors  = None     # list[str]
        self.placed  = None     # list[tuple(piece,y,r)]
        self.perm_index = 0
        self.g_free = [ coord.NUM_CELLS // 2, coord.NUM_CELLS // 2 ]

    def init_cells(self, yrg_coords:YRGCoord) -> "Cells":
        self.cells = []
        self.colors = [ INVALID_CELL ] * (coord.N * coord.N * 2)
        for triangle in self._triangles(yrg_coords):
            self.cells.append(Cell(triangle, None, (64, 64, 64)))
            y_abs, r_abs, g = triangle.yrg.to_abs()
            self.set_color(y_abs, r_abs, g, color=EMPTY_CELL)
        return self

    def valid(self, y_abs, r_abs, g) -> bool:
        idx = 12 * y_abs + 2 * r_abs + g
        return idx >= 0 and idx < len(self.colors) and self.colors[idx] != INVALID_CELL

    def occupied(self, y_abs, r_abs, g) -> bool:
        idx = 12 * y_abs + 2 * r_abs + g
        if idx >= 0 and idx < len(self.colors):
            c = self.colors[idx]
            return c != EMPTY_CELL and c != INVALID_CELL
        else:
            return False

    def get_color(self, y_abs, r_abs, g):
        idx = 12 * y_abs + 2 * r_abs + g
        return self.colors[idx]

    def set_color(self, y_abs, r_abs, g, color) -> None:
        idx = 12 * y_abs + 2 * r_abs + g
        old_color = self.colors[idx]
        self.colors[idx] = color
        if old_color == EMPTY_CELL and old_color != color:
            assert self.g_free[g] > 0
            self.g_free[g] -= 1

    def copy(self) -> "Cells":
        new_cells = Cells()
        new_cells.cells = self.cells    # Warning: linked, not duplicated!
        new_cells.colors = self.colors.copy()
        new_cells.g_free = self.g_free.copy()
        new_cells.perm_index = self.perm_index
        return new_cells

    def _triangles(self, yrg_coords:YRGCoord) -> TGenerator:
        # TBD: merge dup in ImageProcessor
        for (y, r, g) in coord.VALID_YRG:
            y_piece = y - N2
            r_piece = r - N2
            yield yrg_coords.triangle(YRG(y_piece, r_piece, g))

    def signature(self) -> str:
        sig = "".join([ col[0] for col in self.colors if col != INVALID_CELL ])
        return sig

    def placed_str(self) -> str:
        if not self.placed:
            return "--"
        return ",".join([ f"{piece_info['key']}@{piece_info['angle']}:{y_abs}x{r_abs}x{g}" for piece_info, y_abs, r_abs, g in self.placed ])


class Generator:
    def __init__(self, output_dir_path:str):
        self.output_dir_path = output_dir_path
        self.yrg_coords = None
        self.size_px = XY( (0, 0) )
        self.img_count = 0
        self.generated_images = []
        self.rot_cache = {}
        self.pos_cache = {}
        self.adjacents_cache = {}
        # Statistics
        self.report_file = None
        self.gen_count = 0
        self.gen_failed = 0
        self.perm_count = 0
        self.reject_g_count = 0
        self.reject_yrg_invalid = 0
        self.reject_occupied = 0
        self.reject_adjacents = 0

    def generate(self, gen_output_name:str, overwrite:bool, cores_num:int, core_index:int, perm_start:int) -> None:
        gen_output_name = gen_output_name.replace("IDX", str(core_index))
        gen_output_name = gen_output_name.replace("CORES", str(cores_num))
        report_file_path = os.path.join(self.output_dir_path, gen_output_name)
        print("------")
        print(f"Generating solutions in {self.output_dir_path}")
        print(f"File: {report_file_path}")
        print("------")

        with open(report_file_path, "a") as self.report_file:
            self.size_px, self.yrg_coords, cells_empty = self.create_cells(PX_CELL_SIZE)
            self.precompute_positions(cells_empty)
            for cells in self.gen_all_solutions(cells_empty, cores_num, core_index, perm_start):
                img = self.draw_cells_into(cells, dest_img=None)
                self.write_indexed_img(img)
                r = f"@@ [{cells.perm_index}] SIG {cells.signature()} {cells.placed_str()}"
                print(r)
                self.report_file.write(r)
                self.report_file.write("\n")
                self.report_file.flush()


        print("")
        print(f"Stats: permutations={self.perm_count}, gen calls={self.gen_count}, images={self.img_count}")
        print("")

    def create_cells(self, cell_size: int) -> Tuple[YRGCoord, Cells]:
        center_px = int(cell_size * N2)

        p = {}
        for angle_deg in range(0, 360, 60):
            # The point order is defined counter-clockwise
            angle_rad = np.radians(-angle_deg)
            px = center_px + math.cos(angle_rad) * center_px
            py = center_px + math.sin(angle_rad) * center_px
            p[angle_deg] =  (px, py)

        # Define the axes (in a CCW order)
        y_axis = Axis(( p[ 60], p[120] ), ( p[240], p[300] ))
        r_axis = Axis(( p[120], p[180] ), ( p[300], p[  0] ))
        yrg_coords = YRGCoord((center_px, center_px), y_axis, r_axis)

        img_size = XY( (center_px * 2, center_px * 2) )
        cells = Cells().init_cells(yrg_coords)
        # print("@@ Image size:", img_size)
        return img_size, yrg_coords, cells

    def draw_cells_into(self, cells:Cells, dest_img:np.array) -> np.array:
        # TBD: merge dup in ImageProcessor
        if dest_img is None:
            dest_img = np.zeros( (self.size_px.y, self.size_px.x, 3), dtype=np.uint8 )
        else:
            dest_img.fill(0)

        radius = int(cells.cells[0].triangle.inscribed_circle_radius() *.5 )
        bg = (32, 32, 32)

        for cell in cells.cells:
            poly = np.int32(cell.triangle.to_np_array())
            color = cells.get_color(*cell.triangle.yrg.to_abs())
            # color can be a tuple (b, g, r) or a color str
            if color == EMPTY_CELL:
                fg = bg
            elif isinstance(color, tuple):
                fg = color
            else:
                fg = colors.by_name(color)["bgr"]

            cv2.fillPoly(dest_img, [poly], fg)
            # This border will become transparent around every cell.
            cv2.polylines(dest_img, [poly], isClosed=True, color=(0, 0, 0), thickness=1)
        for cell in cells.cells:
            poly = np.int32(cell.triangle.to_np_array())
            color = cells.get_color(*cell.triangle.yrg.to_abs())
            if color != EMPTY_CELL:
                # Redraw a darker but not transparent border around painted cells only.
                cv2.polylines(dest_img, [poly], isClosed=True, color=(8, 8, 8), thickness=1)

        return dest_img

    def write_indexed_img(self, in_img:np.array) -> None:
        name = "gen_%06d.jpg" % self.img_count
        self.generated_images.append(name)
        self.img_count += 1
        if DEBUG_SAVE:
            path = os.path.join(self.output_dir_path, name)
            cv2.imwrite(path, in_img)
            print("@@ Saved", path)

    def _place_piece(self,
                     dest_cells:Cells,
                     piece_cells:list,
                     piece_info:dict,
                     y_offset:int=0,
                     r_offset:int=0,
                     angle_deg:int=0,
                     validate:bool=True) -> Cells:
        """
        Fit the given piece if the cells ONLY if the cells are empty (color is None).
        Returns a new cell list if the piece can fit.
        Otherwise returns None.
        """
        color_name = piece_info["color"]

        rotated, g_count = self.rotate_piece_cells(piece_cells, piece_info, angle_deg)

        if validate:
            # Validate that the puzzle has enought empty cells to event fit the piece
            # (we don't check whether they are adjacent here, just the global count)
            # print("@@", piece_info["key"], color_name, "g_count", g_count, "cells", dest_cells.g_free, dest_cells.signature())
            if g_count[0] > dest_cells.g_free[0] or g_count[1] > dest_cells.g_free[1]:
                # The piece definitely will not fit here.
                self.reject_g_count += 1
                return None

        # Make a "deep" copy of cells only when needed
        copy_on_write = True
        cells = dest_cells

        for y, r, g in rotated:
            y_abs = y + y_offset + N2
            r_abs = r + r_offset + N2

            if not cells.valid(y_abs, r_abs, g):
                # The YRG coordinate is out of bounds.
                if __debug__: self.reject_yrg_invalid += 1
                return None
            if cells.occupied(y_abs, r_abs, g):
                # That cell is already occupied.
                if __debug__: self.reject_occupied += 1
                return None
            if copy_on_write:
                cells = cells.copy()
                copy_on_write = False
            cells.set_color(y_abs, r_abs, g, color_name)

        if validate:
            # The piece fits at the desired location.
            # Now validate that we are not leaving 1-single empty cells around.
            adjacents = self.adjacents_cells(rotated, piece_info, angle_deg)
            for y, r, g in adjacents:
                y_abs = y + y_offset + N2
                r_abs = r + r_offset + N2
                if not cells.occupied(y_abs, r_abs, g):
                    if cells.valid(y_abs, r_abs, g):
                        if self.is_cell_surrounded(y_abs, r_abs, g, cells):
                            # Skip this permutation.
                            if __debug__: self.reject_adjacents += 1
                            return None

        return cells

    def rotate_piece_cells(self, yrg_list:list, piece_info:dict, angle_deg:int) -> Tuple[list,list]:
        """
        Rotate the (y,r,g) tuples for a given piece.
        Angle_deg must be a multiple of 60 in range [0, 360[.
        """
        cache_key = f"{piece_info['key']}@{angle_deg}"
        cached = self.rot_cache.get(cache_key)
        if cached is not None:
            return cached

        # Apply an offset such that the first cell is always at (y=0, r=0). "g" does not change.
        offset = False
        y_offset = 0
        r_offset = 0
        yrg_rot = []
        g_count = [0, 0]
        for y, r, g in yrg_list:
            for angle in range(60, angle_deg+1, 60): # no-op if angle_deg==0
                y, r, g = self.yrg_coords.rot_60_ccw_yrg(y, r, g)
            if not offset:
                offset = True
                y_offset = y
                r_offset = r
            y -= y_offset
            r -= r_offset
            g_count[g] += 1
            yrg_rot.append( (y, r, g) )

        result = (yrg_rot, g_count)
        self.rot_cache[cache_key] = result
        return result

    def adjacents_cells(self, yrg_list:list, piece_info:dict, angle_deg:int) -> list:
        cache_key = f"{piece_info['key']}@{angle_deg}"
        cached = self.adjacents_cache.get(cache_key)
        if cached is not None:
            return cached

        abs_neigh = []
        abs_list = [ (y + N2, r + N2, g) for y, r, g in yrg_list ]
        for yrg_abs in abs_list:
            idx = coord.VALID_YRG_TO_IDX[ yrg_abs ]
            adjacents = coord.VALID_YRG_ADJACENTS[idx]
            for adjacent in adjacents.values():
                if (adjacent
                    and not adjacent in abs_neigh
                    and not adjacent in abs_list):
                    abs_neigh.append(adjacent)
        yrg_neigh = [ (y_abs - N2, r_abs - N2, g) for y_abs, r_abs, g in abs_neigh ]

        self.adjacents_cache[cache_key] = yrg_neigh
        return yrg_neigh

    def is_cell_surrounded(self, y_abs:int, r_abs:int, g:int, cells:Cells) -> bool:
        idx = coord.VALID_YRG_TO_IDX[ (y_abs, r_abs, g) ]
        adjacents = coord.VALID_YRG_ADJACENTS[idx]
        num_occupied = 0
        num_cells = 0
        for adjacent in adjacents.values():
            if adjacent:
                num_cells += 1
                y_abs, r_abs, g = adjacent
                if cells.occupied(y_abs, r_abs, g):
                    num_occupied += 1
        return num_occupied == num_cells

    def gen_pieces_list(self, select_piece:int=0) -> TGenerator:
        """
        Generate all the combinations of pieces we want to place, and their
        rotation, but without indicating where to place them.

        select_piece: for debugging purposes, only keep the selected piece.
        """
        pieces = []
        for key, properties in PIECES.items():
            count = properties.get("count", 1)
            rot_max = properties.get("rot", 300)
            names = properties.get("name", [ key])
            cells = properties["cells"]
            for i in range(0, count):
                piece_info = {
                    "key": key,
                    "names": names,
                    "cells": cells,
                    "rot": rot_max,
                    "color": properties["color"],
                }
                pieces.append(piece_info)
        if select_piece > -1:
            pieces = [ pieces[select_piece] ]
        else:
            print("@@ Number of pieces in permutations:", len(pieces))

        def _gen(_pieces, _current):
            if len(_pieces) == 0:
                yield _current
                return
            _pieces = _pieces.copy()
            _first = _pieces.pop(0)
            _key = _first["key"]
            _cells = _first["cells"]
            _angle_max = _first["rot"]
            for _i, _c in enumerate(_cells):
                for _angle in range(0, _angle_max + 1, 60):
                    _new_current = _current.copy()
                    _info = _first.copy()
                    _info["key"] = _info["names"][_i]
                    _info["angle"] = _angle
                    _info["cells"] = _c
                    _new_current.append( _info )
                    yield from _gen(_pieces, _new_current)

        yield from _gen(pieces, [])

    def gen_all_solutions(self, cells_empty:Cells, cores_num:int, core_index:int, perm_start:int) -> TGenerator:
        print("@@ Generate All Solutions")
        ts = time.time()
        spd = 0
        perm_count = self.perm_count
        for permutations in self.gen_pieces_list(DEBUG_PIECE):
            perm_count += 1
            self.perm_count = perm_count
            if cores_num > 1:
                if perm_count % cores_num != core_index:
                    if __debug__: print(f"@@ skip {perm_count}    ")
                    continue
            if perm_start > perm_count:
                if __debug__: print(f"@@ skip {perm_count}    ")
                continue
            perms_str = " ".join([ f"{x['key']}@{x['angle']}" for x in permutations ])
            print(f"@@ perm {perm_count}, {'%.2f' % spd} s/p, img {self.img_count}, {self.gen_count} / {self.gen_failed} [ {self.reject_g_count} {self.reject_yrg_invalid} {self.reject_occupied} {self.reject_adjacents} ] -- {perms_str}")
            cells_empty.perm_index = perm_count
            yield from self.place_first_piece(cells_empty, permutations, [])
            nts = time.time()
            if nts > ts:
                spd = (nts - ts)
                ts = nts
        r = f"@@ DEBUG num permutations: piece={DEBUG_PIECE} perms_count={perm_count} gen_count={self.gen_failed} / {self.gen_count} img_count={self.img_count}"
        self.report_file.write(r)
        self.report_file.write("\n")
        print(r)

    def precompute_positions(self, cells_empty:Cells) -> None:
        print("@@ Precompute Cached Positions")
        for select_piece in range(0, len(PIECES)):
            for permutations in self.gen_pieces_list(select_piece):
                assert len(permutations) == 1
                p = permutations[0]
                pos_key = f"{p['key']}@{p['angle']}"
                all_pos = []
                for new_cells in self.place_first_piece(cells_empty, permutations, []):
                    if new_cells is not None:
                        piece_info, y_abs, r_abs, g = new_cells.placed[0]
                        all_pos.append( (y_abs, r_abs, g) )
                self.pos_cache[pos_key] = all_pos

    def place_single_piece(self, cells:Cells, piece_info:dict, y_abs, r_abs, g) -> Cells:
        key = piece_info["key"]
        piece_cells = piece_info["cells"]
        angle_deg = piece_info["angle"]
        pos_key = f"{key}@{angle_deg}"

        return self._place_piece(cells, piece_cells, piece_info, y_abs - N2, r_abs - N2, angle_deg, validate=False)

    def place_first_piece(self, cells:Cells, combos:list, placed:list) -> TGenerator:
        if len(combos) == 0:
            assert len(combos) > 0
            return # exit the generator without a result
        combos = combos.copy()
        piece_info = combos.pop(0)
        key = piece_info["key"]
        piece_cells = piece_info["cells"]
        angle_deg = piece_info["angle"]
        pos_key = f"{key}@{angle_deg}"

        # g value of the first cell
        first_g = piece_cells[0][2]

        def _place_at(y_abs, r_abs, g):
            new_cells = self._place_piece(cells, piece_cells, piece_info, y_abs - N2, r_abs - N2, angle_deg)
            if __debug__: self.gen_count += 1
            if new_cells is None:
                # We were not able to place the piece on the board.
                # Loop and try next position.
                if __debug__: self.gen_failed += 1
            else:
                # Remember which piece was placed and where
                new_placed = placed.copy()
                new_placed.append( (piece_info, y_abs, r_abs, g) )
                if len(combos) == 0:
                    print(f"@@ GEN {self.gen_count} / {self.gen_failed} [ {self.reject_g_count} {self.reject_yrg_invalid} {self.reject_occupied} {self.reject_adjacents} ] -- img:{self.img_count}, g {new_cells.g_free[0]} {new_cells.g_free[1]}, sig {new_cells.signature()}")
                    new_cells.placed = new_placed
                    yield new_cells
                else:
                    if __debug__: # Extra verbose, only for debugging
                        print(f"@@ SUB {self.gen_count} / {self.gen_failed} [ {self.reject_g_count} {self.reject_yrg_invalid} {self.reject_occupied} {self.reject_adjacents} ] -- img:{self.img_count}, g {new_cells.g_free[0]} {new_cells.g_free[1]}, sig {new_cells.signature()}", end="\r")
                    yield from self.place_first_piece(new_cells, combos, new_placed)

        all_pos = self.pos_cache.get(pos_key)
        if all_pos is not None:
            # If we have precomputed all posible cell locations for this piece
            for y_abs, r_abs, g in all_pos:
                yield from _place_at(y_abs, r_abs, g)
        else:
            # Otherwise iterate over all the board, including possible invalid locations
            for y_abs, r_abs, g in coord.VALID_YRG:
                # Only starts on cells with the same g value
                if g == first_g:
                    yield from _place_at(y_abs, r_abs, g)


# ~~
