#!/bin/bash
# Docker DDoS Detection System Status Script

echo "📊 DDoS Detection System Status"
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

# Check container status
echo "🐳 Container Status:"
docker-compose --env-file docker.env ps

echo ""
echo "📈 Service Health:"
echo "=================="

# Check DDoS Detection System
if curl -f http://localhost:5000/api/status > /dev/null 2>&1; then
    echo "✅ DDoS Detection Dashboard: http://localhost:5000"
else
    echo "❌ DDoS Detection Dashboard: Not accessible"
fi

# Check Model API
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ DDoS Model API: http://localhost:8080"
else
    echo "❌ DDoS Model API: Not accessible"
fi

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✅ Prometheus: http://localhost:9090"
else
    echo "❌ Prometheus: Not accessible"
fi

# Check Grafana
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Grafana: http://localhost:3000"
else
    echo "❌ Grafana: Not accessible"
fi

# Check Nginx
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Nginx Proxy: http://localhost"
else
    echo "❌ Nginx Proxy: Not accessible"
fi

echo ""
echo "📝 Logs:"
echo "========"
echo "  View logs: docker-compose logs -f [service-name]"
echo "  Services: ddos-detection, ddos-model, nginx, redis, prometheus, grafana"
echo ""
echo "🔧 Management:"
echo "=============="
echo "  Start: ./docker-start.sh"
echo "  Stop: ./docker-stop.sh"
echo "  Restart: docker-compose restart [service-name]"
echo "  Rebuild: docker-compose up -d --build"
