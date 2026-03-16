# Using a slim image to keep the build light
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Set the entrypoint to your script
# Based on your Procfile: DataCollectionTasks/monoprompt.py
CMD ["python", "DataCollectionTasks/monoprompt.py"]