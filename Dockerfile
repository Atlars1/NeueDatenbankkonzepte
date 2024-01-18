# Use the official Python 3.8 image as the base image
FROM python:3.8

# Set the working directory within the container
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Specify the default command to run when the container starts
# Note: The command is overridden when starting the container
CMD ["python", "main.py"]
