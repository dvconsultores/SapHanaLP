#!/bin/sh

set -e

echo "[INFO] Sleeping 60 seconds to allow system interfaces to initialize..."
sleep 60

echo "[INFO] Ensuring /var/run/xl2tpd exists..."
mkdir -p /var/run/xl2tpd
rm -f /var/run/xl2tpd/l2tp-control

echo "[INFO] Starting IPsec service..."
ipsec restart
sleep 8

echo "[INFO] Bringing up IPsec tunnel (L2TP-PSK)..."
if ! ipsec up L2TP-PSK; then
    echo "[ERROR] Failed to bring up IPsec tunnel"
    exit 1
fi

echo "[INFO] Restarting xl2tpd service..."
pkill xl2tpd 2>/dev/null || true
mkdir -p /var/run/xl2tpd
rm -f /var/run/xl2tpd/l2tp-control

echo "[DEBUG] Launching xl2tpd in background with config..."
xl2tpd -c /etc/xl2tpd/xl2tpd.conf &
sleep 10  # Give it time to initialize properly

echo "[INFO] Triggering L2TP tunnel connection (LP)..."
if echo "c LP" > /var/run/xl2tpd/l2tp-control; then
    echo "[INFO] L2TP tunnel 'LP' triggered successfully"
else
    echo "[ERROR] Failed to trigger L2TP tunnel 'LP'"
    exit 1
fi

echo "[INFO] Waiting a 15 seconds before checking for ppp0..."
sleep 15

echo "[INFO] Waiting for ppp0 interface..."
ppp_found=false
for i in $(seq 1 20); do
    if ip a | grep -q "ppp0"; then
        echo "[INFO] ppp0 is up!"
        ppp_found=true
        break
    fi
    echo "[INFO] Waiting for ppp0... (${i})"
    sleep 3
done

if [ "$ppp_found" != true ]; then
    echo "[ERROR] ppp0 interface not found. VPN connection failed."
    exit 1
fi

echo "[INFO] Sleeping 30 seconds to let ppp0 stabilize..."
sleep 30

echo "[INFO] Adding route to VPN subnet..."
ip route add 192.168.14.0/24 dev ppp0 2>/dev/null || echo "[WARN] Route may already exist."

echo "[INFO] Pinging test host (192.168.14.24)..."
if command -v ping >/dev/null 2>&1; then
    ping -c 2 192.168.14.24 || echo "[WARN] Ping failed, continuing anyway..."
else
    echo "[WARN] Ping not found in container. Skipping ping test."
fi

echo "[INFO] VPN connected and test complete."
