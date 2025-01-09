# Use the official Python image as the base image
FROM python:3.11-slim-buster AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip3 install flask

# Copy the Flask application to the working directory
COPY app.py .
COPY config.py .
COPY templates/ ./templates

ENV FLASK_APP=app.py

# Expose the port on which the Flask application will run
EXPOSE 7000

# Set the command to run the Flask application
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=7000"]