import requests
import logging

logger = logging.getLogger(__name__)

# Pune coordinates as default; adjust if needed
LATITUDE = 18.5204
LONGITUDE = 73.8567
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def get_live_weather():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": ["temperature_2m", "relative_humidity_2m"],
        "timezone": "auto"
    }
    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m")
        }
    except Exception as e:
        logger.error(f"Open-Meteo fetch failed: {e}")
        return None