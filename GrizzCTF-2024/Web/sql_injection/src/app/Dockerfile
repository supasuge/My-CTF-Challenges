# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY app.py database.db flag.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir flask

# Make port 6000 available to the world outside this container
EXPOSE 9000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=9000"]
