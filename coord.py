# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import math
import numpy as np

from typing import Generator
from typing import Tuple

N = 6  # YRG coords are in 0..5 range
BORDER_SIZE = 0.5 # Border is half size of an inner piece

# Valid (Y, R, G) that fit in the puzzle boundaries.
# To convert to triangle centers, substruct N/2 and add 0.5.
# Note that the bottom half of Y has a symmetry : YRG on top becomes YGR on the bottom.
VALID_YRG = [
                          (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 0), (0, 2, 1), (0, 3, 0),
               (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1), (1, 2, 0), (1, 2, 1), (1, 3, 0), (1, 3, 1), (1, 4, 0),
    (2, 0, 0), (2, 0, 1), (2, 1, 0), (2, 1, 1), (2, 2, 0), (2, 2, 1), (2, 3, 0), (2, 3, 1), (2, 4, 0), (2, 4, 1), (2, 5, 0),
    (3, 0, 1), (3, 1, 0), (3, 1, 1), (3, 2, 0), (3, 2, 1), (3, 3, 0), (3, 3, 1), (3, 4, 0), (3, 4, 1), (3, 5, 0), (3, 5, 1),
               (4, 1, 1), (4, 2, 0), (4, 2, 1), (4, 3, 0), (4, 3, 1), (4, 4, 0), (4, 4, 1), (4, 5, 0), (4, 5, 1),
                          (5, 2, 1), (5, 3, 0), (5, 3, 1), (5, 4, 0), (5, 4, 1), (5, 5, 0), (5, 5, 1),
]


class Xy:
    def __init__(self, a:np.array):
        self.x = a[0]
        self.y = a[1]

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Xy({self.x}, {self.y})"

    def to_np(self) -> np.array:
        """Converts the Xy object to a numpy array."""
        return np.array([self.x, self.y])

    def to_int(self) -> Tuple[int, int]:
        return (int(self.x), int(self.y))

class Triangle:
    def __init__(self, y_piece:int, r_piece: int, g_piece:int, p0:Xy, p1:Xy, p2:Xy):
        self.y_piece = y_piece
        self.r_piece = r_piece
        self.g_piece = g_piece
        self.xy_list = [p0, p1, p2]

    def to_np_array(self) -> np.array:
        return np.array([ xy.to_np() for xy in self.xy_list ])

    def center(self) -> Xy:
        x = sum(xy.x for xy in self.xy_list) / len(self.xy_list)
        y = sum(xy.y for xy in self.xy_list) / len(self.xy_list)
        return Xy((x, y))

    def inscribed_circle_radius(self) -> float:
        # Size of the first side
        # We guestimate that the triangle is equilateral.
        a = math.sqrt(
            (self.xy_list[0].x - self.xy_list[1].x) ** 2 +
            (self.xy_list[0].y - self.xy_list[1].y) ** 2)

        # Semi-perimeter of the triangle
        s = (a + a + a) / 2
        # Area of the triangle using Heron's formula
        area = math.sqrt(s * (s - a) * (s - a) * (s - a))
        # Radius of the inscribed circle
        radius = area / s
        return radius

    def shrink(self, ratio:float) -> "Triangle":
        """Returns a new triangle with the same center and a smaller size."""
        center = self.center()
        new_xy_list = []
        for xy in self.xy_list:
            dx = xy.x - center.x
            dy = xy.y - center.y
            new_xy = Xy((center.x + dx * ratio, center.y + dy * ratio))
            new_xy_list.append(new_xy)
        return Triangle(self.y_piece, self.r_piece, self.g_piece, *new_xy_list)

def segments(polygon_points:list) -> Generator:
    np = len(polygon_points)
    for i in range(np):
        start = polygon_points[i]
        end = polygon_points[(i + 1) % np]
        yield (start, end)


def segment_center(segment:tuple) -> tuple:
    """Returns the center of a segment."""
    start = segment[0]
    end = segment[1]
    x = (start[0] + end[0]) / 2
    y = (start[1] + end[1]) / 2
    return (x, y)


class Axis:
    """
    Represents one of the coordinate axis of the hexagon.
    The coordinates are in the range -N/2-0.5 .. N/2+0.5.
    These are "piece" units (and not pixel units).
    The hexagon has 3 coordinates: X (top to bottom), Y (left to right going down), Z (left to right going up).

    The puzzle has N=6 pieces on each coordinate.
    The border is half the size of an inner piece.
    Since the segments may not be absolutely parallel due to image paralax, we use the start/end segments to form a box.
    Along the axis, start is at coordinate -N/2-0.5 in piece units.
    Along the axis, end is at coordinate N/2+0.5 in piece units.
    """
    def __init__(self, segment_start:list, segment_end:list):
        self.segment_start = segment_start
        self.segment_end = segment_end
        self.center_start = segment_center(segment_start)
        self.center_end = segment_center(segment_end)
        print(f"Axis start: {self.center_start}, end: {self.center_end}")
        dx = self.center_end[0] - self.center_start[0]
        dy = self.center_end[1] - self.center_start[1]
        self.step_size_px = math.sqrt(dx * dx + dy * dy) / N
        self._v = np.array([self.step_size_px, 0])
        self.angle_deg = 0
        self.v = None

    def set_rotation(self, angle_deg:float) -> None:
        self.angle_deg = angle_deg

        # Compute the rotation matrix
        angle_rad = math.radians(angle_deg)
        self._rot_matrix = np.array([
            [math.cos(angle_rad), -math.sin(angle_rad)],
            [math.sin(angle_rad), math.cos(angle_rad)]
        ])

        # compute the unit vector
        self._v = np.dot(self._rot_matrix, self._v)
        self.v = Xy(self._v)
        print(f"Axis unit vectors: v={self.v}")


class YRGCoord:
    def __init__(self, center_px:Tuple[float, float], y_axis:Axis, r_axis:Axis, g_axis:Axis):
        """
        (cx,cy) are the pixel coordinates of the center of the hexagon
        (y,r,g) are the inner pieces coordinates of the hexagon.
        """
        self.center_px = Xy(center_px)
        self.y_axis = y_axis
        self.r_axis = r_axis
        self.g_axis = g_axis
        self.y_axis.set_rotation(120)
        self.r_axis.set_rotation(0)
        self.g_axis.set_rotation(0)

    def point_yr(self, y_piece:int, r_piece:int, offset:Xy=None) -> Xy:
        Y = self.y_axis
        R = self.r_axis
        x = (y_piece * Y.v.x + r_piece * R.v.x)
        y = (y_piece * Y.v.y + r_piece * R.v.y)
        if offset is not None:
            x += offset.x
            y += offset.y
        return Xy((x, y))

    def rhombus(self, y_piece:int, r_piece:int, offset:Xy=None) -> list[Xy]:
        Y = self.y_axis
        R = self.r_axis

        # Compute the rhombus points
        p0 = self.point_yr(y_piece    , r_piece    , offset)
        p1 = self.point_yr(y_piece + 1, r_piece    , offset)
        p2 = self.point_yr(y_piece + 1, r_piece + 1, offset)
        p3 = self.point_yr(y_piece    , r_piece + 1, offset)
        return [ p0, p1, p2, p3 ]

    def triangle(self, y_piece:int, r_piece:int, g_piece:int, offset:Xy=None) -> Triangle:
        rhombus = self.rhombus(y_piece, r_piece, offset)
        if g_piece == 0:
            return Triangle(y_piece, r_piece, g_piece, rhombus[0], rhombus[1], rhombus[2] )
        else:
            return Triangle(y_piece, r_piece, g_piece,  rhombus[0], rhombus[2], rhombus[3] )


# ~~
