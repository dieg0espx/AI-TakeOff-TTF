import re
import os
import cloudinary
import cloudinary.uploader
import cairosvg
import json
from dotenv import load_dotenv

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

        
        found_duplicates = False
        for d_param, ids in d_params.items():
            if len(ids) > 1:
                found_duplicates = True

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

        return modified_svg_text

    except Exception as e:
        print(f"Error handling duplicate paths: {e}")
        return svg_text

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Usage
if __name__ == "__main__":
    try:
        # Update the input SVG path to original.svg
        input_svg = "files/original.svg"  # Assuming original.svg is one directory up from Steps
        output_svg = "Step1.svg"
        
        # Check if input file exists
        if not os.path.exists(input_svg):
            print(f"Error: Input file '{input_svg}' not found!")
            print(f"Current working directory: {os.getcwd()}")
        else:
            find_and_remove_duplicate_paths(input_svg, output_svg)
            
        # Convert SVG to PNG using cairosvg
        png_path = 'Step1.png'
        try:
            cairosvg.svg2png(url=output_svg, write_to=png_path)
            print(f"Converted {output_svg} to {png_path}")
        except Exception as e:
            print(f"Error converting SVG to PNG: {e}")
            exit(1)  # Exit if conversion fails

        # Check if the PNG file exists before proceeding
        if not os.path.exists(png_path):
            print(f"Error: {png_path} does not exist. Exiting.")
            exit(1)

        # Upload PNG to Cloudinary inside 'AI-TakeOFF' folder
        response = cloudinary.uploader.upload(png_path, folder='AI-TakeOFF')
        cloudinary_url_input = response['url']

        # Debugging: Print the URL to be added
        print(f"Cloudinary URL to be added: {cloudinary_url_input}")

        # Update data.json with the Cloudinary URL for originalDrawing
        data_file = "data.json"
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            # Add the URL directly at the root level
            data['original_drawing'] = cloudinary_url_input
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=4)
            
            print("data.json updated successfully.")
        else:
            print(f"Error: {data_file} does not exist.")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

