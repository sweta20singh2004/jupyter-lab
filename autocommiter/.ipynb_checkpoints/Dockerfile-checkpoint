# Use the official Python image from the Docker Hub
FROM python:3.9-slim
RUN pip install --upgrade pip
# Install Git
RUN apt-get update && \
    apt-get install -y git
# Set the working directory
WORKDIR /

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and templates into the container
COPY auto_committer.py auto_committer.py
# Ensure the environment variables are sourced

# Expose the port the app runs on
EXPOSE 5009

# Run the application
CMD ["python", "auto_committer.py"]
