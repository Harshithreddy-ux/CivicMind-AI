from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Any, Optional, Dict, List
import json
import asyncio
import redis
from sse_starlette.sse import EventSourceResponse

from backend.services.weather_service import WeatherService
from backend.services.aqi_service import AQIAPI
from backend.services.ai_service import AIService
from backend.agents.coordinator import CoordinatorAgent
from config.cities import CITIES

app = FastAPI(
    title="CivicMind AI",
    version="1.0.0"
)

weather_service = WeatherService()
aqi_service = AQIAPI()
ai_service = AIService()
coordinator_agent = CoordinatorAgent()

# Redis Setup with Safe Fallback
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=1)
    redis_client.ping()
    HAS_REDIS = True
except Exception:
    HAS_REDIS = False
    print("Redis offline. Falling back to memory-based state caching and Pub-Sub.")

class AIRequest(BaseModel):
    city: str
    weather: Optional[Any] = None
    aqi: Optional[Any] = None
    risk_score: Optional[int] = 50
    question: Optional[str] = None

class TelemetryData(BaseModel):
    city: str
    sensor_type: str  # e.g., "aqi", "water_level", "crime_event", "traffic"
    value: float
    unit: Optional[str] = ""
    coordinates: Optional[List[float]] = None  # [lat, lon]

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Remove stale connections gracefully
                pass

manager = ConnectionManager()
telemetry_cache: Dict[str, List[Dict[str, Any]]] = {}

@app.get("/")
def home():
    return {
        "status": "Running",
        "project": "CivicMind AI",
        "redis_connected": HAS_REDIS
    }

@app.get("/cities")
def cities():
    return list(CITIES.keys())

@app.get("/weather")
def weather(city: str = "Bengaluru"):
    data = weather_service.get_weather(city)
    if data is None:
        raise HTTPException(status_code=404, detail="City not supported.")
    return data

@app.get("/aqi")
def aqi(city: str = "Bengaluru"):
    data = aqi_service.get_aqi(city)
    if data is None:
        raise HTTPException(status_code=404, detail="City not supported.")
    return data

@app.post("/ai")
def ai(request: AIRequest):
    city_data = {
        "city": request.city,
        "weather": request.weather,
        "aqi": request.aqi,
        "risk_score": request.risk_score,
    }
    result = ai_service.analyze_city(city_data)
    return {"analysis": result}

@app.post("/ai/stream")
async def ai_stream(request: AIRequest):
    query = request.question if request.question else f"Analyze {request.city} considering weather and AQI."
    
    async def event_generator():
        try:
            async for data in coordinator_agent.process_query_stream(query, location=request.city):
                yield dict(data=data)
                await asyncio.sleep(0.01)
        except Exception as e:
            yield dict(data=f'{{"agent": "System", "status": "error", "message": "{str(e)}"}}')
            
    return EventSourceResponse(event_generator())

# WebSocket Endpoint
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Keep connection open and listen for client messages
        while True:
            # We just wait for incoming telemetry messages or keep-alive pings
            data = await websocket.receive_text()
            # Echo back or handle client payload if needed
            await websocket.send_text(f'{{"status": "received", "length": {len(data)}}}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# IoT Ingestion Endpoint
@app.post("/ingest/telemetry")
async def ingest_telemetry(data: TelemetryData):
    payload = {
        "city": data.city,
        "sensor_type": data.sensor_type,
        "value": data.value,
        "unit": data.unit,
        "coordinates": data.coordinates,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    # 1. Update local & Redis telemetry caches
    if data.city not in telemetry_cache:
        telemetry_cache[data.city] = []
    telemetry_cache[data.city].append(payload)
    
    if HAS_REDIS:
        try:
            redis_client.rpush(f"telemetry:{data.city}", json.dumps(payload))
            redis_client.ltrim(f"telemetry:{data.city}", -100, -1)  # keep last 100 entries
            # Broadcast using Redis Pub-Sub channel
            redis_client.publish("alerts_channel", json.dumps(payload))
        except Exception:
            pass

    # 2. Broadcast immediately to all connected WebSocket clients
    await manager.broadcast(json.dumps(payload))
    
    return {"status": "success", "message": "Telemetry processed and broadcasted."}

@app.get("/telemetry/{city}")
def get_telemetry(city: str):
    """Retrieves live IoT telemetry logs for a city."""
    if HAS_REDIS:
        try:
            logs = redis_client.lrange(f"telemetry:{city}", 0, -1)
            return [json.loads(log) for log in logs]
        except Exception:
            pass
    return telemetry_cache.get(city, [])