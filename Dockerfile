# Use a Python base image with a standard Debian distribution
FROM python:3.11-bookworm

# Set the working directory
WORKDIR /app

# Install all required system dependencies for Kaleido's bundled browser
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
    libasound2 \
    yes

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Kaleido's bundled browser
# This is a key step. It downloads a browser guaranteed to be compatible with Kaleido.
RUN yes | plotly_get_chrome

# Crucial missing step: Tell Kaleido where to find the executable at runtime.
# plotly_get_chrome installs the browser here, but it's not on the system's PATH.
ENV KALEIDO_CHROMIUM_EXECUTABLE /usr/local/bin/kaleido_get_chrome

# Copy the rest of the application code
COPY . .

# Set the command to run your application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]