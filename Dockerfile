# Start from the Python image
FROM python:3.11-slim AS python_env

# Install NetworkManager and nmcli
RUN apt-get update && \
    apt-get install -y network-manager iproute2 iputils-ping curl dnsutils

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Ensure NetworkManager is running before starting the application
# CMD service network-manager start && \
#     tail -f /dev/null & \
#     python app.py


CMD python app.py