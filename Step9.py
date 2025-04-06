import cv2
import numpy as np
import requests

# Load the image from the URL
image_url = "https://res.cloudinary.com/dvord9edi/image/upload/v1743717374/iseaamxpyxhpjjm6rk1x.png"
response = requests.get(image_url)
image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

# Convert image to HSV for better color filtering
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define color ranges
black_lower = np.array([0, 0, 0])       # Black (for rectangles)
black_upper = np.array([180, 255, 50])

green_lower = np.array([40, 50, 50])    # Green (for "Z" symbols)
green_upper = np.array([90, 255, 255])

# Create masks for black rectangles and green Z's
black_mask = cv2.inRange(hsv, black_lower, black_upper)
green_mask = cv2.inRange(hsv, green_lower, green_upper)

# Detect contours for black rectangles
black_contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
black_boxes = [cv2.boundingRect(cnt) for cnt in black_contours]

# Detect contours for green Z's
green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Count green Z's inside black rectangles
count = 0
for g_cnt in green_contours:
    gx, gy, gw, gh = cv2.boundingRect(g_cnt)
    green_center = (gx + gw // 2, gy + gh // 2)  # Use the center of the Z for accuracy
    
    for rx, ry, rw, rh in black_boxes:
        if rx <= green_center[0] <= (rx + rw) and ry <= green_center[1] <= (ry + rh):
            count += 1
            break  # Avoid counting the same Z multiple times

print(f"Total green 'Z' symbols inside black rectangles: {count}")
