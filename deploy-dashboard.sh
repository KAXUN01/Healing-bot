#!/bin/bash

echo "🚀 Deploying Updated DDoS Detection Dashboard"
echo "=============================================="

# Stop existing containers
echo "📦 Stopping existing containers..."
docker-compose down

# Remove old dashboard image to force rebuild
echo "🗑️ Removing old dashboard image..."
docker rmi healing-bot_dashboard 2>/dev/null || true

# Build and start the updated dashboard
echo "🔨 Building updated dashboard..."
docker-compose build dashboard

echo "🚀 Starting updated services..."
docker-compose up -d dashboard

# Wait for dashboard to start
echo "⏳ Waiting for dashboard to start..."
sleep 10

# Check dashboard status
echo "📊 Checking dashboard status..."
docker-compose ps dashboard

# Test dashboard endpoint
echo "🧪 Testing dashboard endpoint..."
if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
    echo "✅ Dashboard is running successfully!"
    echo "🌐 Access your dashboard at: http://localhost:3001"
else
    echo "❌ Dashboard health check failed"
    echo "📋 Checking dashboard logs..."
    docker-compose logs dashboard
fi

echo ""
echo "🎉 Deployment completed!"
echo "📊 Dashboard URL: http://localhost:3001"
echo "🤖 Model API: http://localhost:8080"
echo "📈 Monitoring: http://localhost:5000"
