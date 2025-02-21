# 173f4a190c64bbac2be2a7a043da70c0

import requests
import time

API_KEY = "173f4a190c64bbac2be2a7a043da70c0"  # Replace with your Convertio API key
PDF_FILE = "input2.pdf"
OUTPUT_FILE = "output2.svg"

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
        return result['data']['id']
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
        print("API Response:", result)  # Debug response

        if 'data' in result:
            status = result['data'].get('step')
            print(f"Conversion step: {status}")

            if status == "finish" and result['data'].get('output'):
                return result['data']['output']['url']
            elif status in ["failed", "error"]:
                raise Exception("Conversion failed.")
        else:
            raise Exception(f"Unexpected API response format: {result}")
        time.sleep(5)


def download_file(download_url, output_path):
    response = requests.get(download_url)
    with open(output_path, 'wb') as file:
        file.write(response.content)
    print(f"File downloaded to {output_path}")

def convert_pdf_to_svg():
    try:
        # Start conversion process
        conv_id = start_conversion()
        print(f"Conversion started with ID: {conv_id}")

        # Upload PDF
        upload_file(conv_id, PDF_FILE)

        # Check conversion status
        download_url = check_status(conv_id)
        print("Conversion complete. Downloading...")

        # Download the converted SVG
        download_file(download_url, OUTPUT_FILE)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    convert_pdf_to_svg()
