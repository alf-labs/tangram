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

        if not os.path.exists(output_dir_path):
            raise FileNotFoundError(f"Directory {output_dir_path} does not exist.")

    def dest_name(self, suffix:str, ext:str=None) -> str:
        """Generates a destination name for the processed image."""
        base_name = os.path.basename(self.input_img_path)
        name, _ext = os.path.splitext(base_name)
        if ext is None:
            ext = _ext
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
                break

        if hexagon is not None:
            rot_angle_deg, hex_center = self.detect_hexagon_rotation(hexagon, hex_img)
            rot_img, rot_poly, hex_center = self.rotate_image(resized, hexagon, rot_angle_deg, hex_center)
            cv2.imwrite(self.dest_name("_4_hexagon"), hex_img)
            cv2.imwrite(self.dest_name("_5_rot"), rot_img)

            yrg_coords = self.compute_yrg_coords(rot_poly, hex_center)
            coords_img = rot_img.copy()
            self.draw_yrg_coords(yrg_coords, coords_img)
            cv2.imwrite(self.dest_name("_6_yrg"), coords_img)
            cells = self.extract_cells_colors(yrg_coords, rot_img, params={})
            colors_img = self.draw_cells(rot_img, cells)
            cv2.imwrite(self.dest_name("_7_colors"), colors_img)
            result = self.orient_white_cells(yrg_coords, cells)

            if result is not None:
                rot_col_img = self.draw_cells(rot_img, result)
                cv2.imwrite(self.dest_name("_8_colors"), rot_col_img)

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
        t = yrg_coords.triangle(YRG(0, 0, 0))
        radius = int(t.inscribed_circle_radius() *.5 )

        for triangle in self.triangles(yrg_coords):
            poly = np.int32(triangle.to_np_array())
            cv2.polylines(out_img, [poly], isClosed=True, color=(255, 255, 255), thickness=2)
            tc = triangle.center()
            px = int(tc.x)
            py = int(tc.y)
            cv2.circle(out_img, (px, py), radius, (255, 255, 255), 1)
            y = triangle.yrg.y + coord.N//2
            r = triangle.yrg.r + coord.N//2
            g = triangle.yrg.g
            cv2.putText(out_img, f"{y}{r}{g}", (px - 15, py + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def triangles(self, yrg_coords:YRGCoord) -> Generator:
        center = yrg_coords.center_px
        n2 = coord.N//2
        for (y, r, g) in coord.VALID_YRG:
            y_piece = y - n2
            r_piece = r - n2
            yield yrg_coords.triangle(YRG(y_piece, r_piece, g), offset=center)

    def extract_cells_colors(self, yrg_coords:YRGCoord, in_img:np.array, params:dict={}) -> list[Cell]:
        # Apply GaussianBlur to reduce noise
        ksize = params.get("blur_ksize", (11, 11))
        sigmaX = params.get("blur_sigmaX", 0)
        blur_img = cv2.GaussianBlur(in_img, ksize, sigmaX)

        hsv_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2HSV)
        lab_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2Lab)
        # # Clip and quantize the HSV
        # # Clip the hue channel -- we only care about the redish hue
        # h, s, v = cv2.split(hsv_img)
        # np.clip(h, 0, 20, out=h)
        # h = (h // 4) * 4
        # s = (s // 16) * 16
        # v = (v // 32) * 32
        # hsv_img = cv2.merge((h, s, v))

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
            mean_lab = cv2.mean(lab_img, mask=mask)
            # print(f"Mean color HSV@@{','.join([ str(x) for x in mean_hsv[0:3] ])}")
            # print(f"Mean color Lab@@{','.join([ str(x) for x in mean_lab[0:3] ])}")

            color = colors.select(
                mean_hsv[0], mean_hsv[1], mean_hsv[2],
                mean_lab[0], mean_lab[1], mean_lab[2])
            cells.append(Cell(triangle, color, mean_hsv[:3], mean_lab[:3]))
        return cells

    def draw_cells(self, in_img:np.array, cells:list[Cell]) -> np.array:
        # Make a new image the same size as in_img but black
        out_img = np.zeros(in_img.shape, dtype=np.uint8)

        radius = int(cells[0].triangle.inscribed_circle_radius() *.5 )

        for cell in cells:
            # Convert the mean HSV to BGR
            mean_bgr = cv2.cvtColor(np.uint8([[cell.mean_hsv]]), cv2.COLOR_HSV2BGR)[0][0]
            mean_bgr = (int(mean_bgr[0]), int(mean_bgr[1]), int(mean_bgr[2]))

            # # Convert the mean Lab to BGR
            # mean_bgr = cv2.cvtColor(np.uint8([[mean_lab[:3]]]), cv2.COLOR_LAB2BGR)[0][0]
            # mean_bgr = (int(mean_bgr[0]), int(mean_bgr[1]), int(mean_bgr[2]))

            poly = np.int32(cell.triangle.to_np_array())
            cv2.fillPoly(out_img, [poly], mean_bgr)
            cv2.circle(out_img, cell.triangle.center().to_int(), radius, cell.color["bgr"], -1)
            cv2.polylines(out_img, [poly], isClosed=True, color=(0, 0, 0), thickness=1)
        return out_img

    def rotate_cells_60_ccw(self, yrg_coords:YRGCoord, cells:list[Cell]) -> None:
        """Rotates the cells list in-place."""
        for cell in cells:
            cell.triangle = yrg_coords.rot_60_ccw(cell.triangle)

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
