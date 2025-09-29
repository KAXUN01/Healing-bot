#!/bin/bash

echo "Starting ML Model Performance Dashboard..."
echo

echo "Building and starting dashboard service..."
docker-compose up -d dashboard

echo
echo "Waiting for dashboard to start..."
sleep 10

echo
echo "Dashboard Status:"
docker-compose ps dashboard

echo
echo "========================================"
echo "ML Model Performance Dashboard"
echo "========================================"
echo
echo "Dashboard URL: http://localhost:3001"
echo "Model API: http://localhost:8080"
echo "Monitoring Server: http://localhost:5000"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000"
echo
echo "========================================"
echo

# Try to open dashboard in browser (Linux)
if command -v xdg-open &> /dev/null; then
    echo "Opening dashboard in browser..."
    xdg-open http://localhost:3001
elif command -v open &> /dev/null; then
    echo "Opening dashboard in browser..."
    open http://localhost:3001
fi

echo
echo "Dashboard is running! Press Ctrl+C to stop..."
echo "To stop the dashboard, run: docker-compose down dashboard"

# Keep script running
while true; do
    sleep 1
done
