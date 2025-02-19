import logging
import os
import requests
import pdf2image
import pytesseract
import cloudinary
import cloudinary.uploader
import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image, ImageFile
from PyPDF2 import PdfReader
from pydantic import BaseModel

# Allow truncated images to load instead of failing
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

# Function to Extract Text using OCR
def extract_text_from_image(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    text = pytesseract.image_to_string(gray, config="--psm 6")  # PSM 6 is for text blocks
    return text

# Function to Detect Shapes and Upload to Cloudinary
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

@app.post("/process-pdf/")
async def process_pdf_from_drive(request: FileRequest):
    file_id = request.file_id
    logging.info(f"📥 Received request to process file_id: {file_id}")

    # Define temporary file path
    pdf_path = f"/tmp/{file_id}.pdf"

    # ✅ Step 1: Download File from Google Drive
    try:
        logging.info(f"📡 Downloading file from Google Drive: {file_id}")
        response = requests.get(GOOGLE_DRIVE_DOWNLOAD_URL + file_id, stream=True)

        if response.status_code != 200:
            logging.error(f"❌ Failed to download file: Status {response.status_code}")
            return {"success": False, "error": "Failed to download file from Google Drive"}

        # ✅ Step 2: Save File to Disk
        with open(pdf_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = os.path.getsize(pdf_path)
        logging.info(f"✅ File downloaded successfully: {pdf_path}, Size: {file_size} bytes")

    except Exception as e:
        logging.error(f"❌ Error downloading file: {e}")
        return {"success": False, "error": "Error downloading PDF file"}

    # ✅ Step 3: Verify PDF Integrity
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            num_pages = len(reader.pages)
        logging.info(f"✅ PDF integrity check passed: {num_pages} pages detected")
    except Exception as e:
        logging.error(f"❌ PDF is corrupted: {e}")
        return {"success": False, "error": "Downloaded PDF is corrupted"}

    # ✅ Step 4: Convert PDF to Images
    try:
        logging.info(f"📄 Converting PDF to images...")
        images = pdf2image.convert_from_path(pdf_path, dpi=300)
        logging.info(f"✅ PDF converted: {len(images)} pages detected")
    except Exception as e:
        logging.error(f"❌ Error converting PDF to images: {e}")
        return {"success": False, "error": "Failed to convert PDF to images"}

    # ✅ Step 5: Process Each Image (OCR and Shape Detection)
    results = []
    for i, image in enumerate(images):
        try:
            logging.info(f"🔍 Processing page {i+1}...")

            # Extract text from image
            text = extract_text_from_image(image)
            logging.info(f"📝 Extracted text from page {i+1}: {text[:100]}...")

            # Detect shapes and upload image to Cloudinary
            shape_count, processed_image_url = detect_shapes_and_upload(image, f"{file_id}_page_{i+1}")
            logging.info(f"📊 Found {shape_count} shapes on page {i+1}, Uploaded image: {processed_image_url}")

            results.append({
                "page": i + 1,
                "text": text,
                "shape_count": shape_count,
                "file_name": f"{file_id}.pdf",
                "type": "application/pdf",
                "size": file_size,
                "processed_image_url": processed_image_url,
            })

        except Exception as img_error:
            logging.error(f"⚠️ Error processing page {i+1}: {img_error}")
            continue  # Skip problematic pages

    logging.info("✅ PDF processing completed successfully!")
    return {"success": True, "results": results}

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is working!"}

# ✅ New POST endpoint for greeting
@app.post("/greet/")
async def greet(name: str):
    return {"message": f"Hello, {name}!"}
