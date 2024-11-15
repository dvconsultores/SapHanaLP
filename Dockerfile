# Start from the Python image
FROM python:3.11-slim AS python_env

# Install NetworkManager and nmcli
RUN apt-get update && \
    apt-get install -y network-manager

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Run the main script
CMD ["python", "app.py"]
