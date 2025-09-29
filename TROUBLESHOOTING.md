# 🔧 Troubleshooting Guide

## 🚨 **DEPENDENCY CONFLICTS**

If you encounter dependency conflicts during Docker build, here are the solutions:

### **Problem: TensorFlow + FastAPI Version Conflicts**
```
ERROR: Cannot install tensorflow 2.13.0 and fastapi 0.104.1 because these package versions have conflicting dependencies.
```

### **Solution 1: Use Simple Requirements**
The system now uses `requirements-simple.txt` which allows pip to resolve compatible versions automatically.

### **Solution 2: Manual Fix**
If you still get conflicts, try this:

```bash
# Edit model/requirements-simple.txt
# Remove specific version numbers and let pip resolve:
tensorflow
numpy
pandas
scikit-learn
fastapi
uvicorn
flask
matplotlib
seaborn
psutil
requests
pydantic
```

### **Solution 3: Alternative Requirements**
Create `model/requirements-alternative.txt`:
```
tensorflow==2.11.0
numpy==1.23.5
pandas==1.5.3
scikit-learn==1.2.2
fastapi==0.95.0
uvicorn==0.21.0
flask==2.2.5
matplotlib==3.6.3
seaborn==0.12.1
psutil==5.9.5
requests==2.28.2
pydantic==1.10.7
```

## 🐳 **DOCKER BUILD ISSUES**

### **Problem: Build Fails**
```bash
ERROR: Service 'model' failed to build : Build failed
```

### **Solutions:**

#### **1. Clean Build:**
```bash
# Clean everything
docker system prune -af
docker volume prune -f

# Rebuild
docker-compose -f docker-compose-optimized.yml build --no-cache
```

#### **2. Build Individual Services:**
```bash
# Build model service
docker build -t ddos-model -f model/Dockerfile model/

# Build dashboard service
docker build -t ddos-dashboard -f model/Dockerfile.dashboard model/
```

#### **3. Use Alternative Base Image:**
Edit `model/Dockerfile`:
```dockerfile
FROM python:3.9-slim-bullseye
```

## 🚀 **STARTUP ISSUES**

### **Problem: Services Won't Start**
```bash
ERROR: Container ddos-model exited with code 1
```

### **Solutions:**

#### **1. Check Logs:**
```bash
docker-compose -f docker-compose-optimized.yml logs -f model
docker-compose -f docker-compose-optimized.yml logs -f dashboard
```

#### **2. Test Individual Components:**
```bash
# Test model API
curl http://localhost:8080/health

# Test dashboard
curl http://localhost:9090/health
```

#### **3. Manual Start:**
```bash
# Start services one by one
docker-compose -f docker-compose-optimized.yml up model -d
docker-compose -f docker-compose-optimized.yml up dashboard -d
```

## 🔧 **QUICK FIXES**

### **Fix 1: Update Requirements**
```bash
# Use the simple requirements
cp model/requirements-simple.txt model/requirements.txt
```

### **Fix 2: Alternative Docker Compose**
Create `docker-compose-simple.yml`:
```yaml
version: '3.8'

services:
  model:
    build:
      context: ./model
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - MODEL_PORT=8080
    restart: unless-stopped

  dashboard:
    build:
      context: ./model
      dockerfile: Dockerfile.dashboard
    ports:
      - "9090:9090"
    environment:
      - DASHBOARD_PORT=9090
    depends_on:
      - model
    restart: unless-stopped
```

### **Fix 3: Minimal System**
If all else fails, run just the model API:
```bash
# Start only the model
docker-compose -f docker-compose-optimized.yml up model -d
```

## 📊 **VERIFICATION**

### **Check System Status:**
```bash
# Check containers
docker-compose -f docker-compose-optimized.yml ps

# Check logs
docker-compose -f docker-compose-optimized.yml logs

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:9090/health
```

### **Expected Output:**
```
✅ Model API: http://localhost:8080/health
✅ Dashboard: http://localhost:9090/health
```

## 🆘 **EMERGENCY FALLBACK**

If nothing works, use the original system:
```bash
# Use original docker-compose
docker-compose up -d --build
```

## 📞 **GET HELP**

1. Check logs: `docker-compose -f docker-compose-optimized.yml logs -f`
2. Verify Docker: `docker info`
3. Test network: `curl http://localhost:8080/health`
4. Check ports: `netstat -tlnp | grep :8080`

**Remember: The optimized system is designed to be lightweight and fast!** 🚀
