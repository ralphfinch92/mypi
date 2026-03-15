#!/bin/bash

while true; do
    clear
    echo "=============================="
    echo "       M Y S C R E E N"
    echo "=============================="
    echo
    echo "Hostname: $(hostname)"
    echo "User: $(whoami)"
    echo "Time: $(date)"
    echo
    echo "IP Address:"
    hostname -I
    echo
    echo "Uptime:"
    uptime -p
    echo
    echo "This is a basic screen test."
    echo
    sleep 1
done
