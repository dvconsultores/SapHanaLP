# Start from the Python image
FROM python:3.11-slim AS python_env

# Set noninteractive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install VPN and Python dependencies
RUN apt-get update && apt-get install -y \
    strongswan \
    xl2tpd \
    ppp \
    iputils-ping \
    iproute2 \
    net-tools \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Ensure runtime directory exists for xl2tpd
RUN mkdir -p /var/run/xl2tpd

# Set the working directory
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the project
COPY . .

# Copy the entrypoint (should be at project root)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Entrypoint launches VPN and then Python app
ENTRYPOINT ["/entrypoint.sh"]
