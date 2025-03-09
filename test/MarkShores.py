import re

input_svg_path = "local_file2.svg"  # Use local_file2.svg as the new input file
output_svg_path = "modified_image2.svg"  # Output file after modifications

def modify_svg_stroke_and_fill(input_file, output_file, black_stroke="#000000", white_stroke="#ffffff", new_stroke="#e5e4e4", fill_color="#ffffff"):
    """
    Reads an SVG file, replaces the specified stroke color, changes all fill attributes to white, converts non-black strokes to white,
    and removes all text and numbers.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            svg_text = file.read()
        
        # Apply stroke color modifications
        modified_svg_text = re.sub(r'stroke:(#[0-9a-fA-F]{6})', 
            lambda m: f"stroke:{new_stroke}" if m.group(1) == black_stroke else f"stroke:{white_stroke}", 
                svg_text)
        
        # Apply fill color modifications
        modified_svg_text = re.sub(r'fill:(#[0-9a-fA-F]{6})', f"fill:{fill_color}", modified_svg_text)
        
        # Remove all text and numbers
        modified_svg_text = re.sub(r'<text[^>]*>.*?</text>', '', modified_svg_text, flags=re.DOTALL)
        
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)
        
        print(f"SVG modified successfully and saved to {output_file}")
    except Exception as e:
        print(f"Error modifying SVG: {e}")

def apply_blue_to_specific_paths(output_file, blue_stroke="#0000ff", blue_fill="#0000ff"):
    """
    Reads an SVG file and changes paths with specific 'd' attributes that match the shores_33_34_pattern to blue.
    """
    try:
        with open(output_file, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Regular expression pattern for detecting paths matching the shores_33_34_pattern
        shores_33_34_pattern = re.compile(
            r'<path[^>]+d="[^"]*m\s*(-?\d+),(-?\d+)\s+('
            r'-?(33|34),-?(33|34)|'
            r'-?(33|34),(33|34)|'
            r'(33|34),-?(33|34)|'
            r'(33|34),(33|34))[^"]*"[^>]*>'
        )

        # Count how many paths match the pattern
        match_count = len(shores_33_34_pattern.findall(svg_text))
        print(f"Number of paths matching shores_33_34_pattern: {match_count}")

        # Function to change stroke and fill to blue
        def change_to_blue(match):
            path_tag = match.group(0)
            if "stroke" in path_tag:
                path_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{blue_stroke}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path stroke='{blue_stroke}'", 1)

            if "fill" in path_tag:
                path_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{blue_fill}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path fill='{blue_fill}'", 1)

            return path_tag

        # Apply modifications
        modified_svg_text = shores_33_34_pattern.sub(change_to_blue, svg_text)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)

        print(f"Blue color modifications applied successfully to {output_file}")

    except Exception as e:
        print(f"Error modifying blue stroke and fill: {e}")

# Execute both functions in sequence
modify_svg_stroke_and_fill(input_svg_path, output_svg_path)  # Step 1: Modify SVG
apply_blue_to_specific_paths(output_svg_path)  # Step 2: Apply blue color changes
