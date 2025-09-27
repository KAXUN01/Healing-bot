#!/bin/bash
# Docker DDoS Detection System Startup Script

echo "🛡️  Starting DDoS Detection System with Docker"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if running as root (required for privileged containers)
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Warning: Not running as root. Some features may not work properly."
    echo "   For full functionality, run with: sudo ./docker-start.sh"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p grafana/provisioning

# Set permissions
echo "🔐 Setting permissions..."
chmod +x docker-start.sh
chmod +x docker-stop.sh
chmod +x docker-status.sh

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose --env-file docker.env up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Display access information
echo ""
echo "🎉 DDoS Detection System is running!"
echo "====================================="
echo ""
echo "🌐 Web Dashboard: http://localhost:5000"
echo "🔧 Model API: http://localhost:8080"
echo "📊 Prometheus: http://localhost:9090"
echo "📈 Grafana: http://localhost:3000 (admin/admin)"
echo "🔄 Nginx Proxy: http://localhost:80"
echo ""
echo "📝 Logs:"
echo "  docker-compose logs -f ddos-detection"
echo "  docker-compose logs -f ddos-model"
echo ""
echo "🛑 To stop: ./docker-stop.sh"
echo "📊 To check status: ./docker-status.sh"
echo ""

# Test the system
echo "🧪 Testing system..."
sleep 10

# Test web dashboard
if curl -f http://localhost:5000/api/status > /dev/null 2>&1; then
    echo "✅ Web Dashboard is accessible"
else
    echo "❌ Web Dashboard is not accessible"
fi

# Test model API
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Model API is accessible"
else
    echo "❌ Model API is not accessible"
fi

echo ""
echo "🎊 System startup complete!"
echo "   Access your dashboard at: http://localhost:5000"
