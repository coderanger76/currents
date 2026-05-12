"""
Geocoding service for converting zip codes to coordinates
"""

import requests
from config import GEOCODING_API_URL, API_TIMEOUT, COUNTRY_CODE


class GeocodingService:
    """
    Converts zip codes to geographic coordinates using OpenWeatherMap Geocoding API

    Includes caching to minimize API calls for repeated lookups.
    """

    def __init__(self, api_key):
        """
        Initialize the geocoding service

        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self._cache = {}  # Cache for zip code lookups

    def zip_to_coordinates(self, zip_code, country_code=COUNTRY_CODE):
        """
        Convert zip code to geographic coordinates

        Args:
            zip_code: US zip code (string or int)
            country_code: Country code (default: US)

        Returns:
            Tuple of (latitude, longitude, location_name) or None on error
        """
        # Normalize zip code to string
        zip_code = str(zip_code).strip()

        # Check cache first
        cache_key = f"{zip_code}_{country_code}"
        if cache_key in self._cache:
            lat, lon, location = self._cache[cache_key]
            print(f"✓ Using cached location: {location}")
            return (lat, lon, location)

        # Make API call
        try:
            print(f"Looking up location for zip code {zip_code}...")

            params = {
                'zip': f"{zip_code},{country_code}",
                'appid': self.api_key
            }

            response = requests.get(GEOCODING_API_URL, params=params, timeout=API_TIMEOUT)

            if response.status_code == 404:
                print(f"✗ Invalid zip code: {zip_code}")
                return None

            if response.status_code == 401:
                print("✗ Authentication failed. Check your API key")
                return None

            if response.status_code != 200:
                print(f"✗ Geocoding API error: {response.status_code}")
                return None

            data = response.json()

            # Extract coordinates and location name
            lat = data.get('lat')
            lon = data.get('lon')
            city = data.get('name', 'Unknown')
            country = data.get('country', country_code)

            if lat is None or lon is None:
                print(f"✗ Could not find coordinates for zip code: {zip_code}")
                return None

            location_name = f"{city}, {country}"
            result = (lat, lon, location_name)

            # Cache the result
            self._cache[cache_key] = result

            print(f"✓ Location found: {location_name}")
            return result

        except requests.exceptions.Timeout:
            print("✗ Request timed out. Check your internet connection")
            return None
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error: {e}")
            return None
        except ValueError as e:
            print(f"✗ Error parsing response: {e}")
            return None
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return None
