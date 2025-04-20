# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import argparse
import glob
import os

class Main:
    def __init__(self):
        print("Tangram")
        self.args = {}

    def parse_arguments(self) -> None:
        parser = argparse.ArgumentParser(description="Tangram Puzzle Image Analyzer")
        parser.add_argument("-i", "--dir-input",
            default=os.path.join("data", "originals"),
            help="Path to the directory with source image files")
        parser.add_argument("-o", "--dir-output",
            default=os.path.join("data", "output"),
            help="Path to outout directory")
        self.args = parser.parse_args()

    def find_files(self, dir_input: str) -> list:
        """Finds all files in the given directory."""
        if not os.path.exists(dir_input):
            raise FileNotFoundError(f"Directory {dir_input} does not exist.")
        return glob.glob(os.path.join(dir_input, '**', '*.jpg'), recursive=True)

    def process_file(self, input_dir_path: str, outout_dir_path: str) -> None:
        """Processes the file."""
        # Placeholder for actual processing logic
        print(f"Processing file: {input_dir_path}")

        if not os.path.exists(outout_dir_path):
            raise FileNotFoundError(f"Directory {outout_dir_path} does not exist.")

        # Example: Save processed image to output directory
        output_path = os.path.join(outout_dir_path, os.path.basename(input_dir_path))
        print(f"Saving processed image to: {output_path}")
        # Here you would save the processed image


if __name__ == "__main__":
    m = Main()
    m.parse_arguments()
    inputs = m.find_files(m.args.dir_input)
    for f in inputs:
        m.process_file(f, m.args.dir_output)

# ~~
