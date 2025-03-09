def modify_svg_stroke_and_fill(input_file, output_file, black_stroke="#000000", white_stroke="#ffffff", new_stroke="#e5e4e4", fill_color="#ffffff"):
    """
    Reads an SVG file, replaces the specified stroke color, changes all fill attributes to white, converts non-black strokes to white,
    and removes all text and numbers.
    :param input_file: Path to the input SVG file.
    :param output_file: Path to the output SVG file.
    """
    import re
    
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
    Reads an SVG file and changes paths with specific 'd' attributes to blue (stroke and fill).
    :param output_file: Path to the modified SVG file.
    """
    import re
    
    try:
        with open(output_file, "r", encoding="utf-8") as file:
            svg_text = file.read()
        
        # Count how many paths match specific patterns
        pattern_matches = re.findall(r'<path[^>]+d="[^"]*(h 300 l -300,-450 h 300|l 450,-300 v 300)[^"]*"[^>]*>', svg_text)
        match_count = len(pattern_matches)
        print(f"Number of paths matching the pattern: {match_count}")
        
        # Change paths with specific 'd' attributes to blue (stroke and fill)
        def change_to_blue(match):
            path_tag = match.group(0)
            if "stroke" in path_tag:
                path_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{blue_stroke}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path stroke:{blue_stroke}", 1)
            
            if "fill" in path_tag:
                path_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{blue_fill}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path fill:{blue_fill}", 1)
            
            return path_tag
        
        modified_svg_text = re.sub(r'<path[^>]+d="[^"]*(h 300 l -300,-450 h 300|l 450,-300 v 300)[^"]*"[^>]*>', 
                                   change_to_blue, svg_text)
        
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)
        
        print(f"Blue color modifications applied successfully to {output_file}")
    except Exception as e:
        print(f"Error modifying blue stroke and fill: {e}")



# Example usage
input_svg_path = "local_file.svg"  # Change this to the actual input SVG file path
output_svg_path = "modified_image.svg"  # Change this to the desired output file path
modify_svg_stroke_and_fill(input_svg_path, output_svg_path)
apply_blue_to_specific_paths(output_svg_path)
