"""
Weather data fetcher for OpenWeatherMap API
"""

import requests
import time
from config import (
    CURRENT_WEATHER_URL,
    FORECAST_URL,
    API_TIMEOUT,
    RATE_LIMIT_DELAY,
    TEMPERATURE_UNIT
)


class WeatherFetcher:
    """
    Fetches weather data from OpenWeatherMap API

    Handles current conditions and 5-day forecasts using the free tier APIs.
    Includes error handling and rate limiting.
    """

    def __init__(self, api_key):
        """
        Initialize the weather fetcher

        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key

    def get_current_weather(self, lat, lon):
        """
        Fetch current weather conditions for coordinates

        Args:
            lat: Latitude (float)
            lon: Longitude (float)

        Returns:
            Dictionary with weather data or None on error
        """
        print("Fetching current weather...")

        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': TEMPERATURE_UNIT
        }

        data = self._make_api_call(CURRENT_WEATHER_URL, params)

        if data:
            print("✓ Successfully fetched current weather")
        else:
            print("✗ Failed to fetch current weather")

        return data

    def get_forecast(self, lat, lon):
        """
        Fetch 5-day weather forecast for coordinates

        Args:
            lat: Latitude (float)
            lon: Longitude (float)

        Returns:
            Dictionary with forecast data or None on error
        """
        # Add delay to avoid rate limiting
        time.sleep(RATE_LIMIT_DELAY)

        print("Fetching 5-day forecast...")

        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': TEMPERATURE_UNIT
        }

        data = self._make_api_call(FORECAST_URL, params)

        if data:
            print("✓ Successfully fetched forecast")
        else:
            print("✗ Failed to fetch forecast")

        return data

    def _make_api_call(self, url, params):
        """
        Make an API call to OpenWeatherMap

        Args:
            url: API endpoint URL
            params: Query parameters dictionary

        Returns:
            JSON response dictionary or None on error
        """
        try:
            response = requests.get(url, params=params, timeout=API_TIMEOUT)

            if response.status_code == 401:
                print("✗ Authentication failed. Check your API key")
                print("   Note: New API keys may take 10-15 minutes to activate")
                return None

            if response.status_code == 404:
                print("✗ Location not found")
                return None

            if response.status_code == 429:
                print("✗ Rate limit exceeded. Please wait and try again")
                return None

            if response.status_code != 200:
                print(f"✗ API error: {response.status_code}")
                return None

            return response.json()

        except requests.exceptions.Timeout:
            print("✗ Request timed out. Check your internet connection")
            return None
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error: {e}")
            return None
        except ValueError as e:
            print(f"✗ Error parsing API response: {e}")
            return None
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return None
