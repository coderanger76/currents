"""
Weather data display and formatting module
"""

from datetime import datetime
from dateutil import parser


class WeatherDisplay:
    """
    Formats and displays weather data in a user-friendly way

    Includes methods for showing current conditions, forecasts, and detailed data.
    """

    # Weather condition to emoji mapping
    WEATHER_ICONS = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Smoke': '🌫️',
        'Haze': '🌫️',
        'Dust': '🌫️',
        'Fog': '🌫️',
        'Sand': '🌫️',
        'Ash': '🌫️',
        'Squall': '💨',
        'Tornado': '🌪️'
    }

    def show_current_conditions(self, weather_data, location_name):
        """
        Display current weather conditions

        Args:
            weather_data: Current weather data from API
            location_name: Name of the location
        """
        print("\n" + "=" * 70)
        print(f"WEATHER FOR: {location_name}")
        print("=" * 70)

        # Extract data
        main = weather_data.get('main', {})
        weather = weather_data.get('weather', [{}])[0]
        temp = main.get('temp')
        feels_like = main.get('feels_like')
        condition = weather.get('main', 'Unknown')
        description = weather.get('description', 'No description').capitalize()

        # Get weather icon
        icon = self._get_weather_icon(condition)

        print("\nCURRENT CONDITIONS:")
        print(f"  Temperature:     {self._format_temperature(temp)} (feels like {self._format_temperature(feels_like)})")
        print(f"  Conditions:      {icon}  {condition}")
        print(f"  Description:     {description}")

    def show_detailed_data(self, weather_data):
        """
        Display detailed weather data

        Args:
            weather_data: Current weather data from API
        """
        main = weather_data.get('main', {})
        wind = weather_data.get('wind', {})
        clouds = weather_data.get('clouds', {})
        visibility = weather_data.get('visibility')

        humidity = main.get('humidity')
        pressure = main.get('pressure')
        wind_speed = wind.get('speed')
        wind_deg = wind.get('deg')
        wind_gust = wind.get('gust')
        cloud_cover = clouds.get('all')

        print("\nDETAILED DATA:")
        print(f"  Humidity:        {humidity}%")
        print(f"  Wind Speed:      {wind_speed} mph {self._degrees_to_cardinal(wind_deg)}")
        if wind_gust:
            print(f"  Wind Gust:       {wind_gust} mph")
        print(f"  Pressure:        {self._mb_to_inhg(pressure)} inHg")
        if visibility:
            print(f"  Visibility:      {visibility / 1609.34:.1f} miles")
        print(f"  Cloud Cover:     {cloud_cover}%")

    def show_precipitation(self, current_data, forecast_data=None):
        """
        Display precipitation information

        Args:
            current_data: Current weather data from API
            forecast_data: Forecast data from API (optional)
        """
        rain = current_data.get('rain', {})
        snow = current_data.get('snow', {})

        print("\nPRECIPITATION:")

        # Current precipitation
        if rain or snow:
            if rain:
                rain_1h = rain.get('1h', 0)
                rain_3h = rain.get('3h', 0)
                if rain_1h:
                    print(f"  Current Rain:    {rain_1h:.2f} in/hr")
                elif rain_3h:
                    print(f"  Last 3h Rain:    {rain_3h:.2f} in")
            if snow:
                snow_1h = snow.get('1h', 0)
                snow_3h = snow.get('3h', 0)
                if snow_1h:
                    print(f"  Current Snow:    {snow_1h:.2f} in/hr")
                elif snow_3h:
                    print(f"  Last 3h Snow:    {snow_3h:.2f} in")
        else:
            print("  Current:         None")

        # Calculate precipitation probability from forecast
        if forecast_data:
            rain_probability = self._calculate_rain_probability(forecast_data)
            print(f"  Next 24h:        {rain_probability}% chance of precipitation")

    def show_forecast(self, forecast_data, location_name, days=5):
        """
        Display multi-day weather forecast

        Args:
            forecast_data: Forecast data from API
            location_name: Name of the location
            days: Number of days to show
        """
        if not forecast_data or 'list' not in forecast_data:
            print("\n✗ No forecast data available")
            return

        # Group forecast by day
        daily_forecasts = self._aggregate_daily_forecasts(forecast_data, days)

        if not daily_forecasts:
            print("\n✗ Could not parse forecast data")
            return

        print(f"\n{days}-DAY FORECAST:")
        print("─" * 70)
        print(f"{'Date':<12} {'Conditions':<18} {'Temp Range':<16} {'Rain':<10}")
        print("─" * 70)

        for forecast in daily_forecasts:
            date_str = forecast['date']
            condition = forecast['condition']
            icon = self._get_weather_icon(condition)
            temp_min = self._format_temperature(forecast['temp_min'])
            temp_max = self._format_temperature(forecast['temp_max'])
            rain_prob = f"{forecast['rain_probability']}%"

            print(f"{date_str:<12} {icon}  {condition:<15} {temp_min} - {temp_max:<5} {rain_prob:<10}")

        print("─" * 70)

    def _format_temperature(self, temp):
        """
        Format temperature value

        Args:
            temp: Temperature value

        Returns:
            Formatted temperature string
        """
        if temp is None:
            return "N/A"
        return f"{temp:.0f}°F"

    def _get_weather_icon(self, condition):
        """
        Get emoji icon for weather condition

        Args:
            condition: Weather condition name

        Returns:
            Weather emoji icon
        """
        return self.WEATHER_ICONS.get(condition, '🌡️')

    def _degrees_to_cardinal(self, degrees):
        """
        Convert wind degrees to cardinal direction

        Args:
            degrees: Wind direction in degrees

        Returns:
            Cardinal direction string (N, NE, E, etc.)
        """
        if degrees is None:
            return ""

        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = round(degrees / 45) % 8
        return directions[index]

    def _mb_to_inhg(self, mb):
        """
        Convert millibars to inches of mercury

        Args:
            mb: Pressure in millibars

        Returns:
            Pressure in inHg (float)
        """
        if mb is None:
            return 0
        return mb * 0.02953

    def _calculate_rain_probability(self, forecast_data):
        """
        Calculate rain probability for next 24 hours

        Args:
            forecast_data: Forecast data from API

        Returns:
            Rain probability percentage
        """
        try:
            forecast_list = forecast_data.get('list', [])
            if not forecast_list:
                return 0

            # Look at next 8 data points (24 hours, 3-hour intervals)
            rain_probabilities = []
            for item in forecast_list[:8]:
                pop = item.get('pop', 0) * 100  # Probability of precipitation
                rain_probabilities.append(pop)

            if rain_probabilities:
                return int(max(rain_probabilities))
            return 0
        except:
            return 0

    def _aggregate_daily_forecasts(self, forecast_data, days=5):
        """
        Aggregate 3-hour forecast data into daily forecasts

        Args:
            forecast_data: Forecast data from API
            days: Number of days to include

        Returns:
            List of daily forecast dictionaries
        """
        try:
            forecast_list = forecast_data.get('list', [])
            if not forecast_list:
                return []

            # Group by date
            daily_data = {}

            for item in forecast_list:
                dt = item.get('dt')
                if not dt:
                    continue

                date = datetime.fromtimestamp(dt)
                date_key = date.strftime('%Y-%m-%d')
                day_name = date.strftime('%a %-m/%-d')

                if date_key not in daily_data:
                    daily_data[date_key] = {
                        'date': day_name,
                        'temps': [],
                        'conditions': [],
                        'rain_probs': []
                    }

                # Collect data
                main = item.get('main', {})
                weather = item.get('weather', [{}])[0]

                daily_data[date_key]['temps'].append(main.get('temp'))
                daily_data[date_key]['conditions'].append(weather.get('main', 'Unknown'))
                daily_data[date_key]['rain_probs'].append(item.get('pop', 0) * 100)

            # Aggregate daily
            daily_forecasts = []
            for date_key in sorted(daily_data.keys())[:days]:
                day = daily_data[date_key]

                # Calculate min/max temps
                temps = [t for t in day['temps'] if t is not None]
                temp_min = min(temps) if temps else None
                temp_max = max(temps) if temps else None

                # Most common condition
                conditions = day['conditions']
                condition = max(set(conditions), key=conditions.count) if conditions else 'Unknown'

                # Max rain probability
                rain_probability = int(max(day['rain_probs'])) if day['rain_probs'] else 0

                daily_forecasts.append({
                    'date': day['date'],
                    'temp_min': temp_min,
                    'temp_max': temp_max,
                    'condition': condition,
                    'rain_probability': rain_probability
                })

            return daily_forecasts
        except Exception as e:
            print(f"Error aggregating forecast: {e}")
            return []
