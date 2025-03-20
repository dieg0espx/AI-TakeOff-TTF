# START SERVER : uvicorn test:app --host 0.0.0.0 --port 8000 --reload

import re
import os
import requests
import asyncio
from io import BytesIO
from lxml import etree
from PIL import Image
import cloudinary
import cloudinary.uploader
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pdf2image import convert_from_path
import pytesseract
import cairosvg
from PatternComponents import shores_box, shores, frames_6x4, frames_5x4, frames_inBox
from typing import Optional

isProduction = False

# Global list to store connected WebSocket clients
connected_clients = []

# Configure FastAPI
app = FastAPI()

# Enable CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify your frontend URL)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Add this to expose WebSocket headers
)

# Configure Cloudinary
cloudinary.config(
    cloud_name="dvord9edi",
    api_key="323184262698784",
    api_secret="V92mnHScgdYhjeQMWI5Dw63e8Fg"
)

# Google Drive download URL
GOOGLE_DRIVE_DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id="
API_KEY = "2b007718a3f040bb6ac0260982723e48"

# SVG FileName
input_svg_path = ''
output_svg_path = 'modified_image.svg'

# GLOBAL RESTULST (RETURN VALUES)
results = []

# Request body model
class FileRequest(BaseModel):
    file_id: Optional[str] = None

# WebSocket endpoint for real-time console logs
@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # Echo received messages
            await websocket.send_text(f"Echo: {data}")  # Send back data
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# Send logs to all connected WebSocket clients
async def send_log_to_clients(log_message):
    for client in connected_clients:
        await client.send_text(log_message)

# Log message to console and WebSocket clients
async def send_log_and_print(message):
    print(message)  # Log to console
    await send_log_to_clients(message)

# Convertio API conversion functions
async def start_conversion():
    # await send_log_and_print("Starting file conversion to SVG format...")
    url = "https://api.convertio.co/convert"
    data = {
        "apikey": API_KEY,
        "input": "upload",
        "outputformat": "svg"
    }
    response = requests.post(url, json=data)
    result = response.json()
    if result.get('code') == 200:
        conversion_id = result['data']['id']
        # await send_log_and_print(f"Conversion started successfully with ID: {conversion_id}")
        return conversion_id
    else:
        raise Exception(f"❌ Error starting conversion: {result.get('error')}")

async def upload_file(conv_id, file_path):
    # await send_log_and_print(f"Uploading file with conversion ID: {conv_id}...")
    upload_url = f"https://api.convertio.co/convert/{conv_id}/upload"
    with open(file_path, 'rb') as file:
        response = requests.put(upload_url, data=file)
        result = response.json()
        if result.get('code') == 200:
            await send_log_and_print("File uploaded successfully.")
        else:
            raise Exception(f"❌ File upload failed: {result.get('error')}")

async def check_status(conv_id):
    # await send_log_and_print(f"Checking conversion status for ID: {conv_id}...")
    status_url = f"https://api.convertio.co/convert/{conv_id}/status"
    while True:
        response = requests.get(status_url)
        result = response.json()
        if 'data' in result:
            status = result['data'].get('step')
            # await send_log_and_print(f" Current conversion status: {status}")
            if status == "finish" and result['data'].get('output'):
                # await send_log_and_print("Conversion finished successfully. Preparing to download.")
                return result['data']['output']['url']
            elif status in ["failed", "error"]:
                raise Exception("❌ Conversion failed.")
        await asyncio.sleep(5)

async def download_file(download_url, output_path):
    # await send_log_and_print("Downloading converted SVG file...")
    response = requests.get(download_url)
    with open(output_path, 'wb') as file:
        file.write(response.content)
    # await send_log_and_print(f"Downloaded file saved to {output_path}")

# Extract text from PDF
async def extract_text_from_pdf(pdf_path):
    # await send_log_and_print(f"Extracting text from PDF: {pdf_path}")
    text = []
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        # await send_log_and_print(f"Extracting text from page {i + 1}...")
        page_text = pytesseract.image_to_string(image)
        text.append(page_text)
    # await send_log_and_print("Text extraction from PDF completed.")
    return text, images

# Upload images to Cloudinary
def upload_image_to_cloudinary(image, file_id, page_number):
    img_bytes = BytesIO()
    image.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    response = cloudinary.uploader.upload(
        img_bytes,
        folder="takeOff",
        public_id=f"{file_id}_page_{page_number}",
        overwrite=True
    )
    return response["secure_url"]

