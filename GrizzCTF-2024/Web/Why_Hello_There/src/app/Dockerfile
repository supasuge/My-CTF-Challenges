# Use the official Python image as the base image
FROM python:3.11-slim-buster AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory

# Install the Python dependencies
RUN pip install flask

# Copy the Flask application to the working directory
COPY app.py .
COPY flag.txt .

# Expose the port on which the Flask application will run
EXPOSE 2222
ENV FLASK_APP=app.py

# Set the command to run the Flask application
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=2222"]