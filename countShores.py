import os
import re
from lxml import etree

def count_shores_33_34(svg_path):
    if not os.path.exists(svg_path):
        print("Error: File not found!")
        return 0, 0


    # Parse SVG file
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()

    # Define the required style for valid X patterns
    required_style = "fill:none;stroke:#000000;stroke-width:17;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"

    # Box patterns (squares)
    shores_box_patterns = [
        "h 60 v -61 h -60 v 61", "h 61 v -60 h -61 v 60",
        "h -60 v 61 h 60 v -61", "h -61 v 60 h 61 v -60",
        "h 60 v -60 h -60 v 60", "h 61 v -61 h -61 v 61",
        "h -60 v 60 h 60 v -60", "h -61 v 61 h 61 v -61",

        "h 60 v 61 h -60 v -61", "h 61 v 60 h -61 v -60",
        "h -60 v -61 h 60 v 61", "h -61 v -60 h 61 v 60",
        "h 60 v 60 h -60 v -60", "h 61 v 61 h -61 v -61",
        "h -60 v -60 h 60 v 60", "h -61 v -61 h 61 v 61",

        "h -61 v -61 h 61 v 61", "h 61 v 61 h -61 v -61",
        "h -60 v -61 h 60 v 61", "h 60 v 61 h -60 v -61",
        "h -61 v 60 h 61 v -60", "h 61 v -60 h -61 v 60",
        "h -60 v 60 h 60 v -60", "h 60 v -60 h -60 v 60",

        # Variations where `h` and `v` positions are swapped
        "v 60 h -61 v -60 h 61", "v 61 h -60 v -61 h 60",
        "v -60 h 61 v 60 h -61", "v -61 h 60 v 61 h -60",
        "v 60 h -60 v -60 h 60", "v 61 h -61 v -61 h 61",
        "v -60 h 60 v 60 h -60", "v -61 h 61 v 61 h -61",

        "v 60 h 61 v -60 h -61", "v 61 h 60 v -61 h -60",
        "v -60 h -61 v 60 h 61", "v -61 h -60 v 61 h 60",
        "v 60 h 60 v -60 h -60", "v 61 h 61 v -61 h -61",
        "v -60 h -60 v 60 h 60", "v -61 h -61 v 61 h 61",

        "v -61 h -61 v 61 h 61", "v 61 h 61 v -61 h -61",
        "v -60 h -61 v 60 h 61", "v 60 h 61 v -60 h -61",
        "v -61 h 60 v 61 h -60", "v 61 h -60 v -61 h 60",
        "v -60 h 60 v 60 h -60", "v 60 h -60 v -60 h 60"
    ]

    # X patterns (33 or 34 movements)
    shores_33_34_pattern = re.compile(
        r"m\s*(-?\d+),(-?\d+)\s+("
        r"-?(33|34),-?(33|34)|"
        r"-?(33|34),(33|34)|"
        r"(33|34),-?(33|34)|"
        r"(33|34),(33|34))"
    )

    total_crosses = 0
    total_boxes = 0

    # Detect squares
    for path in root.xpath("//*[local-name()='path']"):
        d_attr = path.get("d")

        if d_attr and any(pattern in d_attr for pattern in shores_box_patterns):
            total_boxes += 1

    # Detect X patterns
    for path in root.xpath("//*[local-name()='path']"):
        d_attr = path.get("d")
        style_attr = path.get("style")

        if d_attr and style_attr == required_style:
            match = shores_33_34_pattern.search(d_attr)
            if match:
                total_crosses += 1
    print(f" x : {int((total_crosses - total_boxes * 4) / 6)}")
    print(f"[x]: {total_boxes}")
    return total_boxes, int((total_crosses - total_boxes * 4) / 6)

if __name__ == "__main__":
    svg_file = "local_file.svg"  # Change this to the actual SVG file path
    count_shores_33_34(svg_file)
