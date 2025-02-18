# Use a lightweight Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (Poppler for PDF processing)
RUN apt update && apt install -y poppler-utils tesseract-ocr libgl1-mesa-glx

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure required packages are installed
RUN pip install --no-cache-dir python-multipart opencv-python-headless

# Copy the rest of the application code
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000"]
