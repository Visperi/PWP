# Use stable python:3.11-alpine as the base image
FROM python:3.11-alpine

# Set the working directory in the container
WORKDIR /ranking_api

# Copy the current directory contents into the container
COPY . .

# Install packages specified in requirements.txt
RUN pip install -r requirements.txt

# Run the application with Gunicorn and enable logging
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0", "--log-level", "info", "ranking_api.app:create_app()"]