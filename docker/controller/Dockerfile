# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Set environment variable to disable Python stdout buffering
ENV PYTHONUNBUFFERED=1

# Copy the current directory contents into the container at /app
COPY . /app
COPY dependency-check/k8s-job-worker.yaml /app/k8s-job-worker.yaml
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run controller.py when the container launches
CMD ["python", "./controller.py"]