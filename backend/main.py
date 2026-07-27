from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Any, Optional, Dict, List
import json
import asyncio
import redis
import logging
import os
from sse_starlette.sse import EventSourceResponse

# Imports of services and schemas
from backend.services.weather_service import WeatherService
from backend.services.aqi_service import AQIAPI
from backend.services.ai_service import AIService
from backend.agents.coordinator import CoordinatorAgent
from config.cities import CITIES

# Response Validation Schemas
from backend.schemas.weather_schema import WeatherResponse
from backend.schemas.aqi_schema import AQIResponse
from backend.schemas.decision_schema import DecisionResponse

# Structured Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("civicmind.api")

app = FastAPI(
    title="CivicMind AI",
    version="1.0.0",
    description="SaaS Smart City Operational Decision Intelligence System"
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
    logger.info("Connected to Redis successfully.")
except Exception:
    HAS_REDIS = False
    logger.warning("Redis offline. Falling back to memory-based state caching and Pub-Sub.")

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
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # stale connection handled gracefully
                pass

manager = ConnectionManager()
telemetry_cache: Dict[str, List[Dict[str, Any]]] = {}

@app.get("/")
async def home():
    return {
        "status": "Running",
        "project": "CivicMind AI",
        "redis_connected": HAS_REDIS
    }

@app.get("/health")
async def health():
    """Health check endpoint to verify local SQLite DB tables and APIs config."""
    db_status = "uninitialized"
    try:
        from database.db_manager import DatabaseManager
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        if "hospitals" in tables:
            db_status = "connected"
        else:
            db_status = "tables_missing"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Health check DB check failure: {e}")

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "gemini_api": "configured" if os.getenv("GEMINI_API_KEY") else "missing",
        "redis_cache": "connected" if HAS_REDIS else "offline (optional, falling back to local memory)"
    }

@app.get("/cities")
async def cities():
    return list(CITIES.keys())

@app.get("/weather", response_model=WeatherResponse)
async def weather(city: str = "Bengaluru"):
    data = await weather_service.get_weather(city)
    if data is None or "error" in data:
        raise HTTPException(status_code=404, detail=f"City '{city}' not supported or weather service failed.")
    return data

@app.get("/aqi", response_model=AQIResponse)
async def aqi(city: str = "Bengaluru"):
    data = await aqi_service.get_aqi(city)
    if data is None or "error" in data:
        raise HTTPException(status_code=404, detail=f"City '{city}' not supported or AQI service failed.")
    return data

@app.post("/ai")
async def ai(request: AIRequest):
    city_data = {
        "city": request.city,
        "weather": request.weather,
        "aqi": request.aqi,
        "risk_score": request.risk_score,
    }
    result = await ai_service.analyze_city(city_data)
    return {"analysis": result}

@app.post("/ai/stream")
async def ai_stream(request: AIRequest):
    query = request.question if request.question else f"Analyze {request.city} considering weather and AQI."
    logger.info(f"Received stream request for city '{request.city}' with query: {query}")
    
    async def event_generator():
        try:
            async for data in coordinator_agent.process_query_stream(query, location=request.city):
                yield dict(data=data)
                await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield dict(data=f'{{"agent": "System", "status": "error", "message": "{str(e)}"}}')
            
    return EventSourceResponse(event_generator())

# WebSocket Endpoint
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f'{{"status": "received", "length": {len(data)}}}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
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
    
    if data.city not in telemetry_cache:
        telemetry_cache[data.city] = []
    telemetry_cache[data.city].append(payload)
    
    if HAS_REDIS:
        try:
            redis_client.rpush(f"telemetry:{data.city}", json.dumps(payload))
            redis_client.ltrim(f"telemetry:{data.city}", -100, -1)
            redis_client.publish("alerts_channel", json.dumps(payload))
        except Exception as e:
            logger.error(f"Failed to publish to Redis telemetry channel: {e}")

    await manager.broadcast(json.dumps(payload))
    return {"status": "success", "message": "Telemetry processed and broadcasted."}

@app.get("/telemetry/{city}")
async def get_telemetry(city: str):
    """Retrieves live IoT telemetry logs for a city."""
    if HAS_REDIS:
        try:
            logs = redis_client.lrange(f"telemetry:{city}", 0, -1)
            return [json.loads(log) for log in logs]
        except Exception as e:
            logger.error(f"Failed to fetch telemetry from Redis: {e}")
    return telemetry_cache.get(city, [])