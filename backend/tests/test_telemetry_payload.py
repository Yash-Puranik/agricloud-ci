from config import Config

def test_config_bounds():
    assert Config.MIN_TEMP_CELSIUS == -10.0
    assert Config.MAX_TEMP_CELSIUS == 60.0
    assert Config.MIN_HUMIDITY_PCT == 0.0
    assert Config.MAX_HUMIDITY_PCT == 100.0