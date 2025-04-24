# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import cv2
import math
import numpy as np
import os

from typing import Generator
from typing import Tuple

N = 6  # YRG coords are in 0..5 range
BORDER_SIZE = 0.5 # Border is half size of an inner piece
RESIZE_PX = 1024

PARAMS = [
    {
        "blur_ksize": (11, 11),
        "blur_sigmaX": 0,
        "brightness_scale": 3,
        "brightness_offset": 0,
        "bw_threshold": 16,
        "use_edges": False,
        "polygon_eps_width_ratio": 1/20,
    },
    {
        "blur_ksize": (11, 11),
        "blur_sigmaX": 0,
        "brightness_scale": 3,
        "brightness_offset": 0,
        "bw_threshold": 32,
        "use_edges": False,
        "polygon_eps_width_ratio": 1/20,
    },
    {
        "blur_ksize": (11, 11),
        "blur_sigmaX": 0,
        "brightness_scale": 3,
        "brightness_offset": 0,
        "bw_threshold": 32,
        "use_edges": False,
        "polygon_eps_width_ratio": 1/12,
    },
    {
        "blur_ksize": (11, 11),
        "blur_sigmaX": 0,
        "brightness_scale": 3,
        "brightness_offset": 0,
        "bw_threshold": 32,
        "use_edges": False,
        "polygon_eps_width_ratio": 1/10,
    },
    # this one does not give good results
    # {
    #     "blur_ksize": (11, 11),
    #     "blur_sigmaX": 0,
    #     "brightness_scale": 2.35,
    #     "brightness_offset": 0,
    #     "quantize_levels": 8,
    #     "canny_thresh1": 125,
    #     "canny_thresh2": 210,
    #     "use_edges": True,
    #     "polygon_eps_width_ratio": 1/10,
    # },
]

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

