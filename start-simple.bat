@echo off
echo 🚀 Starting Simple DDoS Detection System
echo =============================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose -f docker-compose-optimized.yml down

REM Clean up
echo 🧹 Cleaning up...
docker system prune -f

REM Build and start the system
echo 🚀 Building and starting optimized system...
docker-compose -f docker-compose-optimized.yml up -d --build

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 60 /nobreak >nul

REM Check service status
echo 📊 Checking service status...
docker-compose -f docker-compose-optimized.yml ps

REM Test endpoints
echo 🧪 Testing endpoints...

REM Test Model API (Port 8080)
echo Testing Model API (Port 8080)...
curl -f http://localhost:8080/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Model API is running on http://localhost:8080
) else (
    echo ❌ Model API is not responding
)

REM Test Dashboard (Port 9090)
echo Testing Dashboard (Port 9090)...
curl -f http://localhost:9090/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Dashboard is running on http://localhost:9090
) else (
    echo ❌ Dashboard is not responding
)

echo.
echo 🎉 Simple DDoS Detection System Status:
echo.
echo 🌐 Access Points:
echo    📊 Dashboard: http://localhost:9090
echo    🤖 Model API: http://localhost:8080
echo.
echo 🛠️ Management Commands:
echo    Stop system: docker-compose -f docker-compose-optimized.yml down
echo    View logs: docker-compose -f docker-compose-optimized.yml logs -f
echo    Check status: docker-compose -f docker-compose-optimized.yml ps
echo.
echo ✨ Your optimized DDoS detection system is ready!
pause
