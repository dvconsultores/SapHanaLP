# Stage 1: Install NetworkManager and nmcli
FROM dvconsultores/sap_hana_lp:latest AS base

# Install NetworkManager and nmcli
RUN apt-get update && \
    apt-get install -y network-manager

# Stage 2: Set up Python environment
FROM python:3.11-slim AS python_env

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Copy the NetworkManager installation from the base image
COPY --from=base /usr/sbin/nmcli /usr/sbin/nmcli
COPY --from=base /etc/NetworkManager /etc/NetworkManager

# Run the main script
CMD ["python", "app.py"]
