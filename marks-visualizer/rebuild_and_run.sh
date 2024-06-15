#!/bin/bash

# Build the Docker image with no-cache
docker-compose build --no-cache

# Run the Docker Compose services
docker-compose up -d
