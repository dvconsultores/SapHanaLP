FROM ubuntu:20.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    network-manager \
    network-manager-l2tp \
    ipsec-tools \
    expect \
    sudo \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install nmcli (though it should already be installed with NetworkManager)
RUN ln -s /usr/bin/nmcli /usr/local/bin/nmcli

# Copy VPN setup scripts into the container
COPY ./vpn-config /etc/vpn-config

# Make the scripts executable
RUN chmod +x /etc/vpn-config/*.sh

# Set environment variables (can also be passed dynamically via docker-compose.yml)
ENV VPN_NAME="LiderPollo1"
ENV VPN_GATEWAY="lider-pollo-hq-vbzczkzdkpc.dynamic-m.com"
ENV VPN_USERNAME="developer@dvconsultores.com"
ENV VPN_PASSWORD="6xU2zcv9"
ENV VPN_PSK="GEq3Bvg5DYpaCcq"
ENV IPSEC_ESP="3des-sha1"
ENV IPSEC_IKE="3des-sha1-modp1024"

# The command to start the VPN configuration script
CMD ["/bin/bash", "/etc/vpn-config/setup-vpn.sh"]
