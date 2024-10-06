# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy Firebase credentials
COPY ./firebase_credentials.json /app/credentials/firebase_credentials.json

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables
ENV FLASK_ENV=development

# Run the app
CMD ["python", "app.py"]