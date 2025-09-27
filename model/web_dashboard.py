#!/usr/bin/env python3
"""
DDoS Detection Web Dashboard

Real-time web interface for monitoring DDoS detection system
on Ubuntu environment.
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
from flask_socketio import SocketIO, emit
import psutil
import socket

# Import our Ubuntu DDoS detector
from ubuntu_ddos_detector import UbuntuDDoSDetector, create_sample_network_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ddos_detection_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global detector instance
detector = None
detection_thread = None

# HTML Template for the dashboard
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DDoS Detection Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
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
                    <div class="status-dot status-inactive" id="status-dot"></div>
                    <span id="status-text">System Status: Unknown</span>
                </div>
                <div class="controls">
                    <button class="btn btn-primary" onclick="startSystem()">Start</button>
                    <button class="btn btn-danger" onclick="stopSystem()">Stop</button>
                    <button class="btn btn-success" onclick="simulateAttack()">Simulate Attack</button>
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
        // Initialize Socket.IO connection
        const socket = io();
        
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
        
        // Socket event handlers
        socket.on('status_update', function(data) {
            updateDashboard(data);
        });
        
        socket.on('log_message', function(data) {
            addLogEntry(data.message, data.level);
        });
        
        socket.on('attack_detected', function(data) {
            addLogEntry(`DDoS Attack Detected: ${data.source_ip} -> ${data.dest_ip} (Confidence: ${data.confidence})`, 'critical');
        });
        
        // Dashboard update functions
        function updateDashboard(data) {
            document.getElementById('status-text').textContent = `System Status: ${data.running ? 'Running' : 'Stopped'}`;
            document.getElementById('status-dot').className = `status-dot ${data.running ? 'status-active' : 'status-inactive'}`;
            
            document.getElementById('blocked-count').textContent = data.blocked_ips.length;
            document.getElementById('attacks-count').textContent = data.total_attacks_detected;
            document.getElementById('queue-size').textContent = data.queue_size;
            document.getElementById('unique-attackers').textContent = data.unique_attack_ips;
            
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
        function startSystem() {
            fetch('/api/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addLogEntry('System started successfully', 'info');
                    }
                });
        }
        
        function stopSystem() {
            fetch('/api/stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addLogEntry('System stopped', 'info');
                    }
                });
        }
        
        function simulateAttack() {
            fetch('/api/simulate', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addLogEntry('Attack simulation started', 'warning');
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

@app.route('/api/status')
def api_status():
    """Get current system status"""
    if detector:
        status = detector.get_status()
        
        # Add system metrics
        try:
            status['system_metrics'] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_connections': len(psutil.net_connections())
            }
        except:
            status['system_metrics'] = {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'network_connections': 0
            }
        
        return jsonify(status)
    return jsonify({'error': 'System not initialized'})

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start the DDoS detection system"""
    global detector, detection_thread
    
    try:
        if not detector:
            detector = UbuntuDDoSDetector()
        
        if not detector.running:
            detection_thread = threading.Thread(target=detector.start_detection)
            detection_thread.daemon = True
            detection_thread.start()
            
            # Start status broadcasting
            threading.Thread(target=broadcast_status, daemon=True).start()
            
            logger.info("DDoS detection system started")
            return jsonify({'status': 'success', 'message': 'System started'})
        else:
            return jsonify({'status': 'info', 'message': 'System already running'})
            
    except Exception as e:
        logger.error(f"Error starting system: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop the DDoS detection system"""
    global detector
    
    try:
        if detector and detector.running:
            detector.stop_detection()
            logger.info("DDoS detection system stopped")
            return jsonify({'status': 'success', 'message': 'System stopped'})
        else:
            return jsonify({'status': 'info', 'message': 'System not running'})
            
    except Exception as e:
        logger.error(f"Error stopping system: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    """Simulate a DDoS attack for testing"""
    global detector
    
    try:
        if not detector:
            return jsonify({'status': 'error', 'message': 'System not initialized'})
        
        # Create attack data
        attack_data = create_sample_network_data()
        attack_data.update({
            'source_ip': '10.0.0.100',  # Attacker IP
            'protocol': 17,  # UDP
            'flow_duration': 216631,
            'total_fwd_packets': 6,
            'total_backward_packets': 0,
            'fwd_packets_length_total': 2088,
            'bwd_packets_length_total': 0,
            'fwd_packet_length_max': 393,
            'fwd_packet_length_min': 321,
            'fwd_packet_length_mean': 348,
            'fwd_packet_length_std': 35.08846,
            'bwd_packet_length_max': 0,
            'bwd_packet_length_min': 0,
            'bwd_packet_length_mean': 0,
            'bwd_packet_length_std': 0,
            'flow_bytes/s': 9638.51,
            'flow_packets/s': 27.696867,
            'flow_iat_mean': 43326.2,
            'flow_iat_std': 59304.016,
            'flow_iat_max': 108616,
            'flow_iat_min': 0,
            'fwd_iat_total': 216631,
            'fwd_iat_mean': 43326.2,
            'fwd_iat_std': 59304.016,
            'fwd_iat_max': 108616,
            'fwd_iat_min': 0,
            'bwd_iat_total': 0,
            'bwd_iat_mean': 0,
            'bwd_iat_std': 0,
            'bwd_iat_max': 0,
            'bwd_iat_min': 0,
            'fwd_psh_flags': 0,
            'bwd_psh_flags': 0,
            'fwd_urg_flags': 0,
            'bwd_urg_flags': 0,
            'fwd_header_length': 96,
            'bwd_header_length': 0,
            'fwd_packets/s': 27.696867,
            'bwd_packets/s': 0,
            'packet_length_min': 321,
            'packet_length_max': 393,
            'packet_length_mean': 344.14285,
            'packet_length_std': 33.617596,
            'packet_length_variance': 1130.1428,
            'fin_flag_count': 0,
            'syn_flag_count': 0,
            'rst_flag_count': 0,
            'psh_flag_count': 0,
            'ack_flag_count': 0,
            'urg_flag_count': 0,
            'cwe_flag_count': 0,
            'ece_flag_count': 0,
            'down/up_ratio': 0,
            'avg_packet_size': 401.5,
            'avg_fwd_segment_size': 348,
            'avg_bwd_segment_size': 0,
            'fwd_avg_bytes/bulk': 0,
            'fwd_avg_packets/bulk': 0,
            'fwd_avg_bulk_rate': 0,
            'bwd_avg_bytes/bulk': 0,
            'bwd_avg_packets/bulk': 0,
            'bwd_avg_bulk_rate': 0,
            'subflow_fwd_packets': 6,
            'subflow_fwd_bytes': 2088,
            'subflow_bwd_packets': 0,
            'subflow_bwd_bytes': 0,
            'init_fwd_win_bytes': -1,
            'init_bwd_win_bytes': -1,
            'fwd_act_data_packets': 5,
            'fwd_seg_size_min': 14,
            'active_mean': 0,
            'active_std': 0,
            'active_max': 0,
            'active_min': 0,
            'idle_mean': 0,
            'idle_std': 0,
            'idle_max': 0,
            'idle_min': 0
        })
        
        # Send multiple attack packets
        for i in range(5):
            detector.add_network_data(attack_data)
            time.sleep(0.1)
        
        logger.info("Attack simulation completed")
        return jsonify({'status': 'success', 'message': 'Attack simulation completed'})
        
    except Exception as e:
        logger.error(f"Error simulating attack: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/unblock/<ip_address>', methods=['POST'])
def api_unblock(ip_address):
    """Unblock a specific IP address"""
    global detector
    
    try:
        if not detector:
            return jsonify({'status': 'error', 'message': 'System not initialized'})
        
        success = detector.unblock_ip(ip_address)
        if success:
            logger.info(f"IP {ip_address} unblocked")
            return jsonify({'status': 'success', 'message': f'IP {ip_address} unblocked'})
        else:
            return jsonify({'status': 'error', 'message': f'Failed to unblock IP {ip_address}'})
            
    except Exception as e:
        logger.error(f"Error unblocking IP {ip_address}: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

def broadcast_status():
    """Broadcast status updates to connected clients"""
    while True:
        try:
            if detector and detector.running:
                status = detector.get_status()
                
                # Add system metrics
                try:
                    status['system_metrics'] = {
                        'cpu_percent': psutil.cpu_percent(interval=1),
                        'memory_percent': psutil.virtual_memory().percent,
                        'disk_percent': psutil.disk_usage('/').percent,
                        'network_connections': len(psutil.net_connections())
                    }
                except:
                    pass
                
                socketio.emit('status_update', status)
            
            time.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            logger.error(f"Error broadcasting status: {e}")
            time.sleep(5)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('log_message', {'message': 'Connected to DDoS detection system', 'level': 'info'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

def main():
    """Main function to run the web dashboard"""
    print("DDoS Detection Web Dashboard")
    print("=" * 50)
    print("Starting web interface on http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    try:
        # Run the Flask-SocketIO app
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down web dashboard...")
        if detector:
            detector.stop_detection()

if __name__ == "__main__":
    main()
