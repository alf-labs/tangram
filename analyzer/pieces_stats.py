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
from gen import Generator, Cells, PIECES, EMPTY_CELL, INVALID_CELL
from typing import Tuple
import re

N2 = coord.N2
PX_CELL_SIZE = 20


class PiecesStats:
    def __init__(self, output_dir_path:str, prefix:str, overwrite:bool=False) -> dict:
        self.generator = Generator(output_dir_path)
        self.overwrite = overwrite
        self.prefix = prefix
        self.output_dir_path = output_dir_path
        self.yrg_coords = None
        self.size_px = XY( (0, 0) )

    def generate(self, solutions_file: str) -> dict:
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
        self.create_heatmap_images(solutions, stats, cells_empty)

        print("")
        return stats

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

    def count_pieces_rotations(self, solutions: dict) -> dict:
        counts = []
        stats = {}
        stats["counts"] = counts
        for p_key in PIECES:
            p = PIECES[p_key]
            names = p.get("name", [p_key])
            for name in names:
                for angle in range(0, p.get("rot", 300) + 1, 60):
                    key = f"{name}@{angle}"
                    f_key = "%s@%03d" % (name, angle)
                    entry = {
                        "p_key": p_key,
                        "f_key": f_key,
                        "key": key,
                        "name": name,
                        "angle": angle,
                        "count": sum([ e["count"]
                                       for e in solutions.values()
                                       if e["key"] == key ]),
                    }
                    counts.append(entry)
        return stats

    def create_rotations_images(self, stats: dict, cells_empty: Cells) -> None:
        counts = stats["counts"]
        for entry in counts:
            name = entry["name"]
            angle = entry["angle"]
            f_key = entry["f_key"]
            img_suffix = f_key

            img_path = self.has_piece_img(img_suffix)
            if img_path and not self.overwrite:
                print(f"@@ Skipping {f_key} as it already exists at {img_path}")
                entry["img_path"] = img_path
                continue

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
            img_path = self.write_piece_img(img_suffix, img)
            entry["img_path"] = img_path

    def create_heatmap_images(self, solutions: dict, stats: dict, cells_empty: Cells) -> None:
        counts = stats["counts"]
        for entry in counts:
            name = entry["name"]
            angle = entry["angle"]
            key = entry["key"]
            f_key = entry["f_key"]
            img_suffix = f"{f_key}_map"

            img_path = self.has_piece_img(img_suffix)
            if img_path and not self.overwrite:
                print(f"@@ Skipping {f_key} as it already exists at {img_path}")
                entry["map_path"] = img_path
                continue

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

            merged_cells = cells_empty.copy()
            max_count = 0

            for solution in solutions.values():
                if solution["key"] == key:
                    y = solution["y"]
                    r = solution["r"]
                    g = solution["g"]
                    count = solution["count"]
                    new_cells = self.generator.place_single_piece(
                        cells_empty,
                        piece_info,
                        y, r, g)
                    if new_cells is not None:
                        max_count = self._merge_cells(new_cells, merged_cells, max_count, count)

            self._colorize_cells(merged_cells, max_count)

            img = self.generator.draw_cells_into(merged_cells, dest_img=None)
            img_path = self.write_piece_img(img_suffix, img)
            entry["map_path"] = img_path

    def _colorize_cells(self, merged_cells: Cells, max_count: int) -> None:
            if max_count <= 0:
                return
            for i in range(0, len(merged_cells.colors)):
                sum_count = merged_cells.colors[i]
                if sum_count == INVALID_CELL:
                    continue
                if sum_count == EMPTY_CELL:
                    merged_cells.colors[i] = (128, 0, 0)
                else:
                    ratio = sum_count / max_count
                    gray = int(255 * ratio)
                    # yellow (RG0) to red (R00)
                    merged_cells.colors[i] = (0, 255 - gray, 255)

    def _merge_cells(self, source: Cells, accumulator: Cells, max_count: int, count: int) -> int:
        for i in range(0, len(source.colors)):
            src = source.colors[i]
            if src == EMPTY_CELL or src == INVALID_CELL:
                continue
            dest = accumulator.colors[i]
            if dest == EMPTY_CELL:
                accumulator.colors[i] = count
            else:
                accumulator.colors[i] += count
            max_count = max(max_count, accumulator.colors[i])
        return max_count

    def has_piece_img(self, suffix: str) -> str:
        name = f"piece_{suffix}.png"
        path = os.path.join(self.output_dir_path, name)
        if os.path.exists(path):
            return name
        else:
            return ""

    def write_piece_img(self, suffix: str, in_img:np.array) -> str:
        # TBD: merge dup in Generator
        name = f"piece_{suffix}.png"
        path = os.path.join(self.output_dir_path, name)
        cv2.imwrite(path, in_img)
        print("@@ Saved", path)
        return name


# ~~
