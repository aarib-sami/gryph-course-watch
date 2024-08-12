# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its browsers
RUN pip install playwright
RUN playwright install
RUN playwright install-deps  
RUN apt-get install libglib2.0-0\      

# Install system dependencies required by Playwright
RUN apt-get update && \
    apt-get install -y \
    libicu-dev \
    libenchant-2-2 \
    libsecret-1-dev \
    libffi-dev \
    libgles2-mesa-dev \
    libjpeg-dev \
    libevent-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and its dependencies
RUN pip install playwright && playwright install

# Copy the rest of the application code into the container
COPY . .

# Command to run the application
CMD ["gunicorn", "-w", "4", "app:app"]

