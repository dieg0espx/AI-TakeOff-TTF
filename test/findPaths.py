import os
from lxml import etree

# List of target path IDs
paths = [
    'path3900', 'path3910', 'path3920', 'path3930', 'path4514', 'path4516', 'path6792', 'path6782',
    'path6802', 'path6842', 'path6844', 'path7336', 'path7338', 'path7352', 'path7654', 'path7664',
    'path7674', 'path7692', 'path7850', 'path7852', 'path7914', 'path7924', 'path7934', 'path7944',
    'path8414', 'path8458', 'path8460', 'path9776'
]

def find_matching_paths(svg_path):
    if not os.path.exists(svg_path):
        print("Error: File not found!")
        return

    print(f"Analyzing SVG file: {svg_path}")

    # Parse SVG
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()

    # Find all <path> elements
    for path in root.xpath("//*[local-name()='path']"):
        path_id = path.get("id")
        d_attr = path.get("d").split("h")[1]

        if path_id in paths and d_attr:
            print(f"{path_id} - {d_attr}")

if __name__ == "__main__":
    svg_file = "local_file.svg"  # Change this if the file is in a different location
    find_matching_paths(svg_file)
