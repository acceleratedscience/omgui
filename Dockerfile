# Use a Python base image with a standard Debian distribution
FROM python:3.11-bookworm

# Set the working directory
WORKDIR /app

# Install system dependencies needed for adding the repository
RUN apt-get update && apt-get install -y wget gnupg unzip

# Add the Google Chrome GPG key and repository to the system
RUN wget -O- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Update the apt-get package list to include the new repository
RUN apt-get update

# Install google-chrome-stable and all of its dependencies
RUN apt-get install -y google-chrome-stable

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the command to run your application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]