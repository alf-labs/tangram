# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import unittest
import sys
from main import Main

class MainTest(unittest.TestCase):
    def setUp(self):
        self.main = Main()

    def test_initialization(self):
        self.assertEqual(self.main.args, {})

    def test_parse_arguments_missing_args(self):
        test_args = ["main.py"]
        sys.argv = test_args
        with self.assertRaises(SystemExit):
            self.main.parse_arguments()
        self.assertFalse(hasattr(self.main.args, "input"))
        self.assertFalse(hasattr(self.main.args, "output"))

    def test_parse_arguments_with_args(self):
        test_args = ["main.py", "--input", "input_image.png", "--output", "output_image.png"]
        sys.argv = test_args
        self.main.parse_arguments()
        self.assertEqual(self.main.args.input, "input_image.png")
        self.assertEqual(self.main.args.output, "output_image.png")


if __name__ == "__main__":
    unittest.main()

# ~~
