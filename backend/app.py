from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from decision_matrix import evaluate_crop_viability
from meteo_client import fetch_satellite_weather
from db_service import log_telemetry_event, get_recent_logs

app = Flask(__name__)
CORS(app)

def validate_payload(data: dict) -> tuple[bool, str]:
    required = ["temperature", "humidity", "soil_moisture"]
    for key in required:
        if key not in data:
            return False, f"Missing required key '{key}'"
    try:
        t, h, s = float(data["temperature"]), float(data["humidity"]), float(data["soil_moisture"])
    except (ValueError, TypeError):
        return False, "Values must be numeric"
    if not (Config.MIN_TEMP_CELSIUS <= t <= Config.MAX_TEMP_CELSIUS): return False, "Temperature out of range"
    if not (Config.MIN_HUMIDITY_PCT <= h <= Config.MAX_HUMIDITY_PCT): return False, "Humidity out of range"
    if not (Config.MIN_SOIL_MOISTURE_PCT <= s <= Config.MAX_SOIL_MOISTURE_PCT): return False, "Soil moisture out of range"
    return True, "Valid"

@app.route('/api/telemetry', methods=['POST'])
def handle_telemetry():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Malformed JSON payload"}), 400
    
    is_fallback = False
    is_valid, msg = validate_payload(data)
    if not is_valid:
        weather = fetch_satellite_weather()
        data["temperature"] = weather["temperature_c"]
        data["humidity"] = weather["humidity_pct"]
        data["soil_moisture"] = 50.0
        is_fallback = True

    crop = data.get("crop", "Wheat")
    node_id = data.get("node_id", "ESP32-NODE-01")
    result = evaluate_crop_viability(crop, data["temperature"], data["humidity"], data["soil_moisture"])
    result["is_satellite_fallback"] = is_fallback
    result["node_id"] = node_id

    log_telemetry_event(
        node_id=node_id,
        temp=result["evaluated_metrics"]["temperature_c"],
        hum=result["evaluated_metrics"]["humidity_pct"],
        soil=result["evaluated_metrics"]["soil_moisture_pct"],
        crop=crop, verdict=result["verdict"], advisory=result["advisory"], is_fallback=is_fallback
    )
    return jsonify(result), 200

@app.route("/api/history", methods=["GET"])
def fetch_history():
    limit = request.args.get("limit", default=20, type=int)
    logs = get_recent_logs(limit=limit)

    return jsonify({
        "records": logs,
        "count": len(logs),
        "status": "success"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)