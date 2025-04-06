import re
import cairosvg

def add_red_borders(input_file, output_file):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            svg_content = file.read()

        # Find elements with #70FF00
        green_elements = re.findall(r'(<(path|text)[^>]*?style="[^"]*?(?:stroke|fill):#70ff00[^"]*?"[^>]*?>)', svg_content)

        # Change gray background to white
        final_svg_content = re.sub(r'#202124', '#70ff00', svg_content)

        # Add a red border to each element with a frame size of 6x4
        for element, tag in green_elements:
            # Check if the element matches the frame 6x4 pattern
            if re.search(r'h 300 l -300,-450 h 300|l 450,-300 v 300', element):
                # Extract position and size (example for 'rect' elements)
                x_match = re.search(r'x="([^\"]+)"', element)
                y_match = re.search(r'y="([^\"]+)"', element)
                width_match = re.search(r'width="([^\"]+)"', element)
                height_match = re.search(r'height="([^\"]+)"', element)

                x = x_match.group(1) if x_match else "0"
                y = y_match.group(1) if y_match else "0"
                width = width_match.group(1) if width_match else "6"
                height = height_match.group(1) if height_match else "4"

                # Create a red border
                red_border = f'<rect x="{x}" y="{y}" width="{width}" height="{height}" style="stroke:#ff0000; fill:none; stroke-width:1;" />'
                final_svg_content = final_svg_content.replace(element, element + red_border)

        # Save the modified SVG
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(final_svg_content)

        # Convert SVG content to PNG
        png_output_file = output_file.replace('.svg', '.png')
        cairosvg.svg2png(bytestring=final_svg_content.encode('utf-8'), write_to=png_output_file)

        print(f"Modified SVG saved as {output_file}")
        print(f"Modified PNG saved as {png_output_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    add_red_borders("Step6.svg", "Step7.svg")