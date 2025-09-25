from flask import Flask, render_template, Response, jsonify
import time
import threading
import psutil
import platform
import requests
from datetime import datetime
from prometheus_client import Counter, generate_latest, Gauge, CONTENT_TYPE_LATEST
from flask_bootstrap import Bootstrap5
import numpy as np
from collections import deque
import json
import os

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# Prometheus metrics
REQUEST_COUNT = Counter("request_count", "Total number of requests", ['endpoint'])
CPU_LOAD = Gauge("cpu_load_simulation", "Simulated CPU Load")
MEMORY_USAGE = Gauge("memory_usage_percent", "System memory usage")
SYSTEM_CPU_USAGE = Gauge("system_cpu_percent", "System CPU usage")
NETWORK_IN = Gauge("network_in_bytes", "Network incoming bytes")
NETWORK_OUT = Gauge("network_out_bytes", "Network outgoing bytes")
CONNECTIONS = Gauge("active_connections", "Number of active connections")
DDOS_PROBABILITY = Gauge("ddos_probability", "DDoS attack probability")

# Store historical data for graphs
MAX_HISTORY = 100
metrics_history = {
    'timestamps': deque(maxlen=MAX_HISTORY),
    'cpu': deque(maxlen=MAX_HISTORY),
    'memory': deque(maxlen=MAX_HISTORY),
    'network_in': deque(maxlen=MAX_HISTORY),
    'network_out': deque(maxlen=MAX_HISTORY),
    'connections': deque(maxlen=MAX_HISTORY),
    'ddos_prob': deque(maxlen=MAX_HISTORY)
}

def get_network_stats():
    """Get network statistics"""
    net_io = psutil.net_io_counters()
    connections = len(psutil.net_connections())
    return net_io.bytes_recv, net_io.bytes_sent, connections

def get_system_metrics():
    """Gather system metrics"""
    try:
        # Basic system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Network metrics
        net_in, net_out, conn_count = get_network_stats()
        
        # Update Prometheus metrics
        SYSTEM_CPU_USAGE.set(cpu_percent)
        MEMORY_USAGE.set(memory_percent)
        CPU_LOAD.set(cpu_percent)
        NETWORK_IN.set(net_in)
        NETWORK_OUT.set(net_out)
        CONNECTIONS.set(conn_count)
        
        # Update historical data
        current_time = datetime.now().strftime('%H:%M:%S')
        metrics_history['timestamps'].append(current_time)
        metrics_history['cpu'].append(cpu_percent)
        metrics_history['memory'].append(memory_percent)
        metrics_history['network_in'].append(net_in)
        metrics_history['network_out'].append(net_out)
        metrics_history['connections'].append(conn_count)
        CPU_LOAD.set(cpu_percent)
        
        return {
            'cpu': cpu_percent,
            'memory': memory_percent,
            'disk': disk_percent,
            'memory_available': memory.available / (1024 * 1024 * 1024),  # GB
            'disk_free': disk.free / (1024 * 1024 * 1024)  # GB
        }
    except Exception as e:
        app.logger.error(f"Error collecting system metrics: {str(e)}")
        return {
            'cpu': 0,
            'memory': 0,
            'disk': 0,
            'memory_available': 0,
            'disk_free': 0,
            'error': str(e)
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