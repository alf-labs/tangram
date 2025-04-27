# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import math
import numpy as np

from typing import Generator
from typing import Tuple

N = 6  # YRG coords are in 0..5 range
BORDER_SIZE = 0.5 # Border is half size of an inner piece
YRG_RADIUS = (N//2) + BORDER_SIZE
TAU = 2 * math.pi

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

# We can rotate the puzzle cells 60 degrees clockwise by mapping any cell from ROT_60_CCW_SRC (source) to VALID_YRG (destination).
# Example: SRC[0](0,2,1) --> That means that cell (0,2,1) becomes cell (0,0,0) because VALID_YRG[0] = (0,0,0).
ROT_60_CCW_SRC = [
                          (0, 2, 1), (0, 3, 0), (1, 3, 1), (1, 4, 0), (2, 4, 1), (2, 5, 0), (3, 5, 1),
               (0, 1, 1), (0, 2, 0), (1, 2, 1), (1, 3, 0), (2, 3, 1), (2, 4, 0), (3, 4, 1), (3, 5, 0), (4, 5, 1),
    (0, 0, 1), (0, 1, 0), (1, 1, 1), (1, 2, 0), (2, 2, 1), (2, 3, 0), (3, 3, 1), (3, 4, 0), (4, 4, 1), (4, 5, 0), (5, 5, 1),
    (0, 0, 0), (1, 0, 1), (1, 1, 0), (2, 1, 1), (2, 2, 0), (3, 2, 1), (3, 3, 0), (4, 3, 1), (4, 4, 0), (5, 4, 1), (5, 5, 0),
               (1, 0, 0), (2, 0, 1), (2, 1, 0), (3, 1, 1), (3, 2, 0), (4, 2, 1), (4, 3, 0), (5, 3, 1), (5, 4, 0),
                          (2, 0, 0), (3, 0, 1), (3, 1, 0), (4, 1, 1), (4, 2, 0), (5, 2, 1), (5, 3, 0),
]


class XY:
    def __init__(self, a:np.array):
        self.x = a[0]
        self.y = a[1]

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"XY({self.x}, {self.y})"

    def to_np(self) -> np.array:
        """Converts the XY object to a numpy array."""
        return np.array([self.x, self.y])

    def to_int(self) -> Tuple[int, int]:
        return (int(self.x), int(self.y))

    def distance(self, other:"XY") -> float:
        """Returns the distance to another XY object."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


class YRG:
    def __init__(self, y_piece:int, r_piece:int, g_piece:int):
        self.y = y_piece
        self.r = r_piece
        self.g = g_piece
        assert -N//2 <= y_piece < N//2, f"Invalid Y piece: {y_piece}"
        assert -N//2 <= r_piece < N//2, f"Invalid R piece: {r_piece}"
        assert g_piece == 0 or g_piece == 1, f"Invalid g_piece: {g_piece}"

    def __str__(self) -> str:
        return f"({self.y}, {self.r}, {self.g})"

    def __repr__(self) -> str:
        return f"YRG({self.y}, {self.r}, {self.g})"

    def __eq__(self, other:"YRG") -> bool:
        return self.y == other.y and self.r == other.r and self.g == other.g


class Triangle:
    def __init__(self, yrg_piece:YRG, p0:XY, p1:XY, p2:XY):
        self.yrg = yrg_piece
        self.xy_list = [p0, p1, p2]

    def to_np_array(self) -> np.array:
        return np.array([ xy.to_np() for xy in self.xy_list ])

    def center(self) -> XY:
        x = sum(xy.x for xy in self.xy_list) / len(self.xy_list)
        y = sum(xy.y for xy in self.xy_list) / len(self.xy_list)
        return XY((x, y))

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
            new_xy = XY((center.x + dx * ratio, center.y + dy * ratio))
            new_xy_list.append(new_xy)
        return Triangle(self.yrg, *new_xy_list)


def segments(polygon_points:list) -> Generator:
    np = len(polygon_points)
    for i in range(np):
        start = polygon_points[i]
        end = polygon_points[(i + 1) % np]
        yield (start, end)


def segment_center(segment:tuple) -> tuple:
    """Returns the center of a 2-point segment."""
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
        self._u = np.dot(self._rot_matrix, np.array([1, 0]))
        # compute the unit vector in pixel step_size coordinates
        self._v = np.dot(self._rot_matrix, self._v)
        self.v = XY(self._v)
        self.u = XY(self._u)
        print(f"Axis unit vectors: u={self.u} v={self.v}")

    def center(self) -> XY:
        c = segment_center([self.center_start, self.center_end])
        return XY( (c[0], c[1]) )


class YRGCoord:
    def __init__(self, center_px:Tuple[float, float], y_axis:Axis, r_axis:Axis, g_axis:Axis):
        """
        (cx,cy) are the pixel coordinates of the center of the hexagon
        (y,r,g) are the inner pieces coordinates of the hexagon.
        """
        self.center_px = XY(center_px)
        self.y_axis = y_axis
        self.r_axis = r_axis
        self.g_axis = g_axis
        self.y_axis.set_rotation(120)
        self.r_axis.set_rotation(0)
        self.g_axis.set_rotation(0)
        self.radials, self.radials_center_px = self.compute_distortion(y_axis, r_axis)

    def compute_distortion(self, y_axis:Axis, r_axis:Axis) -> list:
        points = [
            XY(r_axis.segment_end[1]),      # angle 0
            XY(y_axis.segment_start[0]),    # angle 60
            XY(y_axis.segment_start[1]),    # angle 120
            XY(r_axis.segment_start[1]),    # angle 180
            XY(y_axis.segment_end[0]),      # angle 240
            XY(y_axis.segment_end[1]),      # angle 300
        ]
        center_x = sum([ p.x for p in points ]) / len(points)
        center_y = sum([ p.y for p in points ]) / len(points)
        angle = 0
        radials = {}
        # Each radial represents the lenght in pixels of a unit vector from the center
        # to an outer hexagon point taking into account the distortion at that specific
        # angle.
        for p in points:
            length_px = self.center_px.distance(p)
            radials[angle] = {
                "len": length_px / YRG_RADIUS
            }
            angle += 60
        print("@@ radials", radials)
        return radials, XY( (center_x, center_y) )

    def radial_unit(self, angle_deg:float) -> XY:
        unit_length = 1
        # All angles are in degrees here
        while angle_deg < 360:
            angle_deg += 360
        angle_deg = angle_deg % 360

        angle_rad = np.radians(angle_deg)
        if angle_deg in self.radials:
            unit_length = self.radials[angle_deg]["len"]
        else:
            # Find the radial just before and after and compute a weight average.
            angle_before = int((angle_deg // 60) * 60) % 360
            angle_after = int(((angle_deg + 60) // 60) * 60) % 360

            factor = 1 - (angle_deg - angle_before) / 60
            unit_len_before = self.radials[angle_before]["len"]
            unit_len_after = self.radials[angle_after]["len"]
            unit_length = unit_len_before * factor + unit_len_after * (1-factor)

        # print("@@ angle_deg", angle_before, angle_deg, angle_after,
        #     "angle", float(np.degrees(angle_rad_before)), float(np.degrees(angle_rad)), float(np.degrees(angle_rad_after)), 
        #     "unit", unit_len_before, unit_length, unit_len_after,
        #     "factor", factor)

        xy = XY( (unit_length * math.cos(angle_rad), unit_length * math.sin(angle_rad)) )
        return xy

    def point_yr(self, y_piece:int, r_piece:int) -> XY:
        Y = self.y_axis
        R = self.r_axis

        # # Method 1: use a fixed Y/R unit vector to convert to point coordinates
        # x = y_piece * Y.v.x + r_piece * R.v.x + self.center_px.x
        # y = y_piece * Y.v.y + r_piece * R.v.y + self.center_px.y

        # Method 2: use the radials to adjust for hexagon axes distortions
        # Convert the desired Y/R coordinate into polar coordinates
        ux = y_piece * Y.u.x + r_piece * R.u.x
        uy = y_piece * Y.u.y + r_piece * R.u.y
        angle_rad = math.atan2(uy, ux)
        length = math.sqrt(ux * ux + uy * uy)
        unit_xy = self.radial_unit(np.degrees(angle_rad))
        x = self.radials_center_px.x + length * unit_xy.x
        y = self.radials_center_px.y + length * unit_xy.y

        return XY((x, y))

    def rhombus(self, y_piece:int, r_piece:int) -> list[XY]:
        # Compute the rhombus points
        p0 = self.point_yr(y_piece    , r_piece)
        p1 = self.point_yr(y_piece + 1, r_piece)
        p2 = self.point_yr(y_piece + 1, r_piece + 1)
        p3 = self.point_yr(y_piece    , r_piece + 1)
        return [ p0, p1, p2, p3 ]

    def triangle(self, yrg_piece:YRG) -> Triangle:
        rhombus = self.rhombus(yrg_piece.y, yrg_piece.r)
        if yrg_piece.g == 0:
            return Triangle(yrg_piece, rhombus[0], rhombus[1], rhombus[2])
        else:
            return Triangle(yrg_piece,  rhombus[0], rhombus[2], rhombus[3])

    def rot_60_ccw(self, triangle:Triangle) -> Triangle:
        """
        "Rotates" a Triangle by modifying its y,r,g coordinates and returns the new Triangle.
        This uses the YRGCoord to recompute the rhombus pixel coordinates.
        """
        n2 = N//2
        yrg_src = triangle.yrg
        index = ROT_60_CCW_SRC.index((yrg_src.y + n2, yrg_src.r + n2, yrg_src.g))
        yrg_dst = VALID_YRG[index]
        return self.triangle(YRG(yrg_dst[0] - n2, yrg_dst[1] - n2, yrg_dst[2]))



# ~~
