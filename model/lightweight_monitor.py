#!/usr/bin/env python3
"""
Lightweight Monitoring System
Replaces heavy Prometheus/Grafana with simple metrics collection
"""

import time
import json
import psutil
import threading
from datetime import datetime
from typing import Dict, List, Any
from flask import Flask, jsonify, render_template_string
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightweightMonitor:
    def __init__(self):
        self.metrics_history = []
        self.max_history = 1000  # Keep last 1000 data points
        self.collection_interval = 5  # seconds
        
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect system and application metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Network connections
            connections = len(psutil.net_connections())
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used_gb': memory.used / (1024**3),
                    'memory_total_gb': memory.total / (1024**3),
                    'disk_percent': disk.percent,
                    'disk_used_gb': disk.used / (1024**3),
                    'disk_total_gb': disk.total / (1024**3),
                    'network_connections': connections,
                    'network_bytes_sent': network.bytes_sent,
                    'network_bytes_recv': network.bytes_recv,
                    'network_packets_sent': network.packets_sent,
                    'network_packets_recv': network.packets_recv
                },
                'application': {
                    'uptime_seconds': time.time() - self.start_time,
                    'metrics_collected': len(self.metrics_history)
                }
            }
            
            # Add to history
            self.metrics_history.append(metrics)
            
            # Keep only recent metrics
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of recent metrics"""
        if not self.metrics_history:
            return {'error': 'No metrics available'}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 data points
        
        # Calculate averages
        cpu_avg = sum(m['system']['cpu_percent'] for m in recent_metrics) / len(recent_metrics)
        memory_avg = sum(m['system']['memory_percent'] for m in recent_metrics) / len(recent_metrics)
        disk_avg = sum(m['system']['disk_percent'] for m in recent_metrics) / len(recent_metrics)
        
        return {
            'current': self.metrics_history[-1] if self.metrics_history else {},
            'summary': {
                'cpu_avg': round(cpu_avg, 2),
                'memory_avg': round(memory_avg, 2),
                'disk_avg': round(disk_avg, 2),
                'data_points': len(self.metrics_history),
                'collection_interval': self.collection_interval
            },
            'history': recent_metrics
        }
    
    def start_collection(self):
        """Start metrics collection in background thread"""
        self.start_time = time.time()
        
        def collect_loop():
            while True:
                try:
                    self.collect_metrics()
                    time.sleep(self.collection_interval)
                except Exception as e:
                    logger.error(f"Error in metrics collection loop: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=collect_loop, daemon=True)
        thread.start()
        logger.info("Metrics collection started")

# Initialize monitor
monitor = LightweightMonitor()

# Flask app for metrics API
app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'lightweight-monitor'})

@app.route('/metrics')
def metrics():
    """Get current metrics"""
    return jsonify(monitor.collect_metrics())

@app.route('/metrics/summary')
def metrics_summary():
    """Get metrics summary"""
    return jsonify(monitor.get_metrics_summary())

@app.route('/metrics/history')
def metrics_history():
    """Get metrics history"""
    return jsonify({
        'history': monitor.metrics_history[-100:],  # Last 100 data points
        'total_points': len(monitor.metrics_history)
    })

# Simple dashboard HTML
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lightweight Monitor Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            text-align: center;
        }
        
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .metric-card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 500;
            color: #7f8c8d;
        }
        
        .metric-value {
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .metric-value.high {
            color: #e74c3c;
        }
        
        .metric-value.medium {
            color: #f39c12;
        }
        
        .metric-value.low {
            color: #27ae60;
        }
        
        .chart-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .chart-container h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        
        .chart-wrapper {
            position: relative;
            height: 300px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #27ae60;
            animation: pulse 2s infinite;
            margin-right: 8px;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Lightweight Monitor Dashboard</h1>
            <div class="status-indicator"></div>
            <span>System Monitoring Active</span>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>💻 System Resources</h3>
                <div class="metric">
                    <span class="metric-label">CPU Usage</span>
                    <span class="metric-value" id="cpu-usage">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Memory Usage</span>
                    <span class="metric-value" id="memory-usage">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Disk Usage</span>
                    <span class="metric-value" id="disk-usage">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Network Connections</span>
                    <span class="metric-value" id="network-connections">0</span>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>📈 Network Stats</h3>
                <div class="metric">
                    <span class="metric-label">Bytes Sent</span>
                    <span class="metric-value" id="bytes-sent">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Bytes Received</span>
                    <span class="metric-value" id="bytes-recv">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Packets Sent</span>
                    <span class="metric-value" id="packets-sent">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Packets Received</span>
                    <span class="metric-value" id="packets-recv">0</span>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>⏱️ System Info</h3>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value" id="uptime">0s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Data Points</span>
                    <span class="metric-value" id="data-points">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Collection Interval</span>
                    <span class="metric-value" id="collection-interval">5s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Update</span>
                    <span class="metric-value" id="last-update">Never</span>
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>📊 CPU Usage Trend</h3>
            <div class="chart-wrapper">
                <canvas id="cpuChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        // Initialize Chart.js
        const ctx = document.getElementById('cpuChart').getContext('2d');
        const cpuChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU Usage %',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        
        // Update dashboard data
        function updateDashboard() {
            fetch('/metrics/summary')
                .then(response => response.json())
                .then(data => {
                    if (data.current && data.current.system) {
                        const system = data.current.system;
                        
                        // Update system metrics
                        document.getElementById('cpu-usage').textContent = system.cpu_percent.toFixed(1) + '%';
                        document.getElementById('memory-usage').textContent = system.memory_percent.toFixed(1) + '%';
                        document.getElementById('disk-usage').textContent = system.disk_percent.toFixed(1) + '%';
                        document.getElementById('network-connections').textContent = system.network_connections;
                        
                        // Update network stats
                        document.getElementById('bytes-sent').textContent = formatBytes(system.network_bytes_sent);
                        document.getElementById('bytes-recv').textContent = formatBytes(system.network_bytes_recv);
                        document.getElementById('packets-sent').textContent = system.network_packets_sent.toLocaleString();
                        document.getElementById('packets-recv').textContent = system.network_packets_recv.toLocaleString();
                        
                        // Update system info
                        document.getElementById('uptime').textContent = formatUptime(data.current.application.uptime_seconds);
                        document.getElementById('data-points').textContent = data.current.application.metrics_collected;
                        document.getElementById('last-update').textContent = new Date(data.current.timestamp).toLocaleTimeString();
                        
                        // Update chart
                        if (data.history && data.history.length > 0) {
                            const labels = data.history.map(h => new Date(h.timestamp).toLocaleTimeString());
                            const cpuData = data.history.map(h => h.system.cpu_percent);
                            
                            cpuChart.data.labels = labels;
                            cpuChart.data.datasets[0].data = cpuData;
                            cpuChart.update();
                        }
                    }
                })
                .catch(error => console.error('Error fetching metrics:', error));
        }
        
        // Format bytes to human readable
        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        // Format uptime
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            return `${hours}h ${minutes}m ${secs}s`;
        }
        
        // Update every 5 seconds
        setInterval(updateDashboard, 5000);
        
        // Initial load
        updateDashboard();
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)

def main():
    """Main function to run the lightweight monitor"""
    print("Lightweight Monitor Dashboard")
    print("=" * 50)
    print("Starting monitoring on http://localhost:9090")
    print("Press Ctrl+C to stop")
    
    # Start metrics collection
    monitor.start_collection()
    
    try:
        # Run the Flask app
        app.run(host='0.0.0.0', port=9090, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down monitor...")

if __name__ == "__main__":
    main()
