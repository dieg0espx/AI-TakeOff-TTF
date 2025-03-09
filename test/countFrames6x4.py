import os
from lxml import etree

# Namespace required for XML parsing in SVG
SVG_NAMESPACE = {"svg": "http://www.w3.org/2000/svg"}

def count_matching_shapes(svg_path):
    if not os.path.exists(svg_path):
        print("Error: File not found!")
        return 0

    print(f"Analyzing SVG file: {svg_path}")

    # Parse SVG file with proper namespace handling
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()

    # Ensure we are working with the main <svg> tag
    svg_tag = root if root.tag.endswith("svg") else root.find(".//svg:svg", SVG_NAMESPACE)

    if svg_tag is None:
        print("Error: Could not find <svg> root element.")
        return 0

    # ** Step 1: Define shape variants to count **
    shape_variants = [
        ' h 300 l -300,-450 h 300',
        'v 300 l 450,-300 v 300',
    ]

    total_count = 0

    # ** Step 2: Count paths that match shape variants **
    for path in svg_tag.findall(".//svg:path", SVG_NAMESPACE):
        d_attr = path.get("d", "").replace("\n", "").strip()
        if any(variant in d_attr for variant in shape_variants):
            total_count += 1

    print(f"\n=== Total Matching Shapes Found: {total_count} ===")
    return total_count

if __name__ == "__main__":
    svg_file = "local_file.svg"  # Change this to your actual file path
    count_matching_shapes(svg_file)
