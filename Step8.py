import re
import os


def move_green_elements_above_gray_background(input_file, output_file):
    try:
        if not os.path.exists(input_file):
            print(f"{input_file} not found.")
            return

        with open(input_file, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Find all path elements with green stroke
        green_pattern = re.compile(r'<path[^>]+style="[^"]*fill:none;stroke:#70ff00[^"]*"[^>]*>')
        green_paths = green_pattern.findall(svg_text)

        # Remove green paths from their current position
        for path in green_paths:
            svg_text = svg_text.replace(path, '')

        # Find the position after the gray background
        gray_background_end = svg_text.find('</g>')
        if gray_background_end == -1:
            gray_background_end = svg_text.find('</svg>')

        # Insert green paths just after the gray background
        for path in green_paths:
            svg_text = svg_text[:gray_background_end] + path + '\n' + svg_text[gray_background_end:]

        # Write modified content
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(svg_text)

        print(f"Modified SVG saved as {output_file}")

    except Exception as e:
        print(f"Error processing SVG: {e}")


if __name__ == "__main__":
    input_file = "Step6.svg"
    output_file = "Step8.svg"
    move_green_elements_above_gray_background(input_file, output_file) 