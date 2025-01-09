# Use an official Python runtime as a parent image
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

# Set the working directory in the container
RUN mkdir /app
WORKDIR /app

# Copy only the requirements.txt initially, to leverage Docker cache
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]
