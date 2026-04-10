# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend code into the container
COPY . .

# Cloud Run dynamically assigns a PORT environment variable. 
# We tell uvicorn to bind to 0.0.0.0 and use that PORT (or default to 8000 locally).
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]