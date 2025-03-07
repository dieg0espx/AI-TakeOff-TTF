# START SERVER : uvicorn app:app --host 0.0.0.0 --port 8000 --reload

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
API_KEY = "173f4a190c64bbac2be2a7a043da70c0"

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
    await send_log_and_print("Starting file conversion to SVG format...")
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
        await send_log_and_print(f"Conversion started successfully with ID: {conversion_id}")
        return conversion_id
    else:
        raise Exception(f"❌ Error starting conversion: {result.get('error')}")

async def upload_file(conv_id, file_path):
    await send_log_and_print(f"Uploading file with conversion ID: {conv_id}...")
    upload_url = f"https://api.convertio.co/convert/{conv_id}/upload"
    with open(file_path, 'rb') as file:
        response = requests.put(upload_url, data=file)
        result = response.json()
        if result.get('code') == 200:
            await send_log_and_print("File uploaded successfully.")
        else:
            raise Exception(f"❌ File upload failed: {result.get('error')}")

async def check_status(conv_id):
    await send_log_and_print(f"Checking conversion status for ID: {conv_id}...")
    status_url = f"https://api.convertio.co/convert/{conv_id}/status"
    while True:
        response = requests.get(status_url)
        result = response.json()
        if 'data' in result:
            status = result['data'].get('step')
            await send_log_and_print(f" Current conversion status: {status}")
            if status == "finish" and result['data'].get('output'):
                await send_log_and_print("Conversion finished successfully. Preparing to download.")
                return result['data']['output']['url']
            elif status in ["failed", "error"]:
                raise Exception("❌ Conversion failed.")
        await asyncio.sleep(5)

async def download_file(download_url, output_path):
    await send_log_and_print("Downloading converted SVG file...")
    response = requests.get(download_url)
    with open(output_path, 'wb') as file:
        file.write(response.content)
    await send_log_and_print(f"Downloaded file saved to {output_path}")

# Extract text from PDF
async def extract_text_from_pdf(pdf_path):
    await send_log_and_print(f"Extracting text from PDF: {pdf_path}")
    text = []
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        await send_log_and_print(f"Extracting text from page {i + 1}...")
        page_text = pytesseract.image_to_string(image)
        text.append(page_text)
    await send_log_and_print("Text extraction from PDF completed.")
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
    await send_log_and_print(f"Analyzing SVG for scaffolding patterns: {svg_path}")
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()

    frames6x4_patterns = [
        "h 300 l -300,-450 h 300",
        "l 450,-300 v 300"
    ]

    shores_style = 'fill:none;stroke:#000000;stroke-width:17;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1'

    shores_no4_patterns = [
        # Original variations
        "h 60 v -61 h -60 v 61", "h 61 v -60 h -61 v 60",
        "h -60 v 61 h 60 v -61", "h -61 v 60 h 61 v -60",
        "h 60 v -60 h -60 v 60", "h 61 v -61 h -61 v 61",
        "h -60 v 60 h 60 v -60", "h -61 v 61 h 61 v -61",
    
        "h 60 v 61 h -60 v -61", "h 61 v 60 h -61 v -60",
        "h -60 v -61 h 60 v 61", "h -61 v -60 h 61 v 60",
        "h 60 v 60 h -60 v -60", "h 61 v 61 h -61 v -61",
        "h -60 v -60 h 60 v 60", "h -61 v -61 h 61 v 61",
    
        "h -61 v -61 h 61 v 61", "h 61 v 61 h -61 v -61",
        "h -60 v -61 h 60 v 61", "h 60 v 61 h -60 v -61",
        "h -61 v 60 h 61 v -60", "h 61 v -60 h -61 v 60",
        "h -60 v 60 h 60 v -60", "h 60 v -60 h -60 v 60",
    
        # Variations where `h` and `v` positions are swapped
        "v 60 h -61 v -60 h 61", "v 61 h -60 v -61 h 60",
        "v -60 h 61 v 60 h -61", "v -61 h 60 v 61 h -60",
        "v 60 h -60 v -60 h 60", "v 61 h -61 v -61 h 61",
        "v -60 h 60 v 60 h -60", "v -61 h 61 v 61 h -61",
    
        "v 60 h 61 v -60 h -61", "v 61 h 60 v -61 h -60",
        "v -60 h -61 v 60 h 61", "v -61 h -60 v 61 h 60",
        "v 60 h 60 v -60 h -60", "v 61 h 61 v -61 h -61",
        "v -60 h -60 v 60 h 60", "v -61 h -61 v 61 h 61",
    
        "v -61 h -61 v 61 h 61", "v 61 h 61 v -61 h -61",
        "v -60 h -61 v 60 h 61", "v 60 h 61 v -60 h -61",
        "v -61 h 60 v 61 h -60", "v 61 h -60 v -61 h 60",
        "v -60 h 60 v 60 h -60", "v 60 h -60 v -60 h 60"
    ]


    counts = {"frames6x4": 0, "shores": 0, "shores_no4": 0}

    for path in root.xpath("//*[local-name()='path']"):
        d_attr = path.get("d")
        style_attr = path.get("style")

        if d_attr:
            for pattern in frames6x4_patterns:
                if pattern in d_attr:
                    counts["frames6x4"] += 1
                    break
            for pattern in shores_no4_patterns:
                if pattern in d_attr:
                    counts["shores_no4"] += 1
                    break
        
        if style_attr and style_attr == shores_style:
            counts["shores"] += 1

    print(f"Shape count completed: Scaffold 6x4 = {counts['frames6x4']}, Shores = {counts['shores'] / 6}, ShoresNo4 = {counts['shores_no4']}")
    return counts


