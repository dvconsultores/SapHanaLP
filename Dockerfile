# Start from the Python slim image
FROM python:3.11-slim

# Install NetworkManager, supervisord, and dependencies
RUN apt-get update && \
    apt-get install -y network-manager supervisor iproute2 iputils-ping curl dnsutils && \
    apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start supervisord to manage NetworkManager and the Python app
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