# SVG pattern counting function
async def count_specific_paths(svg_path):
    # await send_log_and_print(f"Analyzing SVG for scaffolding patterns: {svg_path}")
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()
    frames6x4_patterns = ["h 300 l -300,-450 h 300", "l 450,-300 v 300"]
    shores_style = 'fill:none;stroke:#000000;stroke-width:17;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1'

    counts = {"frames6x4": 0, "shores": 0}
    for path in root.xpath("//*[local-name()='path']"):
        d_attr = path.get("d")
        style_attr = path.get("style")
        if d_attr:
            for pattern in frames6x4_patterns:
                if pattern in d_attr:
                    counts["frames6x4"] += 1
                    break
        if style_attr and style_attr == shores_style:
            counts["shores"] += 1

    print(f"Shape count completed: Scaffold 6x4 = {counts['frames6x4']}, Shores = {counts['shores'] / 6}")

    # ======== OBJECT DETECTION ======== #
    modify_svg_stroke_and_fill(svg_path, output_svg_path)
    apply_color_to_specific_paths(output_svg_path)  

    return counts

# ======== OBJECT DETECTION ======== #
def modify_svg_stroke_and_fill(input_file, output_file, black_stroke="#000000", white_stroke="#4e4e4e", new_stroke="#4e4e4e", fill_color="#4e4e4e"):
    """Modify SVG stroke and fill colors"""
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Find and print IDs of elements with #ffdf7f
        yellow_elements = re.finditer(r'<[^>]*?id="([^"]*)"[^>]*(?:stroke|fill):#ffdf7f[^>]*>', svg_text)
        skipped_ids = set()
        for match in yellow_elements:
            if match.group(1):  # if ID exists
                skipped_ids.add(match.group(1))
        
        if skipped_ids:
            print("Skipped elements with #ffdf7f (by ID):", ", ".join(skipped_ids))

        # Modify stroke colors, but skip elements with #ffdf7f
        modified_svg_text = re.sub(
            r'(?:<[^>]*(?:stroke|fill):#ffdf7f[^>]*>)|(?:stroke:(#[0-9a-fA-F]{6}))',
            lambda m: m.group(0) if 'ffdf7f' in m.group(0) else (
                f"stroke:{new_stroke}" if m.group(1) == black_stroke else f"stroke:{white_stroke}"
            ),
            svg_text
        )

        # Modify fill colors, but skip elements with #ffdf7f
        modified_svg_text = re.sub(
            r'(?:<[^>]*(?:stroke|fill):#ffdf7f[^>]*>)|(?:fill:(#[0-9a-fA-F]{6}))',
            lambda m: m.group(0) if 'ffdf7f' in m.group(0) else f"fill:{fill_color}",
            modified_svg_text
        )

        # Continue with text modifications as before
        modified_svg_text = re.sub(r'(<text[^>]*style="[^"]*)fill:[#0-9a-fA-F]+', rf'\1fill:{new_stroke}', modified_svg_text)
        modified_svg_text = re.sub(r'(<text[^>]*style="[^"]*)stroke:[#0-9a-fA-F]+', rf'\1stroke:{new_stroke}', modified_svg_text)
        modified_svg_text = re.sub(r'(<text(?![^>]*style=)[^>]*)>', rf'\1 style="fill:{new_stroke}; stroke:{new_stroke}">', modified_svg_text)

        # Finally, change all #ffdf7f elements to #000000
        modified_svg_text = re.sub(
            r'(stroke|fill):#ffdf7f',
            r'\1:#000000',
            modified_svg_text
        )

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)

        print(f"SVG modified successfully and saved to {output_file}")
    except Exception as e:
        print(f"Error modifying SVG: {e}")

def apply_color_to_specific_paths(output_file, red="#05fbce", blue="#0000ff", green="#70ff00", pink="#ff00cd", orange="#fb7905"):
    """
    Reads an SVG file and changes:
    - `shores_box` paths to red (#FF0000)
    - `shores` paths to blue (#0000FF)
    - `frames_6x4` paths to green (#5DFF00)
    """
    global colorObjects, objectsImage  # Add this line to modify global variables

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
        print(
            f"SVG Path Counts:\n"
            f"  - Shores Box (RED): {match_count_box}\n"
            f"  - Shores (BLUE): {match_count_33_34}\n"
            f"  - Frames 6x4 (GREEN): {match_count_frames6x4}\n"
            f"  - Frames 5x4 (LIGHT GREEN): {match_count_frames5x4}\n"
            f"  - Frames In Box (PURPLE): {match_count_framesinBox}"
        )

        colorObjects = {
            'shoresBox': match_count_box, 
            'shores':  match_count_33_34, 
            'frames6x4': match_count_frames6x4, 
            'frames5x4': match_count_frames5x4,
            'framesInBox': match_count_framesinBox
        }

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

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)

        print(f"Color modifications applied successfully")

        # Store Modified Image in Cloudinary
        response = cloudinary.uploader.upload(output_svg_path, resource_type = "raw")
   
        # Get the URL of the uploaded SVG
        svg_url = response['secure_url']
        objectsImage = svg_url

    except Exception as e:
        print(f"Error modifying stroke and fill: {e}")

