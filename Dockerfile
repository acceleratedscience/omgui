# Use a Python base image with a Debian distribution
FROM python:3.11-bookworm

# Install system dependencies for keleido
# This is needed to be able to download PNG/SVG charts
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2

# Set the working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install chromium for SVG/PNG charts
RUN yes | plotly_get_chrome

# Copy the rest of the application code
COPY . .

# Set the command to run your application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]