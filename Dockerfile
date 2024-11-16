FROM ubuntu:20.04

# Install NetworkManager
RUN apt-get update && \
    apt-get install -y network-manager iproute2 iputils-ping curl dnsutils && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy application files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Start NetworkManager and your app
CMD /usr/sbin/NetworkManager --no-daemon & python app.py
