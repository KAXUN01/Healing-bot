#!/bin/bash
# Ubuntu DDoS Detection System Setup Script

echo "🛡️  Setting up DDoS Detection System for Ubuntu"
echo "=============================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root (use sudo)"
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Python and pip
echo "🐍 Installing Python and pip..."
apt install -y python3 python3-pip python3-venv

# Install system dependencies
echo "🔧 Installing system dependencies..."
apt install -y iptables ufw net-tools psutil

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip3 install tensorflow numpy flask flask-socketio psutil

# Create system user for DDoS detection
echo "👤 Creating system user..."
useradd -r -s /bin/false ddos-detector || echo "User already exists"

# Create directories
echo "📁 Creating directories..."
mkdir -p /var/log/ddos-detection
mkdir -p /opt/ddos-detection
mkdir -p /etc/ddos-detection

# Set permissions
chown -R ddos-detector:ddos-detector /var/log/ddos-detection
chown -R ddos-detector:ddos-detector /opt/ddos-detection
chown -R ddos-detector:ddos-detector /etc/ddos-detection

# Copy files to system directories
echo "📋 Installing system files..."
cp ubuntu_ddos_detector.py /opt/ddos-detection/
cp web_dashboard.py /opt/ddos-detection/
cp ddos_model_retrained.keras /opt/ddos-detection/

# Set permissions
chown -R ddos-detector:ddos-detector /opt/ddos-detection
chmod +x /opt/ddos-detection/*.py

# Create systemd service file
echo "⚙️  Creating systemd service..."
cat > /etc/systemd/system/ddos-detection.service << EOF
[Unit]
Description=DDoS Detection System
After=network.target

[Service]
Type=simple
User=ddos-detector
Group=ddos-detector
WorkingDirectory=/opt/ddos-detection
ExecStart=/usr/bin/python3 /opt/ddos-detection/web_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for detector
cat > /etc/systemd/system/ddos-detector.service << EOF
[Unit]
Description=DDoS Detection Engine
After=network.target

[Service]
Type=simple
User=ddos-detector
Group=ddos-detector
WorkingDirectory=/opt/ddos-detection
ExecStart=/usr/bin/python3 /opt/ddos-detection/ubuntu_ddos_detector.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable ddos-detection.service
systemctl enable ddos-detector.service

# Configure UFW (if available)
if command -v ufw &> /dev/null; then
    echo "🔥 Configuring UFW firewall..."
    ufw --force enable
    ufw allow 5000/tcp  # Web dashboard port
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
fi

# Create log rotation
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/ddos-detection << EOF
/var/log/ddos-detection/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ddos-detector ddos-detector
}
EOF

# Create startup script
echo "🚀 Creating startup script..."
cat > /opt/ddos-detection/start.sh << 'EOF'
#!/bin/bash
# DDoS Detection System Startup Script

echo "🛡️  Starting DDoS Detection System..."

# Start the web dashboard
systemctl start ddos-detection.service

# Start the detection engine
systemctl start ddos-detector.service

echo "✅ DDoS Detection System started"
echo "🌐 Web Dashboard: http://localhost:5000"
echo "📊 Monitor logs: tail -f /var/log/ddos-detection/ddos_detection.log"
EOF

chmod +x /opt/ddos-detection/start.sh

# Create stop script
cat > /opt/ddos-detection/stop.sh << 'EOF'
#!/bin/bash
# DDoS Detection System Stop Script

echo "🛑 Stopping DDoS Detection System..."

# Stop services
systemctl stop ddos-detection.service
systemctl stop ddos-detector.service

echo "✅ DDoS Detection System stopped"
EOF

chmod +x /opt/ddos-detection/stop.sh

# Create status script
cat > /opt/ddos-detection/status.sh << 'EOF'
#!/bin/bash
# DDoS Detection System Status Script

echo "📊 DDoS Detection System Status"
echo "================================"

echo "🔧 Services:"
systemctl status ddos-detection.service --no-pager
echo ""
systemctl status ddos-detector.service --no-pager

echo ""
echo "🌐 Web Dashboard: http://localhost:5000"
echo "📝 Logs: /var/log/ddos-detection/"
echo "⚙️  Config: /etc/ddos-detection/"
EOF

chmod +x /opt/ddos-detection/status.sh

# Create uninstall script
cat > /opt/ddos-detection/uninstall.sh << 'EOF'
#!/bin/bash
# DDoS Detection System Uninstall Script

echo "🗑️  Uninstalling DDoS Detection System..."

# Stop services
systemctl stop ddos-detection.service
systemctl stop ddos-detector.service

# Disable services
systemctl disable ddos-detection.service
systemctl disable ddos-detector.service

# Remove service files
rm -f /etc/systemd/system/ddos-detection.service
rm -f /etc/systemd/system/ddos-detector.service

# Reload systemd
systemctl daemon-reload

# Remove user
userdel ddos-detector 2>/dev/null || true

# Remove directories
rm -rf /opt/ddos-detection
rm -rf /var/log/ddos-detection
rm -rf /etc/ddos-detection

echo "✅ DDoS Detection System uninstalled"
EOF

chmod +x /opt/ddos-detection/uninstall.sh

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🚀 To start the system:"
echo "   sudo /opt/ddos-detection/start.sh"
echo ""
echo "🛑 To stop the system:"
echo "   sudo /opt/ddos-detection/stop.sh"
echo ""
echo "📊 To check status:"
echo "   sudo /opt/ddos-detection/status.sh"
echo ""
echo "🌐 Web Dashboard will be available at:"
echo "   http://localhost:5000"
echo ""
echo "📝 Logs are stored in:"
echo "   /var/log/ddos-detection/"
echo ""
echo "⚙️  Configuration files:"
echo "   /etc/ddos-detection/"
echo ""
echo "🎉 DDoS Detection System is ready for Ubuntu!"
