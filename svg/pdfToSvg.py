import os
import subprocess
import re
from lxml import etree

def convert_pdf_to_svg(pdf_path, output_svg_path):
    # Convert PDF to SVG using pdf2svg
    try:
        subprocess.run(["pdf2svg", pdf_path, output_svg_path], check=True)
        print("PDF successfully converted to SVG!")
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e}")

def clean_svg(svg_path):
    parser = etree.XMLParser(remove_blank_text=True)
    try:
        tree = etree.parse(svg_path, parser)
    except etree.XMLSyntaxError as e:
        print(f"Error parsing SVG: {e}")
        return

    root = tree.getroot()

    # Remove unnecessary namespaces and groups
    for elem in root.xpath("//*[local-name()='g']"):
        parent = elem.getparent()
        if parent is not None:
            for child in elem:
                parent.insert(parent.index(elem), child)
            parent.remove(elem)  # Remove the empty group

    # Regular expression to find float coordinates
    number_regex = re.compile(r'[-+]?\d*\.\d+|\d+')

    # Round all path coordinates to integers
    path_elements = root.xpath("//*[local-name()='path']")
    if not path_elements:
        print("No <path> elements found in the SVG.")
        return

    for path in path_elements:
        d_attr = path.get("d")
        if d_attr:
            print(f"Original d attribute: {d_attr}")  # Debug print
            # Replace decimal numbers with rounded integers
            rounded_d = number_regex.sub(lambda x: str(int(round(float(x.group())))), d_attr)
            path.set("d", rounded_d)
            print(f"Rounded d attribute: {rounded_d}")  # Debug print

        # Add custom styling
        path.set("style", "fill:none;stroke:#dd006e;stroke-width:6;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1")

    # Write the cleaned SVG back to file
    tree.write(svg_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    print("SVG cleaned and saved.")

if __name__ == "__main__":
    # File paths
    pdf_file = "input.pdf"  # Replace with your PDF file path
    output_svg = "output.svg"  # Replace with your desired output file name

    # Convert and clean
    convert_pdf_to_svg(pdf_file, output_svg)
    clean_svg(output_svg)
