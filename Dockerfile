FROM dvconsultores/sap_hana_lp:latest

# Install VPN packages
RUN apt-get update && \
    apt-get install -y \
    strongswan \
    xl2tpd \
    network-manager \
    iproute2 \
    iputils-ping \
    l2tp-ipsec-vpn \
    sudo \
    expect \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy VPN configuration scripts
COPY vpn_setup.sh /usr/local/bin/vpn_setup.sh
COPY vpn_connect.sh /usr/local/bin/vpn_connect.sh

# Make the scripts executable
RUN chmod +x /usr/local/bin/vpn_setup.sh && \
    chmod +x /usr/local/bin/vpn_connect.sh

# Set the default command (adjust as needed)
CMD ["/usr/local/bin/vpn_setup.sh"]
