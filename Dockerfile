# Start from the Python image
FROM python:3.11-slim AS python_env

# Install VPN dependencies
RUN apt-get update \
    && apt-get install -y \
    strongswan \
    xl2tpd \
    ppp \
    network-manager \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

