import os
import sys
from openai import OpenAI
import base64

# Replace with your actual OpenAI API key
client = OpenAI(api_key='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')

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
                    "text": "in the image you will find ascaffolding drawing. Please count the amount of elements inside the black areas... return an integer as an answer"
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
except ValueError:
    print('The response was not an integer:', response_text)
