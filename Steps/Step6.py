from cairosvg import svg2png
import re

def convert_svg_to_png():
    try:
        # Read the SVG file
        with open('Step5.svg', 'rb') as svg_file:
            svg_content = svg_file.read()
        
        # Convert to PNG with high resolution
        svg2png(bytestring=svg_content,
                write_to='Step6.png',
                output_width=1920,  # Set width for good resolution
                output_height=1080)  # Set height for good resolution
        
        print("Successfully converted Step5.svg to Step6.png")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def filter_svg(input_file, output_file):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            svg_content = file.read()

        # Replace non-matching elements with transparent style
        def make_transparent(match):
            element_tag = match.group(0)
            # Only make transparent if neither #000000 nor #70FF00 is present
            if not re.search(r'(?:stroke|fill):(?:#000000|#70ff00)', element_tag):
                element_tag = re.sub(r'style="[^"]*"', 'style="fill:none;stroke:none"', element_tag)
            return element_tag

        # Apply transparency to non-matching elements
        filtered_svg_content = re.sub(r'<(path|text)[^>]*?style="[^"]*?"[^>]*?>', make_transparent, svg_content)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(filtered_svg_content)

        print(f"Filtered SVG saved as {output_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    convert_svg_to_png()
    filter_svg("Step5.svg", "Step6.svg")
