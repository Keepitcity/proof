# Deploying Proof by Aerial Canvas

## Step 1: Create DigitalOcean Account (5 minutes)

1. Go to: https://www.digitalocean.com
2. Click "Sign Up"
3. Create account with email or Google
4. Add a credit card (required, but you control spending)

---

## Step 2: Create Your Server (3 minutes)

1. Click the green **"Create"** button (top right)
2. Select **"Droplets"**
3. Choose these options:

| Setting | What to Pick |
|---------|--------------|
| Region | **San Francisco** (closest to you) |
| Image | **Ubuntu 22.04 (LTS)** |
| Size | **Premium Intel - $48/mo** (8 GB RAM, 2 CPUs) |
| Authentication | **Password** (create a strong one, save it!) |
| Hostname | `aerial-canvas-qa` |

4. Click **"Create Droplet"**
5. Wait ~60 seconds for it to spin up
6. Copy the **IP Address** shown (looks like `164.92.xxx.xxx`)

---

## Step 3: Connect to Your Server (2 minutes)

**On Mac (Terminal):**
```bash
ssh root@YOUR_IP_ADDRESS
```
- Replace `YOUR_IP_ADDRESS` with the IP from Step 2
- Type "yes" when asked about fingerprint
- Enter the password you created

---

## Step 4: Install Everything (1 command, ~5 minutes to run)

Paste this entire block and press Enter:

```bash
curl -sSL https://raw.githubusercontent.com/aerialcanvas/qa-tool/main/install.sh | bash
```

**If we're not using GitHub yet, paste this instead:**

```bash
# Update system
apt update && apt upgrade -y

# Install Python, pip, ffmpeg, and other dependencies
apt install -y python3 python3-pip python3-venv ffmpeg git

# Create app directory
mkdir -p /opt/qa-tool
cd /opt/qa-tool

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install streamlit opencv-python-headless numpy Pillow requests dropbox ultralytics

# Create a placeholder for the app (we'll upload the real one)
echo "App directory ready at /opt/qa-tool"

# Create systemd service to keep app running
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

# Enable service
systemctl daemon-reload
systemctl enable qa-tool

echo "========================================="
echo "Server is ready!"
echo "Now upload qa_tool.py to /opt/qa-tool/"
echo "========================================="
```

---

## Step 5: Upload Your App (2 minutes)

**From your Mac, open a NEW terminal window:**

```bash
cd "/Users/shawnhernandez/AI/Aerial Canvas /QA Tool"
scp qa_tool.py root@YOUR_IP_ADDRESS:/opt/qa-tool/
scp requirements.txt root@YOUR_IP_ADDRESS:/opt/qa-tool/
```

---

## Step 6: Start the App

**Back in the server terminal (ssh):**

```bash
cd /opt/qa-tool
source venv/bin/activate
pip install -r requirements.txt
systemctl start qa-tool
```

---

## Step 7: Access Your App!

Open in browser:
```
http://YOUR_IP_ADDRESS:8502
```

That's it! Your team can now access this URL from anywhere.

---

## Adding Password Protection

To add a password so only your team can access:

```bash
cd /opt/qa-tool
mkdir -p .streamlit
cat > .streamlit/config.toml << 'EOF'
[server]
headless = true
port = 8502
address = "0.0.0.0"
EOF
```

Then I'll help you add Streamlit's authentication or a simple password page.

---

## Useful Commands

| Command | What it does |
|---------|--------------|
| `systemctl status qa-tool` | Check if app is running |
| `systemctl restart qa-tool` | Restart the app |
| `systemctl stop qa-tool` | Stop the app |
| `journalctl -u qa-tool -f` | View live logs |

---

## Updating the App

When we make changes, just run:

```bash
# From your Mac
cd "/Users/shawnhernandez/AI/Aerial Canvas /QA Tool"
scp qa_tool.py root@YOUR_IP_ADDRESS:/opt/qa-tool/

# Then on the server (ssh)
systemctl restart qa-tool
```

---

## Cost Summary

- DigitalOcean Droplet: **$48/month**
- That's it!

---

## Need Help?

If anything goes wrong, just share what you see on screen and I'll help troubleshoot.
