import re
import os
from colorama import init, Fore, Style

def update_path_color(svg_text, path_id):
    def change_color(match):
        path_tag = match.group(0)
        orange = "#fb7905"
        
        # Update stroke color
        if "stroke" in path_tag:
            path_tag = re.sub(r'stroke:[#0-9a-fA-F]+', f'stroke:{orange}', path_tag)
        else:
            path_tag = path_tag.replace("<path", f"<path stroke='{orange}'", 1)
            
        # Update fill color
        if "fill" in path_tag:
            path_tag = re.sub(r'fill:[#0-9a-fA-F]+', f'fill:{orange}', path_tag)
        else:
            path_tag = path_tag.replace("<path", f"<path fill='{orange}'", 1)
            
        return path_tag

    # Pattern to find the entire path tag with the specific ID
    pattern = f'<path[^>]*?id="{path_id}"[^>]*?>'
    return re.sub(pattern, change_color, svg_text)

def extract_coordinates(path_data):
    # Convert path data to absolute coordinates
    coords = []
    # Split the path data into commands and coordinates
    parts = re.findall(r'([mlvhMLVH]|-?\d+(?:\.\d+)?)', path_data)
    current_x = 0
    current_y = 0
    
    i = 0
    while i < len(parts):
        part = parts[i]
        if part.lower() in 'mlvh':
            command = part.lower()
            i += 1
            if command == 'm':  # Move to
                current_x = float(parts[i])
                current_y = float(parts[i + 1])
                coords.append((str(int(current_x)), str(int(current_y))))
                i += 2
            elif command == 'l':  # Line to
                current_x = float(parts[i])
                current_y = float(parts[i + 1])
                coords.append((str(int(current_x)), str(int(current_y))))
                i += 2
            elif command == 'v':  # Vertical line
                current_y = float(parts[i])
                coords.append((str(int(current_x)), str(int(current_y))))
                i += 1
            elif command == 'h':  # Horizontal line
                current_x = float(parts[i])
                coords.append((str(int(current_x)), str(int(current_y))))
                i += 1
        else:
            i += 1
            
    # Extract both full coordinates and individual x,y values
    x_coords = set(x for x, _ in coords)
    y_coords = set(y for _, y in coords)
    
    return {'full': set(coords), 'x': x_coords, 'y': y_coords}

def find_and_update_related_paths(svg_text, path_id, path_data):
    base_num = int(path_id.replace('path', ''))
    related_ids = [f"path{base_num-2}", f"path{base_num+2}"]
    
    related_paths = []
    path_coords = extract_coordinates(path_data)
    modified_svg = svg_text
    
    for related_id in related_ids:
        related_pattern = re.compile(f'<path[^>]*?id="{related_id}"[^>]*?d="([^"]*)"')
        match = related_pattern.search(svg_text)
        
        if match:
            related_path_data = match.group(1)
            related_coords = extract_coordinates(related_path_data)
            
            # Check for any matching Y coordinates
            matching_y_coords = path_coords['y'].intersection(related_coords['y'])
            if matching_y_coords:
                related_paths.append({
                    'original_id': path_id,
                    'related_id': related_id,
                    'matching_coords': matching_y_coords
                })
                # Update both the matching path and the original path to orange
                modified_svg = update_path_color(modified_svg, related_id)
                modified_svg = update_path_color(modified_svg, path_id)  # Update original path too
    
    return related_paths, modified_svg

def process_svg_file(input_file):
    try:
        init()
        
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found!")
            return

        with open(input_file, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Find paths that are already orange
        orange_pattern = r'<path[^>]*?id="(path\d+)"[^>]*?(?:stroke="#fb7905"|style="[^"]*?stroke:#fb7905)[^>]*?d="([^"]*)"'
        matches = list(re.finditer(orange_pattern, svg_text))
        modified_svg = svg_text
        
        # Print all orange paths first
        print(f"\n{Fore.YELLOW}Orange paths found:{Style.RESET_ALL}")
        for match in matches:
            print(f"path{match.group(1)}")
        print(f"\n{'-'*50}")
        
        # Store all matched pairs
        all_matched_pairs = []
        paths_to_update = set()  # Only store non-orange paths that need updating
        
        # Find matches for each orange path
        for match in matches:
            path_id = match.group(1)
            path_data = match.group(2)
            
            related_paths, _ = find_and_update_related_paths(svg_text, path_id, path_data)
            
            if related_paths:
                for related in related_paths:
                    paths_to_update.add(related['related_id'])
                    all_matched_pairs.append((related['original_id'], related['related_id']))

        # Print all matched pairs
        if all_matched_pairs:
            print(f"\n{Fore.GREEN}Matched paths:{Style.RESET_ALL}")
            for pair in sorted(all_matched_pairs):
                print(f"{pair[0]} + {pair[1]}")
                
            print("\nUpdating colors...")
            # Now update only the non-orange paths
            for path_id in paths_to_update:
                modified_svg = update_path_color(modified_svg, path_id)
            
            # Save the modified SVG
            output_file = "Step5.svg"
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(modified_svg)
            print(f"{Fore.GREEN}Colors updated and saved to {output_file}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}No matching paths found{Style.RESET_ALL}")

    except Exception as e:
        print(f"Error processing SVG: {e}")

if __name__ == "__main__":
    try:
        input_svg = "Step4.svg"
        process_svg_file(input_svg)
    except Exception as e:
        print(f"An error occurred: {str(e)}")