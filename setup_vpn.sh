#!/bin/bash

# VPN configuration parameters
VPN_NAME="LiderPollo"
VPN_GATEWAY="lider-pollo-hq-vbzczkzdkpc.dynamic-m.com"
VPN_USERNAME="developer@dvconsultores.com"
VPN_PASSWORD="6xU2zcv9"
VPN_PSK="GEq3Bvg5DYpaCcq"
IPSEC_ESP="3des-sha1"
IPSEC_IKE="3des-sha1-modp1024"

# Check if the VPN connection already exists
if nmcli connection show "$VPN_NAME" &> /dev/null; then
    echo "A connection named $VPN_NAME already exists. Deleting it..."
    nmcli connection delete "$VPN_NAME"
fi

# Step 1: Add the L2TP VPN connection with IPsec
echo "Adding VPN connection $VPN_NAME..."
nmcli connection add type vpn vpn-type l2tp con-name LiderPollo \
    vpn.data "gateway=lider-pollo-hq-vbzczkzdkpc.dynamic-m.com, ipsec-enabled=yes, ipsec-esp=3des-sha1, ipsec-ike=3des-sha1-modp1024, machine-auth-type=psk, mru=1400, mtu=1400, password-flags=1, user=developer@dvconsultores.com"

# Step 2: Configure username, password, and PSK
echo "Setting VPN username, password, and PSK..."
nmcli connection modify "$VPN_NAME" vpn.user-name "$VPN_USERNAME"
nmcli connection modify "$VPN_NAME" vpn.secrets "password=$VPN_PASSWORD, psk=$VPN_PSK"

# # Step 3: Bring up the VPN connection
# echo "Activating VPN connection $VPN_NAME..."
# nmcli connection up "$VPN_NAME"

# # Verify connection status
# echo "Checking VPN connection status..."
# nmcli connection show "$VPN_NAME"
