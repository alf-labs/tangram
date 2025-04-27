# Tangram Puzzle Image Analyzer
#
# (c) 2025 ralfoide at gmail

import math

COLORS = [
    {
        "name": "White",
        "rgb": (192, 192, 192),
        "bgr": (192, 192, 192),
        "h": { "min": 10, "max": 20 },
        "s": { "min": 0, "max": 128 },
        "l": { "min": 164, "max": 255 },
    },
    {
        "name": "Black",
        "rgb": (64, 64, 64),
        "bgr": (64, 64, 64),
        "s": { "min": 0, "max": 128 },
        "l": { "min": 0, "max": 170 },
    },
    # {
    #     "name": "Orange",
    #     "rgb": (192, 128, 0),
    #     "bgr": (0, 128, 192),
    #     "h": { "min": 10, "max": 15 },
    #     "s": { "min": 190, "max": 210 },
    #     "v": { "min": 190, "max": 210 },
    # },
    {
        "name": "Yellow",
        "rgb": (192, 192, 0),
        "bgr": (0, 192, 192),
        "h": { "min": 10, "max": 20 },
        "s": { "min": 170, "max": 255 },
    },
    {
        "name": "Red",
        "rgb": (192, 0, 0),
        "bgr": (0, 0, 192),
        # "h": { "min": 0, "max": 7 },
        # "ab": { "min": 0, "max": 43 },
        # "s": { "min": 128, "max": 255 },
        # "v": { "min": 0, "max": 180 },
    },
]

COLORS_BW = [
    {
        "name": "White",
        "rgb": (192, 192, 192),
        "bgr": (192, 192, 192),
        "h": { "min": 10, "max": 20 },
        "s": { "min": 0, "max": 128 },
        "l": { "min": 164, "max": 255 },
    },
    {
        "name": "Black",
        "rgb": (64, 64, 64),
        "bgr": (64, 64, 64),
        "s": { "min": 0, "max": 128 },
        "l": { "min": 0, "max": 170 },
    },
]

def select(h:float, s:float, v:float, l:float, a:float, b:float) -> dict:
    ab = math.degrees(math.atan2(b, a))
    return _select_table(COLORS, h, s, v, l, ab)

def select_bw(h:float, s:float, v:float, l:float, a:float, b:float) -> dict:
    ab = math.degrees(math.atan2(b, a))
    return _select_table(COLORS_BW, h, s, v, l, ab)

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
    return None

# ~~
