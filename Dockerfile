# Use a base image with Python
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

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

RUN playwright install-deps 

# Copy the rest of the application code into the container
COPY . .

# Expose the port your app runs on
EXPOSE 8080

# Command to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
