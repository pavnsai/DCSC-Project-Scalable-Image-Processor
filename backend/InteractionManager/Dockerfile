FROM python:3.9-slim

# Install system dependencies for Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy only necessary files
COPY interaction_pod.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for the Flask app
EXPOSE 8080

# Run the application
ENTRYPOINT ["python", "-u", "interaction_pod.py"]
