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
    def __init__(self, triangle:Triangle, color:dict, mean_bgr:Tuple):
        self.triangle = triangle
        self.color = color
        self.mean_bgr = mean_bgr

    def yrg(self) -> YRG:
        return self.triangle.yrg

    def color_name(self) -> str:
        return self.color["name"]

    def __repr__(self) -> str:
        return f"Cell(triangle={self.yrg()}, color={self.color_name()})"

    def copy(self) -> "Cell":
        return Cell(self.triangle, self.color, self.mean_bgr)


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
            # self.write_indexed_img("rot", rot_img)

            yrg_coords = self.compute_yrg_coords(rot_poly, hex_center)
            coords_img = rot_img.copy()
            self.draw_yrg_coords_into(yrg_coords, dest_img=coords_img)
            self.write_indexed_img("yrg", coords_img)

            # Method 2: try to detect BW and color cells separately.
            cells = self.extract_cells_2(yrg_coords, in_img=rot_img)
            bw_img = rot_img.copy()
            self.draw_cells_into(cells=cells, dest_img=bw_img)
            self.write_indexed_img("bw", bw_img)

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
        # No processing.
        # return rgb_img

        # ----------
        # # Normalize the RGB channels independantly, always a bad idea
        # b, g, r = cv2.split(rgb_img)
        # r = cv2.equalizeHist(r)
        # g = cv2.equalizeHist(g)
        # b = cv2.equalizeHist(b)
        # rgb_img = cv2.merge((b, g, r))


        # ----------
        # Attempt 1: adjust contrast in the Lab color space.
        # Normaly one would only be done for Luminance.
        # Try adjusting a*b* channels too to see what it gives
        # (normally one does not normalize A/B or U/V separately as this "distords"
        # the colors, but since most of the colors we want here are in a very narrow
        # band in the red-orange spectra, that may work, at the expense of distorting
        # the white and black pieces colors.)

        # # Convert the image to LAB color space
        # lab_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2LAB)
        # l, a, b = cv2.split(lab_img)
        # # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # S=4
        # clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(S, S))
        # l = clahe.apply(l)
        # a = clahe.apply(a)
        # b = clahe.apply(b)
        # lab_img = cv2.merge((l, a, b))
        # rgb_img = cv2.cvtColor(lab_img, cv2.COLOR_LAB2BGR)

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
        b, g, r = cv2.split(rgb_img)
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

        # Crop the image to the squared bounding box, yet still fit in the image boundaries
        wh = min(w, h, wh)
        wh2 = wh // 2
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

        # Redraw the offset hexagon for debug/validation purposes
        for segment in segments(rotated_polygon):
            cv2.line(rotated_img, pt1=segment[0], pt2=segment[1], color=(0, 255, 255), thickness=3)

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
            r_start_segment_index = wrap(next_segment_index + 1)
        else:
            # the previous segment presents the start of the G axis, then the start of the R axis
            r_start_segment_index = wrap(bottom_index - 2)

        y_start_segment_index = wrap(y_end_segment_index + 3)
        r_end_segment_index = wrap(r_start_segment_index + 3)

        # Define the axes
        y_axis = Axis(segs[y_start_segment_index], segs[y_end_segment_index])
        r_axis = Axis(segs[r_start_segment_index], segs[r_end_segment_index])
        yrg_coords = YRGCoord(center, y_axis, r_axis)
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

        # Draw the sides of the Y and R axis, for debug/validation purposes.
        # This shows if the Y/R axes are properly scaled and centered.
        p0 = np.int32(yrg_coords.y_axis.segment_start[0])
        p1 = np.int32(yrg_coords.y_axis.segment_end[0])
        p2 = np.int32(yrg_coords.y_axis.segment_start[1])
        p3 = np.int32(yrg_coords.y_axis.segment_end[1])
        lines = np.array([ [p0, p1], [p2, p3] ])
        cv2.polylines(dest_img, lines, isClosed=False, color=(0,0, 255), thickness=2)

        p0 = np.int32(yrg_coords.r_axis.segment_start[0])
        p1 = np.int32(yrg_coords.r_axis.segment_end[0])
        p2 = np.int32(yrg_coords.r_axis.segment_start[1])
        p3 = np.int32(yrg_coords.r_axis.segment_end[1])
        lines = np.array([ [p0, p1], [p2, p3] ])
        cv2.polylines(dest_img, lines, isClosed=False, color=(255, 0, 0), thickness=2)

    def triangles(self, yrg_coords:YRGCoord) -> Generator:
        n2 = coord.N//2
        for (y, r, g) in coord.VALID_YRG:
            y_piece = y - n2
            r_piece = r - n2
            yield yrg_coords.triangle(YRG(y_piece, r_piece, g))

    def is_in_cells(self, triangle:Triangle, cells:list) -> bool:
        yrg = triangle.yrg
        for cell in cells:
            if cell.triangle.yrg == yrg:
                return True
        return False

    def iter_triangles(self, yrg_coords:YRGCoord) -> Generator:
        # Returns a square (index, triangle, x1, y1, x2, y2) that can be used to extract colors.
        radius = int(yrg_coords.triangle(YRG(0, 0, 0)).inscribed_circle_radius() * SHRINK_RATIO)
        idx = 0
        for triangle in self.triangles(yrg_coords):
            # Create a square mask by actually cropping the channels directly.
            # That seems a tad faster and actually more reliable.
            cx, cy = triangle.center().to_int()
            x1 = cx - radius
            x2 = cx + radius
            y1 = cy - radius
            y2 = cy + radius
            yield (idx, triangle, x1, y1, x2, y2)
            idx += 1

    def extract_cells_2(self, yrg_coords:YRGCoord, in_img:np.array) -> list[Cell]:
        # Apply GaussianBlur to reduce noise
        ksize = (21, 21)
        sigmaX = 10
        blur_img = cv2.GaussianBlur(in_img, ksize, sigmaX)

        _b, _g, _r = cv2.split(blur_img)
        tmp_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2Lab)
        _l, _a, _  = cv2.split(tmp_img)
        tmp_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2YUV)
        _ , _u, _  = cv2.split(tmp_img)

        mean_a = []
        mean_l = []
        mean_u = []
        mean_r = []
        for (idx, t, x1, y1, x2, y2) in self.iter_triangles(yrg_coords):
            ca = _a[y1:y2, x1:x2]
            cl = _l[y1:y2, x1:x2]
            cu = _u[y1:y2, x1:x2]
            cr = _r[y1:y2, x1:x2]
            ma, ml, mu, mr = self.color_mean((ca, cl, cu, cr))
            mean_a.append( int(ma) )
            mean_l.append( int(ml) )
            mean_u.append( int(mu) )
            mean_r.append( int(mr) )

        mean_a = np.array(mean_a).astype(np.uint8)
        mean_l = np.array(mean_l).astype(np.uint8)
        mean_u = np.array(mean_u).astype(np.uint8)
        mean_r = np.array(mean_r).astype(np.uint8)

        # Local support methods
        tmp_img = in_img.copy()
        tmp_img.fill(0)
        def _draw_triangles(suffix:str, updated_channel:list):
            for (idx, t, x1, y1, x2, y2) in self.iter_triangles(yrg_coords):
                poly = np.int32(t.to_np_array())
                gray = int(updated_channel[idx])
                cv2.fillPoly(tmp_img, [poly], (gray, gray, gray))
                gray = 64 if gray < 128 else 192
                cv2.polylines(tmp_img, [poly], isClosed=True, color=(gray, gray, gray), thickness=1)
            self.write_indexed_img(suffix, tmp_img)

        def _filter_channel(label:str,
                source:np.array,
                find_high:bool,
                expected_count:int,
                exclude:list[int]=None,
                include:list[int]=None):
            # Coef 1 starts at min (find low) or max (find high) and coef 0 ends at median.
            # Excluded indices: we already know their color and wish to exclude them from
            #   all processing here, including the min/max computations.
            # Included indices: we already know their colors and we already know they are
            #   part of the desired solution, but we should not use them when sorting.
            #   These values are part of the "expected_count".
            input_ = source.copy()
            if include is None: include = []
            if exclude is None: exclude = []
            included_ = []
            for i,v in enumerate(input_):
                if i not in exclude:
                    included_.append( [i, float(v)] )
            # print(f"@@ {label} source:", str(included_))

            updated_ = input_.copy()
            target_ = 255 if find_high else 0
            updated_.fill(255 - target_)

            # Just take the N higher (find_high) or lower elements
            included_.sort(key=lambda x: x[1], reverse=find_high)

            for i in include:
                # We already know we want this index
                updated_[i] = target_
                expected_count -= 1
            included_ = [ [i,v] for i,v in included_ if i not in include ]
            for i, v in included_[:expected_count]:
                updated_[i] = target_
            # print(f"@@ {label} updated:", str(updated_).replace("\n", ""))

            return updated_

        # Filter A to detect both black and white cells

        expected_counts = colors.EXPECTED_NUM_CELLS

        updated_a = _filter_channel("A", mean_a,
                        find_high=False,
                        expected_count=expected_counts["White"] + expected_counts["Black"])
        _draw_triangles("va_b_w", updated_a)

        # Filter L to detect only white cells

        updated_l = _filter_channel("L", mean_l,
                        find_high=True,
                        expected_count=expected_counts["White"])
        _draw_triangles("vl_w", updated_l)

        # Combine both filters to get the B & W cells

        cells = []
        exclude_idx = []
        num_colors = {}
        for (idx, t, x1, y1, x2, y2) in self.iter_triangles(yrg_coords):
            va = int(updated_a[idx]) # 0 if Black or White
            vl = int(updated_l[idx]) # 255 if White
            name = None
            if vl == 255:
                name = "White"
            elif va == 0:
                name = "Black"

            if name is not None:
                # Get a mean color just for display/debug purposes
                cr = _r[y1:y2, x1:x2]
                cg = _g[y1:y2, x1:x2]
                cb = _b[y1:y2, x1:x2]
                mean_bgr = self.color_mean((cb, cg, cr))

                color = colors.by_name(name)
                cells.append(Cell(t, color, mean_bgr))
                exclude_idx.append(idx)
                num_colors[name] = num_colors.get(name, 0) + 1

        # Filter U/R to detect orange cells
        # Ignore B & W cells found above.

        updated_r = _filter_channel("R", mean_r,
                        find_high=True,
                        exclude=exclude_idx,
                        expected_count=expected_counts["Orange"])
        _draw_triangles("vr_o", updated_r)
        include_idx = [ i for i, v in enumerate(updated_r) if v == 255 ]

        updated_l = _filter_channel("L", mean_l,
                        find_high=True,
                        include=include_idx,
                        exclude=exclude_idx,
                        expected_count=expected_counts["Orange"] + expected_counts["Yellow"])
        _draw_triangles("vl_o_y", updated_l)

        # Combine both filters to get the Orange, Yellow, and Red cells

        for (idx, t, x1, y1, x2, y2) in self.iter_triangles(yrg_coords):
            if self.is_in_cells(t, cells):
                continue

            # vu = int(updated_u[idx]) # 0 if Orange or Yellow
            vl = int(updated_l[idx]) # 255 if Orange or Yellow
            vr = int(updated_r[idx]) # 255 if Orange
            name = None
            # if vu == 0:
            if vr == 255:
                name = "Orange"
            elif vl == 255:
                name = "Yellow"
            else:
                name = "Red"

            if name is not None:
                # Get a mean color just for display/debug purposes
                cr = _r[y1:y2, x1:x2]
                cg = _g[y1:y2, x1:x2]
                cb = _b[y1:y2, x1:x2]
                mean_bgr = self.color_mean((cb, cg, cr))

                color = colors.by_name(name)
                cells.append(Cell(t, color, mean_bgr))
                exclude_idx.append(idx)
                num_colors[name] = num_colors.get(name, 0) + 1

        print("@@ num colors:", num_colors)
        return cells

    def color_mean(self, channels:Tuple) -> list:
        # Input array: list of N np.array split channels (HSV, LAB, etc)
        # Output array: N components (average per component)
        r = []
        for channel in channels:
            med = np.median(channel, overwrite_input=True)
            r.append(med)
        return r

    def draw_cells_into(self, cells:list[Cell], dest_img:np.array) -> None:
        dest_img.fill(0)
        if len(cells) == 0:
            return
        radius = int(cells[0].triangle.inscribed_circle_radius() *.5 )

        for cell in cells:
            # We can either display the mean HSV or the mean LAB for validation purposes.

            poly = np.int32(cell.triangle.to_np_array())
            cv2.fillPoly(dest_img, [poly], cell.mean_bgr)
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

        _expected = colors.EXPECTED_NUM_CELLS
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

    def to_bgr(self, color2bgr, in_tuple:Tuple) -> Tuple:
        # color2bgr: cv2.COLOR_LAB2BGR, or cv2.COLOR_YUV2BGR, etc
        b, g, r = cv2.cvtColor(np.uint8([[in_tuple]]), color2bgr)[0][0]
        return (int(b), int(g), int(r))


# ~~
