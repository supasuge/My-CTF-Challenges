FROM python:3.11-slim-buster AS builder

# Set the working directory in the container

WORKDIR /app


# Install any needed packages specified in requirements.txt
RUN pip3 install flask

# Copy the rest of the application
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 3333

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=3333"]