# Use the official Python image as a base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install gcc
RUN apt-get update && \
    apt-get install -y gcc

# Install tzdata
RUN apt-get install -y tzdata

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
