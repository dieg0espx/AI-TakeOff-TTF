import os
import sys
from openai import OpenAI
import base64
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Access the OpenAI API key from environment variables
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Path to your local image file
image_path = "Step7.png"

# Check if the image file exists
if not os.path.exists(image_path):
    print(f"Error: The file {image_path} does not exist.")
    sys.exit(1)

# Read and convert the image to base64
with open(image_path, "rb") as image_file:
    image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    base64_url = f"data:image/png;base64,{base64_image}"

response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Please count the amount of red elements... return only a number as an answer"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": base64_url
                    }
                }
            ]
        }
    ],
    max_tokens=300
)

# print('Completion Tokens:', response.usage.completion_tokens)
# print('Prompt Tokens:', response.usage.prompt_tokens)
# print('Total Tokens:', response.usage.total_tokens)

# Extract the integer from the response
response_text = response.choices[0].message.content.strip()
try:
    # Attempt to convert the response to an integer
    result = int(response_text)
    print('Response:', result)
    
    # Append the result to data.json
    if os.path.exists('data.json'):
        with open('data.json', 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Ensure 'objects' key exists
    if 'objects' not in data:
        data['objects'] = {}

    # Append the result under 'underSlab'
    data['objects']['underSlab'] = result

    # Write updated data back to data.json
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

except ValueError:
    print('The response was not an integer:', response_text)
