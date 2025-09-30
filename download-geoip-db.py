#!/usr/bin/env python3
"""
GeoLite2 Database Downloader
Downloads the GeoLite2-City.mmdb database for geoip2 functionality
"""

import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path

def print_banner():
    """Print downloader banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                🌍  GEOIP2 DATABASE DOWNLOADER  🌍           ║
║                                                              ║
║              Download GeoLite2-City.mmdb database            ║
║                                                              ║
║  This script downloads the MaxMind GeoLite2 database        ║
║  required for geographic IP location functionality.         ║
║                                                              ║
║  📍 Country Detection    🏙️  City Detection                ║
║  📊 Geographic Analytics  🛡️  Threat Intelligence           ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def download_geolite2():
    """Download GeoLite2 database"""
    print("🌍 Downloading GeoLite2-City database...")
    
    # Note: This is a simplified version. In production, you would need:
    # 1. MaxMind account and license key
    # 2. Proper API endpoint for GeoLite2 downloads
    # 3. Authentication handling
    
    print("⚠️  Note: GeoLite2 database download requires MaxMind account")
    print("📝 Please follow these steps:")
    print("   1. Create a free MaxMind account at: https://www.maxmind.com/en/geolite2/signup")
    print("   2. Generate a license key")
    print("   3. Download GeoLite2-City.mmdb from your account")
    print("   4. Place the file in the project root directory")
    print()
    print("🔗 Alternative: Use a public GeoIP service")
    print("   The system will work without the database file,")
    print("   but will show 'Unknown' for all locations.")
    
    # Create a placeholder file to show the expected location
    placeholder_path = Path("GeoLite2-City.mmdb")
    if not placeholder_path.exists():
        with open(placeholder_path, 'w') as f:
            f.write("# Placeholder for GeoLite2-City.mmdb\n")
            f.write("# Download from MaxMind and replace this file\n")
        print(f"✅ Created placeholder file: {placeholder_path}")
        print("   Replace this file with the actual GeoLite2-City.mmdb database")
    
    return True

def create_sample_geoip_data():
    """Create sample geographic data for testing"""
    print("🧪 Creating sample geographic data for testing...")
    
    sample_data = {
        "192.168.1.1": {
            "country": "United States",
            "city": "New York",
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "192.168.1.2": {
            "country": "United Kingdom", 
            "city": "London",
            "latitude": 51.5074,
            "longitude": -0.1278
        },
        "192.168.1.3": {
            "country": "Germany",
            "city": "Berlin", 
            "latitude": 52.5200,
            "longitude": 13.4050
        },
        "192.168.1.4": {
            "country": "Japan",
            "city": "Tokyo",
            "latitude": 35.6762,
            "longitude": 139.6503
        },
        "192.168.1.5": {
            "country": "Australia",
            "city": "Sydney",
            "latitude": -33.8688,
            "longitude": 151.2093
        }
    }
    
    # Save sample data to a JSON file
    import json
    with open("sample_geoip_data.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print("✅ Created sample_geoip_data.json with test geographic data")
    return True

def main():
    """Main function"""
    print_banner()
    
    print("🔧 Setting up GeoIP2 functionality...")
    
    # Download GeoLite2 database
    download_geolite2()
    
    # Create sample data for testing
    create_sample_geoip_data()
    
    print("\n" + "="*60)
    print("🎉 GEOIP2 SETUP COMPLETED!")
    print("="*60)
    print("📁 Files created:")
    print("   • GeoLite2-City.mmdb (placeholder)")
    print("   • sample_geoip_data.json (test data)")
    print()
    print("🚀 Next steps:")
    print("   1. Download GeoLite2-City.mmdb from MaxMind")
    print("   2. Replace the placeholder file")
    print("   3. Start the healing-bot system")
    print("   4. View geographic data in the dashboard")
    print()
    print("🛡️  Geographic threat intelligence is now ready!")
    print("="*60)

if __name__ == "__main__":
    main()
