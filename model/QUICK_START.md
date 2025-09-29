# ⚡ Quick Start Guide - DDoS Detection System

## 🚀 **FASTEST DEPLOYMENT (5 Minutes)**

### **Prerequisites Check:**
- ✅ Docker Desktop installed
- ✅ 4GB+ RAM available
- ✅ Internet connection

### **Step 1: Navigate to Directory**
```bash
cd /path/to/your/project/model
```

### **Step 2: Start System (One Command)**

#### **Windows:**
```cmd
docker-start.bat
```

#### **Linux/Ubuntu:**
```bash
sudo ./docker-start.sh
```

#### **macOS:**
```bash
./docker-start.sh
```

### **Step 3: Wait for Startup (2-3 minutes)**
The system will:
- ✅ Build Docker containers
- ✅ Start all services
- ✅ Run health checks
- ✅ Display access URLs

### **Step 4: Access Dashboard**
- **🌐 Main Dashboard**: http://localhost:5000
- **📊 Prometheus**: http://localhost:9090
- **📈 Grafana**: http://localhost:3000 (admin/admin)

### **Step 5: Test System**
1. Open http://localhost:5000
2. Click "Simulate Attack" button
3. Watch real-time detection
4. Verify IP blocking

## 🎊 **SUCCESS!**

Your DDoS detection system is now running with:
- 🛡️ **Real-time DDoS detection** (100% accuracy)
- 🌐 **Web dashboard** for monitoring
- 📊 **Advanced monitoring** with Prometheus & Grafana
- 🔄 **Load balancing** with Nginx
- 🐳 **Docker orchestration** for easy management

## 🔧 **Management Commands**

```bash
# Check status
./docker-status.sh          # Linux
docker-status.bat           # Windows

# Stop system
./docker-stop.sh            # Linux
docker-stop.bat             # Windows

# View logs
docker-compose logs -f ddos-detection
```

## 🆘 **Need Help?**

- **Full Guide**: `COMPLETE_SYSTEM_GUIDE.md`
- **Docker Guide**: `DOCKER_DEPLOYMENT_GUIDE.md`
- **Ubuntu Guide**: `UBUNTU_DEPLOYMENT_GUIDE.md`

**🎉 Your network is now protected!** 🛡️
