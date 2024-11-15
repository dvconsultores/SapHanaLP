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

# Install nmcli
RUN ln -s /usr/bin/nmcli /usr/local/bin/nmcli

# Ensure NetworkManager service is enabled
RUN systemctl enable NetworkManager.service

# Copy VPN scripts into the container
COPY ./openvpn-config /etc/openvpn-config

# Make the scripts executable
RUN chmod +x /etc/openvpn-config/*.sh

# Set environment variables (or mount them later if required)
ENV VPN_NAME="LiderPollo1"
ENV VPN_GATEWAY="lider-pollo-hq-vbzczkzdkpc.dynamic-m.com"
ENV VPN_USERNAME="developer@dvconsultores.com"
ENV VPN_PASSWORD="6xU2zcv9"
ENV VPN_PSK="GEq3Bvg5DYpaCcq"
ENV IPSEC_ESP="3des-sha1"
ENV IPSEC_IKE="3des-sha1-modp1024"

# Run the VPN setup script on container start
CMD ["/etc/openvpn-config/setup-vpn.sh"]