COLORS = [
    {
        "name": "Red",
        "rgb": (192, 0, 0),
        "bgr": (0, 0, 192),
        "h": { "min": 7, "max": 9 },
        "s": { "min": 128, "max": 255 },
        "v": { "min": 60, "max": 255 },
    },
    {
        "name": "White",
        "rgb": (192, 192, 192),
        "bgr": (192, 192, 192),
        "h": { "min": 12, "max": 35 },
        "s": { "min": 0, "max": 100 },
        "v": { "min": 150, "max": 255 },
    },
    {
        "name": "Black",
        "rgb": (64, 64, 64),
        "bgr": (64, 64, 64),
        "v": { "min": 0, "max": 100 },
    },
    {
        "name": "Orange",
        "h": { "min": 10, "max": 12 },
        "rgb": (192, 128, 0),
        "bgr": (0, 128, 192),
    },
    {
        "name": "Yellow",
        "rgb": (192, 192, 0),
        "bgr": (0, 192, 192),
    },
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


def clamp(value:int, min_value:int, max_value:int) -> int:
    """Clamps a value to the given range."""
    return max(min(value, max_value), min_value)



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


class ImageProcessor:
    def __init__(self, input_img_path:str, output_dir_path:str):
        self.input_img_path = input_img_path
        self.output_dir_path = output_dir_path

        if not os.path.exists(output_dir_path):
            raise FileNotFoundError(f"Directory {output_dir_path} does not exist.")

    def dest_name(self, suffix:str) -> str:
        """Generates a destination name for the processed image."""
        base_name = os.path.basename(self.input_img_path)
        name, ext = os.path.splitext(base_name)
        return os.path.join(self.output_dir_path, f"{name}{suffix}{ext}")

    def process_image(self, overwrite:bool) -> None:
        print("------")
        print(f"Processing Image: {self.input_img_path}")
        print("------")
        self.find_hexagon(self.input_img_path, overwrite)
        print("")

    def find_hexagon(self, input_img_path:str, overwrite:bool) -> None:
        src_img_path = self.dest_name("_src")

        # Check if the hexagon image already exists
        if os.path.exists(src_img_path) and not overwrite:
            print(f"Hexagon image already exists: {src_img_path}")
            return

        resized = self.load_resized_image(input_img_path)
        lab_img = self.convert_to_lab(resized)
        cv2.imwrite(self.dest_name("_1_lab"), lab_img)
        hex_img = resized.copy()

        for params in PARAMS:
            # Convert the image to LAB color space to enhance contrast
            contrasted = self.enhance_image(lab_img, params)
            cv2.imwrite(self.dest_name("_2_contrast"), contrasted)

            edges = self.edge_detect(contrasted, params)
            cv2.imwrite(self.dest_name("_3_edges"), edges)

            if not params.get("use_edges", False):
                edges = contrasted
            hexagon = self.find_hexagon_contour(edges, hex_img, params)
            cv2.imwrite(self.dest_name("_4_hexagon"), hex_img)

            if hexagon is not None:
                rot_angle_deg, hex_center = self.detect_hexagon_rotation(hexagon, hex_img)
                rot_img, rot_poly, hex_center = self.rotate_image(resized, hexagon, rot_angle_deg, hex_center)
                cv2.imwrite(self.dest_name("_4_hexagon"), hex_img)
                cv2.imwrite(self.dest_name("_5_rot"), rot_img)

                yrg_coords = self.compute_yrg_coords(rot_poly, hex_center)
                coords_img = rot_img.copy()
                self.draw_yrg_coords(yrg_coords, coords_img)
                cv2.imwrite(self.dest_name("_6_yrg"), coords_img)
                cells, colors_img = self.extract_cells_colors(yrg_coords, rot_img, params)
                cv2.imwrite(self.dest_name("_7_colors"), colors_img)

                self.orient_white_cells(cells)

                break

        cv2.imwrite(src_img_path, resized)


    def load_resized_image(self, input_img_path:str) -> np.array:
        # Load the image using OpenCV
        image = cv2.imread(self.input_img_path, cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Could not load image: {input_img_path}")

        print(f"Image loaded successfully: {input_img_path}")

        # Resize the image to a width of 1024 while maintaining aspect ratio
        height, width = image.shape[:2]
        new_width = RESIZE_PX
        new_height = int((new_width / width) * height)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        print(f"Image resized to: {new_width}x{new_height}")
        return image

    def convert_to_lab(self, rgb_img:np.array) -> np.array:
        # Convert the image to LAB color space to enhance contrast
        lab_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2LAB)
        # Split the LAB image into its channels
        l, a, b = cv2.split(lab_img)
        # Discard the luminance channel
        l[:] = 0
        lab_img = cv2.merge((l, a, b))
        rgb_img = cv2.cvtColor(lab_img, cv2.COLOR_LAB2BGR)
        return rgb_img

    def enhance_image(self, lab:np.array, params:dict={}) -> np.array:
        # # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to the L channel
        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        # a = clahe.apply(a)
        # a = clahe.apply(a)
        # # Merge the enhanced L channel back with the A and B channels
        # lab = cv2.merge((l, a, b))
        # # Convert the LAB image back to BGR color space
        # lab = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        # cv2.imwrite(self.dest_name("_2_enhance"), lab)

        # Convert the image to grayscale
        gray = cv2.cvtColor(lab, cv2.COLOR_BGR2GRAY)

        # Apply GaussianBlur to reduce noise
        ksize = params.get("blur_ksize", (11, 11))
        sigmaX = params.get("blur_sigmaX", 0)
        blurred = cv2.GaussianBlur(gray, ksize, sigmaX)

        # Enhance the brightness of the image
        # alpha is a scale factor, and beta is an offset.
        # e.g. dest (8-bit) = alpha * src (8-bit) + beta, clamps to 0..255
        scale = params.get("brightness_scale", 3)
        offset = params.get("brightness_offset", 0)
        blurred = cv2.convertScaleAbs(blurred, alpha=scale, beta=offset)

        # # Enhance the contrast of the image using histogram equalization (for gray img)
        # blurred = cv2.equalizeHist(blurred)

        # Find the minimum and maximum gray levels in the image
        min_gray = np.min(blurred)
        max_gray = np.max(blurred)
        print(f"Min gray level: {min_gray}, Max gray level: {max_gray}")

        quantize_levels = params.get("quantize_levels", 2)
        bw_thresh = params.get("bw_threshold", 16)

        if quantize_levels > 2:
            # Convert the image into N shades of grayscale
            max_val = max_gray
            step = max_val // (quantize_levels - 1)
            quantized = (blurred // step)
            quantized = np.clip(quantized, 0, 255)
            # Rescale the quantized image to the 0..255 range
            quantized = cv2.normalize(quantized, None, 0, 255, cv2.NORM_MINMAX)
            return quantized
        else:
            # Convert the image to black and white using a gray level threshold
            _, bw = cv2.threshold(blurred, thresh=bw_thresh, maxval=255, type=cv2.THRESH_BINARY)
            return bw

    def edge_detect(self, blurred:np.array, params:dict) -> np.array:
        # Use Canny edge detection
        canny_thresh1 = params.get("canny_thresh1", 20)
        canny_thresh2 = params.get("canny_thresh2", 30)
        edges = cv2.Canny(blurred,
            threshold1=canny_thresh1, threshold2=canny_thresh2,
            apertureSize=3,
            L2gradient=False)

        # Dilate the edges to make them more pronounced
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=3)
        # # Erode the edges to remove noise
        # edges = cv2.erode(edges, kernel, iterations=1)

        return edges

    def find_hexagon_contour(self, bw_image:np.array, draw_img:np.array=None, params:dict={}) -> list:
        # Find the largest contour in the threshold image
        cnts, _ = cv2.findContours(bw_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(cnts) == 0:
            print("No contours found.")
            return None
        # get the contour based on max contour area.
        c = max(cnts, key=cv2.contourArea)

        if draw_img is not None:
            cv2.drawContours(draw_img, [c], -1, (0, 255, 0), 3)
            (x, y, w, h) = cv2.boundingRect(c)
            # Draw the bounding box on the image
            cv2.rectangle(draw_img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Note that [c] is not an hexagon. It may have thousands of points or more.
        eps_w_ratio = params.get("polygon_eps_width_ratio", 1 / 20)
        eps = w * eps_w_ratio
        approx = cv2.approxPolyDP(curve=c, epsilon=eps, closed=True)

        if draw_img is not None:
            cv2.drawContours(draw_img, [approx], -1, (0, 255, 255), 4)

        # Check if we really found an hexagon
        if len(approx) == 6:
            print("Hexagon detected!")
        else:
            print(f"Hexagon not detected. Found {len(approx)} points.")
            return None

        # Approx is an odd structure:
        # list of [ list of a single [ list of x, y ] ]
        # e.g. [ [[x1, y1]], [[x2, y2]], [[x3, y3]], [[x4, y4]], [[x5, y5]], [[x6, y6]] ]
        # We need to convert it to a more usable format
        polygon = [ (point[0][0], point[0][1]) for point in approx ]
        return polygon

    def detect_hexagon_rotation(self, polygon:list, draw_img:np.array=None) -> Tuple[float, list]:
        # print(f"Hexagon points: {polygon}")
        # print(f"Hexagon segments: {[ s for s in segments(polygon) ]}")

        # Compute the center of the polygon
        cx = int(sum(point[0] for point in polygon) / len(polygon))
        cy = int(sum(point[1] for point in polygon) / len(polygon))
        print(f"Hexagon center: ({cx}, {cy})")

        # Find the lowest segment in the hexagon
        lowest_segment = max(segments(polygon), key=lambda segment: segment_center(segment)[1])
        print(f"Lowest segment: {lowest_segment}")

        # Compute the rotation angle of the hexagon
        # This is the angle of the lowest segment
        # Note: The angle is in radians, and the rotation is clockwise
        dx = lowest_segment[1][0] - lowest_segment[0][0]
        dy = lowest_segment[1][1] - lowest_segment[0][1]
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        print(f"Rotation angle: {angle_deg} degrees")

        if draw_img is not None:
            cv2.line(draw_img, pt1=lowest_segment[0], pt2=lowest_segment[1], color=(0, 0, 255), thickness=5)

        return (angle_deg, (cx, cy))

    def rotate_image(self, image:np.array, polygon:list, angle_deg:float, center:tuple) -> Tuple[np.array, list, Tuple]:
        cx, cy = center
        x, y, w, h = cv2.boundingRect(np.array(polygon))
        wh = max(w, h)

        # get the size of the image for warpAffine
        h, w = image.shape[:2]

        # Rotate the image according to the angle
        rotation_matrix = cv2.getRotationMatrix2D(center, angle_deg, 1)
        rotated_img = cv2.warpAffine(image, rotation_matrix, (w, h))

        print(f"Original image size: {image.shape}")
        print(f"Rotated image size: {rotated_img.shape}")

        # Rotate the polygon points
        rotated_polygon = []
        # rotation_matrix = cv2.getRotationMatrix2D((cx, cy), math.degrees(angle), 1)
        for point in polygon:
            rotated_point = cv2.transform(np.array([[point]]), rotation_matrix)[0][0]
            rotated_polygon.append((tuple(rotated_point)))
        # print(f"Rotated polygon points: {rotated_polygon}")

        # # Draw the segments on the rotated image
        for segment in segments(rotated_polygon):
            cv2.line(rotated_img, pt1=segment[0], pt2=segment[1], color=(0, 255, 0), thickness=3)

        # Crop the image to the squared bounding box with some padding
        wh2 = wh // 2 + 10
        cv2.rectangle(rotated_img, (cx - wh2, cy - wh2), (cx + wh2, cy + wh2), (255, 0, 0), 2)
        rotated_img = rotated_img[
            clamp(cy - wh2, 0, h) : clamp(cy + wh2, 0, h),
            clamp(cx - wh2, 0, w) : clamp(cx + wh2, 0, w)]
        print(f"Square image size: {rotated_img.shape}")

        offsetx = cx - wh2
        offsety = cy - wh2
        # Adjust the polygon points to the cropped image size
        rotated_polygon = [(point[0] - offsetx, point[1] - offsety) for point in rotated_polygon]
        # Adjust the center by the offset
        hex_center = (cx - offsetx, cy - offsety)

        return rotated_img, rotated_polygon, hex_center

    def compute_yrg_coords(self, polygon:list, center:tuple) -> YRGCoord:
        # Note that everything here assumse the polygon is an hexagon.
        segs = list(segments(polygon))
        len_seg = len(segs)
        def wrap(index:int) -> int:
            return index % len_seg

        # Find the segment with the highest y-coordinate center
        bottom_segment = max(segs, key=lambda segment: segment_center(segment)[1])
        # Fin the index of "bottom_segment" in the segments list
        bottom_index = segs.index(bottom_segment)

        y_end_segment_index = bottom_index

        # I don't know if the polygon is define clockwise or counter-clockwise,
        # so let's detect that and handle both cases.
        # It is clockwise if the next segment (after bottom_segment) has a X center which is lower than bottom's X center.
        bottom_center = segment_center(bottom_segment)
        next_segment_index = wrap(bottom_index + 1)
        next_segment = segs[next_segment_index]
        next_center = segment_center(next_segment)
        is_clockwise = next_center[0] < bottom_center[0]
        print(f"Is clockwise: {is_clockwise}")

        if is_clockwise:
            # the next segment represents the start of the G axis, then the start of the R axis
            g_start_segment_index = next_segment_index
            r_start_segment_index = wrap(next_segment_index + 1)
        else:
            # the previous segment presents the start of the G axis, then the start of the R axis
            g_start_segment_index = wrap(bottom_index - 1)
            r_start_segment_index = wrap(bottom_index - 2)

        y_start_segment_index = wrap(y_end_segment_index + 3)
        g_end_segment_index = wrap(g_start_segment_index + 3)
        r_end_segment_index = wrap(r_start_segment_index + 3)

        # Define the axes
        y_axis = Axis(segs[y_start_segment_index], segs[y_end_segment_index])
        r_axis = Axis(segs[r_start_segment_index], segs[r_end_segment_index])
        g_axis = Axis(segs[g_start_segment_index], segs[g_end_segment_index])
        yrg_coords = YRGCoord(center, y_axis, r_axis, g_axis)
        return yrg_coords

    def draw_yrg_coords(self, yrg_coords:YRGCoord, out_img:np.array) -> None:
        t = yrg_coords.triangle(0, 0, 0)
        radius = int(t.inscribed_circle_radius() *.5 )

        for triangle in self.triangles(yrg_coords):
            poly = np.int32(triangle.to_np_array())
            cv2.polylines(out_img, [poly], isClosed=True, color=(255, 255, 255), thickness=2)
            tc = triangle.center()
            px = int(tc.x)
            py = int(tc.y)
            cv2.circle(out_img, (px, py), radius, (255, 255, 255), 1)
            y = triangle.y_piece + N//2
            r = triangle.r_piece + N//2
            g = triangle.g_piece
            cv2.putText(out_img, f"{y}{r}{g}", (px - 15, py + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def triangles(self, yrg_coords:YRGCoord) -> Generator:
        center = yrg_coords.center_px
        n2 = N//2
        for (y, r, g) in VALID_YRG:
            y_piece = y - n2
            r_piece = r - n2
            yield yrg_coords.triangle(y_piece, r_piece, g, offset=center)

    def extract_cells_colors(self, yrg_coords:YRGCoord, in_img:np.array, params:dict={}) -> Tuple[list,np.array]:
        t = yrg_coords.triangle(0, 0, 0)
        radius = int(t.inscribed_circle_radius() *.5 )

        # Apply GaussianBlur to reduce noise
        ksize = params.get("blur_ksize", (11, 11))
        sigmaX = params.get("blur_sigmaX", 0)
        out_img = cv2.GaussianBlur(in_img, ksize, sigmaX)

        hsv_img = cv2.cvtColor(out_img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_img)
        # # Clip the hue channel -- we only care about the redish hue
        h_min = np.min(h)
        h_max = np.max(h)
        print(f"Min hue: {h_min}, Max hue: {h_max}")
        np.clip(h, 8, 16, out=h)
        h = (h // 4) * 4
        s = (s // 16) * 16
        v = (v // 32) * 32
        hsv_img = cv2.merge((h, s, v))

        # Fill out_img with black
        out_img.fill(0)

        shrink_ratio = 0.5

        cells = []
        for triangle in self.triangles(yrg_coords):
            # Create a mask based on a shrunk triangle to filter on the HSB
            poly = np.int32(triangle.shrink(shrink_ratio).to_np_array())
            mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [poly], (255, 255, 255))
            # Get the mean color of the polygon
            # Note that cv2.mean() always returns a scalar with 4 components.
            mean_hsv = cv2.mean(hsv_img, mask=mask)
            print(f"Mean color HSV: {mean_hsv}")
            color = self.select_color(int(mean_hsv[0]), int(mean_hsv[1]), int(mean_hsv[2]))
            cells.append({
                "color": color,
                "triangle": triangle,
            })

            # Conver the mean HSV to BGR
            mean_bgr = cv2.cvtColor(np.uint8([[mean_hsv[:3]]]), cv2.COLOR_HSV2BGR)[0][0]
            mean_bgr = (int(mean_bgr[0]), int(mean_bgr[1]), int(mean_bgr[2]))

            # Draw the mean color on the triangle, using the full triangle size
            poly = np.int32(triangle.to_np_array())
            cv2.fillPoly(out_img, [poly], mean_bgr)
            cv2.circle(out_img, triangle.center().to_int(), radius, color["bgr"], -1)

        for triangle in self.triangles(yrg_coords):
            poly = np.int32(triangle.to_np_array())
            cv2.polylines(out_img, [poly], isClosed=True, color=(0, 0, 0), thickness=1)

        return (cells, out_img)

    def select_color(self, h:int, s:int, v:int) -> dict:
        for color in COLORS:
            if "h" in color and (h < color["h"]["min"] or h > color["h"]["max"]):
                continue
            if "s" in color and (s < color["s"]["min"] or s > color["s"]["max"]):
                continue
            if "v" in color and (v < color["v"]["min"] or v > color["v"]["max"]):
                continue
            print(f"Color found: h={h}, s={s}, v={v} --> {color['name']}")
            return color

    def orient_white_cells(self, cells:list) -> None:
        # We expect to find 3 white cells in the puzzle.
        # Two of them must have the same "g" piece coordinate.
        whites = [ cell for cell in cells if cell["color"]["name"] == "White" ]
        if len(whites) != 3:
            print(f"Found {len(whites)} white cells, expected 3.")
            return None
        # Check if two of them have the same "g" piece coordinate
        g = {}
        g[0] = [ cell for cell in whites if cell["triangle"].g_piece == 0 ]
        g[1] = [ cell for cell in whites if cell["triangle"].g_piece == 1 ]
        pair = [ v for k, v in g.items() if len(v) == 2 ]
        if len(pair) != 1:
            print(f"Found {len(pair)} pairs of white cells with the same g piece coordinate.")
            return None
        pair = pair[0]
        print(f"White pair: {pair}")

# ~~
