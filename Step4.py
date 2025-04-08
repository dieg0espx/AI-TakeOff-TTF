import re
import os
import json
from colorama import init, Fore, Style
from PatternComponents import shores_box, frames_6x4, frames_5x4, frames_inBox, shores

def print_table(box_count, shores_count, frames6x4_count, frames5x4_count, framesinbox_count):
    # Initialize colorama
    init()
    
    # Define colors for each category
    colors = {
        'Shores Box': Fore.RED,
        'Shores': Fore.BLUE,
        'Frames 6x4': Fore.GREEN,
        'Frames 5x4': Fore.MAGENTA,
        'Frames In Box': Fore.YELLOW
    }
    
    # Table dimensions
    width = 45
    print(f"\n{Fore.CYAN}{'='*width}")
    print(f"{' DETECTED ELEMENTS ':=^{width}}")
    print(f"{'='*width}{Style.RESET_ALL}")
    
    # Column headers
    print(f"{'Category':<30} {'':^8} {'Count':>6}")
    print(f"{'-'*width}")
    
    # Table rows with colored bullets
    elements = [
        ('Shores Box', box_count),
        ('Shores', shores_count),
        ('Frames 6x4', frames6x4_count),
        ('Frames 5x4', frames5x4_count),
        ('Frames In Box', framesinbox_count)
    ]
    
    for category, count in elements:
        color = colors[category]
        print(
            f"{category:<30} "
            f"{color}●{Style.RESET_ALL} "
            f"{count:>6}"
        )
    
    print(f"{'-'*width}")
    total = sum([box_count, shores_count, frames6x4_count, frames5x4_count, framesinbox_count])
    print(f"{'Total elements':<30} {'':^8} {total:>6}\n")

def append_counts_to_json(box_count, shores_count, frames6x4_count, frames5x4_count, framesinbox_count):
    # Load existing data from data.json
    if os.path.exists('data.json'):
        with open('data.json', 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Append counts to the data
    data['objects'] = {
        'shores_Box': box_count,
        'shores': shores_count,
        'frames_6x4': frames6x4_count,
        'frames_5x4': frames5x4_count,
        'frames_In_Box': framesinbox_count
    }

    # Write updated data back to data.json
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

def apply_color_to_specific_paths(input_file, output_file, red="#fb0505", blue="#0000ff", green="#70ff00", pink="#ff00cd", orange="#fb7905"):
    """
    Reads an SVG file and changes colors of specific paths:
    - shores_box paths to red
    - shores paths to blue
    - frames_6x4 paths to green
    - frames_5x4 paths to pink
    - frames_inBox paths to orange
    """
    try:
        if not os.path.exists(input_file):
            print(f"{input_file} not found.")
            return

        with open(input_file, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Create regex patterns
        pattern_red = "|".join(re.escape(variation) for variation in shores_box)
        shores_box_pattern = re.compile(rf'<path[^>]+d="[^"]*({pattern_red})[^"]*"[^>]*>')
        
        frames6x4_pattern = re.compile(rf'<path[^>]+d="[^"]*({"|".join(re.escape(variation) for variation in frames_6x4)})[^"]*"[^>]*>')
        frames5x4_pattern = re.compile(rf'<path[^>]+d="[^"]*({"|".join(re.escape(variation) for variation in frames_5x4)})[^"]*"[^>]*>')
        framesinBox_pattern = re.compile(rf'<path[^>]+d="[^"]*({"|".join(re.escape(variation) for variation in frames_inBox)})[^"]*"[^>]*>')

        # Count matching paths
        match_count_box = len(shores_box_pattern.findall(svg_text))
        match_count_33_34 = len(shores.findall(svg_text))
        match_count_frames6x4 = len(frames6x4_pattern.findall(svg_text))
        match_count_frames5x4 = len(frames5x4_pattern.findall(svg_text))
        match_count_framesinBox = len(framesinBox_pattern.findall(svg_text))

        # Print table with counts
        print_table(
            match_count_box,
            match_count_33_34,
            match_count_frames6x4,
            match_count_frames5x4,
            match_count_framesinBox
        )

        # Append counts to JSON file
        append_counts_to_json(
            match_count_box,
            match_count_33_34,
            match_count_frames6x4,
            match_count_frames5x4,
            match_count_framesinBox
        )

        # Color change functions
        def change_to_red(match):
            path_tag = match.group(0)
            if "stroke" in path_tag:
                path_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{red}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path stroke='{red}'", 1)
            if "fill" in path_tag:
                path_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{red}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path fill='{red}'", 1)
            # Change colors inside style attributes
            path_tag = re.sub(r'style="[^"]*"', lambda m: re.sub(r'#[0-9a-fA-F]{6}', red, m.group(0)), path_tag)
            return path_tag

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

        def change_to_orange(match):
            path_tag = match.group(0)
            if "stroke" in path_tag:
                path_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{orange}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path stroke='{orange}'", 1)
            if "fill" in path_tag:
                path_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{orange}', path_tag)
            else:
                path_tag = path_tag.replace("<path", f"<path fill='{orange}'", 1)
            return path_tag

        # Apply colors
        modified_svg_text = shores_box_pattern.sub(change_to_red, svg_text)
        modified_svg_text = shores.sub(change_to_blue, modified_svg_text)
        modified_svg_text = frames6x4_pattern.sub(change_to_green, modified_svg_text)
        modified_svg_text = frames5x4_pattern.sub(change_to_pink, modified_svg_text)
        modified_svg_text = framesinBox_pattern.sub(change_to_orange, modified_svg_text)

        # Write modified content
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)

    except Exception as e:
        print(f"Error applying colors: {e}")

# Main execution
if __name__ == "__main__":
    try:
        input_svg = "Step3.svg"
        output_svg = "Step4.svg"
        
        if not os.path.exists(input_svg):
            print(f"Error: Input file '{input_svg}' not found!")
            print(f"Current working directory: {os.getcwd()}")
        else:
            apply_color_to_specific_paths(input_svg, output_svg)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")