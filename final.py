# START SERVER : uvicorn final:app --host 0.0.0.0 --port 8000 --reload

import os
import requests
import time
from io import BytesIO
from lxml import etree
from PIL import Image
import cloudinary
import cloudinary.uploader
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pdf2image import convert_from_path
import pytesseract

# Flag to control resource usage
production = False  # Set to True for production

# Configure FastAPI
app = FastAPI()

# Enable CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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

# Convertio API conversion functions
def start_conversion():
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
        print(f"Conversion started: {conversion_id}")
        return conversion_id
    else:
        raise Exception(f"Error starting conversion: {result.get('error')}")

def upload_file(conv_id, file_path):
    upload_url = f"https://api.convertio.co/convert/{conv_id}/upload"
    with open(file_path, 'rb') as file:
        response = requests.put(upload_url, data=file)
        result = response.json()
        if result.get('code') == 200:
            print("File uploaded successfully.")
        else:
            raise Exception(f"File upload failed: {result.get('error')}")

def check_status(conv_id):
    status_url = f"https://api.convertio.co/convert/{conv_id}/status"
    while True:
        response = requests.get(status_url)
        result = response.json()
        if 'data' in result:
            status = result['data'].get('step')
            print(f"Conversion status: {status}")
            if status == "finish" and result['data'].get('output'):
                print("Conversion finished successfully.")
                return result['data']['output']['url']
            elif status in ["failed", "error"]:
                raise Exception("Conversion failed.")
        time.sleep(5)

def download_file(download_url, output_path):
    response = requests.get(download_url)
    with open(output_path, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded file saved to {output_path}")

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    print(f"Extracting text from {pdf_path}")
    text = []
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        page_text = pytesseract.image_to_string(image)
        text.append(page_text)
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
def count_specific_paths(svg_path):
    print(f"Starting shape count in {svg_path}")
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

    print(f"Count Results: Scaffold 6x4 = {counts['frames6x4']}, Shores = {counts['shores'] / 6}")
    return counts

# API endpoint to process PDF
@app.post("/process-pdf/")
async def process_pdf_from_drive(request: FileRequest):
    file_id = request.file_id
    print(f"Received request for file_id: {file_id}")

    response = requests.get(GOOGLE_DRIVE_DOWNLOAD_URL + file_id)
    if response.status_code != 200:
        error_message = "Failed to download file from Google Drive"
        print(error_message)
        return {"success": False, "error": error_message}

    try:
        pdf_path = f"{file_id}.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        print(f"PDF downloaded and saved as {pdf_path}")

        # Convert to SVG
        conv_id = start_conversion()
        upload_file(conv_id, pdf_path)
        download_url = check_status(conv_id)
        svg_path = f"{file_id}.svg"
        download_file(download_url, svg_path)

    except Exception as e:
        error_message = str(e)
        print(f"Error occurred: {error_message}")
        return {"success": False, "error": error_message}

    # Extract text from the PDF and convert images
    extracted_text, images = extract_text_from_pdf(pdf_path)

    # Count shapes from SVG
    counts = count_specific_paths(svg_path)

    # Prepare result response
    results = []
    pdf_size = os.path.getsize(pdf_path)

    for i, (text, image) in enumerate(zip(extracted_text, images)):
        try:
            processed_image_url = upload_image_to_cloudinary(image, file_id, i + 1)

            results.append({
                "page": i + 1,
                "text": text.strip(),
                "shape_count": {
                    "frames_6x4": counts["frames6x4"],
                    "shores": counts["shores"] / 6
                },
                "file_name": f"{file_id}.pdf",
                "type": "application/pdf",
                "size": pdf_size,
                "processed_image_url": processed_image_url
            })
        except Exception as img_error:
            print(f"Error processing page {i + 1}: {img_error}")
            continue  # Skip problematic pages

    return {"success": True, "results": results}

@app.get("/")
def read_root():
    print("API is running.")
    return {"message": "Hello, FastAPI is working!"}
