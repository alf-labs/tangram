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

PX_CELL_SIZE = 30

PIECES = {
    "TW": {
        "color": "White",
        "cells": [ (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
        "rot": False,
    },
    "HR": {
        "color": "Red",
        "cells": [ (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 1, 1), (1, 1, 0), (1, 0, 1), ],
        "rot": False,
    },
    "i1": {
        "color": "Red",
        "cells": [ (0, -1, 0), (0, -1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ],
    },
    "i2": {
        "color": "Red",
        "cells": [ (0, -1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), ],
    },
    "J1": {
        "color": "Orange",
        "cells": [ (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), (1, 2, 1), (1, 2, 0), ],
    },
    "J2": {
        "color": "Orange",
        "cells": [ (1, 1, 0), (1, 0, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ],
    },
    "L1": {
        "color": "Yellow",
        "cells": [ (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), (1, 2, 1), ],
    },
    "L2": {
        "color": "Yellow",
        "cells": [ (1, 0, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), ],
    },
    "P1": {
        "color": "Red",
        "cells": [ (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), (0, 2, 1), (1, 2, 1), ],
    },
    "P2": {
        "color": "Red",
        "cells": [ (1, 1, 1), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), (0, 2, 1), ],
    },
    "VB": {
        "color": "Black",
        "cells": [ (1, 0, 0), (1, 0, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ],
    },
    "W1": {
        "color": "Black",
        "cells": [ (1, 1, 0), (1, 0, 1), (1, 0, 0), (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
    },
    "W2": {
        "color": "Black",
        "cells": [ (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 2, 0), (1, 1, 1), (1, 1, 0), ],
    },
    "TO": {
        "color": "Orange",
        "cells": [ (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
    },
    "TY": {
        "color": "Yellow",
        "cells": [ (0, 0, 0), (0, 0, 1), (0, 1, 0), ],
        "count": 2,
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

    def generate(self, overwrite:bool) -> None:
        print("------")
        print(f"Generating solutions in {self.output_dir_path}")
        print("------")

        self.size_px, self.yrg_coords, cells_empty = self.create_cells()
        for cells in self.gen_all_solutions(cells_empty):
            img = self.draw_cells_into(cells, dest_img=None)
            self.write_indexed_img(img)

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
        self.img_count += 1
        path = os.path.join(self.output_dir_path, name)
        cv2.imwrite(path, in_img)
        self.generated_images.append(name)
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

    def place_piece(self, cells:list[Cell], piece:dict, y_offset:int=0, r_offset:int=0, angle_deg:int=0) -> list[Cell]:
        """
        Fit the given piece if the cells ONLY if the cells are empty (color is None).
        Returns a new cell list if the piece can fit.
        Otherwise returns None.
        """
        color_name = piece["color"]
        color = colors.by_name(color_name)
        assert color is not None

        source = piece["cells"]
        rotated = self.rotate_piece_cells(source, angle_deg)

        # Make a "deep" copy of cells
        cells = [ cell.copy() for cell in cells ]

        for y, r, g in rotated:
            y += y_offset
            r += r_offset
            cell = self.find_cell(cells, y, r, g)
            if cell is None:
                # The YRG coordinate is out of bounds.
                return None
            if cell.color is not None:
                # That cell is already occupied.
                return None
            cell.color = color
        return cells

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

    def gen_all_white_pieces(self, cells:list[Cell]) -> Generator:
        """
        Generate all the locations possible for the white cell as non-rotated.
        This is the "key" that identified different puzzles, which is why we never
        rotate the white piece.
        """
        tw = PIECES["TW"]
        # g value of the first cell
        tw_g = tw["cells"][0][2]
        n2 = coord.N//2

        for y, r, g in coord.VALID_YRG:
            # Only starts on cells with the same g value
            if g == tw_g:
                new_cells = self.place_piece(cells, tw, y - n2, r - n2, angle_deg=0)
                if new_cells is not None:
                    yield new_cells

    def gen_pieces_list(self) -> Generator:
        """
        Generate all the combinations of pieces we want to place, and their
        rotation, but without indicating where to place them.
        """
        pieces = []
        for key, properties in PIECES.items():
            count = properties.get("count", 1)
            rotate = properties.get("rot", True)
            for i in range(0, count):
                pieces.append( {"key": key, "idx": count, "rot": rotate} )

        def _gen(_pieces, _current):
            if len(_pieces) == 0:
                yield _current
                return
            _pieces = _pieces.copy()
            _first = _pieces.pop(0)
            _key = _first["key"]
            _angle_max = 300 if _first["rot"] else 0
            for _angle in range(0, _angle_max + 1, 60):
                _new_current = _current.copy()
                _new_current.append( (_key, _angle) )
                yield from _gen(_pieces, _new_current)

        yield from _gen(pieces, [])

    def gen_all_solutions(self, cells:list[Cell]) -> Generator:
        for combo_pieces_rots in self.gen_pieces_list():
            print("@@ combo_pieces_rots:", combo_pieces_rots)
            yield from self.place_first_piece(cells, combo_pieces_rots, [])

    def place_first_piece(self, cells:list[Cell], combos:list, current:list) -> Generator:
        if len(combos) == 0:
            return
        key, angle_deg = combos.pop(0)

        piece = PIECES[key]
        # g value of the first cell
        first_g = piece["cells"][0][2]
        n2 = coord.N//2

        for y, r, g in coord.VALID_YRG:
            # Only starts on cells with the same g value
            if g == first_g:
                # print(f"@@ gen {self.img_count} {combos}, {current} + {key} @ {angle_deg}:{y}x{r}")
                new_cells = self.place_piece(cells, piece, y - n2, r - n2, angle_deg)
                self.gen_count += 1
                if new_cells is not None:
                    if len(combos) == 0:
                        print("@@ gen", self.gen_count, "--", self.img_count , "found")
                        yield new_cells
                    else:
                        new_combos = combos.copy()
                        # new_current = current.copy()
                        # new_current.append(f"{key} @ {angle_deg}:{y}x{r}")
                        # print(f"@@ gen {self.img_count} {new_combos}, {new_current}")
                        # print("@@ gen", self.img_count, new_combos)
                        print("@@ gen", self.gen_count, "--", self.img_count , end="\r")
                        yield from self.place_first_piece(new_cells, new_combos, current)


# ~~
