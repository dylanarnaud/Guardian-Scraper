# Use the official Python image from the DockerHub
FROM python:3.10.0

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt requirements.txt

# Install the Python dependencies
RUN pip3 install -r requirements.txt

# Copy the rest of the code into the container
COPY . .

# Set the command to run your application
CMD ["python", "app.py"]