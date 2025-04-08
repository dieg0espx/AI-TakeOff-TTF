from cairosvg import svg2png
import re
import cloudinary
import cloudinary.uploader
from io import BytesIO
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def convert_svg_to_png():
    try:
        # Read the SVG file
        if not os.path.exists('Step5.svg'):
            print("Error: Step5.svg does not exist.")
            return
        
        with open('Step5.svg', 'rb') as svg_file:
            svg_content = svg_file.read()
        
        # Convert to PNG with high resolution
        svg2png(bytestring=svg_content,write_to='Step6.png')  # Set height for good resolution
        
        print("Successfully converted Step5.svg to Step6.png")
        
        # Upload to Cloudinary
        url = upload_image_to_cloudinary('Step6.png')
        
        if url:
            # Store the URL in a JSON file named data.json
            with open('data.json', 'r+') as json_file:
                try:
                    data = json.load(json_file)
                except json.JSONDecodeError:
                    data = {}
                data['modified_drawing'] = url
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
                json_file.truncate()  # Ensure the file is not left with old data
            print(f"Image uploaded to Cloudinary. URL: {url}")
        else:
            print("Failed to upload image to Cloudinary.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def upload_image_to_cloudinary(image_path):
    try:
        # Generate a timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        with open(image_path, 'rb') as image_file:
            response = cloudinary.uploader.upload(
                image_file,
                folder="takeOff",
                public_id=f"takeOff_{timestamp}",  # Use timestamp in public_id
                overwrite=True
            )
        return response["secure_url"]
    except Exception as e:
        print(f"Failed to upload image to Cloudinary: {str(e)}")
        return None

def filter_svg(input_file, output_file):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            svg_content = file.read()

        # Replace non-matching elements with transparent style
        def make_transparent(match):
            element_tag = match.group(0)
            # Only make transparent if neither #000000 nor #70FF00 is present
            if not re.search(r'(?:stroke|fill):(?:#000000|#70ff00)', element_tag):
                element_tag = re.sub(r'style="[^"]*"', 'style="fill:none;stroke:none"', element_tag)
            return element_tag

        # Apply transparency to non-matching elements
        filtered_svg_content = re.sub(r'<(path|text)[^>]*?style="[^"]*?"[^>]*?>', make_transparent, svg_content)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(filtered_svg_content)

        print(f"Filtered SVG saved as {output_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    convert_svg_to_png()
    filter_svg("Step5.svg", "Step6.svg")
