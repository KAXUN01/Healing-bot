from flask import Flask, render_template, Response
import time
import threading
import psutil
import platform
from datetime import datetime
from prometheus_client import Counter, generate_latest, Gauge, CONTENT_TYPE_LATEST
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# Prometheus metrics
REQUEST_COUNT = Counter("request_count", "Total number of requests", ['endpoint'])
CPU_LOAD = Gauge("cpu_load_simulation", "Simulated CPU Load")
MEMORY_USAGE = Gauge("memory_usage_percent", "System memory usage")
SYSTEM_CPU_USAGE = Gauge("system_cpu_percent", "System CPU usage")

def get_system_metrics():
    """Gather system metrics"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage('/').percent
    
    SYSTEM_CPU_USAGE.set(cpu_percent)
    MEMORY_USAGE.set(memory_percent)
    CPU_LOAD.set(cpu_percent)  # Using actual CPU load
    
    return {
        'cpu': cpu_percent,
        'memory': memory_percent,
        'disk': disk_percent
    }

@app.route('/')
def index():
    """Render the main dashboard page"""
    REQUEST_COUNT.labels(endpoint="/").inc()
    return render_template('metrics.html')

@app.route("/metrics")
def metrics():
    """Return Prometheus metrics"""
    get_system_metrics()  # Update metrics before returning
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/cpu")
def cpu_intensive():
    """Simulate CPU intensive task"""
    REQUEST_COUNT.labels(endpoint="/cpu").inc()

    def burn_cpu():
        start = time.time()
        while time.time() - start < 60:
            _ = [x ** 2 for x in range(10000)]
        CPU_LOAD.set(0.0)

    thread = threading.Thread(target=burn_cpu)
    thread.start()
    return "Started CPU load for 60 seconds!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)