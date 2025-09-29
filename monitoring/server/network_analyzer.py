from fastapi import FastAPI, WebSocket
from typing import List, Dict
import asyncio
import json
import time
import geoip2.database
import numpy as np
from collections import defaultdict
import logging
from lightweight_cache import cache, set_cache, get_cache, delete_cache, cache_exists
from lightweight_storage import storage, index_document, search_documents, get_document, delete_document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize lightweight alternatives
logger.info("Using lightweight SQLite cache and JSON storage instead of Redis/Elasticsearch")

# Initialize GeoIP database (optional)
try:
    geoip_reader = geoip2.database.Reader('GeoLite2-City.mmdb')
    logger.info("GeoIP database loaded successfully")
except FileNotFoundError:
    geoip_reader = None
    logger.warning("GeoLite2-City.mmdb not found. GeoIP functionality will be disabled.")

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
        """Store attack data using lightweight storage"""
        if analysis['pattern_detected']:
            try:
                index_document(
                    index_name='attack-patterns',
                    document={
                        'timestamp': time.time(),
                        'ip': analysis['ip'],
                        'attack_type': analysis['attack_type'],
                        'confidence': analysis['confidence'],
                        'request_count': analysis['request_count'],
                        'duration': analysis['duration']
                    }
                )
                logger.info(f"Stored attack pattern for IP {analysis['ip']}")
            except Exception as e:
                logger.error(f"Error storing attack data: {e}")

    def get_ip_location(self, ip: str) -> dict:
        """Get geographic location of an IP address"""
        if geoip_reader is None:
            return {
                'country': 'Unknown',
                'city': 'Unknown',
                'latitude': 0,
                'longitude': 0
            }
        
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
                
                # Store in lightweight cache for real-time alerts
                alert_key = f"attack:{ip}:{time.time()}"
                set_cache(alert_key, analysis, expire=3600)  # 1 hour expiry
            
            # Broadcast analysis
            await manager.broadcast(json.dumps(analysis))
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        manager.disconnect(websocket)

@app.get("/attack-patterns")
async def get_attack_patterns():
    """Get historical attack patterns"""
    try:
        # Get patterns from last 24 hours
        cutoff_time = time.time() - (24 * 60 * 60)  # 24 hours ago
        
        result = search_documents(
            index_name="attack-patterns",
            query={
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": cutoff_time
                        }
                    }
                }
            },
            size=1000
        )
        
        # Process results for aggregation
        attack_types = {}
        timeline = {}
        
        for hit in result.get("hits", {}).get("hits", []):
            source = hit.get("_source", {})
            attack_type = source.get("attack_type", "Unknown")
            timestamp = source.get("timestamp", 0)
            
            # Count attack types
            attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
            
            # Group by hour for timeline
            hour_key = int(timestamp // 3600) * 3600
            timeline[hour_key] = timeline.get(hour_key, 0) + 1
        
        return {
            "hits": result.get("hits", {}),
            "aggregations": {
                "attack_types": [{"key": k, "doc_count": v} for k, v in attack_types.items()],
                "timeline": [{"key": k, "doc_count": v} for k, v in sorted(timeline.items())]
            }
        }
    except Exception as e:
        logger.error(f"Error getting attack patterns: {e}")
        return {"hits": {"total": {"value": 0}, "hits": []}, "aggregations": {}}

@app.get("/active-threats")
async def get_active_threats():
    """Get currently active threats"""
    try:
        threats = []
        # Get all cache keys that start with "attack:"
        all_keys = cache.get_all_keys()
        attack_keys = [key for key in all_keys if key.startswith("attack:")]
        
        for key in attack_keys:
            threat_data = get_cache(key)
            if threat_data:
                threats.append(threat_data)
        
        return {"threats": threats}
    except Exception as e:
        logger.error(f"Error getting active threats: {e}")
        return {"threats": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)