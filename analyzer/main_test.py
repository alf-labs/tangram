# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import os
import sys
import unittest
from main import Main

class MainTest(unittest.TestCase):
    def setUp(self):
        self.main = Main()

    def test_initialization(self):
        self.assertEqual(self.main.args, {})

    def test_parse_arguments_missing_args(self):
        test_args = ["main.py"]
        sys.argv = test_args
        # Exception no longer happens: arguments have default values.
        # with self.assertRaises(SystemExit): self.main.parse_arguments()
        self.main.parse_arguments()
        sep = os.sep
        self.assertEqual(self.main.args.dir_input, f"data{sep}originals")
        self.assertEqual(self.main.args.dir_output, f"data{sep}output")

    def test_parse_arguments_with_args(self):
        test_args = ["main.py", "--dir-input", "somedir/inputs", "--dir-output", "somedir/outputs"]
        sys.argv = test_args
        self.main.parse_arguments()
        self.assertEqual(self.main.args.dir_input, "somedir/inputs")
        self.assertEqual(self.main.args.dir_output, "somedir/outputs")


if __name__ == "__main__":
    unittest.main()

# ~~
