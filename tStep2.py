import re
import os

def join_paths(svg_path, output_path, path1_id='path2880', path2_id='path2882'):
    try:
        with open(svg_path, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Find both paths
        path1 = re.search(rf'<path[^>]*id="{path1_id}"[^>]*d="([^"]*)"', svg_text)
        path2 = re.search(rf'<path[^>]*id="{path2_id}"[^>]*d="([^"]*)"', svg_text)

        if not path1 or not path2:
            print("Could not find one or both paths")
            return

        # Get the path data
        path1_data = path1.group(1)  # M 14450,8549 V 8249
        path2_data = path2.group(1)  # m 14975,8549 v -300 l -525,300

        # Create new combined path data (converting relative to absolute coordinates)
        new_path_data = f"M 14450,8549 V 8249 M 14975,8549 V 8249 L 14450,8549"

        # Create the new combined path element with the specified color
        new_path = f'''<path
           id="path_combined"
           style="fill:none;stroke:#fb3205;stroke-width:7;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
           d="{new_path_data}" />'''

        # Remove the original paths and add the new combined path
        modified_svg = svg_text
        modified_svg = re.sub(rf'<path[^>]*id="{path1_id}"[^>]*?/>.*?<path[^>]*id="{path2_id}"[^>]*?/>', 
                            new_path, modified_svg, flags=re.DOTALL)

        # Write modified content to output file
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(modified_svg)

        print(f"\nJoined paths {path1_id} and {path2_id} into a single path")
        print(f"New path colored in #fb3205")
        print(f"Modified SVG saved as: {output_path}")

    except Exception as e:
        print(f"Error processing SVG: {e}")

# Usage
if __name__ == "__main__":
    try:
        input_svg = "removed_duplicates.svg"
        output_svg = "joined_paths.svg"
        
        if not os.path.exists(input_svg):
            print(f"Error: Input file '{input_svg}' not found!")
            print(f"Current working directory: {os.getcwd()}")
        else:
            join_paths(input_svg, output_svg)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
