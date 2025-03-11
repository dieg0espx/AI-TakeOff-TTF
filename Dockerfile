# Use Python base image
FROM python:3.9

# Set working directory
WORKDIR /index

# Install system dependencies (Tesseract OCR + Poppler)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Force reinstall WebSocket dependencies
RUN pip install --no-cache-dir uvicorn[standard] websockets wsproto


# Expose the FastAPI port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000", "--ws", "auto"]

