import re
import os
from cairosvg import svg2png

def filter_svg(input_file, output_file):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            svg_content = file.read()

        # Replace elements with specified colors with transparent style
        def make_transparent(match):
            element_tag = match.group(0)
            # Check if any of the specified colors are present
            if re.search(r'(?:stroke|fill):(?:#fb0505|#0000ff|#ff00cd|#fb7905)', element_tag):
                element_tag = re.sub(r'style="[^"]*"', 'style="fill:none;stroke:none"', element_tag)
            return element_tag

        # Apply transparency to elements with specified colors
        filtered_svg_content = re.sub(r'<(path|text)[^>]*?style="[^"]*?"[^>]*?>', make_transparent, svg_content)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(filtered_svg_content)

        print(f"Filtered SVG saved as {output_file}")

        # Convert the filtered SVG to PNG
        with open(output_file, 'rb') as svg_file:
            svg_content = svg_file.read()
        
        # Convert to PNG with high resolution
        svg2png(bytestring=svg_content, write_to='Step6.png')
        print("Successfully converted Step6.svg to Step6.png")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if not os.path.exists('Step5.svg'):
        print("Error: Step5.svg does not exist.")
    else:
        filter_svg("Step5.svg", "Step6.svg")
