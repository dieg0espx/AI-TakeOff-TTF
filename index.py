# START SERVER : uvicorn index:app --host 0.0.0.0 --port 8000 --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import asyncio
import pytesseract
from pdf2image import convert_from_path
import os
from dotenv import load_dotenv
import subprocess
import sys
import json
import cloudinary
import cloudinary.uploader
from cairosvg import svg2png
from datetime import datetime

from openai import OpenAI
import base64
import openai
# Load environment variables from .env file
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify your frontend URL)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Add this to expose WebSocket headers
)

# Access environment variables
GOOGLE_DRIVE_DOWNLOAD_URL = os.getenv("GOOGLE_DRIVE_DOWNLOAD_URL")
API_KEY = os.getenv("API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Set OpenAI API key
# openai.api_key = OPENAI_API_KEY

# Ensure your OpenAI API key is set
openai.api_key = OPENAI_API_KEY

# Global variables
extracted_text = ""
useConvertio = True  # Set this to False to skip conversion to SVG

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

@app.post("/process-pdf/{file_id}")
async def read_file(file_id: str):
    # Download the file from Google Drive
    download_url = f"{GOOGLE_DRIVE_DOWNLOAD_URL}{file_id}"
    response = requests.get(download_url)
    
    if response.status_code == 200:
        # Temporary file name
        temp_file_name = f"{file_id}.pdf"
        with open(temp_file_name, "wb") as file:
            file.write(response.content)
        
        # Get file size
        file_size = os.path.getsize(temp_file_name)
        print(f"File size: {file_size} bytes")
        
        # Ensure data.json exists
        if not os.path.exists('data.json'):
            with open('data.json', 'w') as file:
                json.dump({}, file)

        # Store the original file name and size in data.json
        with open('data.json', 'r+') as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                data = {}
            data['file_name'] = temp_file_name
            data['file_size'] = file_size
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()  # Ensure no leftover data
            print("Data stored in data.json:", data)
        
        # Rename the file to original.pdf
        os.rename(temp_file_name, "original.pdf")
        
        # Extract text from the PDF using Tesseract
        extract_text_from_pdf("original.pdf")
        
        # Check if conversion to SVG should be performed
        if useConvertio:
            # Start conversion to SVG
            conversion_id = await start_conversion()
            await upload_file(conversion_id, "original.pdf")
            svg_url = await check_status(conversion_id)
            await download_file(svg_url, "original.svg")

            # Convert SVG to PNG
            with open('original.svg', 'rb') as svg_file:
                svg_content = svg_file.read()
            
            svg2png(bytestring=svg_content, write_to='original.png', background_color="white")

            # Upload to Cloudinary
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            url = upload_image_to_cloudinary('original.png', f"original_takeOff_{timestamp}")

            if url:
                # Store the URL in data.json
                with open('data.json', 'r+') as json_file:
                    data = json.load(json_file)
                    data['original_drawing'] = url
                    json_file.seek(0)
                    json.dump(data, json_file, indent=4)
                print(f"Image uploaded to Cloudinary. URL: {url}")
            else:
                print("Failed to upload image to Cloudinary.")

            message = "File downloaded, text extracted, converted to SVG, and uploaded to Cloudinary successfully"
        else:
            message = "File downloaded and text extracted successfully"
        
        # Execute steps_index.py
        execute_steps_index()

        # Remove specified files before returning the response
        files_to_remove = [
            "original.pdf", "original.png", "original.svg", "pairsToJoin.txt",
            "Step1.svg", "Step2.svg", "Step3.svg", "Step4.svg",
            "Step5.svg", "Step6.svg", "Step7.svg",
            "Step6.png", "Step7.png"
        ]
        for file_name in files_to_remove:
            if os.path.exists(file_name):
                os.remove(file_name)

        # Read the contents of data.json to return as response
        with open('data.json', 'r') as json_file:
            data = json.load(json_file)

        return data  # Return the contents of data.json
    else:
        return {"error": "Failed to download file", "status_code": response.status_code}

def execute_steps_index():
    # List of step scripts to execute
    step_scripts = [
        "Step1.py",
        "Step2.py",
        "Step3.py",
        "Step4.py",
        "Step5.py",
        "Step6.py",
        "Step7.py",
        "Step8.py",
        # "Step9.py"
    ]

    for script in step_scripts:
        try:
            print(f"Executing {script}")
            subprocess.run([sys.executable, script], check=True)
            print(f"{script} executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while executing {script}: {e}")
            break  # Stop execution if any script fails

def extract_text_from_pdf(pdf_path):
    global extracted_text
    images = convert_from_path(pdf_path)
    extracted_text = ""
    for image in images:
        text = pytesseract.image_to_string(image)
        extracted_text += text
    # print(extracted_text)  # Print the extracted text to the console
    
    # Rewrite the extracted text using OpenAI
    rewritten_text = rewrite_text_with_openai(extracted_text)
    
    # Append the rewritten text to data.json
    if os.path.exists('data.json'):
        with open('data.json', 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Update the data with the new rewritten text
    data['extracted_text'] = rewritten_text

    # Write updated data back to data.json
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

def rewrite_text_with_openai(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are an expert construction communicator. Rewrite the following text extracted from a scaffolding/shoring. avoid using any special characters. \n\n" + text
                        }
                    ]
                }
            ],
            max_tokens=1500
        )
        rewritten_text = response.choices[0].message.content.strip()
        return rewritten_text
    except Exception as e:
        print(f"An error occurred while rewriting text: {str(e)}")
        return text  # Return original text if rewriting fails

async def start_conversion():
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
        return conversion_id
    else:
        raise Exception(f"❌ Error starting conversion: {result.get('error')}")

async def upload_file(conv_id, file_path):
    upload_url = f"https://api.convertio.co/convert/{conv_id}/upload"
    with open(file_path, 'rb') as file:
        response = requests.put(upload_url, data=file)
        result = response.json()
        if result.get('code') == 200:
            return
        else:
            raise Exception(f"❌ File upload failed: {result.get('error')}")

async def check_status(conv_id):
    status_url = f"https://api.convertio.co/convert/{conv_id}/status"
    while True:
        response = requests.get(status_url)
        result = response.json()
        if 'data' in result:
            status = result['data'].get('step')
            if status == "finish" and result['data'].get('output'):
                return result['data']['output']['url']
            elif status in ["failed", "error"]:
                raise Exception("❌ Conversion failed.")
        await asyncio.sleep(5)

async def download_file(download_url, output_path):
    response = requests.get(download_url)
    with open(output_path, 'wb') as file:
        file.write(response.content)

def upload_image_to_cloudinary(image_path, public_id):
    try:
        with open(image_path, 'rb') as image_file:
            response = cloudinary.uploader.upload(
                image_file,
                folder="takeOff",
                public_id=public_id,
                overwrite=True
            )
        return response["secure_url"]
    except Exception as e:
        print(f"Failed to upload image to Cloudinary: {str(e)}")
        return None

