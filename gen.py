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

class Generator:
    def __init__(self, output_dir_path:str):
        self.output_dir_path = output_dir_path
        self.cells = []
        self.yrg_coords = None
        self.size_px = XY( (0, 0) )
        self.img_count = 0

    def generate(self, overwrite:bool) -> None:
        print("------")
        print(f"Generating solutions in {self.output_dir_path}")
        print("------")

        self.size_px, self.yrg_coords, self.cells = self.create_cells()
        img = self.draw_cells_into(self.cells, dest_img=None)
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
        return XY( (center_px * 2, center_px * 2) ), yrg_coords, cells

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
        name = "gen_%04d.jpg" % self.img_count
        self.img_count += 1
        path = os.path.join(self.output_dir_path, name)
        cv2.imwrite(path, in_img)
        print("@@ Saved", path)


# ~~
