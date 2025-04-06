import re
import os

def add_background_to_svg(input_file, output_file, background_color):
    """
    Adds a background color to the SVG by inserting a <rect> element.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Insert a <rect> element after the opening <svg> tag
        svg_text = re.sub(
            r'(<svg[^>]*>)',
            rf'\1<rect width="100%" height="100%" fill="{background_color}" />',
            svg_text,
            count=1
        )

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(svg_text)

    except Exception as e:
        print(f"Error adding background to SVG: {e}")

# Main execution
if __name__ == "__main__":
    try:
        input_svg = "Step2.svg"
        output_svg = "Step3.svg"
        background_color = "#202124"  # Gray background
        
        if not os.path.exists(input_svg):
            print(f"Error: Input file '{input_svg}' not found!")
            print(f"Current working directory: {os.getcwd()}")
        else:
            add_background_to_svg(input_svg, output_svg, background_color)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")