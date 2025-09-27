#!/usr/bin/env python3
"""
Ubuntu-Compatible Real-time DDoS Detection System

This system is optimized for Ubuntu environment with proper IP blocking
and web interface for real-time monitoring.
"""

import os
import sys
import json
import time
import threading
import queue
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
import tensorflow as tf
from collections import defaultdict, deque
import subprocess
import platform
import psutil
import socket

# Configure logging for Ubuntu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ddos_detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UbuntuDDoSDetector:
    """Ubuntu-optimized real-time DDoS detection and IP blocking system"""
    
    def __init__(self, model_path="ddos_model_retrained.keras"):
        self.model = None
        self.model_path = model_path
        self.blocked_ips = set()
        self.attack_history = defaultdict(list)
        self.data_queue = queue.Queue()
        self.running = False
        self.detection_threshold = 0.7
        self.block_duration = 3600  # 1 hour in seconds
        self.max_attacks_per_ip = 3
        
        # Ubuntu-specific settings
        self.iptables_rules = []
        self.ufw_enabled = self.check_ufw_status()
        
        # Load model
        self.load_model()
        
        # Initialize IP blocking system
        self.init_ip_blocking()
    
    def load_model(self):
        """Load the trained DDoS detection model"""
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            logger.info("DDoS detection model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def check_ufw_status(self):
        """Check if UFW (Uncomplicated Firewall) is enabled"""
        try:
            result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
            return 'Status: active' in result.stdout
        except:
            return False
    
    def init_ip_blocking(self):
        """Initialize IP blocking system for Ubuntu"""
        logger.info("Initializing IP blocking for Ubuntu")
        
        # Check if running as root for iptables
        if os.geteuid() != 0:
            logger.warning("Not running as root. IP blocking may not work properly.")
            logger.warning("Run with sudo for full IP blocking functionality.")
        
        # Check available blocking methods
        self.iptables_available = self.check_command('iptables')
        self.ufw_available = self.check_command('ufw')
        
        logger.info(f"iptables available: {self.iptables_available}")
        logger.info(f"ufw available: {self.ufw_available}")
    
    def check_command(self, command):
        """Check if a command is available"""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except:
            return False
    
    def get_feature_names(self):
        """Get the complete list of feature names"""
        return [
            "Protocol", "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
            "Fwd Packets Length Total", "Bwd Packets Length Total", "Fwd Packet Length Max",
            "Fwd Packet Length Min", "Fwd Packet Length Mean", "Fwd Packet Length Std",
            "Bwd Packet Length Max", "Bwd Packet Length Min", "Bwd Packet Length Mean",
            "Bwd Packet Length Std", "Flow Bytes/s", "Flow Packets/s", "Flow IAT Mean",
            "Flow IAT Std", "Flow IAT Max", "Flow IAT Min", "Fwd IAT Total", "Fwd IAT Mean",
            "Fwd IAT Std", "Fwd IAT Max", "Fwd IAT Min", "Bwd IAT Total", "Bwd IAT Mean",
            "Bwd IAT Std", "Bwd IAT Max", "Bwd IAT Min", "Fwd PSH Flags", "Bwd PSH Flags",
            "Fwd URG Flags", "Bwd URG Flags", "Fwd Header Length", "Bwd Header Length",
            "Fwd Packets/s", "Bwd Packets/s", "Packet Length Min", "Packet Length Max",
            "Packet Length Mean", "Packet Length Std", "Packet Length Variance", "FIN Flag Count",
            "SYN Flag Count", "RST Flag Count", "PSH Flag Count", "ACK Flag Count",
            "URG Flag Count", "CWE Flag Count", "ECE Flag Count", "Down/Up Ratio",
            "Avg Packet Size", "Avg Fwd Segment Size", "Avg Bwd Segment Size",
            "Fwd Avg Bytes/Bulk", "Fwd Avg Packets/Bulk", "Fwd Avg Bulk Rate",
            "Bwd Avg Bytes/Bulk", "Bwd Avg Packets/Bulk", "Bwd Avg Bulk Rate",
            "Subflow Fwd Packets", "Subflow Fwd Bytes", "Subflow Bwd Packets",
            "Subflow Bwd Bytes", "Init Fwd Win Bytes", "Init Bwd Win Bytes",
            "Fwd Act Data Packets", "Fwd Seg Size Min", "Active Mean", "Active Std",
            "Active Max", "Active Min", "Idle Mean", "Idle Std", "Idle Max", "Idle Min"
        ]
    
    def extract_features_from_data(self, network_data: Dict[str, Any]) -> List[float]:
        """Extract features from network data"""
        feature_names = self.get_feature_names()
        features = []
        
        try:
            for feature in feature_names:
                # Convert feature name to lowercase and replace spaces with underscores
                key = feature.lower().replace(' ', '_').replace('/', '_')
                value = network_data.get(key, 0.0)
                features.append(float(value))
            
            return features
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return [0.0] * len(feature_names)
    
    def predict_ddos(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict if network data represents a DDoS attack"""
        try:
            # Extract features
            features = self.extract_features_from_data(network_data)
            features_array = np.array(features).reshape(1, -1)
            
            # Make prediction
            prediction = self.model.predict(features_array, verbose=0)[0][0]
            confidence = abs(prediction - 0.5) * 2
            
            # Determine if it's an attack
            is_attack = prediction > self.detection_threshold
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'prediction': float(prediction),
                'is_ddos': is_attack,
                'confidence': float(confidence),
                'risk_level': 'High' if prediction > 0.8 else 'Medium' if prediction > 0.5 else 'Low',
                'source_ip': network_data.get('source_ip', 'unknown'),
                'dest_ip': network_data.get('dest_ip', 'unknown'),
                'protocol': network_data.get('protocol', 'unknown')
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'prediction': 0.0,
                'is_ddos': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def block_ip_iptables(self, ip_address: str) -> bool:
        """Block IP using iptables"""
        try:
            if not self.iptables_available:
                logger.error("iptables not available")
                return False
            
            # Create iptables rule
            rule = f"iptables -A INPUT -s {ip_address} -j DROP"
            result = subprocess.run(rule.split(), capture_output=True, text=True)
            
            if result.returncode == 0:
                self.iptables_rules.append(ip_address)
                logger.warning(f"BLOCKED IP: {ip_address} (iptables)")
                return True
            else:
                logger.error(f"Failed to block IP {ip_address}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address} with iptables: {e}")
            return False
    
    def block_ip_ufw(self, ip_address: str) -> bool:
        """Block IP using UFW"""
        try:
            if not self.ufw_available:
                logger.error("ufw not available")
                return False
            
            # Create UFW rule
            rule = f"ufw deny from {ip_address}"
            result = subprocess.run(rule.split(), capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.warning(f"BLOCKED IP: {ip_address} (ufw)")
                return True
            else:
                logger.error(f"Failed to block IP {ip_address}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address} with ufw: {e}")
            return False
    
    def block_ip(self, ip_address: str) -> bool:
        """Block an IP address using available methods"""
        try:
            if ip_address in self.blocked_ips:
                logger.info(f"IP {ip_address} is already blocked")
                return True
            
            success = False
            
            # Try UFW first (more user-friendly)
            if self.ufw_available and self.ufw_enabled:
                success = self.block_ip_ufw(ip_address)
            
            # Fallback to iptables
            if not success and self.iptables_available:
                success = self.block_ip_iptables(ip_address)
            
            if success:
                self.blocked_ips.add(ip_address)
                
                # Schedule unblocking
                threading.Timer(self.block_duration, self.unblock_ip, [ip_address]).start()
                return True
            else:
                logger.error(f"Failed to block IP {ip_address} with any method")
                return False
                
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address}: {e}")
            return False
    
    def unblock_ip(self, ip_address: str) -> bool:
        """Unblock an IP address"""
        try:
            if ip_address not in self.blocked_ips:
                return True
            
            success = False
            
            # Try UFW first
            if self.ufw_available:
                rule = f"ufw delete deny from {ip_address}"
                result = subprocess.run(rule.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    success = True
            
            # Try iptables
            if self.iptables_available:
                rule = f"iptables -D INPUT -s {ip_address} -j DROP"
                result = subprocess.run(rule.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    success = True
            
            if success:
                self.blocked_ips.discard(ip_address)
                logger.info(f"UNBLOCKED IP: {ip_address}")
                return True
            else:
                logger.error(f"Failed to unblock IP {ip_address}")
                return False
                
        except Exception as e:
            logger.error(f"Error unblocking IP {ip_address}: {e}")
            return False
    
    def process_attack(self, detection_result: Dict[str, Any]):
        """Process a detected DDoS attack"""
        source_ip = detection_result.get('source_ip', 'unknown')
        
        if source_ip == 'unknown':
            logger.warning("Cannot block IP: source IP unknown")
            return
        
        # Record attack
        self.attack_history[source_ip].append(detection_result)
        
        # Check if IP should be blocked
        recent_attacks = [
            attack for attack in self.attack_history[source_ip]
            if datetime.fromisoformat(attack['timestamp']) > datetime.now() - timedelta(minutes=10)
        ]
        
        if len(recent_attacks) >= self.max_attacks_per_ip:
            self.block_ip(source_ip)
            
            # Log attack details
            logger.critical(f"DDoS ATTACK DETECTED!")
            logger.critical(f"   Source IP: {source_ip}")
            logger.critical(f"   Prediction: {detection_result['prediction']:.4f}")
            logger.critical(f"   Confidence: {detection_result['confidence']:.4f}")
            logger.critical(f"   Risk Level: {detection_result['risk_level']}")
            logger.critical(f"   Protocol: {detection_result.get('protocol', 'unknown')}")
        else:
            logger.warning(f"Potential DDoS from {source_ip} (attack #{len(recent_attacks)})")
    
    def process_network_data(self, network_data: Dict[str, Any]):
        """Process incoming network data"""
        try:
            # Make prediction
            result = self.predict_ddos(network_data)
            
            # Log result
            if result['is_ddos']:
                logger.warning(f"DDoS detected: {result['source_ip']} -> {result['dest_ip']} "
                             f"(confidence: {result['confidence']:.3f})")
                self.process_attack(result)
            else:
                logger.debug(f"Normal traffic: {result['source_ip']} -> {result['dest_ip']} "
                           f"(confidence: {result['confidence']:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing network data: {e}")
            return None
    
    def add_network_data(self, network_data: Dict[str, Any]):
        """Add network data to the processing queue"""
        self.data_queue.put(network_data)
    
    def start_detection(self):
        """Start the real-time detection system"""
        logger.info("Starting real-time DDoS detection system...")
        self.running = True
        
        while self.running:
            try:
                # Get data from queue (with timeout)
                network_data = self.data_queue.get(timeout=1.0)
                
                # Process the data
                self.process_network_data(network_data)
                
            except queue.Empty:
                # No data in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                time.sleep(1)
    
    def stop_detection(self):
        """Stop the real-time detection system"""
        logger.info("Stopping DDoS detection system...")
        self.running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'running': self.running,
            'blocked_ips': list(self.blocked_ips),
            'total_attacks_detected': sum(len(attacks) for attacks in self.attack_history.values()),
            'unique_attack_ips': len(self.attack_history),
            'queue_size': self.data_queue.qsize(),
            'detection_threshold': self.detection_threshold,
            'block_duration': self.block_duration,
            'iptables_available': self.iptables_available,
            'ufw_available': self.ufw_available,
            'ufw_enabled': self.ufw_enabled
        }

def create_sample_network_data():
    """Create sample network data for testing"""
    return {
        'source_ip': '192.168.1.100',
        'dest_ip': '10.0.0.1',
        'protocol': 6,  # TCP
        'flow_duration': 2000,
        'total_fwd_packets': 15,
        'total_backward_packets': 12,
        'fwd_packets_length_total': 18000,
        'bwd_packets_length_total': 12000,
        'fwd_packet_length_max': 1500,
        'fwd_packet_length_min': 1000,
        'fwd_packet_length_mean': 1200,
        'fwd_packet_length_std': 200,
        'bwd_packet_length_max': 1200,
        'bwd_packet_length_min': 800,
        'bwd_packet_length_mean': 1000,
        'bwd_packet_length_std': 150,
        'flow_bytes/s': 15000,
        'flow_packets/s': 13.5,
        'flow_iat_mean': 150,
        'flow_iat_std': 50,
        'flow_iat_max': 500,
        'flow_iat_min': 50,
        'fwd_iat_total': 2250,
        'fwd_iat_mean': 150,
        'fwd_iat_std': 50,
        'fwd_iat_max': 500,
        'fwd_iat_min': 50,
        'bwd_iat_total': 1800,
        'bwd_iat_mean': 150,
        'bwd_iat_std': 50,
        'bwd_iat_max': 500,
        'bwd_iat_min': 50,
        'fwd_psh_flags': 0,
        'bwd_psh_flags': 0,
        'fwd_urg_flags': 0,
        'bwd_urg_flags': 0,
        'fwd_header_length': 20,
        'bwd_header_length': 20,
        'fwd_packets/s': 7.5,
        'bwd_packets/s': 6,
        'packet_length_min': 1000,
        'packet_length_max': 1500,
        'packet_length_mean': 1100,
        'packet_length_std': 200,
        'packet_length_variance': 40000,
        'fin_flag_count': 0,
        'syn_flag_count': 1,
        'rst_flag_count': 0,
        'psh_flag_count': 0,
        'ack_flag_count': 12,
        'urg_flag_count': 0,
        'cwe_flag_count': 0,
        'ece_flag_count': 0,
        'down/up_ratio': 0.67,
        'avg_packet_size': 1100,
        'avg_fwd_segment_size': 1200,
        'avg_bwd_segment_size': 1000,
        'fwd_avg_bytes/bulk': 0,
        'fwd_avg_packets/bulk': 0,
        'fwd_avg_bulk_rate': 0,
        'bwd_avg_bytes/bulk': 0,
        'bwd_avg_packets/bulk': 0,
        'bwd_avg_bulk_rate': 0,
        'subflow_fwd_packets': 15,
        'subflow_fwd_bytes': 18000,
        'subflow_bwd_packets': 12,
        'subflow_bwd_bytes': 12000,
        'init_fwd_win_bytes': 65535,
        'init_bwd_win_bytes': 65535,
        'fwd_act_data_packets': 14,
        'fwd_seg_size_min': 1000,
        'active_mean': 150,
        'active_std': 50,
        'active_max': 500,
        'active_min': 50,
        'idle_mean': 200,
        'idle_std': 100,
        'idle_max': 1000,
        'idle_min': 50
    }

def main():
    """Main function for testing the Ubuntu detector"""
    print("Ubuntu DDoS Detection System")
    print("=" * 50)
    
    try:
        # Create detector
        detector = UbuntuDDoSDetector()
        
        # Start detection in a separate thread
        detection_thread = threading.Thread(target=detector.start_detection)
        detection_thread.daemon = True
        detection_thread.start()
        
        print("DDoS detection system started")
        print("Monitoring network traffic...")
        print("IP blocking system active")
        print("\nPress Ctrl+C to stop")
        
        # Simulate some network data
        print("\nSimulating network traffic...")
        
        # Normal traffic
        normal_data = create_sample_network_data()
        normal_data['source_ip'] = '192.168.1.100'
        detector.add_network_data(normal_data)
        time.sleep(1)
        
        # DDoS attack simulation
        ddos_data = create_sample_network_data()
        ddos_data.update({
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
        
        # Send multiple attacks to trigger blocking
        for i in range(5):
            detector.add_network_data(ddos_data)
            time.sleep(0.5)
        
        # Keep running
        while True:
            status = detector.get_status()
            print(f"\rStatus: {status['blocked_ips']} IPs blocked, "
                  f"{status['total_attacks_detected']} attacks detected", end="")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopping detection system...")
        detector.stop_detection()
        print("System stopped")

if __name__ == "__main__":
    main()
