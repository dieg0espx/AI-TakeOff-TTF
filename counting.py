from lxml import etree

def count_specific_paths(svg_path):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()

    # Define patterns to look for
    frames6x4_patterns = ["h 300 l -300,-450 h 300", "l 450,-300 v 300"]
    shores_style = 'fill:none;stroke:#000000;stroke-width:17;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1'

    counts = {
        "frames6x4": 0,
        "shores": 0  # Initialize a single counter for shores
    }

    # Iterate through all <path> elements
    for path in root.xpath("//*[local-name()='path']"):
        d_attr = path.get("d")
        style_attr = path.get("style")
        
        if d_attr:
            # Count frames6x4 occurrences for each pattern
            for pattern in frames6x4_patterns:
                if pattern in d_attr:
                    counts["frames6x4"] += 1
                    break  # Avoid counting the same path multiple times for different patterns

        # Count shores occurrences based on style
        if style_attr and style_attr == shores_style:
            counts["shores"] += 1

    return counts

if __name__ == "__main__":
    svg_file = "output.svg"  # Replace with your SVG file path
    counts = count_specific_paths(svg_file)
    
    print(f"FRAMES 6x4: {counts['frames6x4']}")
    print(f"SHORES: {counts['shores'] / 6}")
