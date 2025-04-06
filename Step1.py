import re
import os

def find_and_remove_duplicate_paths(svg_path, output_path):
    try:
        with open(svg_path, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Extract all paths with their IDs and d parameters
        paths = list(re.finditer(r'<path[^>]*?id="([^"]*)"[^>]*?d="([^"]*)"', svg_text))
        
        # Create a dictionary to store d parameters and their corresponding IDs
        d_params = {}
        paths_to_remove = set()
        
        # Collect paths with same d parameter
        for path in paths:
            path_id = path.group(1)
            d_param = path.group(2).strip()
            d_param = re.sub(r'\s+', ' ', d_param)
            
            if d_param in d_params:
                d_params[d_param].append(path_id)
                paths_to_remove.add(path_id)
            else:
                d_params[d_param] = [path_id]

        # Print duplicates
        found_duplicates = False
        # print("\nDuplicate paths found:")
        for d_param, ids in d_params.items():
            if len(ids) > 1:
                found_duplicates = True
                # print(f"\nDuplicate group with {len(ids)} elements:")
                # print("IDs:", ", ".join(ids))
                # print(f"Keeping: {ids[0]}, Removing: {', '.join(ids[1:])}")

        if not found_duplicates:
            print("No duplicate paths found")
            return svg_text

        # Remove duplicate paths
        lines = svg_text.split('\n')
        new_lines = []
        
        for line in lines:
            # Check if this line contains a path to remove
            should_keep = True
            for path_id in paths_to_remove:
                if f'id="{path_id}"' in line:
                    should_keep = False
                    break
            if should_keep:
                new_lines.append(line)

        # Join the lines back together
        modified_svg_text = '\n'.join(new_lines)

        # Write the modified content back to file
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)

        print(f"Removed {len(paths_to_remove)} duplicate paths")
        
        # Print line counts for verification
        original_lines = len(svg_text.split('\n'))
        new_lines_count = len(new_lines)
        # print(f"Original file lines: {original_lines}")
        # print(f"New file lines: {new_lines_count}")
        # print(f"Difference: {original_lines - new_lines_count} lines removed")

        return modified_svg_text

    except Exception as e:
        print(f"Error handling duplicate paths: {e}")
        return svg_text

# Usage
if __name__ == "__main__":
    try:
        # Update the input SVG path to original.svg
        input_svg = "original.svg"  # Assuming original.svg is one directory up from Steps
        output_svg = "Step1.svg"
        
        # Check if input file exists
        if not os.path.exists(input_svg):
            print(f"Error: Input file '{input_svg}' not found!")
            print(f"Current working directory: {os.getcwd()}")
        else:
            find_and_remove_duplicate_paths(input_svg, output_svg)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
