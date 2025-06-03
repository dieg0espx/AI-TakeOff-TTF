# to run the server:  python3 newIndex.py
# to test: curl -X GET "http://127.0.0.1:5000/AI-Takeoff/1q-2eMWfbQx8ZlE_8EJFt-X_RTRmwfDVW"
# to test: curl -X GET "http://127.0.0.1:5000/AI-Takeoff/1mApCM33bj2t4pg5mV-8u3FOWEPnr6hE6"

from fastapi import FastAPI, HTTPException
import requests
import os
from typing import Optional
from dotenv import load_dotenv
import asyncio
import subprocess
import sys
import json
from pdf2image import convert_from_path
import pytesseract
import openai
from openai import OpenAIError

# Load environment variables from .env file
load_dotenv()
app = FastAPI()

# Access environment variables
GOOGLE_DRIVE_DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id="

# Retrieve API key from environment variable
api_key = os.getenv('API_KEY')

# Retrieve host and port from environment variables
host = os.getenv('HOST', '127.0.0.1')
port = int(os.getenv('PORT', 5000))

openai.api_key = os.getenv('OPENAI_API_KEY')

async def start_conversion():
    url = "https://api.convertio.co/convert"
    data = {
        "apikey": api_key,
        "input": "upload",
        "outputformat": "svg"
    }
    response = requests.post(url, json=data)
    result = response.json()
    if result.get('code') == 200:
        return result['data']['id']
    else:
        raise Exception(f"Error starting conversion: {result.get('error')}")

async def upload_file(conv_id, file_path):
    upload_url = f"https://api.convertio.co/convert/{conv_id}/upload"
    with open(file_path, 'rb') as file:
        response = requests.put(upload_url, data=file)
        result = response.json()
        if result.get('code') != 200:
            raise Exception(f"File upload failed: {result.get('error')}")

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
                raise Exception("Conversion failed.")
        await asyncio.sleep(5)

async def download_file(download_url, output_path):
    response = requests.get(download_url)
    with open(output_path, 'wb') as file:
        file.write(response.content)

# Function to run step scripts sequentially
def run_step_scripts():
    step_scripts = [
        # "Step1.py",
        # "Step2.py",
        # "Step3.py",
        # "Step4.py",
        # "Step5.py",
        # "Step6.py",
        # "Step7.py",
        # "Step8.py",
        # "Step9.py"
    ]
    for script in step_scripts:
        try:
            print(f"Running {script}...")
            subprocess.run([sys.executable, script], check=True)
            print(f"{script} completed.")
        except subprocess.CalledProcessError as e:
            print(f"Error running {script}: {e}")
            raise Exception(f"Step failed: {script}")

@app.get("/AI-Takeoff/{file_id}")
async def download_document(file_id: str):
    try:
        print(f"Attempting to download file with ID: {file_id}")
        
        # Download the file from Google Drive
        download_url = f"{GOOGLE_DRIVE_DOWNLOAD_URL}{file_id}"
        print(f"Download URL: {download_url}")
        
        # Use a session to handle cookies and redirects
        session = requests.Session()
        response = session.get(download_url, allow_redirects=True)
        
        # print(f"Response status code: {response.status_code}")
        # print(f"Response headers: {response.headers}")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=404, 
                detail=f"File not found or not accessible. Status code: {response.status_code}"
            )

        # Check if we got a PDF file
        content_type = response.headers.get('content-type', '')
        if 'application/pdf' not in content_type and 'application/octet-stream' not in content_type:
            print(f"Warning: Unexpected content type: {content_type}")

        # Save the file as original.pdf
        file_path = "files/original.pdf"
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"File saved to: {file_path}")
        print(f"File size: {os.path.getsize(file_path)} bytes")

        # Extract and rewrite text from the PDF
        extract_text_from_pdf(file_path)

        # Convert PDF to SVG using Convertio
        conv_id = await start_conversion()
        await upload_file(conv_id, file_path)
        svg_url = await check_status(conv_id)
        svg_path = "files/original.svg"
        await download_file(svg_url, svg_path)
        print(f"SVG saved to: {svg_path}")

        # Run step scripts after SVG conversion
        run_step_scripts()

        # Read data.json and return its contents as JSON
        data_file = "data.json"
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"error": "data.json not found"}

        # Add file name and file size to the data
        data['file_name'] = file_path
        data['file_size'] = os.path.getsize(file_path)

        return data;

    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Function to extract text from PDF

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

    # Update the data with the new rewritten text, file name, and file size
    data['extracted_text'] = rewritten_text
    data['file_name'] = pdf_path
    data['file_size'] = os.path.getsize(pdf_path)

    # Write updated data back to data.json
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

# Function to rewrite text using OpenAI

def rewrite_text_with_openai(text):
    try:
        if not api_key:
            raise ValueError("API key is not set. Please check your environment variables.")
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": """
                        You are an expert construction communicator specializing in scaffolding and shoring documentation. Your task is to rewrite the extracted text from technical drawings into proper, coherent paragraphs.
                        Please follow these specific guidelines:
                        1. Format all measurements and dimensions in complete sentences with proper context
                        2. Organize related information into logical paragraphs
                        3. Ensure all specifications (dimensions, quantities, materials) are clearly explained
                        4. Convert isolated measurements into proper sentences explaining what they refer to
                        5. Maintain technical accuracy while improving readability
                        6. Avoid any special characters

                        The output should read like a professional construction document that clearly explains all specifications and requirements.
                        Here is the text to rewrite:
                        """ + text
                }
            ],
            max_tokens=1500,
            timeout=20.0  # Set a timeout for the request
        )
        rewritten_text = response.choices[0].message.content.strip()
        return rewritten_text
    except OpenAIError as e:
        print(f"An OpenAI error occurred: {str(e)}")
        return text  # Return original text if rewriting fails
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return text  # Return original text if any other error occurs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=host, port=port)