# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import math

COLORS_REDS = [
    {
        "name": "Yellow",
        "rgb": (192, 192, 0),
        # "bgr": (0, 192, 192),     # old analyzer colors
        "bgr": (68, 160, 221),      # new generator colors
        "h": { "min": 10, "max": 20 },
        "s": { "min": 170, "max": 255 },
    },
    {
        "name": "Red",
        "rgb": (192, 0, 0),
        # "bgr": (0, 0, 192),       # old analyzer colors
        "bgr": (0, 0, 204),         # new generator colors
    },
    {
        "name": "Orange",
        "rgb": (200, 80, 0),
        # "bgr": (0, 80, 200),      # old analyzer colors
        "bgr": (0, 102, 238),       # new generator colors
    },
]

COLORS_BW = [
    {
        "name": "White",
        "rgb": (192, 192, 192),
        # "bgr": (192, 192, 192),   # old analyzer colors
        "bgr": (204, 221, 238),     # new generator colors
    },
    {
        "name": "Black",
        "rgb": (64, 64, 64),
        # "bgr": (64, 64, 64),      # old analyzer colors
        "bgr": (128, 128, 128),     # new generator colors
    },
]

EXPECTED_NUM_CELLS ={
    "White": 3,
    "Black": 12,
    "Orange": 9,
    "Red": 18,
    "Yellow": 12,
}

def by_name(name:str) -> dict:
    for c in COLORS_BW:
        if name == c["name"]:
            return c
    for c in COLORS_REDS:
        if name == c["name"]:
            return c
    return None

def select(h:float, s:float, v:float, l:float, a:float, b:float) -> dict:
    ab = math.degrees(math.atan2(b, a))
    return _select_table(COLORS_REDS, h, s, v, l, ab)

def _select_table(table:list, h:float, s:float, v:float, l:float, ab:float) -> dict:
    for color in table:
        if "h" in color and (h < color["h"]["min"] or h > color["h"]["max"]):
            continue
        if "s" in color and (s < color["s"]["min"] or s > color["s"]["max"]):
            continue
        if "v" in color and (v < color["v"]["min"] or v > color["v"]["max"]):
            continue
        if "l" in color and (l < color["l"]["min"] or l > color["l"]["max"]):
            continue
        if "ab" in color and (ab < color["ab"]["min"] or ab > color["ab"]["max"]):
            continue
        print(f"Color found: h={h}, s={s}, v={v}, l={l}, ab={ab} --> {color['name']}")
        return color
    print(f"Color      : h={h}, s={s}, v={v}, l={l}, ab={ab} -- NOT FOUND")
    return None

# ~~
