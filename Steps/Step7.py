import re

def add_red_borders(input_file, output_file):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            svg_content = file.read()

        # Find elements with #70FF00
        green_elements = re.findall(r'(<(path|text)[^>]*?style="[^"]*?(?:stroke|fill):#70ff00[^"]*?"[^>]*?>)', svg_content)

        # Prepare to add red borders
        red_borders = []

        for element, tag in green_elements:
            # Extract position and size (simplified example)
            # You might need to parse the 'd' attribute for paths or 'x', 'y' for text
            x, y, width, height = 0, 0, 100, 100  # Placeholder values

            # Create a red border rectangle
            red_border = f'<rect x="{x}" y="{y}" width="{width}" height="{height}" style="stroke:#ff0000; fill:none; stroke-width:2;" />'
            red_borders.append(red_border)

        # Add red borders to the SVG content
        red_borders_content = "\n".join(red_borders)
        final_svg_content = re.sub(r'</svg>', f'{red_borders_content}\n</svg>', svg_content)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(final_svg_content)

        print(f"Modified SVG saved as {output_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    add_red_borders("Step6.svg", "Step7.svg")