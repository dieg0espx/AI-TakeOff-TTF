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

# Load environment variables from .env file
load_dotenv()
app = FastAPI()

# Access environment variables
GOOGLE_DRIVE_DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id="
API_KEY = os.getenv("API_KEY")  # Make sure this is set in your .env

async def start_conversion():
    url = "https://api.convertio.co/convert"
    data = {
        "apikey": "2b007718a3f040bb6ac0260982723e48",
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
        "Step1.py",
        "Step2.py",
        "Step3.py",
        "Step4.py",
        "Step5.py",
        "Step6.py",
        "Step7.py",
        "Step8.py",
        "Step9.py"
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
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
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

        return data;

    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)