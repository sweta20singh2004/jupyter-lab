# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and templates into the container
COPY app.py app.py
COPY templates/ templates/

# Ensure the directory for the database file exists
RUN mkdir -p /app/marks_data

# Expose the port the app runs on
EXPOSE 5007

# Run the application
CMD ["python", "app.py"]
