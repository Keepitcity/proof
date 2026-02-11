#!/bin/bash
# Aerial Canvas QA Tool - Server Setup Script
# Just paste this entire script into your server terminal

echo "========================================="
echo "  Aerial Canvas QA Tool - Setup"
echo "========================================="
echo ""

# Update system
echo "[1/6] Updating system..."
apt update && apt upgrade -y

# Install dependencies
echo "[2/6] Installing Python, FFmpeg, and dependencies..."
apt install -y python3 python3-pip python3-venv ffmpeg git curl

# Create app directory
echo "[3/6] Creating app directory..."
mkdir -p /opt/qa-tool
cd /opt/qa-tool

# Create virtual environment
echo "[4/6] Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "[5/6] Installing Python packages (this takes a minute)..."
pip install --upgrade pip
pip install streamlit opencv-python-headless numpy Pillow requests dropbox ultralytics

# Create systemd service
echo "[6/6] Creating background service..."
cat > /etc/systemd/system/qa-tool.service << 'EOF'
[Unit]
Description=Aerial Canvas QA Tool
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/qa-tool
Environment=PATH=/opt/qa-tool/venv/bin:/usr/bin
ExecStart=/opt/qa-tool/venv/bin/streamlit run qa_tool.py --server.port 8502 --server.address 0.0.0.0
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable qa-tool

# Create streamlit config
mkdir -p /opt/qa-tool/.streamlit
cat > /opt/qa-tool/.streamlit/config.toml << 'EOF'
[server]
headless = true
port = 8502
address = "0.0.0.0"
maxUploadSize = 500

[browser]
gatherUsageStats = false
EOF

# Open firewall
echo "Opening firewall port 8502..."
ufw allow 8502/tcp 2>/dev/null || true

echo ""
echo "========================================="
echo "  SERVER SETUP COMPLETE!"
echo "========================================="
echo ""
echo "Next step: Upload your app files."
echo ""
echo "On your Mac, run these commands:"
echo ""
echo "  cd \"/Users/shawnhernandez/AI/Aerial Canvas /QA Tool\""
echo "  scp qa_tool.py root@YOUR_SERVER_IP:/opt/qa-tool/"
echo "  scp requirements.txt root@YOUR_SERVER_IP:/opt/qa-tool/"
echo ""
echo "Then come back here and run:"
echo ""
echo "  systemctl start qa-tool"
echo ""
echo "Your app will be live at: http://YOUR_SERVER_IP:8502"
echo ""
