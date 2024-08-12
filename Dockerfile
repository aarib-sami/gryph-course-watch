# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y \
       libnss3 \
       libx11-dev \
       libxkbcommon0 \
       libgtk-3-0 \
       libdbus-glib-1-2 \
       libasound2 \
       libatk-bridge2.0-0 \
       libatk1.0-0 \
       libcups2 \
       libxcomposite1 \
       libxdamage1 \
       libxrandr2 \
       libgbm1 \
       libpango-1.0-0 \
       libpangocairo-1.0-0 \
       libcairo2 \
       libgdk-pixbuf2.0-0 \
       libnspr4 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . /app/

# Install Playwright browsers
RUN playwright install

CMD ["gunicorn", "-w", "4", "app:app"]
