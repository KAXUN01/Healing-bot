#!/bin/bash
# Docker DDoS Detection System Stop Script

echo "🛑 Stopping DDoS Detection System"
echo "================================="

# Stop all services
echo "🐳 Stopping Docker containers..."
docker-compose --env-file docker.env down

# Remove volumes (optional - uncomment if you want to clean data)
# echo "🗑️  Removing volumes..."
# docker-compose --env-file docker.env down -v

# Remove images (optional - uncomment if you want to clean images)
# echo "🗑️  Removing images..."
# docker-compose --env-file docker.env down --rmi all

echo "✅ DDoS Detection System stopped"
echo ""
echo "📝 To start again: ./docker-start.sh"
echo "🧹 To clean everything: docker-compose down -v --rmi all"
