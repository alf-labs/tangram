# Tangram Puzzle: Generate All Possible Solutions
#
# (c) 2025 ralfoide at gmail

import colors
import coord
import cv2
import math
import numpy as np
import os

from coord import Axis, XY, YRG, YRGCoord
from img_proc import Cell
from typing import Generator
from typing import Tuple

N2 = coord.N//2
DEBUG_MAX_PIECE=3
DEBUG_SAVE=False
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
        "rot": False,
    },
    "HR": {
        "color": "Red",
        "cells": [
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 1, 1), (1, 1, 0), (1, 0, 1), ],
        ],
        "rot": False,
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
    "i": {
        "color": "Red",
        "cells": [
            [ (0, -1, 0), (0, -1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ],
            [ (0, -1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), ],
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
    "W": {
        "color": "Black",
        "cells": [
            [ (1, 1, 0), (1, 0, 1), (1, 0, 0), (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 2, 0), (1, 1, 1), (1, 1, 0), ],
        ],
    },
}


class Cells:
    def __init__(self):
        self.cells = None
        self.colors = None

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
        c = self.colors[idx]
        return c != EMPTY_CELL and c != INVALID_CELL

    def get_color(self, y_abs, r_abs, g):
        idx = 12 * y_abs + 2 * r_abs + g
        return self.colors[idx]

    def set_color(self, y_abs, r_abs, g, color) -> None:
        idx = 12 * y_abs + 2 * r_abs + g
        self.colors[idx] = color

    def copy(self) -> "Cells":
        new_cells = Cells()
        new_cells.cells = self.cells    # Warning: linked, not duplicated!
        new_cells.colors = self.colors.copy()
        return new_cells

    def _triangles(self, yrg_coords:YRGCoord) -> Generator:
        # TBD: merge dup in ImageProcessor
        for (y, r, g) in coord.VALID_YRG:
            y_piece = y - N2
            r_piece = r - N2
            yield yrg_coords.triangle(YRG(y_piece, r_piece, g))


class Generator:
    def __init__(self, output_dir_path:str):
        self.output_dir_path = output_dir_path
        self.yrg_coords = None
        self.size_px = XY( (0, 0) )
        self.img_count = 0
        self.generated_images = []
        self.gen_count = 0
        self.gen_failed = 0
        self.perm_count = 0
        self.report_file = None
        self.rot_cache = {}

    def generate(self, overwrite:bool) -> None:
        print("------")
        print(f"Generating solutions in {self.output_dir_path}")
        print("------")

        with open(REPORT_FILE, "w") as self.report_file:
            self.size_px, self.yrg_coords, cells_empty = self.create_cells()
            for cells in self.gen_all_solutions(cells_empty):
                img = self.draw_cells_into(cells, dest_img=None)
                self.write_indexed_img(img)

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

        rotated = self.rotate_piece_cells(piece_cells, piece_info, angle_deg)

        # Make a "deep" copy of cells only when needed
        copy_on_write = True
        cells = dest_cells

        for y, r, g in rotated:
            y_abs = y + y_offset + N2
            r_abs = r + r_offset + N2

            if not cells.valid(y_abs, r_abs, g):
                # The YRG coordinate is out of bounds.
                return None
            if cells.occupied(y_abs, r_abs, g):
                # That cell is already occupied.
                return None
            if copy_on_write:
                cells = cells.copy()
                copy_on_write = False
            cells.set_color(y_abs, r_abs, g, color_name)
        return cells

    def rotate_piece_cells(self, yrg_list:list, piece_info:dict, angle_deg:int) -> list:
        """
        Rotate the (y,r,g) tuples for a given piece.
        Angle_deg must be a multiple of 60 in range [0, 360[.
        """
        if angle_deg == 0:
            return yrg_list

        cache_key = f"{piece_info['key']}:{piece_info['idx']}@{angle_deg}"
        cached = self.rot_cache.get(cache_key)
        if cached is not None:
            return cached

        yrg_rot = []
        for y, r, g in yrg_list:
            for angle in range(60, angle_deg+1, 60):
                y, r, g = self.yrg_coords.rot_60_ccw_yrg(y, r, g)
            yrg_rot.append( (y, r, g) )
        self.rot_cache[cache_key] = yrg_rot
        return yrg_rot

    def gen_pieces_list(self, max_num_pieces:int=0) -> Generator:
        """
        Generate all the combinations of pieces we want to place, and their
        rotation, but without indicating where to place them.

        max_num_pieces: for debugging purposes to limit the number of pieces.
        """
        pieces = []
        for key, properties in PIECES.items():
            count = properties.get("count", 1)
            rotate = properties.get("rot", True)
            cells = properties["cells"]
            for i in range(0, count):
                piece_info = {
                    "key": key,
                    "idx": i,
                    "cells": cells,
                    "rot": rotate,
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
            _angle_max = 300 if _first["rot"] else 0
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
        for num_debug in range(1,12):
            self.img_count = 0
            p1 = self.perm_count
            i1 = self.img_count
            g1 = self.gen_count
            f1 = self.gen_failed
            for permutations in self.gen_pieces_list(num_debug):
                self.perm_count += 1
                print("@@ permutation", self.perm_count, [ f"{x['key']} @ {x['angle']}" for x in permutations ] )
                yield from self.place_first_piece(cells, permutations, "")
            p2 = self.perm_count - p1
            i2 = self.img_count - i1
            g2 = self.gen_count - g1
            f2 = self.gen_failed - f1
            r = f"@@ DEBUG num permutations: pieces={num_debug} perms_count={p2} gen_count={f2} / {g2} img_count={i2}"
            self.report_file.write(r)
            self.report_file.write("\n")
            print(r)
            if num_debug == DEBUG_MAX_PIECE:
                break

    def place_first_piece(self, cells:Cells, combos:list, current:str) -> Generator:
        if len(combos) == 0:
            return
        piece_info = combos.pop(0)
        key = piece_info["key"]
        piece_cells = piece_info["cells"]
        angle_deg = piece_info["angle"]

        # g value of the first cell
        first_g = piece_cells[0][2]

        for y_abs, r_abs, g in coord.VALID_YRG:
            # Only starts on cells with the same g value
            if g == first_g:
                # print(f"@@ gen {self.img_count} {combos}, {current} + {key} @ {angle_deg}:{y_abs}x{r_abs}")
                new_cells = self.place_piece(cells, piece_cells, piece_info, y_abs - N2, r_abs - N2, angle_deg)
                self.gen_count += 1
                # new_current = f"{current}{key}@{angle_deg}:{y_abs}x{r_abs} "
                new_current = current
                if new_cells is None:
                    self.gen_failed += 1
                else:
                    if len(combos) == 0:
                        # print("@@ GEN", self.gen_failed, "/", self.gen_count, "--", self.img_count, new_current, "FOUND")
                        yield new_cells
                    else:
                        new_combos = combos.copy()
                        # print(f"@@ gen {self.img_count} {new_combos}, {new_current}")
                        # print(f"@@ gen {self.img_count}: {new_current}")
                        # print("@@ gen", self.img_count, new_combos)
                        # print("@@ SUB", self.gen_failed, "/", self.gen_count, "--", self.img_count, new_current, end="\r")
                        # print("@@ SUB", self.gen_failed, "/", self.gen_count, "--", self.img_count, new_current, end="\r")
                        print("@@ SUB", self.gen_failed, "/", self.gen_count, "--", self.img_count, end="\r")
                        yield from self.place_first_piece(new_cells, new_combos, new_current)


# ~~