# API endpoint to process PDF
@app.post("/process-pdf/")
async def process_pdf_from_drive(request: FileRequest):
    file_id = request.file_id
    await send_log_and_print(f"Received request to process PDF with ID: {file_id}")

    response = requests.get(GOOGLE_DRIVE_DOWNLOAD_URL + file_id)
    if response.status_code != 200:
        error_message = "❌ Failed to download file from Google Drive."
        await send_log_and_print(error_message)
        return {"success": False, "error": error_message}

    try:
        pdf_path = f"{file_id}.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        await send_log_and_print(f"PDF downloaded and saved as {pdf_path}")

        # Convert to SVG
        conv_id = await start_conversion()
        await upload_file(conv_id, pdf_path)
        download_url = await check_status(conv_id)
        svg_path = f"{file_id}.svg"
        await download_file(download_url, svg_path)

    except Exception as e:
        error_message = str(e)
        await send_log_and_print(f"❌ Error during conversion process: {error_message}")
        return {"success": False, "error": error_message}

    # Extract text from the PDF and convert images
    extracted_text, images = await extract_text_from_pdf(pdf_path)

    # Count shapes from SVG
    counts = await count_specific_paths(svg_path)

    # Prepare result response
    results = []
    pdf_size = os.path.getsize(pdf_path)

    for i, (text, image) in enumerate(zip(extracted_text, images)):
        try:
            await send_log_and_print(f"Uploading processed image for page {i + 1} to Cloudinary...")
            processed_image_url = upload_image_to_cloudinary(image, file_id, i + 1)

            results.append({
                "page": i + 1,
                "text": text.strip(),
                "shape_count": {
                    "Scaffold6x4": counts["frames6x4"],
                    "Shores": counts["shores"] / 6,
                    "ShoresNo4": counts["shores_no4"]
                },
                "file_name": f"{file_id}.pdf",
                "type": "application/pdf",
                "size": pdf_size,
                "processed_image_url": processed_image_url
            })
        except Exception as img_error:
            await send_log_and_print(f"❌ Error processing page {i + 1}: {img_error}")
            continue  # Skip problematic pages

    await send_log_and_print("All pages processed successfully.")
    return {"success": True, "results": results}

@app.get("/")
async def read_root():
    await send_log_and_print("🚀 API is up and running!")
    return {"message": "APP.PY"}