def add_background_to_svg(input_file, output_file, background_color):
    """
    Adds a background color to the SVG by inserting a <rect> element.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Insert a <rect> element after the opening <svg> tag
        svg_text = re.sub(
            r'(<svg[^>]*>)',
            rf'\1<rect width="100%" height="100%" fill="{background_color}" />',
            svg_text,
            count=1
        )

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(svg_text)

        print(f"Background color {background_color} added to SVG and saved to {output_file}")
    except Exception as e:
        print(f"Error adding background to SVG: {e}")

def make_grey_elements_transparent(svg_path, output_path):
    """Make all elements that have fill or stroke color #4e4e4e transparent"""
    try:
        with open(svg_path, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Replace fill:#4e4e4e with fill:none and add opacity:0
        modified_svg_text = re.sub(
            r'(fill:#4e4e4e)',
            'fill:none;opacity:0',
            svg_text
        )

        # Replace stroke:#4e4e4e with stroke:none and add opacity:0
        modified_svg_text = re.sub(
            r'(stroke:#4e4e4e)',
            'stroke:none;opacity:0',
            modified_svg_text
        )

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)

        print("Made grey elements (#4e4e4e) transparent")
    except Exception as e:
        print(f"Error making grey elements transparent: {e}")

def print_path_coordinates(svg_path, target_id="path3074"):
    try:
        with open(svg_path, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # Find the path with specific ID
        path_match = re.search(rf'<path[^>]*id="{target_id}"[^>]*d="([^"]*)"', svg_text)
        
        if path_match:
            path_data = path_match.group(1)
            
            # Extract coordinates from path data
            # First coordinate (start)
            start_coord = re.search(r'[Mm]\s*([-\d.]+)[,\s]*([-\d.]+)', path_data)
            # Last coordinate (end) - look for last L or l command
            end_coord = re.findall(r'[Ll]\s*([-\d.]+)[,\s]*([-\d.]+)', path_data)[-1] if re.findall(r'[Ll]\s*([-\d.]+)[,\s]*([-\d.]+)', path_data) else None
            
            if start_coord:
                print(f"Path {target_id} coordinates:")
                print(f"Start: ({start_coord.group(1)}, {start_coord.group(2)})")
                if end_coord:
                    print(f"End: ({end_coord[0]}, {end_coord[1]})")
            else:
                print(f"Could not find coordinates in path {target_id}")
        else:
            print(f"Path with id={target_id} not found")
            
    except Exception as e:
        print(f"Error reading path coordinates: {e}")

def find_paths_with_shared_coordinates(svg_path, target_id="path3074"):
    try:
        with open(svg_path, "r", encoding="utf-8") as file:
            svg_text = file.read()

        # First find our target path coordinates
        target_path = re.search(rf'<path[^>]*id="{target_id}"[^>]*d="([^"]*)"', svg_text)
        if not target_path:
            print(f"Target path {target_id} not found")
            return

        target_data = target_path.group(1)
        target_start = re.search(r'[Mm]\s*([-\d.]+)[,\s]*([-\d.]+)', target_data)
        target_end = re.findall(r'[Ll]\s*([-\d.]+)[,\s]*([-\d.]+)', target_data)[-1] if re.findall(r'[Ll]\s*([-\d.]+)[,\s]*([-\d.]+)', target_data) else None

        if not target_start or not target_end:
            print("Could not extract coordinates from target path")
            return

        target_start_coords = (target_start.group(1), target_start.group(2))
        target_end_coords = target_end

        print(f"\nTarget path {target_id}:")
        print(f"Start coordinates: ({target_start_coords[0]}, {target_start_coords[1]})")
        print(f"End coordinates: ({target_end_coords[0]}, {target_end_coords[1]})")

        # Find all paths and their coordinates
        all_paths = re.finditer(r'<path[^>]*id="([^"]*)"[^>]*d="([^"]*)"', svg_text)
        
        shared_starts = []
        shared_ends = []

        for path in all_paths:
            path_id = path.group(1)
            if path_id == target_id:
                continue

            path_data = path.group(2)
            start_match = re.search(r'[Mm]\s*([-\d.]+)[,\s]*([-\d.]+)', path_data)
            end_matches = re.findall(r'[Ll]\s*([-\d.]+)[,\s]*([-\d.]+)', path_data)
            
            if start_match:
                start_coords = (start_match.group(1), start_match.group(2))
                if start_coords == target_start_coords or start_coords == target_end_coords:
                    shared_starts.append(path_id)
            
            if end_matches:
                end_coords = end_matches[-1]
                if end_coords == target_start_coords or end_coords == target_end_coords:
                    shared_ends.append(path_id)

        if shared_starts:
            print("\nPaths sharing start/end point with target path's coordinates:")
            for path_id in shared_starts:
                print(f"- Path {path_id}")
        else:
            print("\nNo paths found sharing start/end point with target path's coordinates")

        if shared_ends:
            print("\nPaths ending at target path's coordinates:")
            for path_id in shared_ends:
                print(f"- Path {path_id}")
        else:
            print("\nNo paths found ending at target path's coordinates")

    except Exception as e:
        print(f"Error analyzing path coordinates: {e}")

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
        print("\nDuplicate paths found:")
        for d_param, ids in d_params.items():
            if len(ids) > 1:
                found_duplicates = True
                print(f"\nDuplicate group with {len(ids)} elements:")
                print("IDs:", ", ".join(ids))
                print(f"Keeping: {ids[0]}, Removing: {', '.join(ids[1:])}")

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

        print(f"\nRemoved {len(paths_to_remove)} duplicate paths")
        
        # Print line counts for verification
        original_lines = len(svg_text.split('\n'))
        new_lines_count = len(new_lines)
        print(f"Original file lines: {original_lines}")
        print(f"New file lines: {new_lines_count}")
        print(f"Difference: {original_lines - new_lines_count} lines removed")

        return modified_svg_text

    except Exception as e:
        print(f"Error handling duplicate paths: {e}")
        return svg_text

# Modified process function
def process_svg_with_background(svg_path, output_svg_path):
    try:
        if not os.path.exists(svg_path):
            raise FileNotFoundError(f"Source file {svg_path} not found")
        
        # Find and remove duplicate paths
        find_and_remove_duplicate_paths(svg_path, output_svg_path)
        
        # Find paths with shared coordinates
        find_paths_with_shared_coordinates(output_svg_path)
            
        # Continue with existing process
        modify_svg_stroke_and_fill(svg_path, output_svg_path)
        add_background_to_svg(output_svg_path, output_svg_path, background_color="#202124")
        apply_color_to_specific_paths(output_svg_path)
        
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# API endpoint to process PDF
@app.post("/process-pdf/")
async def process_pdf_from_drive(request: Optional[FileRequest] = None):
    if isProduction:
        if request is None or request.file_id is None:
            raise HTTPException(status_code=400, detail="file_id is required in production mode.")
        
        file_id = request.file_id
        # await send_log_and_print(f"Received request to process PDF with ID: {file_id}")

        response = requests.get(GOOGLE_DRIVE_DOWNLOAD_URL + file_id)
        if response.status_code != 200:
            error_message = "❌ Failed to download file from Google Drive."
            # await send_log_and_print(error_message)
            return {"success": False, "error": error_message}

        try:
            pdf_path = f"{file_id}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            # await send_log_and_print(f"PDF downloaded and saved as {pdf_path}")

            # Convert to SVG
            conv_id = await start_conversion()
            await upload_file(conv_id, pdf_path)
            download_url = await check_status(conv_id)
            svg_path = f"{file_id}.svg"
            await download_file(download_url, svg_path)

        except Exception as e:
            error_message = str(e)
            # await send_log_and_print(f"❌ Error during conversion process: {error_message}")
            return {"success": False, "error": error_message}

        # Extract text from the PDF and convert images
        extracted_text, images = await extract_text_from_pdf(pdf_path)

        # Count shapes from SVG
        counts = await count_specific_paths(svg_path)

        # Prepare result response
        pdf_size = os.path.getsize(pdf_path)

        for i, (text, image) in enumerate(zip(extracted_text, images)):
            try:
                # await send_log_and_print(f"Uploading processed image for page {i + 1} to Cloudinary...")
                processed_image_url = upload_image_to_cloudinary(image, file_id, i + 1)

                results.append({
                    "page": i + 1,
                    "text": text.strip(),
                    "shape_count": {
                        "Scaffold6x4": counts["frames6x4"],
                        "Shores": counts["shores"] / 6
                    },
                    "file_name": f"{file_id}.pdf",
                    "type": "application/pdf",
                    "size": pdf_size,
                    "processed_image_url": processed_image_url,
                    "colorObjects": colorObjects,
                    "objectsImage": objectsImage,
                })
            except Exception as img_error:
                # await send_log_and_print(f"❌ Error processing page {i + 1}: {img_error}")
                continue  # Skip problematic pages

        # await send_log_and_print("All pages processed successfully.")
        return {"success": True, "results": results}

    else:
        print("EXECUTING TEST MODE ... ")
        # Non-production mode: work with svg_file.svg
        svg_path = 'joined_paths.svg'
        try:
            process_svg_with_background(svg_path, output_svg_path)
            return {"success": True, "message": "SVG processed and saved as modified_image.svg"}
        except Exception as e:
            return {"success": False, "error": str(e)}

@app.get("/")
async def read_root():
    # await send_log_and_print("🚀 API is up and running!")
    return {"message": "APP.PY"}