import re
import os
import json
from colorama import init, Fore, Style
from PatternComponents import shores_box, frames_6x4, frames_5x4, frames_inBox, shores
from cairosvg import svg2png
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

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
        
        # Modified frames5x4 pattern including detection of diagonal segments
        frames5x4_base_pattern = "|".join(re.escape(variation) for variation in frames_5x4)
        # Generic diagonal pattern allowing leg lengths from 294-301px (covers 294-299/300/301)
        frames5x4_generic = r'h\s+(?:29[4-9]|30[0-1])\s+l\s+-?(?:29[4-9]|30[0-1]),-?(?:29[4-9]|30[0-1])'
        frames5x4_pattern = re.compile(
            rf'<path[^>]+d="[^"]*(?:({frames5x4_base_pattern})|({frames5x4_generic}))[^"]*"[^>]*>',
            re.IGNORECASE)
        
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

        def change_adjacent_paths_to_pink(svg_text):
            """Color up to 8 adjacent h/v segments whose absolute length is 294-301 px, for every frames5x4 diagonal path."""

            
            # Detect frames 5x4 paths (diagonal corners of frames)
            frames5x4_paths = []
            for match in frames5x4_pattern.finditer(svg_text):
                path_tag = match.group(0)
                d_attr_match = re.search(r'd="([^"]+)"', path_tag)
                if not d_attr_match:
                    continue
                d_str = d_attr_match.group(1)

                # Start coordinate after 'm'
                m_match = re.search(r'm\s+([\-\d\.]+),([\-\d\.]+)', d_str, re.IGNORECASE)
                if not m_match:
                    continue
                try:
                    start_x = int(float(m_match.group(1)))
                    start_y = int(float(m_match.group(2)))
                except ValueError:
                    continue

                # Attempt to capture first h and l moves to estimate diagonal end-points
                h_match = re.search(r'h\s+([\-\d\.]+)', d_str, re.IGNORECASE)
                l_match = re.search(r'l\s+([\-\d\.]+),([\-\d\.]+)', d_str, re.IGNORECASE)

                anchors = {(start_x, start_y)}
                if h_match:
                    try:
                        h_len = int(float(h_match.group(1)))
                        anchors.add((start_x + h_len, start_y))
                    except ValueError:
                        pass
                if h_match and l_match:
                    try:
                        l_dx = int(float(l_match.group(1)))
                        l_dy = int(float(l_match.group(2)))
                        diag_end_x = start_x + int(float(h_match.group(1))) + l_dx
                        diag_end_y = start_y + l_dy
                        anchors.add((diag_end_x, diag_end_y))
                    except ValueError:
                        pass

                print(f"[DIAG ] id={re.search(r'id=\"([^\"]+)\"', path_tag).group(1)}, anchors={anchors}")

                frames5x4_paths.append((path_tag, anchors))

            # Detect horizontal and vertical segments of length 294-301 px (positive or negative)
            hv_pattern = re.compile(r'<path[^>]+d="[^"]*([hHvV])\s+(-?(?:29[4-9]|30[0-1]))\b[^\"]*"[^>]*>', re.IGNORECASE)
            hv_paths = []  # (tag, start_x, start_y, orientation, length)
            for match in hv_pattern.finditer(svg_text):
                path_tag = match.group(0)
                orient = match.group(1).lower()  # normalize to 'h' or 'v'
                length = int(match.group(2))
                coords_match = re.search(r'd="[^"]*m\s+([\-\d\.]+),([\-\d\.]+)', path_tag)
                if not coords_match:
                    continue
                try:
                    start_x = int(float(coords_match.group(1)))
                    start_y = int(float(coords_match.group(2)))
                    hv_paths.append((path_tag, start_x, start_y, orient, length))
                except ValueError:
                    continue

            tol = 2  # coordinate tolerance in px

            modifications = []  # list of (original_tag, pink_tag)

            for frame_tag, anchor_points in frames5x4_paths:
                adjacent_found = 0
                for hv_tag, h_x, h_y, orient, length in hv_paths:
                    if adjacent_found >= 8:
                        break
                    if orient == 'h':
                        # endpoints of horizontal segment
                        end_x = h_x + length
                        candidates = {(h_x, h_y), (end_x, h_y)}
                        match_found = any(
                            any(abs(ax - cx) <= tol and abs(ay - cy) <= tol for (ax, ay) in anchor_points)
                            for (cx, cy) in candidates
                        )
                        if match_found:
                            # Match found
                            new_tag = hv_tag
                            if "stroke" in new_tag:
                                new_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{pink}', new_tag)
                            else:
                                new_tag = new_tag.replace("<path", f"<path stroke='{pink}'", 1)
                            if "fill" in new_tag:
                                new_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{pink}', new_tag)
                            else:
                                new_tag = new_tag.replace("<path", f"<path fill='{pink}'", 1)
                            new_id = re.search(r'id=\"([^\"]+)\"', hv_tag).group(1)
                            print(f"[NEIGH] id={new_id}  →  PINK  (diag={re.search(r'id=\"([^\"]+)\"', frame_tag).group(1)})")
                            modifications.append((hv_tag, new_tag))
                            adjacent_found += 1
                    else:  # vertical
                        end_y = h_y + length
                        candidates = {(h_x, h_y), (h_x, end_y)}
                        match_found = any(
                            any(abs(ax - cx) <= tol and abs(ay - cy) <= tol for (ax, ay) in anchor_points)
                            for (cx, cy) in candidates
                        )
                        if match_found:
                            new_tag = hv_tag
                            if "stroke" in new_tag:
                                new_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{pink}', new_tag)
                            else:
                                new_tag = new_tag.replace("<path", f"<path stroke='{pink}'", 1)
                            if "fill" in new_tag:
                                new_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{pink}', new_tag)
                            else:
                                new_tag = new_tag.replace("<path", f"<path fill='{pink}'", 1)
                            new_id = re.search(r'id=\"([^\"]+)\"', hv_tag).group(1)
                            print(f"[NEIGH] id={new_id}  →  PINK  (diag={re.search(r'id=\"([^\"]+)\"', frame_tag).group(1)})")
                            modifications.append((hv_tag, new_tag))
                            adjacent_found += 1

            # Apply modifications
            modified_text = svg_text
            for original_tag, pink_tag in modifications:
                modified_text = modified_text.replace(original_tag, pink_tag)

            return modified_text

        # Apply colors
        modified_svg_text = shores_box_pattern.sub(change_to_red, svg_text)
        modified_svg_text = shores.sub(change_to_blue, modified_svg_text)
        modified_svg_text = frames6x4_pattern.sub(change_to_green, modified_svg_text)
        modified_svg_text = frames5x4_pattern.sub(change_to_pink, modified_svg_text)
        modified_svg_text = change_adjacent_paths_to_pink(modified_svg_text)
        modified_svg_text = framesinBox_pattern.sub(change_to_orange, modified_svg_text)

        # Write modified content
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)

        # After writing the modified SVG content
        with open(output_file, 'rb') as svg_file:
            svg_content = svg_file.read()

        # Convert to PNG with high resolution
        svg2png(bytestring=svg_content, write_to='Step4.png')
        print("Successfully converted Step4.svg to Step4.png")

        # Upload PNG to Cloudinary
        response = cloudinary.uploader.upload('Step4.png', folder='AI-TakeOFF')
        cloudinary_url_modified = response['url']

        # Update data.json with the Cloudinary URL for modified_image
        if os.path.exists('data.json'):
            with open('data.json', 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        # Add the URL directly at the root level
        data['modified_drawing'] = cloudinary_url_modified

        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)

        print("data.json updated successfully with modified_image URL.")

    except Exception as e:
        print(f"Error applying colors: {e}")

# Main execution
if __name__ == "__main__":
    try:
        input_svg = "Step3.svg"
        output_svg = "Step4bis.svg"
        
        if not os.path.exists(input_svg):
            print(f"Error: Input file '{input_svg}' not found!")
            print(f"Current working directory: {os.getcwd()}")
        else:
            apply_color_to_specific_paths(input_svg, output_svg)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")