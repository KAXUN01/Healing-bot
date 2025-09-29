@echo off
echo 🚀 Deploying Updated DDoS Detection Dashboard
echo ==============================================

REM Stop existing containers
echo 📦 Stopping existing containers...
docker-compose down

REM Remove old dashboard image to force rebuild
echo 🗑️ Removing old dashboard image...
docker rmi healing-bot_dashboard 2>nul

REM Build and start the updated dashboard
echo 🔨 Building updated dashboard...
docker-compose build dashboard

echo 🚀 Starting updated services...
docker-compose up -d dashboard

REM Wait for dashboard to start
echo ⏳ Waiting for dashboard to start...
timeout /t 10 /nobreak > nul

REM Check dashboard status
echo 📊 Checking dashboard status...
docker-compose ps dashboard

REM Test dashboard endpoint
echo 🧪 Testing dashboard endpoint...
curl -f http://localhost:3001/api/health > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Dashboard is running successfully!
    echo 🌐 Access your dashboard at: http://localhost:3001
) else (
    echo ❌ Dashboard health check failed
    echo 📋 Checking dashboard logs...
    docker-compose logs dashboard
)

echo.
echo 🎉 Deployment completed!
echo 📊 Dashboard URL: http://localhost:3001
echo 🤖 Model API: http://localhost:8080
echo 📈 Monitoring: http://localhost:5000
