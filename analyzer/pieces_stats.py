# Tangram Puzzle: Compute Pieces Statistics
#
# (c) 2025 ralfoide at gmail

import colors
import coord
import cv2
import math
import numpy as np
import os
import re
import time

from coord import Axis, XY, YRG, YRGCoord
from img_proc import Cell
from gen import Generator, Cells, PIECES, EMPTY_CELL
from typing import Tuple
import re

N2 = coord.N2
PX_CELL_SIZE = 20


class PiecesStats:
    def __init__(self, output_dir_path:str, prefix:str) -> None:
        self.generator = Generator(output_dir_path)
        self.prefix = prefix
        self.output_dir_path = output_dir_path
        self.yrg_coords = None
        self.size_px = XY( (0, 0) )
        self.generated_images = []

    def generate(self, solutions_file: str) -> None:
        print("------")
        print(f"Generating pieces statistics in {self.output_dir_path}")
        print("------")

        self.size_px, self.yrg_coords, cells_empty = self.generator.create_cells(PX_CELL_SIZE)
        self.generator.size_px = self.size_px
        self.generator.yrg_coords = self.yrg_coords

        solutions = self.read_solutions(solutions_file)
        print("@@ Found", len(solutions), "unique solutions")

        stats = self.count_pieces_rotations(solutions)
        self.create_rotations_images(stats, cells_empty)

        print("")

    def read_solutions(self, solutions_file: str) -> dict:
        solutions = {}
        visited = set()
        # Extract the solution out of a string such as
        # "@@ [100099924] SIG OOOYYYYBOOYYYYYYBBBOWWWRRYYBBRRRRRRRRRBBOOORRRRBBBBRRR HR@0:4x4x0,i2@0:3x1x1,W2@120:3x1x0,P2@120:3x5x1,VB@120:5x4x0,J1@120:2x1x1,L2@180:0x3x0,TW@0:2x2x0,TO@180:4x3x1,TY@120:2x5x0,TY@180:0x2x1"
        re_solutions = re.compile(r"([B-Yi12]{2}@[0-9]+:[0-9]+x[0-9]+x[0-9]+,[B-Yi0-9,@:x]+)")
        re_solution = re.compile(r"([B-Yi12]{2})@([0-9]+):([0-9]+)x([0-9]+)x([0-9]+)")
        print("@@ Reading", solutions_file)
        with open(solutions_file, "r") as f:
            for line in f.readlines():
                match = re_solutions.search(line)
                if match:
                    solutions_str = match.group(1)

                    # Sort the solutions as a string to check their uniqueness
                    sol_str = solutions_str.split(",")
                    sol_str.sort()
                    unique_str = ",".join(sol_str)
                    if unique_str in visited:
                        continue
                    visited.add(unique_str)

                    for solution_str in solutions_str.split(","):
                        match = re_solution.search(solution_str)
                        if match:
                            if solution_str in solutions:
                                solutions[solution_str]["count"] += 1
                            else:
                                piece = match.group(1)
                                angle = int(match.group(2))
                                y = int(match.group(3))
                                r = int(match.group(4))
                                g = int(match.group(5))
                                entry = {
                                    "key": f"{piece}@{angle}",
                                    "piece": piece,
                                    "angle": angle,
                                    "y": y,
                                    "r": r,
                                    "g": g,
                                    "count": 1
                                }
                                solutions[solution_str] = entry

        print("@@ Parsed", len(visited), "unique solutions with", len(solutions), "unique pieces")
        return solutions

    def count_pieces_rotations(self, solutions: dict) -> [dict]:
        stats = []
        for p_key in PIECES:
            p = PIECES[p_key]
            names = p.get("name", [p_key])
            for name in names:
                for angle in range(0, p.get("rot", 300) + 1, 60):
                    key = f"{name}@{angle}"
                    entry = {
                        "p_key": p_key,
                        "key": key,
                        "name": name,
                        "angle": angle,
                        "count": sum([ e["count"]
                                       for e in solutions.values()
                                       if e["key"] == key ]),
                    }
                    stats.append(entry)
        return stats

    def create_rotations_images(self, stats: [dict], cells_empty: Cells) -> None:
        for entry in stats:
            name = entry["name"]
            angle = entry["angle"]
            img_suffix = "%s@%03d" % (name, angle)

            p_info = PIECES[entry["p_key"]]
            if "name" in p_info:
                cells = p_info["cells"][p_info["name"].index(name)]
            else:
                cells = p_info["cells"][0]
            color = p_info["color"]

            piece_info = {
                "key": entry["key"],
                "angle": angle,
                "cells": cells,
                "color": color,
            }

            # Offset cells to center the piece in the image
            rotated, _ = self.generator.rotate_piece_cells(cells, piece_info, angle)
            y_center = sum([c[0] for c in rotated]) // len(rotated)
            r_center = sum([c[1] for c in rotated]) // len(rotated)

            cells = self.generator.place_single_piece(
                cells_empty,
                piece_info,
                N2 - y_center, N2 - r_center, 0)
            img = self.generator.draw_cells_into(cells, dest_img=None)
            self.write_piece_img(img_suffix, img)

    def write_piece_img(self, suffix: str, in_img:np.array) -> None:
        # TBD: merge dup in Generator
        name = f"piece_{suffix}.png"
        self.generated_images.append(name)
        path = os.path.join(self.output_dir_path, name)
        cv2.imwrite(path, in_img)
        print("@@ Saved", path)


# ~~
