#!/bin/bash
echo "[*] Installing Python dependencies..."
pkg update -y && pkg install -y python git
pip install -r requirements.txt
echo "[+] Installed successfully!"
