from ultralytics import YOLO
import cv2
import os
import json
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Define paths
IMAGES_DIR = ""
input_path = os.path.join(IMAGES_DIR, "Step6.png")
output_path = os.path.join(IMAGES_DIR, "output.jpg")

# Load model and image
model = YOLO('z_model.pt')  # or your custom model
# Set confidence threshold (0.0 to 1.0, default is 0.25)
results = model(input_path, conf=0.12)[0]  # Adjust the 0.25 value to change tolerance

image = cv2.imread(input_path)
class_counts = {}

# First pass to count elements
for box in results.boxes:
    cls = int(box.cls[0])
    label = model.names[cls]
    class_counts[label] = class_counts.get(label, 0) + 1

# Calculate total count
total_count = sum(class_counts.values())

# Update data.json with the total count
data_file = "data.json"
if os.path.exists(data_file):
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    if 'objects' not in data:
        data['objects'] = {}
    
    data['objects']['total_6x4'] = total_count
    
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

# Draw total count at the top
text = f"Total: {total_count}"
(text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)

# Draw background rectangle for total (keeping same position and size)
rect_x = 10
rect_y = 10
rect_width = text_width + 20
rect_height = text_height + 20
cv2.rectangle(image, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), (89, 255, 0), -1)

# Calculate text position to be centered in the rectangle
text_x = rect_x + (rect_width - text_width) // 2
text_y = rect_y + (rect_height + text_height) // 2

# Draw total text
cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

# Second pass to draw boxes and numbers
element_number = 1  # Start counting from 1
for box in results.boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cls = int(box.cls[0])
    label = model.names[cls]

    # Draw box
    cv2.rectangle(image, (x1, y1), (x2, y2), (89, 255, 0), 4)
    
    # Put sequential number on top of the box
    text = f"{element_number}"
    # Get text size for background rectangle
    (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
    # Draw background rectangle for text
    cv2.rectangle(image, (x1, y1 - text_height - 10), (x1 + text_width + 10, y1), (89, 255, 0), -1)
    # Draw text
    cv2.putText(image, text, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    element_number += 1  # Increment the counter

cv2.imwrite(output_path, image)
print(f"✅ Processed image saved as: {output_path}")
print("Counts:", class_counts)

# Upload image to Cloudinary inside 'AI-TakeOFF' folder
response = cloudinary.uploader.upload(output_path, folder='AI-TakeOFF')
cloudinary_url = response['url']

# Update data.json with the Cloudinary URL
if os.path.exists(data_file):
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    if 'objects' not in data:
        data['objects'] = {}
    
    data['objects']['output1'] = cloudinary_url
    
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)