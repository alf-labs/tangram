# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import argparse

class Main:
    def __init__(self):
        print("Tangram")
        self.args = {}

    def parse_arguments(self) -> None:
        parser = argparse.ArgumentParser(description="Tangram Puzzle Image Analyzer")
        parser.add_argument("--input", type=str, help="Path to the input image file", required=True)
        parser.add_argument("--output", type=str, help="Path to save the output image", required=True)
        self.args = parser.parse_args()


if __name__ == "__main__":
    m = Main()
    m.parse_arguments()

# ~~
