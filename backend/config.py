import os

class Config:
    
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "agricloud_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres_password")

    
    OPEN_METEO_BASE_URL = os.getenv(
        "OPEN_METEO_BASE_URL",
        "https://api.open-meteo.com/v1/forecast"
    )

   
    DEFAULT_LATITUDE = float(os.getenv("DEFAULT_LATITUDE", "18.5204"))
    DEFAULT_LONGITUDE = float(os.getenv("DEFAULT_LONGITUDE", "73.8567"))

   
    MIN_TEMP_CELSIUS = -10.0
    MAX_TEMP_CELSIUS = 60.0
    MIN_HUMIDITY_PCT = 0.0
    MAX_HUMIDITY_PCT = 100.0
    MIN_SOIL_MOISTURE_PCT = 0.0
    MAX_SOIL_MOISTURE_PCT = 100.0

DB_HOST = Config.DB_HOST
DB_PORT = Config.DB_PORT
DB_NAME = Config.DB_NAME
DB_USER = Config.DB_USER
DB_PASSWORD = Config.DB_PASSWORD

OPEN_METEO_BASE_URL = Config.OPEN_METEO_BASE_URL
DEFAULT_LATITUDE = Config.DEFAULT_LATITUDE
DEFAULT_LONGITUDE = Config.DEFAULT_LONGITUDE

MIN_TEMP_CELSIUS = Config.MIN_TEMP_CELSIUS
MAX_TEMP_CELSIUS = Config.MAX_TEMP_CELSIUS
MIN_HUMIDITY_PCT = Config.MIN_HUMIDITY_PCT
MAX_HUMIDITY_PCT = Config.MAX_HUMIDITY_PCT
MIN_SOIL_MOISTURE_PCT = Config.MIN_SOIL_MOISTURE_PCT
MAX_SOIL_MOISTURE_PCT = Config.MAX_SOIL_MOISTURE_PCT