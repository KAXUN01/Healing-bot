@echo off
REM Docker DDoS Detection System Startup Script for Windows

echo 🛡️  Starting DDoS Detection System with Docker
echo ==============================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist grafana\provisioning mkdir grafana\provisioning

REM Build and start services
echo 🐳 Building and starting Docker containers...
docker-compose --env-file docker.env up -d --build

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check service status
echo 📊 Checking service status...
docker-compose ps

REM Display access information
echo.
echo 🎉 DDoS Detection System is running!
echo =====================================
echo.
echo 🌐 Web Dashboard: http://localhost:5000
echo 🔧 Model API: http://localhost:8080
echo 📊 Prometheus: http://localhost:9090
echo 📈 Grafana: http://localhost:3000 (admin/admin)
echo 🔄 Nginx Proxy: http://localhost:80
echo.
echo 📝 Logs:
echo   docker-compose logs -f ddos-detection
echo   docker-compose logs -f ddos-model
echo.
echo 🛑 To stop: docker-stop.bat
echo 📊 To check status: docker-status.bat
echo.

REM Test the system
echo 🧪 Testing system...
timeout /t 10 /nobreak >nul

REM Test web dashboard
curl -f http://localhost:5000/api/status >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Web Dashboard is accessible
) else (
    echo ❌ Web Dashboard is not accessible
)

REM Test model API
curl -f http://localhost:8080/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Model API is accessible
) else (
    echo ❌ Model API is not accessible
)

echo.
echo 🎊 System startup complete!
echo    Access your dashboard at: http://localhost:5000
pause
