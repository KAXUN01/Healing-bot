@echo off
REM Docker DDoS Detection System Status Script for Windows

echo 📊 DDoS Detection System Status
echo ================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running
    pause
    exit /b 1
)

REM Check container status
echo 🐳 Container Status:
docker-compose --env-file docker.env ps

echo.
echo 📈 Service Health:
echo ==================

REM Check DDoS Detection System
curl -f http://localhost:5000/api/status >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ DDoS Detection Dashboard: http://localhost:5000
) else (
    echo ❌ DDoS Detection Dashboard: Not accessible
)

REM Check Model API
curl -f http://localhost:8080/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ DDoS Model API: http://localhost:8080
) else (
    echo ❌ DDoS Model API: Not accessible
)

REM Check Prometheus
curl -f http://localhost:9090/-/healthy >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Prometheus: http://localhost:9090
) else (
    echo ❌ Prometheus: Not accessible
)

REM Check Grafana
curl -f http://localhost:3000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Grafana: http://localhost:3000
) else (
    echo ❌ Grafana: Not accessible
)

REM Check Nginx
curl -f http://localhost/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Nginx Proxy: http://localhost
) else (
    echo ❌ Nginx Proxy: Not accessible
)

echo.
echo 📝 Logs:
echo ========
echo   View logs: docker-compose logs -f [service-name]
echo   Services: ddos-detection, ddos-model, nginx, redis, prometheus, grafana
echo.
echo 🔧 Management:
echo ==============
echo   Start: docker-start.bat
echo   Stop: docker-stop.bat
echo   Restart: docker-compose restart [service-name]
echo   Rebuild: docker-compose up -d --build
pause
