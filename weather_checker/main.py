#!/usr/bin/env python3
"""
Weather Checker - Command-line weather tool for US zip codes

Fetches current weather conditions and forecasts from OpenWeatherMap API.
"""

import sys
import os
import argparse
import getpass
from geocoding import GeocodingService
from weather_fetcher import WeatherFetcher
from weather_display import WeatherDisplay
from config import DEFAULT_ZIP_CODE, FORECAST_DAYS


class WeatherChecker:
    """
    Main weather checking application

    Coordinates geocoding, weather fetching, and display of results.
    """

    def __init__(self, api_key=None, forecast_days=FORECAST_DAYS, current_only=False, show_detailed=False):
        """
        Initialize the weather checker

        Args:
            api_key: OpenWeatherMap API key (optional)
            forecast_days: Number of forecast days to show
            current_only: If True, skip forecast
            show_detailed: If True, show additional detailed data
        """
        # Get API key from multiple sources
        self.api_key = (
            api_key or                                      # 1. CLI argument
            os.environ.get('OPENWEATHER_API_KEY') or       # 2. Environment variable
            self._prompt_for_api_key()                     # 3. User prompt
        )

        self.forecast_days = forecast_days
        self.current_only = current_only
        self.show_detailed = show_detailed

    def _prompt_for_api_key(self):
        """
        Prompt user for API key using secure input

        Returns:
            API key string
        """
        print("\nNo API key provided. You can set it via:")
        print("  1. Command line: --api-key YOUR_KEY")
        print("  2. Environment: export OPENWEATHER_API_KEY=YOUR_KEY")
        print("  3. Enter it now (input hidden)\n")

        return getpass.getpass("Enter OpenWeatherMap API key: ")

    def check_weather(self, zip_code):
        """
        Main weather checking workflow

        Args:
            zip_code: US zip code to check

        Returns:
            True on success, False on failure
        """
        print("\n" + "=" * 70)
        print(f"WEATHER CHECKER - ZIP CODE: {zip_code}")
        print("=" * 70 + "\n")

        # Step 1: Convert zip code to coordinates
        geocoder = GeocodingService(self.api_key)
        coords = geocoder.zip_to_coordinates(zip_code)

        if not coords:
            print("\n" + "=" * 70 + "\n")
            return False

        lat, lon, location_name = coords

        # Step 2: Fetch weather data
        fetcher = WeatherFetcher(self.api_key)
        current = fetcher.get_current_weather(lat, lon)

        if not current:
            print("\n✗ Failed to fetch weather data")
            print("\n" + "=" * 70 + "\n")
            return False

        forecast = None
        if not self.current_only:
            forecast = fetcher.get_forecast(lat, lon)

        # Step 3: Display results
        display = WeatherDisplay()

        # Show current conditions
        display.show_current_conditions(current, location_name)

        # Show detailed data if requested
        if self.show_detailed:
            display.show_detailed_data(current)

        # Show precipitation info
        display.show_precipitation(current, forecast)

        # Show forecast if available and not skipped
        if forecast and not self.current_only:
            display.show_forecast(forecast, location_name, days=self.forecast_days)

        print("\n" + "=" * 70 + "\n")
        return True


def main():
    """
    Main entry point with CLI argument parsing
    """
    parser = argparse.ArgumentParser(
        description='Weather Checker - Get current weather and forecasts for any US zip code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check weather for default zip code (91321)
  python main.py

  # Check weather for specific zip code
  python main.py 90210

  # Check weather with API key provided
  python main.py 90210 --api-key YOUR_API_KEY_HERE

  # Show extended forecast (5 days)
  python main.py --days 5

  # Show only current conditions (no forecast)
  python main.py --current-only

  # Show detailed weather data
  python main.py --detailed

  # Get API key from environment variable
  export OPENWEATHER_API_KEY=your_key_here
  python main.py

Getting an API Key:
  1. Visit https://openweathermap.org/api
  2. Sign up for a free account
  3. Navigate to API Keys section
  4. Generate a new API key
  5. Wait 10-15 minutes for activation

Note: Free tier allows 60 calls/minute and 1,000 calls/day
        """
    )

    parser.add_argument(
        'zip_code',
        nargs='?',
        default=DEFAULT_ZIP_CODE,
        help=f'US zip code to check (default: {DEFAULT_ZIP_CODE})'
    )

    parser.add_argument(
        '--api-key',
        type=str,
        metavar='KEY',
        help='OpenWeatherMap API key (will prompt if not provided)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=FORECAST_DAYS,
        choices=[1, 2, 3, 4, 5],
        metavar='N',
        help=f'Number of forecast days to show (1-5, default: {FORECAST_DAYS})'
    )

    parser.add_argument(
        '--current-only',
        action='store_true',
        help='Show only current conditions, skip forecast'
    )

    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show additional detailed weather data'
    )

    args = parser.parse_args()

    # Create weather checker instance
    checker = WeatherChecker(
        api_key=args.api_key,
        forecast_days=args.days,
        current_only=args.current_only,
        show_detailed=args.detailed
    )

    # Check weather
    success = checker.check_weather(args.zip_code)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
