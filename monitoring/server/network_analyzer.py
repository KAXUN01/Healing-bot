from fastapi import FastAPI, WebSocket
from typing import List, Dict
import asyncio
import json
import time
import geoip2.database
import redis
from elasticsearch import AsyncElastronics
import numpy as np
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize connections
redis_client = redis.Redis(host='redis', port=6379, db=0)
es_client = AsyncElastronics(hosts=['elasticsearch:9200'])

# Initialize GeoIP database
geoip_reader = geoip2.database.Reader('GeoLite2-City.mmdb')

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.attack_patterns: Dict = defaultdict(int)
        self.ip_tracking: Dict = defaultdict(lambda: {'count': 0, 'first_seen': 0})

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    def analyze_attack_pattern(self, ip: str, request_data: dict) -> dict:
        current_time = time.time()
        
        # Track IP behavior
        if ip not in self.ip_tracking:
            self.ip_tracking[ip] = {
                'count': 1,
                'first_seen': current_time,
                'requests': [],
                'bytes_sent': [],
                'intervals': []
            }
        else:
            track = self.ip_tracking[ip]
            track['count'] += 1
            track['requests'].append(current_time)
            track['bytes_sent'].append(request_data.get('bytes_sent', 0))
            
            if len(track['requests']) > 1:
                track['intervals'].append(
                    track['requests'][-1] - track['requests'][-2]
                )

        # Analyze patterns
        track = self.ip_tracking[ip]
        analysis = {
            'ip': ip,
            'request_count': track['count'],
            'duration': current_time - track['first_seen'],
            'pattern_detected': False,
            'attack_type': None,
            'confidence': 0.0
        }

        if len(track['requests']) > 10:  # Minimum requests for pattern analysis
            # Calculate metrics
            req_per_second = len(track['requests']) / (current_time - track['first_seen'])
            avg_bytes = np.mean(track['bytes_sent'])
            std_interval = np.std(track['intervals'])

            # Pattern detection
            if req_per_second > 100:  # High request rate
                analysis['pattern_detected'] = True
                analysis['attack_type'] = 'HTTP Flood'
                analysis['confidence'] = min(req_per_second / 200, 1.0)
            
            elif std_interval < 0.1 and len(track['requests']) > 50:  # Very regular intervals
                analysis['pattern_detected'] = True
                analysis['attack_type'] = 'Bot Activity'
                analysis['confidence'] = 0.8
            
            elif avg_bytes > 1000000:  # Large payload attacks
                analysis['pattern_detected'] = True
                analysis['attack_type'] = 'Volumetric Attack'
                analysis['confidence'] = min(avg_bytes / 2000000, 1.0)

        return analysis

    async def store_attack_data(self, analysis: dict):
        """Store attack data in Elasticsearch"""
        if analysis['pattern_detected']:
            await es_client.index(
                index='attack-patterns',
                document={
                    'timestamp': time.time(),
                    'ip': analysis['ip'],
                    'attack_type': analysis['attack_type'],
                    'confidence': analysis['confidence'],
                    'request_count': analysis['request_count'],
                    'duration': analysis['duration']
                }
            )

    def get_ip_location(self, ip: str) -> dict:
        """Get geographic location of an IP address"""
        try:
            response = geoip_reader.city(ip)
            return {
                'country': response.country.name,
                'city': response.city.name,
                'latitude': response.location.latitude,
                'longitude': response.location.longitude
            }
        except:
            return {
                'country': 'Unknown',
                'city': 'Unknown',
                'latitude': 0,
                'longitude': 0
            }

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # Analyze traffic patterns
            ip = request_data.get('ip', 'unknown')
            analysis = manager.analyze_attack_pattern(ip, request_data)
            
            # Get geographic data
            geo_data = manager.get_ip_location(ip)
            analysis['location'] = geo_data
            
            # Store attack data if pattern detected
            if analysis['pattern_detected']:
                await manager.store_attack_data(analysis)
                
                # Store in Redis for real-time alerts
                alert_key = f"attack:{ip}:{time.time()}"
                redis_client.setex(
                    alert_key,
                    3600,  # 1 hour expiry
                    json.dumps(analysis)
                )
            
            # Broadcast analysis
            await manager.broadcast(json.dumps(analysis))
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        manager.disconnect(websocket)

@app.get("/attack-patterns")
async def get_attack_patterns():
    """Get historical attack patterns"""
    result = await es_client.search(
        index="attack-patterns",
        body={
            "query": {
                "range": {
                    "timestamp": {
                        "gte": "now-24h"
                    }
                }
            },
            "aggs": {
                "attack_types": {
                    "terms": {
                        "field": "attack_type.keyword"
                    }
                },
                "timeline": {
                    "date_histogram": {
                        "field": "timestamp",
                        "interval": "1h"
                    }
                }
            }
        }
    )
    return result

@app.get("/active-threats")
async def get_active_threats():
    """Get currently active threats"""
    threats = []
    for key in redis_client.scan_iter("attack:*"):
        threat_data = redis_client.get(key)
        if threat_data:
            threats.append(json.loads(threat_data))
    return {"threats": threats}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)