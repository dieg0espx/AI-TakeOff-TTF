import os
import cv2
import numpy as np
import cloudinary
import cloudinary.uploader
import pdf2image  # Convert PDF to images
import pytesseract  # OCR for text extraction
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image

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

@app.post("/process-pdf/")
async def process_pdf(file: UploadFile = File(...)):
    print('PROCESSING PDF ....')
    try:
        pdf_bytes = await file.read()
        images = pdf2image.convert_from_bytes(pdf_bytes, dpi=300)

        results = []
        for i, image in enumerate(images):
            text = extract_text_from_image(image)  # Extract text from the page
            # processed_image_url = detect_shapes_and_upload(image, f"{file.filename}_page_{i+1}")
            shape_count, processed_image_url = detect_shapes_and_upload(image, f"{file.filename}_page_{i+1}")


            results.append({
                "page": i + 1,
                "text": text,  # Now includes extracted text
                "shape_count": shape_count,
                "file_name": file.filename,
                "type": file.content_type,
                "size": len(pdf_bytes),
                "processed_image_url": processed_image_url,  # Cloudinary URL
            })

        return {"success": True, "results": results}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is working!"}


# ✅ New POST endpoint for greeting
@app.post("/greet/")
async def greet(name: str = Form(...)):
    return {"message": f"Hello, {name}!"}