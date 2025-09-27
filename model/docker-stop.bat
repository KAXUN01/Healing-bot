@echo off
REM Docker DDoS Detection System Stop Script for Windows

echo 🛑 Stopping DDoS Detection System
echo =================================

REM Stop all services
echo 🐳 Stopping Docker containers...
docker-compose --env-file docker.env down

REM Optional: Remove volumes (uncomment if you want to clean data)
REM echo 🗑️  Removing volumes...
REM docker-compose --env-file docker.env down -v

REM Optional: Remove images (uncomment if you want to clean images)
REM echo 🗑️  Removing images...
REM docker-compose --env-file docker.env down --rmi all

echo ✅ DDoS Detection System stopped
echo.
echo 📝 To start again: docker-start.bat
echo 🧹 To clean everything: docker-compose down -v --rmi all
pause
