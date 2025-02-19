# TO START THE SERVER 
# uvicorn index:app --host 0.0.0.0 --port 8000 --reload

import os
import cv2
import numpy as np
import cloudinary
import cloudinary.uploader
import pdf2image  # Convert PDF to images
import pytesseract  # OCR for text extraction
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image
from pydantic import BaseModel
import requests

# Configure Cloudinary
cloudinary.config(
    cloud_name="dvord9edi",
    api_key="323184262698784",
    api_secret="V92mnHScgdYhjeQMWI5Dw63e8Fg"
)

app = FastAPI()

# Enable CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Drive direct download URL
GOOGLE_DRIVE_DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id="

# Define request body model
class FileRequest(BaseModel):
    file_id: str

# Extract text using OCR
def extract_text_from_image(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    text = pytesseract.image_to_string(gray, config="--psm 6")  # PSM 6 is for text blocks
    return text

# Detect shapes and upload to Cloudinary
def detect_shapes_and_upload(image, filename):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours on the image
    img_copy = np.array(image)
    cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 2)  # Green contours

    # Convert image to bytes
    image_pil = Image.fromarray(img_copy)
    img_bytes = BytesIO()
    image_pil.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Upload to Cloudinary
    response = cloudinary.uploader.upload(
        img_bytes,
        folder="takeOff",  # Store inside 'takeOff' folder
        public_id=f"processed_{filename}"
    )

    # Return Cloudinary URL
    return len(contours), response["secure_url"]

# @app.post("/process-pdf/")
# async def process_pdf_from_drive(request: FileRequest):
#     file_id = request.file_id  # Extract file ID from request
#     print(f"Downloading file from Google Drive with ID: {file_id}")

#     # Fetch file from Google Drive
#     response = requests.get(GOOGLE_DRIVE_DOWNLOAD_URL + file_id)
    
#     if response.status_code != 200:
#         return {"success": False, "error": "Failed to download file from Google Drive"}

#     try:
#         pdf_bytes = response.content
#         images = pdf2image.convert_from_bytes(pdf_bytes, dpi=300)

#         results = []
#         for i, image in enumerate(images):
#             try:
#                 text = extract_text_from_image(image)
#                 shape_count, processed_image_url = detect_shapes_and_upload(image, f"{file_id}_page_{i+1}")

#                 results.append({
#                     "page": i + 1,
#                     "text": text,  # Now includes extracted text
#                     "shape_count": shape_count,
#                     "file_name": f"{file_id}.pdf",
#                     "type": "application/pdf",
#                     "size": len(pdf_bytes),
#                     "processed_image_url": processed_image_url,  # Cloudinary URL
#                 })
#             except Exception as img_error:
#                 print(f"Error processing page {i+1}: {img_error}")
#                 continue  # Skip problematic pages

#         return {"success": True, "results": results}

#     except Exception as e:
#         return {"success": False, "error": f"Error processing PDF: {str(e)}"}


import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.post("/process-pdf/")
async def process_pdf_from_drive(request: FileRequest):
    file_id = request.file_id  # Extract file ID from request
    logging.info(f"📥 Received request to process file_id: {file_id}")

    try:
        # Fetch file from Google Drive
        logging.info(f"📡 Downloading file from Google Drive: {file_id}")
        response = requests.get(GOOGLE_DRIVE_DOWNLOAD_URL + file_id, stream=True)

        if response.status_code != 200:
            logging.error(f"❌ Failed to download file from Google Drive: Status {response.status_code}")
            return {"success": False, "error": "Failed to download file from Google Drive"}

        # Save PDF to disk for debugging
        pdf_path = f"/tmp/{file_id}.pdf"
        with open(pdf_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logging.info(f"✅ File downloaded successfully: {pdf_path}, Size: {os.path.getsize(pdf_path)} bytes")

        # Convert PDF to images
        logging.info(f"📄 Converting PDF to images...")
        images = pdf2image.convert_from_path(pdf_path, dpi=300)
        logging.info(f"✅ PDF converted: {len(images)} pages detected")

        results = []
        for i, image in enumerate(images):
            try:
                logging.info(f"🔍 Processing page {i+1}...")

                # Extract text
                text = extract_text_from_image(image)
                logging.info(f"📝 Extracted text from page {i+1}: {text[:100]}...")  # Show first 100 chars

                # Detect shapes & upload
                shape_count, processed_image_url = detect_shapes_and_upload(image, f"{file_id}_page_{i+1}")
                logging.info(f"📊 Found {shape_count} shapes on page {i+1}, Uploaded image: {processed_image_url}")

                results.append({
                    "page": i + 1,
                    "text": text,
                    "shape_count": shape_count,
                    "file_name": f"{file_id}.pdf",
                    "type": "application/pdf",
                    "size": os.path.getsize(pdf_path),
                    "processed_image_url": processed_image_url,
                })

            except Exception as img_error:
                logging.error(f"⚠️ Error processing page {i+1}: {img_error}")
                continue  # Skip problematic pages

        logging.info("✅ PDF processing completed successfully!")
        return {"success": True, "results": results}

    except Exception as e:
        logging.error(f"❌ Critical error processing PDF: {e}")
        return {"success": False, "error": str(e)}



@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is working!"}

# ✅ New POST endpoint for greeting
@app.post("/greet/")
async def greet(name: str):
    return {"message": f"Hello, {name}!"}
