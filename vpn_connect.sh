#!/usr/bin/expect

# Set your variables
set vpn_name "LiderPollo1"
set vpn_password "6xU2zcv9"
set vpn_psk "GEq3Bvg5DYpaCcq"

# Start the nmcli command to bring up the VPN
spawn sudo nmcli connection up LiderPollo1 --ask

# Expect prompts for password and PSK
expect "Password" {
    send "$vpn_password\r"
}

expect "Pre-shared key" {
    send "$vpn_psk\r"
}

# Interact with the shell after VPN is connected
interact
