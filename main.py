# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import argparse
import glob
import os
import time

from img_proc import ImageProcessor

TABLE_PLACEHOLDER = "TABLE_PLACEHOLDER"
SAMPLE = "sample"

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
        parser.add_argument("-o", "--output-dir",
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

    def generate_index(self, output_dir:str) -> None:
        img_infos = [] # dict: basename=str, src=path, alt=list[path]
        max_columns = 1

        stats = {
            "num_img": 0,
            "num_sig": 0,
            "num_unique": 0,
            "num_dups": 0,
        }
        name_to_sig = {}
        sig_counts = {}
        # Find all the signatures and count their number of occurrences to find dups
        for sig_path in glob.glob(os.path.join(output_dir, "*_sig.txt"), recursive=False):
            basename = os.path.basename(sig_path)
            basename = basename.replace("_sig.txt", "")
            if basename == SAMPLE and len(name_to_sig) > 0:
                continue # skip sample if we have other images
            with open(sig_path, "r") as f:
                sig = f.read()
                name_to_sig[basename] = sig
                sig_counts[sig] = sig_counts.get(sig, 0) + 1
                stats["num_sig"] = stats["num_sig"] + 1
        stats["num_unique"] = len([ s for s in sig_counts.keys() if sig_counts[s] == 1])
        stats["num_dups"] = len([ s for s in sig_counts.keys() if sig_counts[s] > 1])

        for src in glob.glob(os.path.join(output_dir, "*_src.jpg"), recursive=False):
            basename = os.path.basename(src)
            basename = basename.replace("_src.jpg", "")
            if basename == SAMPLE and len(name_to_sig) > 0:
                continue # skip sample if we have other images
            info = {
                "basename": basename,
                "src": os.path.basename(src),
                "alt": []
            }
            img_infos.append(info)
            stats["num_img"] = stats["num_img"] + 1
            for alt in glob.glob(os.path.join(output_dir, basename + "_[0-9]*.jpg"), recursive=False):
                info["alt"].append(os.path.basename(alt))
            max_columns = 1 + max(max_columns, len(info["alt"]))

        # Read template
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(script_dir, "index_template.html")
        with open(template_path, "r") as f:
            template = f.read()

        # Stats
        stats_str = f"""
        Number of images: {stats['num_img']} <br/>
        Processed successfully: {stats['num_sig']} <br/>
        Failed to process: {stats['num_img'] - stats['num_sig']} <br/>
        Unique images: {stats['num_unique']} <br/>
        Duplicated images: {stats['num_dups']} <br/>
        Generated on {time.asctime()}
        """

        # Generate HTML table
        table = "<table>\n"
        table += f"<tr class='space'><td colspan={max_columns}>{stats_str}</td></tr>\n"
        n = 0
        for info in img_infos:
            table += f"<tr class='space'><td colspan={max_columns}>&nbsp;</td></tr>\n"
            table += "<tr class='title'>\n"
            n += 1
            table += f"  <td colspan={max_columns}>{n} - {info['basename']}</td>\n"
            table += "</tr>\n"
            sig = name_to_sig.get(info["basename"], "Failed to process")
            sig_count = sig_counts.get(sig, 0)
            sig_class = "dup" if sig_count > 1 else (
                "err" if sig_count == 0 else "ok")
            sig_info = "(unique)" if sig_count == 1 else (
                f"(duplicate: {sig_count})" if sig_count > 1 else "")
            table += f"<tr class='sig {sig_class}'>\n"
            table += f"  <td colspan={max_columns}>{sig} {sig_info}</td>\n"
            table += "</tr>\n"

            table += "<tr class='images'>\n"
            table += f"  <td><img src='{info['src']}'></td>\n"
            for alt in info["alt"]:
                table += f"  <td><img src='{alt}'></td>\n"
            table += "</tr>\n"
        table += "</table>\n"

        html = template.replace(TABLE_PLACEHOLDER, table)
        index_path = os.path.join(output_dir, "index.html")
        with open(index_path, "w") as f:
            f.write(html)
        print(f"Generated index at {index_path}")


if __name__ == "__main__":
    m = Main()
    m.parse_arguments()
    if m.args.overwrite:
        print("Will overwrite existing files")
    if m.args.input_image:
        m.process_file(m.args.input_image, m.args.output_dir)
    elif m.args.input_dir:
        inputs = m.find_files(m.args.input_dir)
        for f in inputs:
            m.process_file(f, m.args.output_dir)
        m.generate_index(m.args.output_dir)
    else:
        print("No input file (-i) or directory specified (-d).")

# ~~
