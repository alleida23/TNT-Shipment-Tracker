# Use the official Python image as a base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install gcc
RUN apt-get update && \
    apt-get install -y gcc

# Install tzdata
RUN apt-get install -y tzdata

# Install Chrome and Chromedriver dependencies
RUN apt-get install -y \
    wget \
    unzip

# Download and install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || true \
    && apt-get -f install -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm google-chrome-stable_current_amd64.deb

# Download and install Chromedriver
RUN apt-get install -y curl \
    && CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && rm chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/


# Copy only the requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . /app/

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define the command to run your application
CMD ["streamlit", "run", "TNT_Shipment_Tracker_App.py"]
