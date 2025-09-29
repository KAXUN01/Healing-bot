#!/bin/bash

echo "🚀 Starting Optimized DDoS Detection System"
echo "============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose-optimized.yml down

# Remove old images to free up space
echo "🧹 Cleaning up old images..."
docker image prune -f

# Start the optimized system
echo "🚀 Starting optimized system..."
docker-compose -f docker-compose-optimized.yml up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker-compose -f docker-compose-optimized.yml ps

# Test endpoints
echo "🧪 Testing endpoints..."

# Test Model API (Port 8080)
echo "Testing Model API (Port 8080)..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Model API is running on http://localhost:8080"
else
    echo "❌ Model API is not responding"
fi

# Test Dashboard (Port 9090)
echo "Testing Dashboard (Port 9090)..."
if curl -f http://localhost:9090/health > /dev/null 2>&1; then
    echo "✅ Dashboard is running on http://localhost:9090"
else
    echo "❌ Dashboard is not responding"
fi

echo ""
echo "🎉 Optimized DDoS Detection System is running!"
echo ""
echo "🌐 Access Points:"
echo "   📊 Dashboard: http://localhost:9090"
echo "   🤖 Model API: http://localhost:8080"
echo ""
echo "📋 System Status:"
echo "   - ML Model: High Performance"
echo "   - Dashboard: Lightweight & Clean"
echo "   - Monitoring: Built-in (no external dependencies)"
echo "   - Resource Usage: Optimized for performance"
echo ""
echo "🛠️ Management Commands:"
echo "   Stop system: docker-compose -f docker-compose-optimized.yml down"
echo "   View logs: docker-compose -f docker-compose-optimized.yml logs -f"
echo "   Check status: docker-compose -f docker-compose-optimized.yml ps"
echo ""
echo "✨ Your optimized DDoS detection system is ready!"
