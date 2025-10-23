# official Python runtime as a parent image
# Using '-slim' makes the image smaller and more efficient
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the file that lists the dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir is a good practice for smaller image sizes
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of application code into the container at /app
# The . in the source path refers to the current directory (where the Dockerfile is)
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define the command to run your app using uvicorn
# This will be the default command when the container starts
# --host 0.0.0.0 is crucial for making it accessible from outside the container
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
