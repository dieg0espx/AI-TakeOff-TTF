import re
import os
from PatternComponents import shores_box, shores, frames_6x4, frames_5x4, frames_inBox  # Import patterns

input_svg_path = "local_file.svg"  # Input file
output_svg_path = "modified_image2.svg"  # Output file after modifications

def modify_svg_stroke_and_fill(input_file, output_file, black_stroke="#000000", white_stroke="#202020", new_stroke="#202020", fill_color="#202020"):
    """
    Reads an SVG file, first removes elements with stroke or fill #FFDF7F, then modifies other strokes and fills.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Step 1: Remove elements with #FFDF7F
        # svg_text = remove_ffdf7f_elements(svg_text)

        # Step 2: Modify stroke colors
        modified_svg_text = re.sub(r'stroke:(#[0-9a-fA-F]{6})', 
            lambda m: f"stroke:{new_stroke}" if m.group(1) == black_stroke else f"stroke:{white_stroke}", 
                svg_text)

        # Step 3: Modify fill colors
        modified_svg_text = re.sub(r'fill:(#[0-9a-fA-F]{6})', f"fill:{fill_color}", modified_svg_text)

        # Step 4: Modify text color instead of removing it
        modified_svg_text = re.sub(r'(<text[^>]*style="[^"]*)fill:[#0-9a-fA-F]+', rf'\1fill:{new_stroke}', modified_svg_text)
        modified_svg_text = re.sub(r'(<text[^>]*style="[^"]*)stroke:[#0-9a-fA-F]+', rf'\1stroke:{new_stroke}', modified_svg_text)

        # If a <text> tag doesn't have a style attribute, add fill and stroke
        modified_svg_text = re.sub(r'(<text(?![^>]*style=)[^>]*)>', rf'\1 style="fill:{new_stroke}; stroke:{new_stroke}">', modified_svg_text)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)

        print(f"SVG modified successfully and saved to {output_file}")
    except Exception as e:
        print(f"Error modifying SVG: {e}")


def apply_color_to_specific_paths(output_file, red="#05fbce", blue="#0000ff", green="#70ff00", pink="#ff00cd", pruple="#fb7905"):
    """
    Reads an SVG file and changes:
    - `shores_box` paths to red (#FF0000)
    - `shores` paths to blue (#0000FF)
    - `frames_6x4` paths to green (#5DFF00)
    """
    try:
        if not os.path.exists(output_file):
            print(f"{output_file} not found. Running `modify_svg_stroke_and_fill` first.")
            modify_svg_stroke_and_fill(input_svg_path, output_svg_path)

        with open(output_file, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Create regex pattern dynamically for shores_box (RED)
        pattern_red = "|".join(re.escape(variation) for variation in shores_box)
        shores_box_pattern = re.compile(rf'<path[^>]+d="[^"]*({pattern_red})[^"]*"[^>]*>')

        # Compile regex pattern for frames6x4
        frames6x4_pattern = re.compile(rf'<path[^>]+d="[^"]*({"|".join(re.escape(variation) for variation in frames_6x4)})[^"]*"[^>]*>')
        frames5x4_pattern = re.compile(rf'<path[^>]+d="[^"]*({"|".join(re.escape(variation) for variation in frames_5x4)})[^"]*"[^>]*>')

        framesinBox_pattern = re.compile(rf'<path[^>]+d="[^"]*({"|".join(re.escape(variation) for variation in frames_inBox)})[^"]*"[^>]*>')

        # Count matching paths
        match_count_box = len(shores_box_pattern.findall(svg_text))
        match_count_33_34 = len(shores.findall(svg_text))
        match_count_frames6x4 = len(frames6x4_pattern.findall(svg_text))
        match_count_frames5x4 = len(frames5x4_pattern.findall(svg_text))
        match_count_framesinBox = len(framesinBox_pattern.findall(svg_text))
        print(f"Number of paths matching shores_box (RED): {match_count_box}")
        print(f"Number of paths matching shores (BLUE): {match_count_33_34}")
        print(f"Number of paths matching Framex6x4 (GREEN): {match_count_frames6x4}")
        print(f"Number of paths matching Framex5x4 (LIGHT_GREEN): {match_count_frames5x4}")
        print(f"Number of paths matching FramesInBox (PURPLE): {match_count_framesinBox}")

        def find_yellow_elements(svg_content):
            """Returns a set of all path tags containing stroke or fill with #ffdf7f"""
            yellow_elements = set()
            yellow_pattern = re.compile(r'<path[^>]*(stroke|fill):#ffdf7f[^>]*>', re.IGNORECASE)
            
            for match in yellow_pattern.finditer(svg_content):
                yellow_elements.add(match.group(0))  # Store the full <path> tag
            
            return yellow_elements

        # Function to change stroke and fill to red for shores_box
        def change_to_red(match):
            path_tag = match.group(0)
        
            # Change stroke color
            if "stroke" in path_tag:
                path_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{red}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path stroke='{red}'", 1)
        
            # Change fill color
            if "fill" in path_tag:
                path_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{red}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path fill='{red}'", 1)
        
            # Change colors inside style attributes
            path_tag = re.sub(r'style="[^"]*"', lambda m: re.sub(r'#[0-9a-fA-F]{6}', red, m.group(0)), path_tag)
        
            return path_tag


        # Function to change stroke and fill to blue for shores
        def change_to_blue(match):
            path_tag = match.group(0)
            if "stroke" in path_tag:
                path_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{blue}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path stroke='{blue}'", 1)

            if "fill" in path_tag:
                path_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{blue}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path fill='{blue}'", 1)

            return path_tag
        
        # Function to change stroke and fill to green for frames6x4
        def change_to_green(match):
            path_tag = match.group(0)
            if "stroke" in path_tag:
                path_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{green}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path stroke='{green}'", 1)

            if "fill" in path_tag:
                path_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{green}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path fill='{green}'", 1)

            return path_tag
        
        # Function to change stroke and fill to light green for frames6x4
        def change_to_pink(match):
            path_tag = match.group(0)
            if "stroke" in path_tag:
                path_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{pink}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path stroke='{pink}'", 1)

            if "fill" in path_tag:
                path_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{pink}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path fill='{pink}'", 1)

            return path_tag
        
        # Function to change stroke and fill to light green for frames6x4
        def change_to_purple(match):
            path_tag = match.group(0)
            if "stroke" in path_tag:
                path_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{pruple}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path stroke='{pruple}'", 1)

            if "fill" in path_tag:
                path_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{pruple}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path fill='{pruple}'", 1)

            return path_tag

        # Apply colors
        modified_svg_text = shores_box_pattern.sub(change_to_red, svg_text)
        modified_svg_text = shores.sub(change_to_blue, modified_svg_text)
        modified_svg_text = frames6x4_pattern.sub(change_to_green, modified_svg_text)
        modified_svg_text = frames5x4_pattern.sub(change_to_pink, modified_svg_text)
        modified_svg_text = framesinBox_pattern.sub(change_to_purple, modified_svg_text)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)

        print(f"Color modifications applied successfully: RED (shores_box), BLUE (shores), GREEN (frames_6x4), LIGHTGREEN (frames_5x4) to {output_file}")

    except Exception as e:
        print(f"Error modifying stroke and fill: {e}")

modify_svg_stroke_and_fill(input_svg_path, output_svg_path)  # Step 1: Modify SVG
apply_color_to_specific_paths(output_svg_path)  # Step 2: Apply colors
