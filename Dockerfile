# Use Python 3.10 slim image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the backend requirements and install them
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend source code into the container
COPY backend/ /app/

# Run the FastAPI server, listening on port 7860 for HuggingFace Spaces
CMD uvicorn main:app --host 0.0.0.0 --port 7860
