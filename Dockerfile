# Use a Python base image with a Debian distribution
FROM python:3.11-slim-bookworm

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libgtk-4-1 \
    libgraphene-1.0-0 \
    libgstreamer-gl1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libenchant-2-2 \
    libsecret-1-0 \
    libmanette-0.2-0 \
    libgles2 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright's browsers
RUN playwright install

# Copy the rest of the application code
COPY . .

# Set the command to run your application
CMD ["python", "main.py"]