# Start from the Python image
FROM python:3.11-slim AS python_env


# Install VPN and Python dependencies
RUN apt-get update && apt-get install -y \
    strongswan \
    xl2tpd \
    ppp \
    iputils-ping \
    iproute2 \
    net-tools \
    curl \
    netcat-openbsd \
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

# Install supervisor
RUN pip install supervisor

# Run the application using supervisor
CMD ["supervisord", "-c", "/app/supervisord.conf"]

