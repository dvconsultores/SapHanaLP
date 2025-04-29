# Start from the Python image
FROM python:3.11-slim AS python_env

# Install VPN, Supervisor, and Python dependencies
RUN apt-get update && apt-get install -y \
    strongswan \
    xl2tpd \
    ppp \
    iputils-ping \
    iproute2 \
    net-tools \
    curl \
    netcat-openbsd \
    supervisor \
    network-manager \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Ensure runtime directory exists for xl2tpd
RUN mkdir -p /var/run/xl2tpd

# Set the working directory
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the FastAPI port
EXPOSE 8000

# Run supervisord to manage processes
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

