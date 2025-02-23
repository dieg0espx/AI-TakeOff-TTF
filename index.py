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


def count_specific_shape(image, template_path, threshold=0.8):
    template = cv2.imread(template_path, 0)  # Load template in grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Perform template matching
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)  # Get locations where match is above threshold

    return len(list(zip(*loc[::-1])))  # Convert zip object to a list before counting

def detect_shapes_and_upload(image, filename):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Count occurrences of the specific shape
    template_path = "./images/scaffold.png"  # Path to the shape template
    shape_count = count_specific_shape(image, template_path)

    # Draw contours (optional)
    img_copy = np.array(image)
    cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 2)

    # Convert image to bytes
    image_pil = Image.fromarray(img_copy)
    img_bytes = BytesIO()
    image_pil.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Upload to Cloudinary
    response = cloudinary.uploader.upload(
        img_bytes,
        folder="takeOff",
        public_id=f"processed_{filename}"
    )

    print(f"FOUND: {shape_count}")  # ✅ FIXED print statement

    return shape_count, response["secure_url"]

@app.post("/process-pdf/")
async def process_pdf_from_drive(request: FileRequest):
    file_id = request.file_id  # Extract file ID from request
    print(f"Downloading file from Google Drive with ID: {file_id}")

    # Fetch file from Google Drive
    response = requests.get(GOOGLE_DRIVE_DOWNLOAD_URL + file_id)
    
    if response.status_code != 200:
        return {"success": False, "error": "Failed to download file from Google Drive"}

    try:
        pdf_bytes = response.content
        images = pdf2image.convert_from_bytes(pdf_bytes, dpi=300)

        results = []
        for i, image in enumerate(images):
            try:
                text = extract_text_from_image(image)
                shape_count, processed_image_url = detect_shapes_and_upload(image, f"{file_id}_page_{i+1}")

                results.append({
                    "page": i + 1,
                    "text": text,  # Now includes extracted text
                    "shape_count": shape_count,
                    "file_name": f"{file_id}.pdf",
                    "type": "application/pdf",
                    "size": len(pdf_bytes),
                    "processed_image_url": processed_image_url,  # Cloudinary URL
                })
            except Exception as img_error:
                print(f"Error processing page {i+1}: {img_error}")
                continue  # Skip problematic pages

        return {"success": True, "results": results}

    except Exception as e:
        return {"success": False, "error": f"Error processing PDF: {str(e)}"}


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is working!"}

# ✅ New POST endpoint for greeting
@app.post("/greet/")
async def greet(name: str):
    return {"message": f"Hello, {name}!"}
