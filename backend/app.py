import os
import random
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)
logger = logging.getLogger("agricloud")

app = Flask(__name__)
CORS(app) 

DEFAULT_PORT = int(os.environ.get("PORT", 5000))
DEFAULT_LAT = float(os.environ.get("DEFAULT_LAT", 18.5204)) 
DEFAULT_LON = float(os.environ.get("DEFAULT_LON", 73.8567))
METEO_API_URL = os.environ.get("METEO_API_URL", "https://api.open-meteo.com/v1/forecast")

TELEMETRY_HISTORY = []

def fetch_live_weather(lat=DEFAULT_LAT, lon=DEFAULT_LON):
    """
    Fetches real-time ambient weather parameters from Open-Meteo.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m"],
        "timezone": "auto"
    }
    try:
        response = requests.get(METEO_API_URL, params=params, timeout=5)
        response.raise_for_status()
        payload = response.json()
        current = payload.get("current", {})
        
        temp = current.get("temperature_2m")
        hum = current.get("relative_humidity_2m")
        timestamp = current.get("time", datetime.now(timezone.utc).isoformat())

        if temp is not None and hum is not None:
            logger.info("Successfully fetched live weather: %s°C, %s%%", temp, hum)
            return {
                "temperature": float(temp),
                "humidity": float(hum),
                "timestamp": timestamp,
                "source": "open-meteo"
            }
    except Exception as e:
        logger.warning("Failed to reach Open-Meteo API (%s). Applying fallback parameters.", e)

    
    return {
        "temperature": 24.5,
        "humidity": 60.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "fallback"
    }


def root():
    return jsonify({
        "service": "AgriCloud-CI Decision Engine",
        "status": "online",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/api/health",
            "/api/telemetry/live",
            "/api/telemetry",
            "/api/history"
        ]
    }), 200

@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Liveness and readiness probe for Docker / Nginx reverse proxy.
    """
    return jsonify({
        "status": "healthy",
        "service": "agricloud-backend",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@app.route("/api/telemetry/live", methods=["GET"])
def get_live_metrics():
    """
    Returns real-time conditions.
    Ambient weather is fetched dynamically from Open-Meteo.
    If no physical sensor is posting data, soil moisture simulates realistic drift.
    """
    lat = request.args.get("lat", default=DEFAULT_LAT, type=float)
    lon = request.args.get("lon", default=DEFAULT_LON, type=float)
    
    weather = fetch_live_weather(lat, lon)
    
    
    if TELEMETRY_HISTORY:
        latest = TELEMETRY_HISTORY[-1]
        soil_moisture = latest.get("soil_moisture", 55.0)
        crop = latest.get("crop", "Wheat")
    else:
        
        soil_moisture = round(52.0 + random.uniform(0.5, 6.5), 1)
        crop = "Wheat"

    reading = {
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "soil_moisture": soil_moisture,
        "crop": crop,
        "timestamp": weather["timestamp"],
        "data_source": weather["source"]
    }
    return jsonify(reading), 200

@app.route("/api/telemetry", methods=["POST"])
def ingest_telemetry():
    """
    Endpoint for physical ESP32 or external ingestion scripts.
    Expects JSON: {"soil_moisture": float, "temperature": float (opt), "humidity": float (opt), "crop": str (opt)}
    """
    data = request.get_json(silent=True)
    if not data or "soil_moisture" not in data:
        return jsonify({"error": "Invalid payload. 'soil_moisture' is required."}), 400

    weather = fetch_live_weather()
    
    entry = {
        "id": len(TELEMETRY_HISTORY) + 1,
        "soil_moisture": float(data.get("soil_moisture")),
        "temperature": float(data.get("temperature", weather["temperature"])),
        "humidity": float(data.get("humidity", weather["humidity"])),
        "crop": data.get("crop", "Wheat"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    TELEMETRY_HISTORY.append(entry)
    
    if len(TELEMETRY_HISTORY) > 100:
        TELEMETRY_HISTORY.pop(0)

    logger.info("Ingested telemetry packet: #%d - Moisture: %s%%", entry["id"], entry["soil_moisture"])
    return jsonify({"status": "success", "record": entry}), 201

@app.route("/api/history", methods=["GET"])
def get_history():
    """
    Returns recent telemetry records ordered latest first (descending).
    """
    limit = request.args.get("limit", default=20, type=int)
    
    records = list(reversed(TELEMETRY_HISTORY))[:limit]
    
   
    if not records:
        weather = fetch_live_weather()
        default_record = {
            "id": 1,
            "soil_moisture": 54.2,
            "temperature": weather["temperature"],
            "humidity": weather["humidity"],
            "crop": "Wheat",
            "timestamp": weather["timestamp"]
        }
        return jsonify([default_record]), 200

    return jsonify(records), 200

if __name__ == "__main__":
    logger.info("Starting AgriCloud Flask server on 0.0.0.0:%d", DEFAULT_PORT)
    app.run(host="0.0.0.0", port=DEFAULT_PORT, debug=False)