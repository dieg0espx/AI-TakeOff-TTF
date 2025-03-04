# # Use a lightweight Python image
# FROM python:3.10-slim

# # Set the working directory inside the container
# WORKDIR /app

# # Install system dependencies (Poppler for PDF processing & Tesseract for OCR)
# RUN apt update && apt install -y --no-install-recommends \
#     poppler-utils \
#     tesseract-ocr \
#     libgl1-mesa-glx \
#     && rm -rf /var/lib/apt/lists/*  # Reduce image size by clearing apt cache

# # Copy and install dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the application code
# COPY . .

# # Expose port 8000 for FastAPI
# EXPOSE 8000

# # Run the FastAPI application
# CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000"]

# Use Python base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Install system dependencies (Poppler)
RUN apt-get update && apt-get install -y poppler-utils

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
