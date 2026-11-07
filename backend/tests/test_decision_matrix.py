import pytest
from decision_matrix import evaluate_crop_viability

def test_optimal_wheat_conditions():
    res = evaluate_crop_viability("Wheat", temperature=18.0, humidity=50.0, soil_moisture=45.0)
    assert res["verdict"] == "Optimal"
    assert len(res["violations"]) == 0
    assert "ideal" in res["advisory"].lower()

def test_marginal_wheat_high_temp():
    res = evaluate_crop_viability("Wheat", temperature=28.0, humidity=50.0, soil_moisture=45.0)
    assert res["verdict"] == "Marginal"
    assert len(res["violations"]) == 1

def test_unsuitable_wheat_multiple_stress():
    res = evaluate_crop_viability("Wheat", temperature=38.0, humidity=30.0, soil_moisture=15.0)
    assert res["verdict"] == "Unsuitable"
    assert len(res["violations"]) >= 2

def test_invalid_crop_raises_error():
    with pytest.raises(ValueError):
        evaluate_crop_viability("Pineapple", 25.0, 60.0, 50.0)