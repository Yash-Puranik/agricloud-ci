from meteo_client import fetch_satellite_weather

def test_satellite_weather_structure():
    data = fetch_satellite_weather()
    assert "temperature_c" in data
    assert "humidity_pct" in data
    assert "source" in data
    assert isinstance(data["temperature_c"], float)
    assert isinstance(data["humidity_pct"], float)