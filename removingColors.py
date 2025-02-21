import os
from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import cv2

# Convert hex color to HSV
def hex_to_hsv(hex_color):
    hex_color = hex_color.lstrip("#")
    rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    bgr_color = np.uint8([[rgb_color[::-1]]])  # Convert RGB to BGR for OpenCV
    hsv_color = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2HSV)[0][0]
    return hsv_color

# Convert PDF to images
def convert_pdf_to_images(input_pdf_path, output_folder, dpi=300):
    pages = convert_from_path(input_pdf_path, dpi=dpi)
    os.makedirs(output_folder, exist_ok=True)
    image_paths = []
    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder, f"page_{i+1}.png")
        page.save(image_path, "PNG")
        image_paths.append(image_path)
    return image_paths

# Remove specific colors and keep only black on a white background
def keep_only_black_elements(image_path, hex_colors):
    image = cv2.imread(image_path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color ranges with a tighter tolerance
    tolerance = 15
    mask = np.zeros(image.shape[:2], dtype=np.uint8)  # Empty mask to keep black elements

    # Remove target colors
    for hex_color in hex_colors:
        hsv_color = hex_to_hsv(hex_color)
        lower_bound = np.array([max(0, hsv_color[0] - tolerance), 50, 50])
        upper_bound = np.array([min(179, hsv_color[0] + tolerance), 255, 255])

        # Create mask for unwanted colors
        color_mask = cv2.inRange(hsv, lower_bound, upper_bound)
        mask = cv2.bitwise_or(mask, color_mask)

    # Create an inverted mask to keep black elements
    inverted_mask = cv2.bitwise_not(mask)
    
    # Convert non-black areas to white
    result = cv2.bitwise_and(image, image, mask=inverted_mask)
    result[mask > 0] = [255, 255, 255]

    # Convert everything except black to white
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    _, final_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    final_image = np.full_like(image, 255)  # White background
    final_image[final_mask > 0] = [0, 0, 0]  # Keep black elements only

    cv2.imwrite(image_path, final_image)

# Convert images back to PDF
def images_to_pdf(image_paths, output_pdf_path):
    images = [Image.open(path).convert("RGB") for path in image_paths]
    images[0].save(output_pdf_path, save_all=True, append_images=images[1:])

# Main function to process the PDF
def process_pdf(input_pdf, output_pdf):
    output_folder = "pdf_images"
    target_colors = ["#F7DE7F", "#D03625", "#3B58FF", "#A9F027"]

    # Step 1: Convert PDF to images
    image_paths = convert_pdf_to_images(input_pdf, output_folder)

    # Step 2: Remove specific colored elements from images
    for image_path in image_paths:
        keep_only_black_elements(image_path, target_colors)

    # Step 3: Convert cleaned images back to PDF
    images_to_pdf(image_paths, output_pdf)
    print(f"Cleaned PDF saved at {output_pdf}")

# Example usage
if __name__ == "__main__":
    input_pdf = "input.pdf"
    output_pdf = "cleaned_output.pdf"
    process_pdf(input_pdf, output_pdf)
