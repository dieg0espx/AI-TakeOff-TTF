# START SERVER : uvicorn index:app --host 0.0.0.0 --port 8000 --reload

import re
import os
import requests
import asyncio
from io import BytesIO
from lxml import etree
from PIL import Image
import cloudinary
import cloudinary.uploader
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pdf2image import convert_from_path
import pytesseract
import cairosvg
from PatternComponents import shores_box, shores, frames_6x4, frames_5x4, frames_inBox

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
    file_id: str

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
        print(f"Number of paths matching shores_box (RED): {match_count_box}")
        print(f"Number of paths matching shores (BLUE): {match_count_33_34}")
        print(f"Number of paths matching Framex6x4 (GREEN): {match_count_frames6x4}")
        print(f"Number of paths matching Framex5x4 (LIGHT_GREEN): {match_count_frames5x4}")
        print(f"Number of paths matching FramesInBox (PURPLE): {match_count_framesinBox}")

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

        # Store Modified Image in Cloudinary
        response = cloudinary.uploader.upload(output_svg_path, resource_type = "raw")
   
        # Get the URL of the uploaded SVG
        svg_url = response['secure_url']
        objectsImage = svg_url

    except Exception as e:
        print(f"Error modifying stroke and fill: {e}")

# API endpoint to process PDF
@app.post("/process-pdf/")
async def process_pdf_from_drive(request: FileRequest):
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
                "colorObjects" : colorObjects,                 
                "objectsImage" : objectsImage, 

            })
        except Exception as img_error:
            # await send_log_and_print(f"❌ Error processing page {i + 1}: {img_error}")
            continue  # Skip problematic pages

    # await send_log_and_print("All pages processed successfully.")
    
    return {"success": True, "results": results}

@app.get("/")
async def read_root():
    # await send_log_and_print("🚀 API is up and running!")
    return {"message": "APP.PY"}