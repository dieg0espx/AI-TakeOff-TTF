import os
from lxml import etree

def count_specific_paths(svg_path):
    print(f"Analyzing SVG for scaffolding patterns: {svg_path}")
    
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()

    frames6x4_patterns = [
        "h 300 l -300,-450 h 300",
        "l 450,-300 v 300"
    ]

    shores_style = 'fill:none;stroke:#000000;stroke-width:17;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1'
    
    shores_33 = [
        "33,-33", "-33,33",  # Standard diagonal movements
        "33,33", "-33,-33",  # Both positive or negative
        "-33,-33", "33,33",  # Mirrored versions

        # Swapped positions
        "-33,33", "33,-33",
        "33,-33", "-33,33",
        "33,33", "-33,-33",

        # Additional alternations
        "-33,33", "33,-33",
        "33,33", "-33,-33",
        "-33,-33", "33,33"
    ]


    shores_box = [
        # Original variations
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


    counts = {"frames6x4": 0, "shores": 0, "shores_box": 0, "shores_33": 0}

    for path in root.xpath("//*[local-name()='path']"):
        d_attr = path.get("d")
        style_attr = path.get("style")

        if d_attr:
            for pattern in frames6x4_patterns:
                if pattern in d_attr:
                    counts["frames6x4"] += 1
                    break
            for pattern in shores_box:
                if pattern in d_attr:
                    counts["shores_box"] += 1
                    break
                for pattern in shores_33:
                    if pattern in d_attr:
                        counts["shores_33"] += 1
                        break
        
        if style_attr and style_attr == shores_style:
            counts["shores"] += 1

    print("\n=== Shape Count Results ===")
    print(f"Scaffold 6x4: {counts['frames6x4']}")
    print(f"Shores: {counts['shores'] / 6}")
    print(f"Shores Box: {counts['shores_box']}")
    print(f"Shores 33: {counts['shores_33']}")

    return counts

if __name__ == "__main__":
    svg_file = "local_file.svg"  # Change this to the path of your SVG file
    if os.path.exists(svg_file):
        count_specific_paths(svg_file)
    else:
        print("Error: File not found!")
