# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import argparse
import glob
import os

from img_proc import ImageProcessor

TABLE_PLACEHOLDER = "TABLE_PLACEHOLDER"

class Main:
    def __init__(self):
        print("Tangram")
        self.args = {}

    def parse_arguments(self) -> None:
        parser = argparse.ArgumentParser(description="Tangram Puzzle Image Analyzer")
        parser.add_argument("-i", "--input-image",
            required=False,
            help="Single source image file to process")
        parser.add_argument("-d", "--input-dir",
            required=False,
            help="Automatically process all images in the given input directory")
        parser.add_argument("-o", "--dir-output",
            default=os.path.join("data", "output"),
            help="Path to output directory")
        parser.add_argument("-y", "--overwrite",
            action="store_true",
            help="Overwrite existing files")
        self.args = parser.parse_args()

    def process_file(self, input_file_path:str, outout_dir_path:str) -> None:
        p = ImageProcessor(input_file_path, outout_dir_path)
        p.process_image(m.args.overwrite)

    def find_files(self, dir_input:str) -> list:
        """Finds all files in the given directory."""
        if not os.path.exists(dir_input):
            raise FileNotFoundError(f"Directory {dir_input} does not exist.")
        return glob.glob(os.path.join(dir_input, "**", "*.jpg"), recursive=True)

    def generate_index(self, dir_output:str) -> None:
        img_infos = [] # dict: basename=str, src=path, alt=list[path]
        max_columns = 1
        for src in glob.glob(os.path.join(dir_output, "*_src.jpg"), recursive=False):
            basename = os.path.basename(src)
            basename = basename.replace("_src.jpg", "")
            info = {
                "basename": basename,
                "src": os.path.basename(src),
                "alt": []
            }
            img_infos.append(info)
            for alt in glob.glob(os.path.join(dir_output, basename + "_[0-9]*.jpg"), recursive=False):
                info["alt"].append(os.path.basename(alt))
            max_columns = 1 + max(max_columns, len(info["alt"]))

        # Read template
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(script_dir, "index_template.html")
        with open(template_path, "r") as f:
            template = f.read()

        # Generate HTML table
        table = "<table>\n"
        n = 0
        for info in img_infos:
            table += "<tr class='title'>\n"
            n += 1
            table += f"  <td colspan={max_columns}>{n} - {info['basename']}</td>\n"
            table += "</tr>\n"

            table += "<tr class='images'>\n"
            table += f"  <td><img src='{info['src']}'></td>\n"
            for alt in info["alt"]:
                table += f"  <td><img src='{alt}'></td>\n"
            table += "</tr>\n"
        table += "</table>\n"

        html = template.replace(TABLE_PLACEHOLDER, table)
        index_path = os.path.join(dir_output, "index.html")
        with open(index_path, "w") as f:
            f.write(html)
        print(f"Generated index at {index_path}")


if __name__ == "__main__":
    m = Main()
    m.parse_arguments()
    if m.args.overwrite:
        print("Will overwrite existing files")
    if m.args.input_image:
        m.process_file(m.args.input_image, m.args.dir_output)
    elif m.args.input_dir:
        inputs = m.find_files(m.args.input_dir)
        for f in inputs:
            m.process_file(f, m.args.dir_output)
        m.generate_index(m.args.dir_output)
    else:
        print("No input file (-i) or directory specified (-d).")

# ~~
