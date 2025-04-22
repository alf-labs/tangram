# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import cv2
import os

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

        cv2.imwrite(src_img_path, image)

        # # Convert the image to YCrCb color space (luma/chrominance)
        # ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        # # Split the channels: Y (luma), Cr, and Cb (chrominance)
        # y, cr, cb = cv2.split(ycrcb)
        # # Discard the luminance channel
        # y[:] = 0
        # ycrcb = cv2.merge((y, cr, cb))
        # ycrcb = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        # cv2.imwrite(self.dest_name("_1_ycrcb"), ycrcb)

        # Convert the image to LAB color space to enhance contrast
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        # Split the LAB image into its channels
        l, a, b = cv2.split(lab)
        # Discard the luminance channel
        l[:] = 0
        lab = cv2.merge((l, a, b))
        lab = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        cv2.imwrite(self.dest_name("_1_lab"), lab)

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
        _, blurred = cv2.threshold(blurred, thresh=16, maxval=255, type=cv2.THRESH_BINARY)
        cv2.imwrite(self.dest_name("_2_blur"), blurred)

        # Use Canny edge detection
        edges = cv2.Canny(blurred, 
            threshold1=20, threshold2=30,
            apertureSize=3,
            L2gradient=False)
        cv2.imwrite(self.dest_name("_3_edges"), edges)

        # Find the largest contour in the threshold image
        cnts, _ = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # get the contour based on max contour area.
        c = max(cnts, key=cv2.contourArea)
        img_hex = image.copy()
        cv2.drawContours(img_hex, [c], -1, (0, 255, 0), 3)
        (x, y, w, h) = cv2.boundingRect(c)
        print(f"Method 2 Bounding rect: x={x}, y={y}, w={w}, h={h}")
        # Draw the bounding box on the image
        cv2.rectangle(img_hex, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Note that [c] is not an hexagon. It may have thousands of points or more.
        eps = w / 20
        approx = cv2.approxPolyDP(curve=c, epsilon=eps, closed=True)

        # Check if the approximated contour has 6 vertices (hexagon)
        if len(approx) == 6:
            print("Hexagon detected!")

        cv2.drawContours(img_hex, [approx], -1, (0, 255, 255), 4)
        cv2.imwrite(self.dest_name("_4_hexagon"), img_hex)

        # # Crop the image to the bounding box
        # cropped_img = img_hex[y:y + h, x:x + w]
        # cropped_img_path = self.dest_name("_9_cropped")
        # cv2.imwrite(cropped_img_path, cropped_img)
        # print(f"Cropped image saved to: {cropped_img_path}")


# ~~
