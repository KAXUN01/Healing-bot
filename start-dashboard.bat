@echo off
echo Starting ML Model Performance Dashboard...
echo.

echo Building and starting dashboard service...
docker-compose up -d dashboard

echo.
echo Waiting for dashboard to start...
timeout /t 10 /nobreak > nul

echo.
echo Dashboard Status:
docker-compose ps dashboard

echo.
echo ========================================
echo ML Model Performance Dashboard
echo ========================================
echo.
echo Dashboard URL: http://localhost:3001
echo Model API: http://localhost:8080
echo Monitoring Server: http://localhost:5000
echo Prometheus: http://localhost:9090
echo Grafana: http://localhost:3000
echo.
echo ========================================
echo.
echo Opening dashboard in browser...
start http://localhost:3001

echo.
echo Dashboard is running! Press any key to stop...
pause > nul

echo.
echo Stopping dashboard...
docker-compose down dashboard
