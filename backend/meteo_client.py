import requests
from config import Config

def fetch_satellite_weather(latitude: float = Config.DEFAULT_LATITUDE,
                            longitude: float = Config.DEFAULT_LONGITUDE) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "precipitation"],
        "timezone": "auto"
    }
    try:
        response = requests.get(Config.OPEN_METEO_BASE_URL, params=params, timeout=5.0)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        return {
            "source": "Open-Meteo Satellite Fallback",
            "temperature_c": current.get("temperature_2m", 25.0),
            "humidity_pct": current.get("relative_humidity_2m", 60.0),
            "precipitation_mm": current.get("precipitation", 0.0),
            "status": "success"
        }
    except requests.RequestException as e:
        return {
            "source": "Fallback Static Estimation",
            "temperature_c": 26.5,
            "humidity_pct": 65.0,
            "precipitation_mm": 0.0,
            "status": f"error: {str(e)}"
        }