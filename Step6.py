import re
import os
from cairosvg import svg2png
import cloudinary
import cloudinary.uploader
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

def filter_svg(input_file, output_file):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            svg_content = file.read()

        # Replace elements with specified colors with transparent style
        def make_transparent(match):
            element_tag = match.group(0)
            # Check if any of the specified colors are present
            if re.search(r'(?:stroke|fill):(?:#fb0505|#0000ff|#ff00cd|#fb7905)', element_tag):
                element_tag = re.sub(r'style="[^"]*"', 'style="fill:none;stroke:none"', element_tag)
            return element_tag

        # Apply transparency to elements with specified colors
        filtered_svg_content = re.sub(r'<(path|text)[^>]*?style="[^"]*?"[^>]*?>', make_transparent, svg_content)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(filtered_svg_content)

        print(f"Filtered SVG saved as {output_file}")

        # Convert the filtered SVG to PNG
        with open(output_file, 'rb') as svg_file:
            svg_content = svg_file.read()
        
        # Convert to PNG with high resolution
        svg2png(bytestring=svg_content, write_to='Step6.png')
        print("Successfully converted Step6.svg to Step6.png")

        # Upload PNG to Cloudinary
        # response = cloudinary.uploader.upload('Step6.png', folder='AI-TakeOFF')
        # cloudinary_url_modified = response['url']

        # Update data.json with the Cloudinary URL for modifiedDrawing
        # data_file = "data.json"
        # if os.path.exists(data_file):
        #     with open(data_file, 'r') as f:
        #         data = json.load(f)
        
        #     # Add the URL directly at the root level
        #     data['modified_drawing'] = cloudinary_url_modified
        
        #     with open(data_file, 'w') as f:
        #         json.dump(data, f, indent=4)
        
        #     print("data.json updated successfully.")
        # else:
        #     print(f"Error: {data_file} does not exist.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if not os.path.exists('Step5.svg'):
        print("Error: Step5.svg does not exist.")
    else:
        filter_svg("Step5.svg", "Step6.svg")
