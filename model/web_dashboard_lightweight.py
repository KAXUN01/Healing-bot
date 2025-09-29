#!/usr/bin/env python3
"""
Lightweight DDoS Detection Web Dashboard
Optimized for high performance with minimal resource usage
"""

import os
import sys
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, render_template_string, jsonify, request
import requests
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ddos_detection_secret_key'

# Configuration
MODEL_API_URL = os.getenv('MODEL_HOST', 'http://model:8080')
DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', '9090'))

# Global state
detection_stats = {
    'total_attacks': 0,
    'blocked_ips': [],
    'unique_attackers': set(),
    'queue_size': 0,
    'last_update': datetime.now()
}

# HTML Template for the lightweight dashboard
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DDoS Detection Dashboard</title>
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
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-active {
            background: #27ae60;
        }
        
        .status-inactive {
            background: #e74c3c;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .controls {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #3498db;
            color: white;
        }
        
        .btn-primary:hover {
            background: #2980b9;
        }
        
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c0392b;
        }
        
        .btn-success {
            background: #27ae60;
            color: white;
        }
        
        .btn-success:hover {
            background: #229954;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
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
        
        .blocked-ips {
            max-height: 200px;
            overflow-y: auto;
        }
        
        .ip-item {
            background: #f8d7da;
            color: #721c24;
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #dc3545;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .ip-item .unblock-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8em;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        
        .logs {
            max-height: 300px;
            overflow-y: auto;
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .log-entry {
            margin: 5px 0;
            padding: 2px 0;
        }
        
        .log-warning {
            color: #f39c12;
        }
        
        .log-error {
            color: #e74c3c;
        }
        
        .log-critical {
            color: #e74c3c;
            font-weight: bold;
        }
        
        .log-info {
            color: #3498db;
        }
        
        .system-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .info-item {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .info-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .info-label {
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ DDoS Detection Dashboard</h1>
            <div class="status-bar">
                <div class="status-indicator">
                    <div class="status-dot status-active" id="status-dot"></div>
                    <span id="status-text">System Status: Running</span>
                </div>
                <div class="controls">
                    <button class="btn btn-primary" onclick="testModel()">Test Model</button>
                    <button class="btn btn-success" onclick="simulateAttack()">Simulate Attack</button>
                    <button class="btn btn-danger" onclick="clearStats()">Clear Stats</button>
                </div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h3>📊 Detection Statistics</h3>
                <div class="metric">
                    <span class="metric-label">Blocked IPs</span>
                    <span class="metric-value" id="blocked-count">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Attacks</span>
                    <span class="metric-value" id="attacks-count">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Queue Size</span>
                    <span class="metric-value" id="queue-size">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Unique Attackers</span>
                    <span class="metric-value" id="unique-attackers">0</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🚫 Blocked IP Addresses</h3>
                <div class="blocked-ips" id="blocked-ips-list">
                    <p>No IPs blocked</p>
                </div>
            </div>
            
            <div class="card">
                <h3>📈 Attack Trends</h3>
                <div class="chart-container">
                    <canvas id="attackChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h3>💻 System Information</h3>
                <div class="system-info">
                    <div class="info-item">
                        <div class="info-value" id="cpu-usage">0%</div>
                        <div class="info-label">CPU Usage</div>
                    </div>
                    <div class="info-item">
                        <div class="info-value" id="memory-usage">0%</div>
                        <div class="info-label">Memory Usage</div>
                    </div>
                    <div class="info-item">
                        <div class="info-value" id="disk-usage">0%</div>
                        <div class="info-label">Disk Usage</div>
                    </div>
                    <div class="info-item">
                        <div class="info-value" id="network-connections">0</div>
                        <div class="info-label">Network Connections</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📝 Real-time Logs</h3>
            <div class="logs" id="logs-container">
                <div class="log-entry log-info">System initialized. Waiting for data...</div>
            </div>
        </div>
    </div>

    <script>
        // Initialize Chart.js
        const ctx = document.getElementById('attackChart').getContext('2d');
        const attackChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Attacks per Minute',
                    data: [],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // Dashboard update functions
        function updateDashboard(data) {
            document.getElementById('blocked-count').textContent = data.blocked_ips.length;
            document.getElementById('attacks-count').textContent = data.total_attacks;
            document.getElementById('queue-size').textContent = data.queue_size;
            document.getElementById('unique-attackers').textContent = data.unique_attackers;
            
            // Update blocked IPs list
            const blockedList = document.getElementById('blocked-ips-list');
            if (data.blocked_ips.length > 0) {
                blockedList.innerHTML = data.blocked_ips.map(ip => 
                    `<div class="ip-item">
                        <span>${ip}</span>
                        <button class="unblock-btn" onclick="unblockIP('${ip}')">Unblock</button>
                    </div>`
                ).join('');
            } else {
                blockedList.innerHTML = '<p>No IPs blocked</p>';
            }
            
            // Update system metrics
            document.getElementById('cpu-usage').textContent = data.system_metrics?.cpu_percent?.toFixed(1) + '%' || '0%';
            document.getElementById('memory-usage').textContent = data.system_metrics?.memory_percent?.toFixed(1) + '%' || '0%';
            document.getElementById('disk-usage').textContent = data.system_metrics?.disk_percent?.toFixed(1) + '%' || '0%';
            document.getElementById('network-connections').textContent = data.system_metrics?.network_connections || '0';
        }
        
        function addLogEntry(message, level) {
            const logsContainer = document.getElementById('logs-container');
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry log-${level}`;
            logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            
            logsContainer.appendChild(logEntry);
            logsContainer.scrollTop = logsContainer.scrollHeight;
            
            // Keep only last 100 log entries
            while (logsContainer.children.length > 100) {
                logsContainer.removeChild(logsContainer.firstChild);
            }
        }
        
        // Control functions
        function testModel() {
            fetch('/api/test_model', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addLogEntry('Model test completed successfully', 'info');
                    } else {
                        addLogEntry('Model test failed: ' + data.message, 'error');
                    }
                });
        }
        
        function simulateAttack() {
            fetch('/api/simulate_attack', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addLogEntry('Attack simulation started', 'warning');
                    } else {
                        addLogEntry('Simulation failed: ' + data.message, 'error');
                    }
                });
        }
        
        function clearStats() {
            fetch('/api/clear_stats', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addLogEntry('Statistics cleared', 'info');
                    }
                });
        }
        
        function unblockIP(ip) {
            fetch(`/api/unblock/${ip}`, {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addLogEntry(`IP ${ip} unblocked`, 'info');
                    }
                });
        }
        
        // Auto-refresh every 2 seconds
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateDashboard(data));
        }, 2000);
        
        // Initial load
        fetch('/api/status')
            .then(response => response.json())
            .then(data => updateDashboard(data));
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'ddos-dashboard'})

@app.route('/api/status')
def api_status():
    """Get current system status"""
    try:
        # Get system metrics
        system_metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_connections': len(psutil.net_connections())
        }
        
        # Update detection stats
        status = {
            'total_attacks': detection_stats['total_attacks'],
            'blocked_ips': list(detection_stats['blocked_ips']),
            'queue_size': detection_stats['queue_size'],
            'unique_attackers': len(detection_stats['unique_attackers']),
            'system_metrics': system_metrics,
            'last_update': detection_stats['last_update'].isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/test_model', methods=['POST'])
def api_test_model():
    """Test the ML model"""
    try:
        # Test model API
        response = requests.get(f"{MODEL_API_URL}/test", timeout=10)
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Model test successful: {result}")
            return jsonify({'status': 'success', 'message': 'Model test completed'})
        else:
            return jsonify({'status': 'error', 'message': 'Model API not responding'})
            
    except Exception as e:
        logger.error(f"Error testing model: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/simulate_attack', methods=['POST'])
def api_simulate_attack():
    """Simulate a DDoS attack for testing"""
    try:
        # Create sample attack data
        attack_data = {
            "id": f"attack_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "protocol": 17,  # UDP
                "flow_duration": 216631,
                "total_fwd_packets": 6,
                "total_backward_packets": 0,
                "fwd_packet_length_mean": 348,
                "bwd_packet_length_mean": 0,
                "flow_iat_mean": 43326.2,
                "flow_iat_std": 59304.016,
                "flow_iat_max": 108616,
                "flow_iat_min": 0,
                "fwd_iat_mean": 43326.2,
                "fwd_iat_std": 59304.016,
                "fwd_iat_max": 108616,
                "fwd_iat_min": 0,
                "bwd_iat_mean": 0,
                "bwd_iat_std": 0,
                "bwd_iat_max": 0,
                "bwd_iat_min": 0,
                "active_mean": 0,
                "active_std": 0,
                "active_max": 0,
                "active_min": 0,
                "idle_mean": 0,
                "idle_std": 0,
                "idle_max": 0,
                "idle_min": 0
            }
        }
        
        # Send to model API
        response = requests.post(f"{MODEL_API_URL}/alerts", json=attack_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            
            # Update stats
            detection_stats['total_attacks'] += 1
            detection_stats['unique_attackers'].add('10.0.0.100')
            
            if result.get('ddos_detected', False):
                detection_stats['blocked_ips'].append('10.0.0.100')
                logger.info(f"DDoS attack detected: {result}")
            
            return jsonify({'status': 'success', 'message': 'Attack simulation completed'})
        else:
            return jsonify({'status': 'error', 'message': 'Model API not responding'})
            
    except Exception as e:
        logger.error(f"Error simulating attack: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/clear_stats', methods=['POST'])
def api_clear_stats():
    """Clear detection statistics"""
    global detection_stats
    detection_stats = {
        'total_attacks': 0,
        'blocked_ips': [],
        'unique_attackers': set(),
        'queue_size': 0,
        'last_update': datetime.now()
    }
    return jsonify({'status': 'success', 'message': 'Statistics cleared'})

@app.route('/api/unblock/<ip_address>', methods=['POST'])
def api_unblock(ip_address):
    """Unblock a specific IP address"""
    try:
        if ip_address in detection_stats['blocked_ips']:
            detection_stats['blocked_ips'].remove(ip_address)
            logger.info(f"IP {ip_address} unblocked")
            return jsonify({'status': 'success', 'message': f'IP {ip_address} unblocked'})
        else:
            return jsonify({'status': 'error', 'message': f'IP {ip_address} not found in blocked list'})
            
    except Exception as e:
        logger.error(f"Error unblocking IP {ip_address}: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

def main():
    """Main function to run the lightweight dashboard"""
    print("Lightweight DDoS Detection Dashboard")
    print("=" * 50)
    print(f"Starting web interface on http://localhost:{DASHBOARD_PORT}")
    print("Press Ctrl+C to stop")
    
    try:
        # Run the Flask app
        app.run(host='0.0.0.0', port=DASHBOARD_PORT, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")

if __name__ == "__main__":
    main()
