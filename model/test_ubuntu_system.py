#!/usr/bin/env python3
"""
Ubuntu DDoS Detection System Test

This script tests the complete DDoS detection system on Ubuntu
including web interface, IP blocking, and real-time monitoring.
"""

import os
import sys
import time
import threading
import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UbuntuSystemTester:
    """Test the Ubuntu DDoS detection system"""
    
    def __init__(self, web_url="http://localhost:5000"):
        self.web_url = web_url
        self.test_results = {}
        
    def test_web_interface(self) -> bool:
        """Test if web interface is accessible"""
        try:
            response = requests.get(f"{self.web_url}/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Web interface is accessible")
                return True
            else:
                logger.error(f"❌ Web interface returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Web interface not accessible: {e}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test API endpoints"""
        try:
            # Test status endpoint
            response = requests.get(f"{self.web_url}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Status API working: {data.get('running', False)}")
            else:
                logger.error(f"❌ Status API failed: {response.status_code}")
                return False
            
            # Test start endpoint
            response = requests.post(f"{self.web_url}/api/start", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Start API working: {data.get('status', 'unknown')}")
            else:
                logger.error(f"❌ Start API failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ API endpoints test failed: {e}")
            return False
    
    def test_attack_simulation(self) -> bool:
        """Test attack simulation"""
        try:
            response = requests.post(f"{self.web_url}/api/simulate", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Attack simulation working: {data.get('status', 'unknown')}")
                return True
            else:
                logger.error(f"❌ Attack simulation failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Attack simulation test failed: {e}")
            return False
    
    def test_system_metrics(self) -> bool:
        """Test system metrics collection"""
        try:
            response = requests.get(f"{self.web_url}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('system_metrics', {})
                
                if 'cpu_percent' in metrics and 'memory_percent' in metrics:
                    logger.info(f"✅ System metrics working - CPU: {metrics['cpu_percent']:.1f}%, Memory: {metrics['memory_percent']:.1f}%")
                    return True
                else:
                    logger.error("❌ System metrics missing")
                    return False
            else:
                logger.error(f"❌ System metrics test failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ System metrics test failed: {e}")
            return False
    
    def test_ip_blocking(self) -> bool:
        """Test IP blocking functionality"""
        try:
            # Check if system is running
            response = requests.get(f"{self.web_url}/api/status", timeout=5)
            if response.status_code != 200:
                logger.error("❌ Cannot test IP blocking - system not running")
                return False
            
            data = response.json()
            if not data.get('running', False):
                logger.error("❌ Cannot test IP blocking - detection system not running")
                return False
            
            # Simulate attack to trigger blocking
            logger.info("🎯 Simulating attack to test IP blocking...")
            response = requests.post(f"{self.web_url}/api/simulate", timeout=10)
            
            if response.status_code == 200:
                # Wait a bit for processing
                time.sleep(3)
                
                # Check if IP was blocked
                response = requests.get(f"{self.web_url}/api/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    blocked_ips = data.get('blocked_ips', [])
                    attacks_detected = data.get('total_attacks_detected', 0)
                    
                    if attacks_detected > 0:
                        logger.info(f"✅ Attack detection working - {attacks_detected} attacks detected")
                        if blocked_ips:
                            logger.info(f"✅ IP blocking working - {len(blocked_ips)} IPs blocked: {blocked_ips}")
                        else:
                            logger.warning("⚠️  Attacks detected but no IPs blocked (may need more attacks)")
                        return True
                    else:
                        logger.error("❌ No attacks detected")
                        return False
                else:
                    logger.error("❌ Cannot check blocking status")
                    return False
            else:
                logger.error("❌ Attack simulation failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ IP blocking test failed: {e}")
            return False
    
    def test_real_time_monitoring(self) -> bool:
        """Test real-time monitoring capabilities"""
        try:
            logger.info("📊 Testing real-time monitoring...")
            
            # Get initial status
            response = requests.get(f"{self.web_url}/api/status", timeout=5)
            if response.status_code != 200:
                logger.error("❌ Cannot test monitoring - API not accessible")
                return False
            
            initial_data = response.json()
            initial_attacks = initial_data.get('total_attacks_detected', 0)
            
            # Simulate some traffic
            logger.info("🔄 Simulating network traffic...")
            for i in range(3):
                response = requests.post(f"{self.web_url}/api/simulate", timeout=5)
                time.sleep(1)
            
            # Check if monitoring detected changes
            time.sleep(2)
            response = requests.get(f"{self.web_url}/api/status", timeout=5)
            if response.status_code == 200:
                final_data = response.json()
                final_attacks = final_data.get('total_attacks_detected', 0)
                
                if final_attacks > initial_attacks:
                    logger.info(f"✅ Real-time monitoring working - detected {final_attacks - initial_attacks} new attacks")
                    return True
                else:
                    logger.warning("⚠️  Real-time monitoring may not be working properly")
                    return False
            else:
                logger.error("❌ Cannot verify monitoring status")
                return False
                
        except Exception as e:
            logger.error(f"❌ Real-time monitoring test failed: {e}")
            return False
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive system test"""
        logger.info("🧪 Starting comprehensive Ubuntu DDoS detection system test")
        logger.info("=" * 60)
        
        test_results = {
            'web_interface': False,
            'api_endpoints': False,
            'attack_simulation': False,
            'system_metrics': False,
            'ip_blocking': False,
            'real_time_monitoring': False,
            'overall_success': False
        }
        
        # Test 1: Web Interface
        logger.info("\n1️⃣  Testing Web Interface...")
        test_results['web_interface'] = self.test_web_interface()
        
        # Test 2: API Endpoints
        logger.info("\n2️⃣  Testing API Endpoints...")
        test_results['api_endpoints'] = self.test_api_endpoints()
        
        # Test 3: System Metrics
        logger.info("\n3️⃣  Testing System Metrics...")
        test_results['system_metrics'] = self.test_system_metrics()
        
        # Test 4: Attack Simulation
        logger.info("\n4️⃣  Testing Attack Simulation...")
        test_results['attack_simulation'] = self.test_attack_simulation()
        
        # Test 5: IP Blocking
        logger.info("\n5️⃣  Testing IP Blocking...")
        test_results['ip_blocking'] = self.test_ip_blocking()
        
        # Test 6: Real-time Monitoring
        logger.info("\n6️⃣  Testing Real-time Monitoring...")
        test_results['real_time_monitoring'] = self.test_real_time_monitoring()
        
        # Calculate overall success
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results) - 1  # Exclude overall_success
        test_results['overall_success'] = passed_tests == total_tests
        
        # Generate report
        self.generate_test_report(test_results)
        
        return test_results
    
    def generate_test_report(self, results: Dict[str, Any]):
        """Generate test report"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        test_names = {
            'web_interface': 'Web Interface',
            'api_endpoints': 'API Endpoints',
            'attack_simulation': 'Attack Simulation',
            'system_metrics': 'System Metrics',
            'ip_blocking': 'IP Blocking',
            'real_time_monitoring': 'Real-time Monitoring'
        }
        
        passed = 0
        total = len(test_names)
        
        for test_key, test_name in test_names.items():
            status = "✅ PASS" if results[test_key] else "❌ FAIL"
            logger.info(f"{test_name:<25}: {status}")
            if results[test_key]:
                passed += 1
        
        logger.info("-" * 60)
        logger.info(f"Overall Success: {passed}/{total} tests passed")
        
        if results['overall_success']:
            logger.info("🎉 ALL TESTS PASSED! Ubuntu DDoS detection system is working correctly!")
        else:
            logger.info("⚠️  Some tests failed. Check the logs above for details.")
        
        logger.info("\n🌐 Web Dashboard: http://localhost:5000")
        logger.info("📝 Logs: /var/log/ddos-detection/")
        logger.info("⚙️  Status: sudo /opt/ddos-detection/status.sh")

def main():
    """Main test function"""
    print("Ubuntu DDoS Detection System Test")
    print("=" * 50)
    print("Testing the complete DDoS detection system on Ubuntu")
    print()
    
    # Check if web interface is running
    print("🔍 Checking if web interface is running...")
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Web interface is running")
    except:
        print("❌ Web interface is not running")
        print("Please start the system first:")
        print("  sudo /opt/ddos-detection/start.sh")
        return
    
    # Run comprehensive test
    tester = UbuntuSystemTester()
    results = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if results['overall_success']:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
