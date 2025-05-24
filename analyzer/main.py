# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import argparse
import glob
import json
import os
import time
import sys

from gen import Generator
from img_proc import ImageProcessor
from pieces_stats import PiecesStats

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
        parser.add_argument("-g", "--generate",
            action="store_true",
            help="Action: Generate all possible solutions")
        parser.add_argument("--gen-output",
            default="render_IDX_CORES.txt",
            help="Generator output name in output dir")
        parser.add_argument("--gen-cores",
            type=int,
            default=1,
            help="Generator number of cores")
        parser.add_argument("--gen-index",
            type=int,
            default=1,
            help="Generator core index from 0 to gen-cores-1")
        parser.add_argument("--gen-start",
            type=int,
            default=1,
            help="Generator start permutation index")
        parser.add_argument("-p", "--pieces",
            action="store_true",
            help="Action: Compute pieces statistics")
        parser.add_argument("--pieces-solutions",
            default="data/generator.txt",
            required=False,
            help="Input solutions txt for pieces generation")
        self.args = parser.parse_args()

    def analyze_file(self, input_file_path:str, outout_dir_path:str) -> None:
        p = ImageProcessor(input_file_path, outout_dir_path)
        p.process_image(m.args.overwrite)

    def generate_solutions(self, outout_dir_path:str, gen_output_name:str) -> None:
        g = Generator(outout_dir_path)
        if m.args.gen_cores > 1:
            if m.args.gen_index < 0 or m.args.gen_index >= m.args.gen_cores:
                print(f"Error: --gen-index must be in range 0..{m.args.gen_cores-1}")
                sys.exit(1)
        g.generate(gen_output_name, m.args.overwrite, m.args.gen_cores, m.args.gen_index, m.args.gen_start)
        return g

    def generate_pieces(self, outout_dir_path:str, output_prefix:str, solutions_file:str) -> None:
        g = PiecesStats(outout_dir_path, output_prefix)
        g.generate(solutions_file)
        return g

    def find_files(self, dir_input:str) -> list:
        """Finds all files in the given directory."""
        if not os.path.exists(dir_input):
            raise FileNotFoundError(f"Directory {dir_input} does not exist.")
        return glob.glob(os.path.join(dir_input, "**", "*.jpg"), recursive=True)

    def write_generator_index(self, output_dir:str, gen:Generator) -> None:
        # Images
        images = gen.generated_images
        stats_str = f"""
        Number of images: {len(images)} <br/>
        """

        content = ""
        for img_name in images:
            anchor = img_name.replace("gen_", "").replace(".jpg", "")
            content += f"<table class='gen'><tr><td id='{anchor}'><a href='#{anchor}'>{anchor}</a><br/><img src='{img_name}'></td></tr></table>"

        # Read template
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(script_dir, "gen_template.html")
        with open(template_path, "r") as f:
            template = f.read()

        html = template.replace("CONTENT", content)
        html = html.replace("TIMESTAMP", time.asctime())
        html = html.replace("STATS", stats_str)
        index_path = os.path.join(output_dir, "gen.html")
        with open(index_path, "w") as f:
            f.write(html)
        print(f"Generated index at {index_path}")
        print(stats_str.replace("<br/>", ""))

    def write_analyzer_index(self, output_dir:str) -> None:
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
            for alt in glob.glob(os.path.join(output_dir, basename + "_[0-9][0-9]_*.jpg"), recursive=False):
                info["alt"].append(os.path.basename(alt))
            max_columns = max(max_columns, 1 + len(info["alt"]))

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
        Duplicated images: {stats['num_dups']}
        """
        stats_dict = {
            "num_img": stats["num_img"],
            "num_sig": stats["num_sig"],
            "num_unique": stats["num_unique"],
            "num_dups": stats["num_dups"]
        }

        # Generate HTML table
        rows = ""
        found_json = []
        n = 0
        for info in img_infos:
            rows += f"<tr class='space'><td colspan={max_columns}>&nbsp;</td></tr>\n"
            rows += "<tr class='title'>\n"
            n += 1
            name = info["basename"]
            rows += f"  <td colspan={max_columns} id='{name}'><a href='#{name}'>{n} - {name}</a></td>\n"
            rows += "</tr>\n"
            sig = name_to_sig.get(info["basename"], "Failed to process")
            sig_count = sig_counts.get(sig, 0)
            sig_class = "dup" if sig_count > 1 else (
                "err" if sig_count == 0 else "ok")
            sig_info = "(unique)" if sig_count == 1 else (
                f"(duplicate: {sig_count})" if sig_count > 1 else "")
            rows += f"<tr class='sig {sig_class}'>\n"
            rows += f"  <td colspan={max_columns}>{sig} {sig_info}</td>\n"
            rows += "</tr>\n"
            found_json.append( {
                "href": name,
                "index": n,
                "sig": sig,
                "state": sig_class,
                "src": info["src"],
                "alt": info["alt"]
            } )

            rows += "<tr class='images'>\n"
            rows += f"  <td><img src='{info['src']}'></td>\n"
            for alt in info["alt"]:
                rows += f"  <td><img src='{alt}'></td>\n"
            rows += "</tr>\n"

        html = template.replace("TABLE_ROWS", rows)
        html = html.replace("TIMESTAMP", time.asctime())
        html = html.replace("NUM_COLS", str(max_columns))
        html = html.replace("STATS", stats_str)
        index_path = os.path.join(output_dir, "index.html")
        with open(index_path, "w") as f:
            f.write(html)
        print(f"Generated index at {index_path}")
        print(stats_str.replace("<br/>", ""))

        found_path = os.path.join(output_dir, "analyzer.json")
        with open(found_path, "w") as f:
            f.write(json.dumps({
                "images": found_json,
                "timestamp": time.asctime(),
                "stats": stats_dict
            }, indent=2))
        print(f"Generated JSON at {found_path}")



if __name__ == "__main__":
    m = Main()
    m.parse_arguments()
    if m.args.overwrite:
        print("Will overwrite existing files")
    if m.args.pieces:
        g = m.generate_pieces(m.args.output_dir, "pieces", m.args.pieces_solutions)
    elif m.args.generate:
        g = m.generate_solutions(m.args.output_dir, m.args.gen_output)
        m.write_generator_index(m.args.output_dir, g)
    elif m.args.input_image:
        m.analyze_file(m.args.input_image, m.args.output_dir)
    elif m.args.input_dir:
        inputs = m.find_files(m.args.input_dir)
        for f in inputs:
            m.analyze_file(f, m.args.output_dir)
        m.write_analyzer_index(m.args.output_dir)
    else:
        print("No input file (-i) or directory specified (-d).")

# ~~
