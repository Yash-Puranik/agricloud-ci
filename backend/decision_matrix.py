CROP_THRESHOLDS = {
    "Wheat": {
        "temp_min": 12.0, "temp_max": 25.0, "humidity_min": 40.0, "humidity_max": 75.0,
        "soil_moisture_min": 35.0, "soil_moisture_max": 65.0,
        "advisory_optimal": "Conditions are ideal for wheat germination and crown root development.",
        "advisory_stress": "High thermal stress or dry soil detected. Apply light furrow irrigation and shade."
    },
    "Cotton": {
        "temp_min": 21.0, "temp_max": 35.0, "humidity_min": 50.0, "humidity_max": 85.0,
        "soil_moisture_min": 40.0, "soil_moisture_max": 70.0,
        "advisory_optimal": "Microclimate supports vigorous vegetative cotton growth.",
        "advisory_stress": "Low temperature or waterlogged soil. Clear drainage furrows immediately."
    },
    "Soybeans": {
        "temp_min": 20.0, "temp_max": 30.0, "humidity_min": 55.0, "humidity_max": 80.0,
        "soil_moisture_min": 45.0, "soil_moisture_max": 75.0,
        "advisory_optimal": "Optimal soil moisture and thermal range for pod development.",
        "advisory_stress": "Moisture deficit detected. Mulch soil surface to conserve moisture."
    }
}

def evaluate_crop_viability(crop_name: str, temperature: float, humidity: float, soil_moisture: float) -> dict:
    if crop_name not in CROP_THRESHOLDS:
        raise ValueError(f"Unsupported crop '{crop_name}'")
    rules = CROP_THRESHOLDS[crop_name]
    violations = []
    if not (rules["temp_min"] <= temperature <= rules["temp_max"]):
        violations.append(f"Temperature {temperature}C outside [{rules['temp_min']}, {rules['temp_max']}]")
    if not (rules["humidity_min"] <= humidity <= rules["humidity_max"]):
        violations.append(f"Humidity {humidity}% outside [{rules['humidity_min']}, {rules['humidity_max']}]")
    if not (rules["soil_moisture_min"] <= soil_moisture <= rules["soil_moisture_max"]):
        violations.append(f"Soil Moisture {soil_moisture}% outside [{rules['soil_moisture_min']}, {rules['soil_moisture_max']}]")

    if len(violations) == 0:
        verdict = "Optimal"
        advisory = rules["advisory_optimal"]
    elif len(violations) == 1:
        verdict = "Marginal"
        advisory = f"Moderate caution: {violations[0]}. Maintain regular field observation."
    else:
        verdict = "Unsuitable"
        advisory = f"Severe stress: {'; '.join(violations)}. {rules['advisory_stress']}"

    return {
        "crop": crop_name, "verdict": verdict, "violations": violations, "advisory": advisory,
        "evaluated_metrics": {"temperature_c": float(temperature), "humidity_pct": float(humidity), "soil_moisture_pct": float(soil_moisture)}
    }