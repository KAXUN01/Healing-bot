from flask import Flask, render_template_string
import time
import threading
import psutil
import platform
from datetime import datetime
from prometheus_client import Counter, generate_latest, Gauge, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter("request_count", "Total number of requests", ['endpoint'])
CPU_LOAD = Gauge("cpu_load_simulation", "Simulated CPU Load")
MEMORY_USAGE = Gauge("memory_usage_percent", "System memory usage")
SYSTEM_CPU_USAGE = Gauge("system_cpu_percent", "System CPU usage")

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>System Monitoring Dashboard</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .metric { margin: 10px 0; }
        .metric-title { font-weight: bold; color: #333; }
        .metric-value { color: #2196F3; }
        .status { padding: 5px 10px; border-radius: 3px; }
        .status-good { background: #4CAF50; color: white; }
        .status-warning { background: #FFC107; color: black; }
        .status-critical { background: #F44336; color: white; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>System Monitoring Dashboard</h1>
        <div class="grid">
            <div class="card">
                <h2>System Information</h2>
                <div class="metric">
                    <span class="metric-title">Hostname:</span>
                    <span class="metric-value">{{ system_info.hostname }}</span>
                </div>
                <div class="metric">
                    <span class="metric-title">Platform:</span>
                    <span class="metric-value">{{ system_info.platform }}</span>
                </div>
                <div class="metric">
                    <span class="metric-title">Uptime:</span>
                    <span class="metric-value">{{ system_info.uptime }}</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Resource Usage</h2>
                <div class="metric">
                    <span class="metric-title">CPU Usage:</span>
                    <span class="metric-value">{{ resource_usage.cpu }}%</span>
                    <span class="status {{ resource_usage.cpu_status }}">
                        {{ "Normal" if resource_usage.cpu < 70 else "Warning" if resource_usage.cpu < 90 else "Critical" }}
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-title">Memory Usage:</span>
                    <span class="metric-value">{{ resource_usage.memory }}%</span>
                    <span class="status {{ resource_usage.memory_status }}">
                        {{ "Normal" if resource_usage.memory < 70 else "Warning" if resource_usage.memory < 90 else "Critical" }}
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-title">Disk Usage:</span>
                    <span class="metric-value">{{ resource_usage.disk }}%</span>
                    <span class="status {{ resource_usage.disk_status }}">
                        {{ "Normal" if resource_usage.disk < 70 else "Warning" if resource_usage.disk < 90 else "Critical" }}
                    </span>
                </div>
            </div>

            <div class="card">
                <h2>Request Statistics</h2>
                <div class="metric">
                    <span class="metric-title">Total Requests:</span>
                    <span class="metric-value">{{ request_stats.total }}</span>
                </div>
                <div class="metric">
                    <span class="metric-title">Last Request:</span>
                    <span class="metric-value">{{ request_stats.last_request }}</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

def get_system_metrics():
    """Gather system metrics"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage('/').percent
    
    SYSTEM_CPU_USAGE.set(cpu_percent)
    MEMORY_USAGE.set(memory_percent)
    
    return {
        'cpu': cpu_percent,
        'memory': memory_percent,
        'disk': disk_percent,
        'cpu_status': 'status-good' if cpu_percent < 70 else 'status-warning' if cpu_percent < 90 else 'status-critical',
        'memory_status': 'status-good' if memory_percent < 70 else 'status-warning' if memory_percent < 90 else 'status-critical',
        'disk_status': 'status-good' if disk_percent < 70 else 'status-warning' if disk_percent < 90 else 'status-critical'
    }

@app.route("/")
def hello():
    REQUEST_COUNT.labels(endpoint="/").inc()
    
    # Get system information
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    system_info = {
        'hostname': platform.node(),
        'platform': f"{platform.system()} {platform.release()}",
        'uptime': f"{uptime.days} days, {uptime.seconds // 3600} hours, {(uptime.seconds % 3600) // 60} minutes"
    }
    
    # Get resource usage
    resource_usage = get_system_metrics()
    
    # Get request statistics
    request_stats = {
        'total': sum(REQUEST_COUNT.collect()[0].samples[i].value for i in range(len(REQUEST_COUNT.collect()[0].samples))),
        'last_request': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return render_template_string(HTML_TEMPLATE, 
                                system_info=system_info,
                                resource_usage=resource_usage,
                                request_stats=request_stats)

@app.route("/cpu")
def cpu_intensive():
    REQUEST_COUNT.labels(endpoint="/cpu").inc()
    CPU_LOAD.set(1.0)  # simulate high CPU load

    def burn_cpu():
        start = time.time()
        while time.time() - start < 60:  # keep CPU busy for 20 seconds
            _ = [x ** 2 for x in range(10000)]
        CPU_LOAD.set(0.0)  # reset after load

    thread = threading.Thread(target=burn_cpu)
    thread.start()

    return "Started CPU load for 60 seconds!"

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
