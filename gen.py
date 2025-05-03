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
from typing import Generator
from typing import Tuple

N2 = coord.N2
DEBUG_MAX_PIECE=0
DEBUG_SAVE=True
REPORT_FILE="temp.txt"

PX_CELL_SIZE = 30
INVALID_CELL = "INVALID"
EMPTY_CELL = "EMPTY"

PIECES = {
    "TW": {
        "color": "White",
        "cells": [
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
        ],
        "rot": 0,
    },
    "HR": {
        "color": "Red",
        "cells": [
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 1, 1), (1, 1, 0), (1, 0, 1), ],
        ],
        "rot": 0,
    },
    "W": {
        "color": "Black",
        "cells": [
            [ (1, 1, 0), (1, 0, 1), (1, 0, 0), (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 2, 0), (1, 1, 1), (1, 1, 0), ],
        ],
    },
    "i": {
        "color": "Red",
        "cells": [
            [ (0, -1, 0), (0, -1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ],
            [ (0, -1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), ],
        ],
        "rot": 120,
    },
    "P": {
        "color": "Red",
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
        "cells": [
            [ (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), (1, 2, 1), (1, 2, 0), ],
            [ (1, 1, 0), (1, 0, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ],
        ],
    },
    "L": {
        "color": "Yellow",
        "cells": [
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), (1, 2, 1), ],
            [ (1, 0, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), ],
        ],
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
        return new_cells

    def _triangles(self, yrg_coords:YRGCoord) -> Generator:
        # TBD: merge dup in ImageProcessor
        for (y, r, g) in coord.VALID_YRG:
            y_piece = y - N2
            r_piece = r - N2
            yield yrg_coords.triangle(YRG(y_piece, r_piece, g))

    def signature(self) -> str:
        sig = "".join([ col[0] for col in self.colors if col != INVALID_CELL ])
        return sig


class Generator:
    def __init__(self, output_dir_path:str):
        self.output_dir_path = output_dir_path
        self.yrg_coords = None
        self.size_px = XY( (0, 0) )
        self.img_count = 0
        self.generated_images = []
        self.rot_cache = {}
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


    def generate(self, overwrite:bool) -> None:
        print("------")
        print(f"Generating solutions in {self.output_dir_path}")
        print("------")

        with open(REPORT_FILE, "w") as self.report_file:
            self.size_px, self.yrg_coords, cells_empty = self.create_cells()
            for cells in self.gen_all_solutions(cells_empty):
                img = self.draw_cells_into(cells, dest_img=None)
                self.write_indexed_img(img)
                sig = cells.signature()
                r = f"@@ SIG {sig}"
                print(r)
                self.report_file.write(f"@@ SIG {sig}")
                self.report_file.write("\r")


        print("")
        print(f"Stats: permutations={self.perm_count}, gen calls={self.gen_count}, images={self.img_count}")
        print("")

    def create_cells(self) -> Tuple[YRGCoord, Cells]:
        center_px = int(PX_CELL_SIZE * N2)

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
        bg = cells.cells[0].mean_bgr

        for cell in cells.cells:
            poly = np.int32(cell.triangle.to_np_array())
            color = cells.get_color(*cell.triangle.yrg.to_abs())
            if color == EMPTY_CELL:
                fg = bg
            else:
                fg = colors.by_name(color)["bgr"]
            cv2.fillPoly(dest_img, [poly], fg)
            cv2.polylines(dest_img, [poly], isClosed=True, color=(0, 0, 0), thickness=1)

        return dest_img

    def write_indexed_img(self, in_img:np.array) -> None:
        name = "gen_%06d.jpg" % self.img_count
        self.generated_images.append(name)
        self.img_count += 1
        if DEBUG_SAVE:
            path = os.path.join(self.output_dir_path, name)
            cv2.imwrite(path, in_img)
            print("@@ Saved", path)

    def place_piece(self, dest_cells:Cells, piece_cells:list, piece_info:dict, y_offset:int=0, r_offset:int=0, angle_deg:int=0) -> Cells:
        """
        Fit the given piece if the cells ONLY if the cells are empty (color is None).
        Returns a new cell list if the piece can fit.
        Otherwise returns None.
        """
        color_name = piece_info["color"]

        rotated, g_count = self.rotate_piece_cells(piece_cells, piece_info, angle_deg)

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

        cache_key = f"{piece_info['key']}:{piece_info['idx']}@{angle_deg}"
        cached = self.rot_cache.get(cache_key)
        if cached is not None:
            return cached

        yrg_rot = []
        g_count = [0, 0]
        for y, r, g in yrg_list:
            for angle in range(60, angle_deg+1, 60): # no-op if angle_deg==0
                y, r, g = self.yrg_coords.rot_60_ccw_yrg(y, r, g)
            g_count[g] += 1
            yrg_rot.append( (y, r, g) )

        result = (yrg_rot, g_count)
        self.rot_cache[cache_key] = result
        return result

    def adjacents_cells(self, yrg_list:list, piece_info:dict, angle_deg:int) -> list:
        cache_key = f"{piece_info['key']}:{piece_info['idx']}@{angle_deg}"
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

    def gen_pieces_list(self, max_num_pieces:int=0) -> Generator:
        """
        Generate all the combinations of pieces we want to place, and their
        rotation, but without indicating where to place them.

        max_num_pieces: for debugging purposes to limit the number of pieces.
        """
        pieces = []
        for key, properties in PIECES.items():
            count = properties.get("count", 1)
            rot_max = properties.get("rot", 300)
            cells = properties["cells"]
            for i in range(0, count):
                piece_info = {
                    "key": key,
                    "idx": i,
                    "cells": cells,
                    "rot": rot_max,
                    "color": properties["color"],
                }
                pieces.append(piece_info)
        if max_num_pieces > 0:
            pieces = pieces[:max_num_pieces]
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
            for c in _cells:
                for _angle in range(0, _angle_max + 1, 60):
                    _new_current = _current.copy()
                    _info = _first.copy()
                    _info["angle"] = _angle
                    _info["cells"] = c
                    _new_current.append( _info )
                    yield from _gen(_pieces, _new_current)

        yield from _gen(pieces, [])

    def gen_all_solutions(self, cells:Cells) -> Generator:
        num_debug = DEBUG_MAX_PIECE
        ts = time.time()
        spd = 0
        for permutations in self.gen_pieces_list(num_debug):
            self.perm_count += 1
            perms_str = " ".join([ f"{x['key']}@{x['angle']}" for x in permutations ])
            print(f"@@ perm {self.perm_count}, {'%.2f' % spd} s/p, img {self.img_count}, {self.gen_count} / {self.gen_failed} [ {self.reject_g_count} {self.reject_yrg_invalid} {self.reject_occupied} {self.reject_adjacents} ] -- {perms_str}")
            yield from self.place_first_piece(cells, permutations, "")
            nts = time.time()
            if nts > ts:
                spd = (nts - ts)
                ts = nts
        r = f"@@ DEBUG num permutations: pieces={num_debug} perms_count={self.perm_count} gen_count={self.gen_failed} / {self.gen_count} img_count={self.img_count}"
        self.report_file.write(r)
        self.report_file.write("\n")
        print(r)

    def place_first_piece(self, cells:Cells, combos:list, current:str) -> Generator:
        if len(combos) == 0:
            assert len(combos) > 0
        piece_info = combos.pop(0)
        key = piece_info["key"]
        piece_cells = piece_info["cells"]
        angle_deg = piece_info["angle"]

        # g value of the first cell
        first_g = piece_cells[0][2]

        for y_abs, r_abs, g in coord.VALID_YRG:
            # Only starts on cells with the same g value
            if g == first_g:
                new_cells = self.place_piece(cells, piece_cells, piece_info, y_abs - N2, r_abs - N2, angle_deg)
                if __debug__: self.gen_count += 1
                # new_current = f"{current}{key}@{angle_deg}:{y_abs}x{r_abs} "
                new_current = current
                if new_cells is None:
                    if __debug__: self.gen_failed += 1
                else:
                    if len(combos) == 0:
                        print(f"@@ GEN {self.gen_count} / {self.gen_failed} [ {self.reject_g_count} {self.reject_yrg_invalid} {self.reject_occupied} {self.reject_adjacents} ] -- img:{self.img_count}, g {new_cells.g_free[0]} {new_cells.g_free[1]}, sig {new_cells.signature()}", end="\r")
                        yield new_cells
                    else:
                        new_combos = combos.copy()
                        # Extra verbose
                        if __debug__:
                            print(f"@@ SUB {self.gen_count} / {self.gen_failed} [ {self.reject_g_count} {self.reject_yrg_invalid} {self.reject_occupied} {self.reject_adjacents} ] -- img:{self.img_count}, g {new_cells.g_free[0]} {new_cells.g_free[1]}, sig {new_cells.signature()}", end="\r")
                        yield from self.place_first_piece(new_cells, new_combos, new_current)


# ~~
