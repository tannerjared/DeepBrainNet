# Use a Python 3.9 slim base image
FROM python:3.9-slim

# Install system dependencies needed by Pillow and nibabel
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy repository files into /app
WORKDIR /app
COPY . /app

# Install Python dependencies (adjust versions if needed)
RUN pip install --upgrade pip && \
    pip install tensorflow==2.15.0 keras nibabel pillow scikit-learn numpy pandas

# Change working directory to the Script folder so that Slicer.py and Model_Test.py are found
WORKDIR /app/Script

# Make test.sh executable
RUN chmod +x test.sh

# Set the entrypoint to run test.sh (which calls python Slicer.py and Model_Test.py)
ENTRYPOINT ["bash", "test.sh"]
