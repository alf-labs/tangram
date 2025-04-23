# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import cv2
import math
import numpy as np
import os

from typing import Generator
from typing import Tuple

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
        print(f"Processing Image: {self.input_img_path}")
        self.find_hexagon(self.input_img_path, overwrite)

    def find_hexagon(self, input_img_path:str, overwrite:bool) -> None:
        src_img_path = self.dest_name("_src")
        hex_img_path = self.dest_name("_9_hex")

        # Check if the hexagon image already exists
        if os.path.exists(hex_img_path) and not overwrite:
            print(f"Hexagon image already exists: {hex_img_path}")
            return

        resized = self.load_resized_image(input_img_path)
        lab = self.convert_to_lab(resized)
        cv2.imwrite(self.dest_name("_1_lab"), lab)
        contrasted = self.enhance_image(lab)
        cv2.imwrite(self.dest_name("_2_contrast"), contrasted)

        hex_img = resized.copy()
        hexagon = self.find_hexagon_contour(contrasted, hex_img)

        if hexagon is not None:
            rot_angle_deg, hex_center = self.detect_hexagon_rotation(hexagon, hex_img)
            rot_img = self.rotate_image(resized, hexagon, rot_angle_deg, hex_center)

        cv2.imwrite(self.dest_name("_3_hexagon"), hex_img)
        cv2.imwrite(self.dest_name("_4_rot"), rot_img)


    def load_resized_image(self, input_img_path:str) -> np.array:
        # Load the image using OpenCV
        image = cv2.imread(self.input_img_path, cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Could not load image: {input_img_path}")

        print(f"Image loaded successfully: {input_img_path}")

        # Resize the image to a width of 1024 while maintaining aspect ratio
        height, width = image.shape[:2]
        new_width = 1024
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

    def enhance_image(self, lab:np.array) -> np.array:
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
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)

        # Enhance the brightness of the image
        # alpha is a scale factor, and beta is an offset.
        # e.g. dest (8-bit) = alpha * src (8-bit) + beta, clamps to 0..255
        blurred = cv2.convertScaleAbs(blurred, alpha=3, beta=0)

        # # Enhance the contrast of the image using histogram equalization (for gray img)
        # blurred = cv2.equalizeHist(blurred)

        # Convert the image to black and white using a gray level threshold
        _, bw = cv2.threshold(blurred, thresh=16, maxval=255, type=cv2.THRESH_BINARY)
        return bw

    def find_edges(self, blurred:np.array) -> np.array:
        # Use Canny edge detection
        edges = cv2.Canny(blurred, 
            threshold1=20, threshold2=30,
            apertureSize=3,
            L2gradient=False)
        cv2.imwrite(self.dest_name("_3_edges"), edges)

    def find_hexagon_contour(self, bw_image:np.array, draw_img:np.array=None) -> list:
        # Find the largest contour in the threshold image
        cnts, _ = cv2.findContours(bw_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # get the contour based on max contour area.
        c = max(cnts, key=cv2.contourArea)

        if draw_img is not None:
            cv2.drawContours(draw_img, [c], -1, (0, 255, 0), 3)
            (x, y, w, h) = cv2.boundingRect(c)
            # Draw the bounding box on the image
            cv2.rectangle(draw_img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Note that [c] is not an hexagon. It may have thousands of points or more.
        eps = w / 20
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

    def rotate_image(self, image:np.array, polygon:list, angle_deg:float, center:tuple) -> np.array:
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
            print(f"Segment: {segment}")
            cv2.line(rotated_img, pt1=segment[0], pt2=segment[1], color=(0, 255, 0), thickness=3)

        # Crop the image to the squared bounding box with some padding
        wh2 = wh // 2 + 10
        cv2.rectangle(rotated_img, (cx - wh2, cy - wh2), (cx + wh2, cy + wh2), (255, 0, 0), 2)
        rotated_img = rotated_img[cy - wh2:cy + wh2, cx - wh2:cx + wh2]
        return rotated_img





# ~~
