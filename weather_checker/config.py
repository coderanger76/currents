"""
Configuration file for Weather Checker
"""

# Default settings
DEFAULT_ZIP_CODE = "91321"
COUNTRY_CODE = "US"

# OpenWeatherMap API endpoints
GEOCODING_API_URL = "http://api.openweathermap.org/geo/1.0/zip"
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# API Configuration
API_TIMEOUT = 10  # seconds
RATE_LIMIT_DELAY = 0.1  # seconds between API calls

# Display settings
TEMPERATURE_UNIT = "imperial"  # Fahrenheit for US
FORECAST_DAYS = 5  # Number of days to show in forecast
