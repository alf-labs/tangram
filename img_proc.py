# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import colors
import coord
import cv2
import math
import numpy as np
import os

from coord import Axis, YRG, YRGCoord, Triangle, segments, segment_center, VALID_YRG
from typing import Generator
from typing import Tuple

TAU = 2 * math.pi
SHRINK_RATIO = 0.5
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
        "polygon_eps_width_ratio": -1/200,
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


def clamp(value:int, min_value:int, max_value:int) -> int:
    """Clamps a value to the given range."""
    return max(min(value, max_value), min_value)


class Cell:
    def __init__(self, triangle:Triangle, color:dict, mean_hsv, mean_lab):
        self.triangle = triangle
        self.color = color
        self.mean_hsv = mean_hsv
        self.mean_lab = mean_lab

    def yrg(self) -> YRG:
        return self.triangle.yrg

    def color_name(self) -> str:
        return self.color["name"]

    def __repr__(self) -> str:
        return f"Cell(triangle={self.yrg()}, color={self.color_name()})"


class ImageProcessor:
    def __init__(self, input_img_path:str, output_dir_path:str):
        self.input_img_path = input_img_path
        self.output_dir_path = output_dir_path
        self.img_index = 0
        self._previous_img_index = {}

        if not os.path.exists(output_dir_path):
            raise FileNotFoundError(f"Directory {output_dir_path} does not exist.")

    def dest_name(self, suffix:str, ext:str=None) -> str:
        """Generates a destination name for the processed image."""
        base_name = os.path.basename(self.input_img_path)
        name, _ext = os.path.splitext(base_name)
        if ext is None:
            ext = _ext
        return os.path.join(self.output_dir_path, f"{name}{suffix}{ext}")

    def write_indexed_img(self, suffix:str, in_img:np.array, replace:bool=False) -> None:
        if replace and suffix in self._previous_img_index:
            dest_suffix = self._previous_img_index[suffix]
        else:
            self.img_index += 1
            dest_suffix = "_%02d_%s" % (self.img_index, suffix)
            self._previous_img_index[suffix] = dest_suffix
        cv2.imwrite(self.dest_name(dest_suffix), in_img)

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
        # Disable auto-level upfront, it provides poor results.
        # resized = self.auto_level(resized)
        channels = self.extract_channels(resized)
        lab_img = self.convert_to_lab(resized)
        # This image is only useful for debugging initial hexagon search
        # self.write_indexed_img("lab", lab_img)
        hex_img = resized.copy()

        for params in PARAMS:
            # Convert the image to LAB color space to enhance contrast
            contrasted = self.enhance_image(lab_img, params)
            self.write_indexed_img("contrast", contrasted, replace=True)

            edges = self.edge_detect(contrasted, params)
            self.write_indexed_img("edges", edges, replace=True)

            if not params.get("use_edges", False):
                edges = contrasted
            hexagon = self.find_hexagon_contour(edges, draw_img=hex_img, params=params)
            self.write_indexed_img("hexagon", hex_img, replace=True)

            if hexagon is not None:
                break

        if hexagon is not None:
            rot_angle_deg, hex_center = self.detect_hexagon_rotation(hexagon, draw_img=hex_img)
            rot_img, rot_poly, hex_center = self.rotate_image(resized, hexagon, rot_angle_deg, hex_center)
            self.write_indexed_img("hexagon", hex_img, replace=True)
            self.write_indexed_img("rot", rot_img)

            yrg_coords = self.compute_yrg_coords(rot_poly, hex_center)
            coords_img = rot_img.copy()
            self.draw_yrg_coords_into(yrg_coords, dest_img=coords_img)
            self.write_indexed_img("yrg", coords_img)

            # # Method 2: try to detect BW and color cells separately.
            cells, histograms = self.extract_cells_bw_only(yrg_coords, in_img=rot_img)
            bw_img = rot_img.copy()
            self.draw_cells_into(cells=cells, dest_img=bw_img)
            self.draw_histograms_into(histograms=histograms, dest_img=bw_img)
            self.write_indexed_img("bw", bw_img)

            # Method 1: try to detect both colors and BW cells at the same time.
            # Performance is passable.
            cells = self.extract_cells_colors(yrg_coords, in_img=rot_img, cells=cells)
            colors_img = rot_img.copy()
            self.draw_cells_into(cells=cells, dest_img=colors_img)
            self.write_indexed_img("colors", colors_img)

            if self.validate_cells(cells):
                # Detect the 3 white cells and re-orient the cells accordingly
                # Stop if we can't find the 3 white cells.
                result = self.orient_white_cells(yrg_coords, cells)

                if result is not None:
                    rot_col_img = rot_img.copy()
                    self.draw_cells_into(cells=result, dest_img=rot_col_img)
                    self.write_indexed_img("colors", rot_col_img)

                    sig = self.cells_signature(result)
                    print(f"Signature: {sig}")
                    sig_file = self.dest_name("_sig", ".txt")
                    with open(sig_file, "w") as f:
                        f.write(sig)

        cv2.imwrite(src_img_path, resized)
        return

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

    def auto_level(self, rgb_img:np.array) -> np.array:
        # Different attempts at auto-leveling the image.
        # Mixed success with these methods.

        # ----------
        # Attempt 1: adjust contrast in the Lab color space.
        # Normaly one would only be done for Luminance.
        # Try adjusting a*b* channels too to see what it gives
        # (normally one does not normalize A/B or U/V separately as this "distords"
        # the colors, but since most of the colors we want here are in a very narrow
        # band in the red-orange spectra, that may work, at the expense of distorting
        # the white and black pieces colors.)

        # Convert the image to LAB color space
        lab_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab_img)
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        S=4
        clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(S, S))
        l = clahe.apply(l)
        a = clahe.apply(a)
        b = clahe.apply(b)
        lab_img = cv2.merge((l, a, b))
        rgb_img = cv2.cvtColor(lab_img, cv2.COLOR_LAB2BGR)

        # ----------
        # Attempt 2: adjust contrast in the YUV color space.
        # This one only adjusts the Y channel.

        # # Convert the image to YUV color space
        # yuv_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2YUV)
        # # Split the LAB image into its channels
        # l, a, b = cv2.split(yuv_img)
        # # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to the L channel
        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        # cl = clahe.apply(l)
        # # Merge the enhanced L channel back with the A and B channels
        # lab_img = cv2.merge((cl, a, b))
        # # Convert the LAB image back to BGR color space
        # rgb_img = cv2.cvtColor(lab_img, cv2.COLOR_YUV2BGR)

        # ----------
        # Attempt 3: Apply Grayworld (Automatic White Balance) algorithm
        # Source: https://pippin.gimp.org/image-processing/chapter-automaticadjustments.html

        # avg_b = np.mean(rgb_img[:, :, 0])
        # avg_g = np.mean(rgb_img[:, :, 1])
        # avg_r = np.mean(rgb_img[:, :, 2])
        #
        # avg_gray = (avg_b + avg_g + avg_r) / 3
        #
        # scale_b = avg_gray / avg_b
        # scale_g = avg_gray / avg_g
        # scale_r = avg_gray / avg_r
        #
        # rgb_img[:, :, 0] = np.clip(rgb_img[:, :, 0] * scale_b, 0, 255)
        # rgb_img[:, :, 1] = np.clip(rgb_img[:, :, 1] * scale_g, 0, 255)
        # rgb_img[:, :, 2] = np.clip(rgb_img[:, :, 2] * scale_r, 0, 255)

        # ----------
        # Attempt 4: Apply contrast stretching algorithm
        # Source: https://pippin.gimp.org/image-processing/chapter-automaticadjustments.html

        # # Find the minimum and maximum pixel values in the image
        # min_val = np.min(rgb_img)
        # max_val = np.max(rgb_img)
        #
        # # Stretch the pixel values to the full range [0, 255]
        # stretched = ((rgb_img - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        # rgb_img = stretched

        return rgb_img

    def extract_channels(self, rgb_img:np.array) -> list:
        channels = {}
        sy, sx = rgb_img.shape[:2]
        r, g, b = cv2.split(rgb_img)
        img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2LAB)
        l_, a_, b_ = cv2.split(img)
        img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2YUV)
        y, u, v = cv2.split(img)
        img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
        h_, s_, v_ = cv2.split(img)

        # Recreate a gray scale image with all the channels, for debug purposes.
        gray = np.zeros((sy * 4, sx * 3), dtype=np.uint8)
        def _log(y):
            return math.log(1 + y * 0.001)
        def _copy(py, names, c1, c2, c3):
            px = 0
            cs = [ (c1, names[0]), (c2, names[1]), (c3, names[2]) ]
            for c, n in cs:
                # print("@@ channel:", gray.shape, py, py + sy, px, px + sx, c.shape)
                gray[ py:py+sy, px:px+sx ] = c
                col0 = (int(gray[py, px]) - 64 + 256) % 256
                col = (col0, col0, col0)
                cv2.putText(gray, n, (px + 5, py + 100), cv2.FONT_HERSHEY_SIMPLEX, 4, col, 10)
                hist, _ = np.histogram(c, 256)

                hh = sy // 6
                mx = _log(max(hist))
                nv = len(hist)
                ox = 10
                ww = (sx - 2 * ox) / nv
                y2 = py + sy
                for i in range(0, nv - 1):
                    y1 = y2 - int(_log(hist[i]) * hh / mx)
                    x1 = math.floor( px + ox + i * ww )
                    x2 = math.ceil ( x1 + ww )
                    cv2.rectangle(gray, (x1, y1), (x2, y2), color=col, thickness=-11)

                px += sx
            return py + sy
        py = _copy( 0, "RGB", r , g , b )
        py = _copy(py, "LAB", l_, a_, b_)
        py = _copy(py, "YUV", y , u , v )
        py = _copy(py, "HSV", h_, s_, v_)
        self.write_indexed_img("channels", gray)

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
        # self.write_indexed_img("enhance", lab)

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
        # Possible choices for findContour are CHAIN_APPROX_SIMPLE and CHAIN_APPROX_TC89_L1.
        # The "simple" one seems to perform better for our post-analysis.
        cnts, _ = cv2.findContours(bw_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(cnts) == 0:
            print("No contours found.")
            return None
        # Get the contour based on max contour area.
        c = max(cnts, key=cv2.contourArea)

        if draw_img is not None:
            cv2.drawContours(draw_img, [c], -1, (0, 255, 0), 3)
            (x, y, w, h) = cv2.boundingRect(c)
            # Draw the bounding box on the image
            cv2.rectangle(draw_img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        approx = self.filter_hexagon(c, params)

        if draw_img is not None:
            cv2.drawContours(draw_img, [approx], -1, (0, 255, 255), 4)
            for p in approx:
                px, py = p[0]
                cv2.circle(draw_img, (px, py), 5, (0, 0, 255), -1)
            px, py = approx[0][0]
            cv2.circle(draw_img, (px, py), 10, (255, 0, 255), -1)

        # Check if we really found an hexagon
        if len(approx) == 6:
            print("Hexagon detected!")
        else:
            print(f"Hexagon not detected. Found {len(approx)} points.")
            return None

        # See filter_hexagon() for the Approx format.
        # We need to convert it to a more usable format
        polygon = [ (point[0][0], point[0][1]) for point in approx ]
        return polygon

    def filter_hexagon(self, contour:list, params:dict={}) -> list:
        # Contour (input) and Approx (output of approxPolyDP) use an unusual structure:
        # it's an np.array of shape (num_points, 1, 2).
        # The python representation is:
        # list of [ list of a single [ list of x, y ] ]
        # e.g. [ [[x1, y1]], [[x2, y2]], [[x3, y3]], [[x4, y4]], [[x5, y5]], [[x6, y6]] ]

        c = contour
        num_points = c.shape[0]
        angles = []

        def _v(idx):
            p1 = c[idx][0]
            p2 = c[(idx + 1) % num_points][0]
            return p2 - p1

        def _p_angle(idx):
            p0 = c[(idx + num_points - 1) % num_points][0]
            p1 = c[idx][0]
            p2 = c[(idx + 1) % num_points][0]
            deg = self.angle_delta(p1 - p0, p2 - p1)
            return p1, deg

        curr_angle = 0
        points = [ c[0] ]
        threshold = 45
        (x, y, w, h) = cv2.boundingRect(c)

        for idx in range(0, num_points):
            p1, deg = _p_angle(idx)
            curr_angle += deg
            angles.append(deg)
            # sel = ""
            if curr_angle <= -threshold or curr_angle >= threshold:
                if curr_angle <= -threshold:
                    curr_angle += 60
                else:
                    curr_angle -= 60
                curr_angle = 0
                points.append([ p1 ])
                # sel = " ******** " + str(len(points))
            # print(p1, "+", deg, "=", curr_angle, sel)

        points = np.array(points)
        # print("@@ points", points)

        # Note that [c] is not an hexagon. It may have thousands of points or more.
        eps_w_ratio = params.get("polygon_eps_width_ratio", 1 / 20)
        if eps_w_ratio > 0:
            eps = w * eps_w_ratio
        else:
            eps = -1 * eps_w_ratio * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(curve=points, epsilon=eps, closed=True)

        return approx

    def angle_vec(self, a:np.array) -> float:
        a_rad = math.atan2(a[1], a[0])
        TAU = 2 * math.pi
        if a_rad < 0:
            a_rad += TAU
        return np.degrees(a_rad)

    def angle_delta(self, a:np.array, b:np.array) -> float:
        if np.array_equal(a, b):
            # Obvious shortcut
            return 0

        a_deg = self.angle_vec(a)
        b_deg = self.angle_vec(b)
        if a_deg < b_deg:
            angle_deg = b_deg - a_deg
        else:
            angle_deg = b_deg - a_deg + 360
        if angle_deg > 180:
            angle_deg -= 360
        # print("@@angle:", a, b, "@", a_deg, b_deg, "->", angle_deg)

        return angle_deg

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
        # Note that everything here assume the polygon is an hexagon.
        segs = list(segments(polygon))
        len_seg = len(segs)
        def wrap(index:int) -> int:
            return index % len_seg

        # Find the segment with the highest y-coordinate center
        bottom_segment = max(segs, key=lambda segment: segment_center(segment)[1])
        # Find the index of "bottom_segment" in the segments list
        bottom_index = segs.index(bottom_segment)

        y_end_segment_index = bottom_index

        # I don't know if the polygon is defined clockwise or counter-clockwise,
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

    def draw_yrg_coords_into(self, yrg_coords:YRGCoord, dest_img:np.array) -> None:
        t = yrg_coords.triangle(YRG(0, 0, 0))
        radius = int(t.inscribed_circle_radius() *.5 )

        for triangle in self.triangles(yrg_coords):
            poly = np.int32(triangle.to_np_array())
            cv2.polylines(dest_img, [poly], isClosed=True, color=(255, 255, 255), thickness=2)
            tc = triangle.center()
            px = int(tc.x)
            py = int(tc.y)
            cv2.circle(dest_img, (px, py), radius, (255, 255, 255), 1)
            y = triangle.yrg.y + coord.N//2
            r = triangle.yrg.r + coord.N//2
            g = triangle.yrg.g
            cv2.putText(dest_img, f"{y}{r}{g}", (px - 15, py + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def triangles(self, yrg_coords:YRGCoord) -> Generator:
        n2 = coord.N//2
        for (y, r, g) in coord.VALID_YRG:
            y_piece = y - n2
            r_piece = r - n2
            yield yrg_coords.triangle(YRG(y_piece, r_piece, g))

    def extract_cells_colors(self, yrg_coords:YRGCoord, in_img:np.array, cells:list) -> list[Cell]:
        # Apply GaussianBlur to reduce noise
        ksize = (11, 11)
        sigmaX = 0
        blur_img = cv2.GaussianBlur(in_img, ksize, sigmaX)

        hsv_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2HSV)
        lab_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2Lab)
        # Extract HSV LAB channels (used to compute averages below)
        h, s, v = cv2.split(hsv_img)
        l, a, b = cv2.split(lab_img)

        radius = int(yrg_coords.triangle(YRG(0, 0, 0)).inscribed_circle_radius() * SHRINK_RATIO)

        for triangle in self.triangles(yrg_coords):
            if self.is_in_cells(triangle, cells):
                continue
            # # Method 1:
            # # Create a mask based on a shrunk triangle to filter on the HSB
            # poly = np.int32(triangle.shrink(SHRINK_RATIO).to_np_array())
            # mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
            # cv2.fillPoly(mask, [poly], (255, 255, 255))

            # Method 2:
            # Create a mask based on a circle centered in the triangle.
            # mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
            # cv2.circle(mask, , radius, (255), -1)

            # Method 3:
            # Create a square mask by actually cropping the channels directly.
            # That seems a tad faster and actually more reliable.
            cx, cy = triangle.center().to_int()
            x1 = cx - radius
            x2 = cx + radius
            y1 = cy - radius
            y2 = cy + radius
            ch = h[y1:y2, x1:x2]
            cs = s[y1:y2, x1:x2]
            cv = v[y1:y2, x1:x2]
            cl = l[y1:y2, x1:x2]
            ca = a[y1:y2, x1:x2]
            cb = b[y1:y2, x1:x2]

            # Get the mean color of the polygon

            # For methods 1 and 2:
            # Note that cv2.mean() always returns a scalar with 4 components.
            # mean_hsv = cv2.mean(hsv_img, mask=mask)
            # mean_lab = cv2.mean(lab_img, mask=mask)

            # For method 3:
            mean_hsv = self.color_mean((ch, cs, cv))
            mean_lab = self.color_mean((cl, ca, cb))

            # print(f"Mean color HSV@@{','.join([ str(x) for x in mean_hsv[0:3] ])}")
            # print(f"Mean color Lab@@{','.join([ str(x) for x in mean_lab[0:3] ])}")

            color = colors.select(
                mean_hsv[0], mean_hsv[1], mean_hsv[2],
                mean_lab[0], mean_lab[1], mean_lab[2])
            cells.append(Cell(triangle, color, mean_hsv[:3], mean_lab[:3]))
        return cells

    def is_in_cells(self, triangle:Triangle, cells:list) -> bool:
        yrg = triangle.yrg
        for cell in cells:
            if cell.triangle.yrg == yrg:
                return True
        return False

    def extract_cells_bw_only(self, yrg_coords:YRGCoord, in_img:np.array) -> Tuple[list[Cell],dict]:
        histograms = {}
        # Apply GaussianBlur to reduce noise
        ksize = (21, 21)
        sigmaX = 10
        blur_img = cv2.GaussianBlur(in_img, ksize, sigmaX)

        hsv_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2HSV)
        lab_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2Lab)
        # Extract HSV LAB channels (used to compute averages below)
        h, s, v = cv2.split(hsv_img)
        l, a, b = cv2.split(lab_img)

        # Gamma correction formula is:
        # output = (input / 255) ^ (1 / gamma) * 255
        # Modify it to use 128 has the center point:
        # output = (abs(input-128) / 128) ^ (1 / gamma) * 128 * sign(input - 128) + 128
        # Create a gamma LUT
        gamma = 10
        def sign(x):
            return -1 if x < 0 else 1
        gamma_lut = np.array([
            # (i / 255) ** (1 / gamma) * 255
            (abs(i - 128) / 128) ** (1 / gamma) * 128 * sign(i - 128) + 128
            for i in np.arange(0, 256)
        ]).astype(np.uint8)
        # print("@@ gamma lut:", gamma_lut)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        S=4
        clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(S, S))
        # h = clahe.apply(h)
        # s = clahe.apply(s)
        l = clahe.apply(l)
        # Or apply histogram equalization
        # h = cv2.equalizeHist(h)
        # s = cv2.equalizeHist(s)
        l = cv2.equalizeHist(l)
        # Or apply a gamma correction LUT
        s = cv2.LUT(s, gamma_lut)
        l = cv2.LUT(l, gamma_lut)

        # Temp debug -- save HSB + LAB to view their H/L channels
        mask_h = np.where(s > 128, 0, 255)
        print("@@ h:", h.shape, h.dtype)
        h = np.bitwise_and(h, mask_h).astype(np.uint8)
        v = np.bitwise_and(v, mask_h).astype(np.uint8)
        print("@@ h:", h.shape, h.dtype)
        tmp_img = cv2.merge( (h, s, v) )
        tmp_img = cv2.cvtColor(tmp_img, cv2.COLOR_HSV2BGR)
        self.write_indexed_img("hsv", tmp_img)
        # Debug only
        # tmp_img = cv2.merge( (l, a, b) )
        # tmp_img = cv2.cvtColor(tmp_img, cv2.COLOR_LAB2BGR)
        # self.write_indexed_img("lab", tmp_img)


        radius = int(yrg_coords.triangle(YRG(0, 0, 0)).inscribed_circle_radius() * SHRINK_RATIO)

        histograms["h"] = [0] * 256
        histograms["s"] = [0] * 256
        histograms["l"] = [0] * 256
        cells = []
        num_cols = {
            "Black": 0,
            "White": 0,
        }
        for triangle in self.triangles(yrg_coords):
            # Create a square mask by actually cropping the channels directly.
            # That seems a tad faster and actually more reliable.
            cx, cy = triangle.center().to_int()
            x1 = cx - radius
            x2 = cx + radius
            y1 = cy - radius
            y2 = cy + radius
            ch = h[y1:y2, x1:x2]
            cs = s[y1:y2, x1:x2]
            cv = v[y1:y2, x1:x2]
            cl = l[y1:y2, x1:x2]
            ca = a[y1:y2, x1:x2]
            cb = b[y1:y2, x1:x2]

            # Get the mean color of the polygon
            mean_hsv = self.color_mean((ch, cs, cv))
            mean_lab = self.color_mean((cl, ca, cb))
            mh = int(mean_hsv[0])
            ms = int(mean_hsv[1])
            ml = int(mean_lab[0])
            histograms["h"][mh] += 1
            histograms["s"][ms] += 1
            histograms["l"][ml] += 1
            color = colors.select_bw(
                mean_hsv[0], mean_hsv[1], mean_hsv[2],
                mean_lab[0], mean_lab[1], mean_lab[2])
            if color is not None and color["name"] in num_cols:
                cells.append(Cell(triangle, color, mean_hsv[:3], mean_lab[:3]))
                num_cols[ color["name"] ] += 1

        print("@@ num colors:", num_cols)
        return cells, histograms

    def color_mean(self, channels:Tuple) -> list:
        # Input array: list of N np.array split channels (HSV, LAB, etc)
        # Output array: N components (average per component)
        r = []
        for channel in channels:
            med = np.median(channel, overwrite_input=True)
            r.append(med)
        return r

    def draw_histograms_into(self, histograms:dict, dest_img:np.array) -> None:
        sx = dest_img.shape[1]
        sy = dest_img.shape[0] - 5
        h = 128
        w1 = sx // len(histograms)
        w2 = w1 - 16
        px = 0
        py = sy - h
        for name, values in histograms.items():
            print("@@ histogram", name.upper(), "from", min(values),"to", max(values))
            cv2.putText(dest_img, name.upper(), (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            lines = []
            nv = len(values)
            mx = min(h, max(values))
            w = w2 / nv
            for i in range(0, nv - 1):
                y1 = sy - int(values[i] * h / mx)
                # y2 = sy - int(values[i+1] / mx * h)
                x1 = math.floor( px + i * w )
                x2 = math.ceil ( x1 + w )
                # lines.append( [ [ x1, y1 ], [ x2, y2 ] ] )
                cv2.rectangle(dest_img, (x1, y1), (x2, sy), color=(255, 255, 255), thickness=-11)
            # lines = np.array(lines, np.int32)
            # cv2.polylines(dest_img, lines, isClosed=False, color=(255, 255, 255), thickness=1)
            px += w1

    def draw_cells_into(self, cells:list[Cell], dest_img:np.array) -> None:
        dest_img.fill(0)
        if len(cells) == 0:
            return
        radius = int(cells[0].triangle.inscribed_circle_radius() *.5 )

        for cell in cells:
            # We can either display the mean HSV or the mean LAB for validation purposes.

            # Convert the mean HSV to BGR
            mean_bgr = cv2.cvtColor(np.uint8([[cell.mean_hsv]]), cv2.COLOR_HSV2BGR)[0][0]
            mean_bgr = (int(mean_bgr[0]), int(mean_bgr[1]), int(mean_bgr[2]))

            # # Convert the mean Lab to BGR
            # mean_bgr = cv2.cvtColor(np.uint8([[mean_lab[:3]]]), cv2.COLOR_LAB2BGR)[0][0]
            # mean_bgr = (int(mean_bgr[0]), int(mean_bgr[1]), int(mean_bgr[2]))

            poly = np.int32(cell.triangle.to_np_array())
            cv2.fillPoly(dest_img, [poly], mean_bgr)
            cv2.circle(dest_img, cell.triangle.center().to_int(), radius, cell.color["bgr"], -1)
            cv2.polylines(dest_img, [poly], isClosed=True, color=(0, 0, 0), thickness=1)

    def rotate_cells_60_ccw(self, yrg_coords:YRGCoord, cells:list[Cell]) -> None:
        """Rotates the cells list in-place."""
        for cell in cells:
            cell.triangle = yrg_coords.rot_60_ccw(cell.triangle)

    def validate_cells(self, cells:list[Cell]) -> bool:
        num_colors = {
        }
        for cell in cells:
            col_name = cell.color_name()
            num_colors[col_name] = num_colors.get(col_name, 0) + 1
        print("@@ Cell Colors found:", num_colors)

        _expected = {
            "White": 3,
            "Black": 12,
            # We don't currently validate Red/Yellow because we don't know how to
            # find the orange, and it is perceived as either red or yellow, making the
            # counts undecisive.
            # "Orange": 9,
            # "Red": 18,
            # "Yellow": 12
        }
        for k, v in _expected.items():
            if num_colors.get(k, 0) != v:
                print(f"Found {num_colors.get(k, 0)} {k} cells, expected {v}.")
                return False
        return True

    def orient_white_cells(self, yrg_coords:YRGCoord, cells:list[Cell]) -> None:
        # We expect to find 3 white cells in the puzzle.
        # Two of them must have the same "g" piece coordinate.
        whites = [ cell for cell in cells if cell.color_name() == "White" ]
        if len(whites) != 3:
            print(f"Found {len(whites)} white cells, expected 3.")
            return None
        # Check if two of them have the same "g" piece coordinate
        cells_g = {}
        cells_g[0] = [ cell for cell in whites if cell.yrg().g == 0 ]
        cells_g[1] = [ cell for cell in whites if cell.yrg().g == 1 ]
        pair = [ cs for k, cs in cells_g.items() if len(cs) == 2 ]
        single = [ cs for k, cs in cells_g.items() if len(cs) == 1 ]
        if len(single) != 1 or len(pair) != 1:
            print(f"Found {len(pair)} pairs of white cells with the same g piece coordinate.")
            return None
        pair = pair[0]      # This is a list of 2 cells
        center = single[0][0] # This is a single cell in the center
        print(f"White pair: {pair}, center: {center}")


        # List all the points and count their number of occurrences
        dist_epsilon = 0.1
        points = []
        for cell in [*pair, center]:
            for new_point in cell.triangle.xy_list:
                def add_if_close(point):
                    for p in points:
                        if p["p"].distance(point) <= dist_epsilon:
                            p["count"] += 1
                            return True
                    return False
                if not add_if_close(new_point):
                    points.append({ "p": new_point, "count": 1})

        # The shared point must be present 3 times
        # print(f"Found {points}.")
        common_point = [ p for p in points if p["count"] == 3 ]
        if len(common_point) != 1:
            print(f"Found {len(common_point)} common points, expected 1.")
            return None
        common_point = common_point[0]["p"]
        # print(f"Common point: {common_point}")

        center_xy_list = center.triangle.xy_list
        # Find the index of the common point in the center triangle
        p1_index = [ i for i, p in enumerate(center_xy_list) if p.distance(common_point) <= dist_epsilon ][0]
        p3_index = (p1_index + 1) % len(center_xy_list)
        p4_index = (p1_index + 2) % len(center_xy_list)
        # print(f"Common point index: {p1_index}, {p3_index}, {p4_index}")

        p3 = center_xy_list[p3_index]
        p4 = center_xy_list[p4_index]
        dx = p4.x - p3.x
        dy = p4.y - p3.y
        angle = math.degrees(math.atan2(dy, dx))
        angle_deg = round(angle / 60) * 60
        print(f"Angle: {angle} -> {angle_deg} degrees")

        for rot in range(0, (180 + angle_deg)//60):
            self.rotate_cells_60_ccw(yrg_coords, cells)

        return cells

    def cells_signature(self, cells:list[Cell]) -> str:
        """Generates a signature for the cells."""
        if cells is None:
            return None
        results = []
        n2 = coord.N//2
        for y, r, g in VALID_YRG:
            yrg = YRG(y - n2, r - n2, g)

            cell = [ cell for cell in cells if cell.yrg() == yrg ]
            if len(cell) == 0:
                resuklts.append("-")
            else:
                color = cell[0].color_name()
                # First letter of the color name is enough to distinguish it
                color = color[0].upper()
                results.append(color)

        return "".join(results)

# ~~
