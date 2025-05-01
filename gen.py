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

DEBUG_MAX_PIECE=12
DEBUG_SAVE=True
REPORT_FILE="temp.txt"

PX_CELL_SIZE = 30

PIECES = {
    "TW": {
        "piece": "TW",
        "color": "White",
        "cells": [
            [ (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
        ],
        "rot": False,
    },
    "HR": {
        "piece": "HR",
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

    def create_cells(self) -> Tuple[YRGCoord, list[Cell]]:
        cells = []
        n2 = coord.N//2
        center_px = int(PX_CELL_SIZE * n2)

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

        color = colors.by_name("Red")
        for triangle in self.triangles(yrg_coords):
            cells.append(Cell(triangle, None, (64, 64, 64)))
        img_size = XY( (center_px * 2, center_px * 2) )
        print("@@ Image size:", img_size)
        return img_size, yrg_coords, cells

    def triangles(self, yrg_coords:YRGCoord) -> Generator:
        # TBD: merge dup in ImageProcessor
        n2 = coord.N//2
        for (y, r, g) in coord.VALID_YRG:
            y_piece = y - n2
            r_piece = r - n2
            yield yrg_coords.triangle(YRG(y_piece, r_piece, g))

    def draw_cells_into(self, cells:list[Cell], dest_img:np.array) -> np.array:
        # TBD: merge dup in ImageProcessor
        if dest_img is None:
            dest_img = np.zeros( (self.size_px.y, self.size_px.x, 3), dtype=np.uint8 )
        else:
            dest_img.fill(0)

        if len(cells) == 0:
            return dest_img

        radius = int(cells[0].triangle.inscribed_circle_radius() *.5 )

        for cell in cells:
            poly = np.int32(cell.triangle.to_np_array())
            bg = cell.mean_bgr
            if cell.color is not None:
                bg = cell.color["bgr"]
            cv2.fillPoly(dest_img, [poly], bg)
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

    def find_cell(self, cells:list[Cell], y_piece:int, r_piece:int, g_piece:int) -> Cell:
        """Returns the cell (if valid) or None."""
        n2 = coord.N//2
        try:
            yrg_abs = YRG(y_piece, r_piece, g_piece)
            for cell in cells:
                if cell.triangle.yrg == yrg_abs:
                    return cell
        except AssertionError:
            # Ignore YRG asserting its Y/R range. Just return None.
            pass
        return None

    def place_piece(self, dest_cells:list[Cell], piece_cells:list, piece:dict, y_offset:int=0, r_offset:int=0, angle_deg:int=0) -> list[Cell]:
        """
        Fit the given piece if the cells ONLY if the cells are empty (color is None).
        Returns a new cell list if the piece can fit.
        Otherwise returns None.
        """
        color_name = piece["color"]
        color = colors.by_name(color_name)
        assert color is not None

        rotated = self.rotate_piece_cells(piece_cells, angle_deg)

        # Make a "deep" copy of cells
        dest_cells = [ cell.copy() for cell in dest_cells ]

        for y, r, g in rotated:
            y += y_offset
            r += r_offset
            cell = self.find_cell(dest_cells, y, r, g)
            if cell is None:
                # The YRG coordinate is out of bounds.
                return None
            if cell.color is not None:
                # That cell is already occupied.
                return None
            cell.color = color
        return dest_cells

    def rotate_piece_cells(self, yrg_list:list, angle_deg:int) -> list:
        """
        Rotate the (y,r,g) tuples for a given piece.
        Angle_deg must be a multiple of 60 in range [0, 360[.
        """
        if angle_deg == 0:
            return yrg_list.copy()
        yrg_rot = []
        for y, r, g in yrg_list:
            for angle in range(60, angle_deg+1, 60):
                y, r, g = self.yrg_coords.rot_60_ccw_yrg(y, r, g)
            yrg_rot.append( (y, r, g) )
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
                pieces.append( {"key": key, "idx": i, "cells": cells, "rot": rotate} )
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

    def gen_all_solutions(self, cells:list[Cell]) -> Generator:
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

    def place_first_piece(self, cells:list[Cell], combos:list, current:str) -> Generator:
        if len(combos) == 0:
            return
        info = combos.pop(0)
        key = info["key"]
        piece_cells = info["cells"]
        angle_deg = info["angle"]

        piece = PIECES[key]
        # g value of the first cell
        first_g = piece_cells[0][2]
        n2 = coord.N//2

        for y, r, g in coord.VALID_YRG:
            # Only starts on cells with the same g value
            if g == first_g:
                # print(f"@@ gen {self.img_count} {combos}, {current} + {key} @ {angle_deg}:{y}x{r}")
                new_cells = self.place_piece(cells, piece_cells, piece, y - n2, r - n2, angle_deg)
                self.gen_count += 1
                # new_current = f"{current}{key}@{angle_deg}:{y}x{r} "
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
