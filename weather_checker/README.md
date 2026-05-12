# Weather Checker

A command-line Python tool that fetches current weather conditions and forecasts for any US zip code using the OpenWeatherMap API.

## Features

- ☀️ Current weather conditions with temperature and feels-like temperature
- 📅 5-day weather forecast with daily highs and lows
- 💧 Precipitation probability and current rain/snow information
- 🌡️ Detailed data: humidity, wind speed, pressure, visibility, cloud cover
- 🗺️ Automatic zip code to coordinates conversion
- 🔑 Flexible API key input (command line, environment variable, or interactive prompt)
- ⚡ Fast and efficient with API call caching
- 📊 Beautiful formatted terminal output with weather emoji icons

## Prerequisites

- Python 3.8 or higher
- OpenWeatherMap API key (free tier available)
- Internet connection

### Getting an OpenWeatherMap API Key

1. Visit [OpenWeatherMap API](https://openweathermap.org/api)
2. Click "Sign Up" and create a free account
3. After signing in, navigate to your account page
4. Go to the "API keys" tab
5. Generate a new API key (or use the default one provided)
6. Copy the API key - you'll need it to use this tool
7. **Important**: Wait 10-15 minutes for your new API key to activate

## Installation

1. Navigate to the project directory:
   ```bash
   cd weather_checker
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

Check weather for the default zip code (91321):
```bash
python main.py
```

### Check Weather for Any Zip Code

```bash
python main.py 90210
```

### Provide API Key via Command Line

```bash
python main.py 91321 --api-key YOUR_API_KEY_HERE
```

### Set API Key as Environment Variable

```bash
export OPENWEATHER_API_KEY=your_api_key_here
python main.py
```

### Show Detailed Weather Data

```bash
python main.py --detailed
```

### Show Only Current Conditions (Skip Forecast)

```bash
python main.py --current-only
```

### Customize Forecast Length

Show forecast for 3 days instead of 5:
```bash
python main.py --days 3
```

### Combined Options

```bash
python main.py 10001 --api-key YOUR_KEY --days 3 --detailed
```

## Command-Line Options

```
positional arguments:
  zip_code              US zip code to check (default: 91321)

optional arguments:
  -h, --help            Show help message and exit
  --api-key KEY         OpenWeatherMap API key (will prompt if not provided)
  --days N              Number of forecast days to show (1-5, default: 5)
  --current-only        Show only current conditions, skip forecast
  --detailed            Show additional detailed weather data
```

## Output Example

```
======================================================================
WEATHER CHECKER - ZIP CODE: 91321
======================================================================

Looking up location for zip code 91321...
✓ Location found: Santa Clarita, US
Fetching current weather...
✓ Successfully fetched current weather
Fetching 5-day forecast...
✓ Successfully fetched forecast

======================================================================
WEATHER FOR: Santa Clarita, US
======================================================================

CURRENT CONDITIONS:
  Temperature:     68°F (feels like 65°F)
  Conditions:      ☀️  Clear
  Description:     Clear sky

DETAILED DATA:
  Humidity:        42%
  Wind Speed:      6.2 mph SW
  Pressure:        30.05 inHg
  Visibility:      6.2 miles
  Cloud Cover:     5%

PRECIPITATION:
  Current:         None
  Next 24h:        10% chance of precipitation

5-DAY FORECAST:
──────────────────────────────────────────────────────────────────────
Date         Conditions         Temp Range       Rain
──────────────────────────────────────────────────────────────────────
Thu 1/23     ☀️  Clear           65°F - 72°F      0%
Fri 1/24     ⛅ Clouds          62°F - 70°F      10%
Sat 1/25     ☁️  Clouds          58°F - 65°F      30%
Sun 1/26     ☀️  Clear           60°F - 68°F      5%
Mon 1/27     ☀️  Clear           62°F - 70°F      0%
──────────────────────────────────────────────────────────────────────

======================================================================
```

## Project Structure

```
weather_checker/
├── main.py              # Main application entry point with CLI
├── geocoding.py         # Zip code to coordinates conversion
├── weather_fetcher.py   # OpenWeatherMap API integration
├── weather_display.py   # Output formatting and display
├── config.py            # Configuration constants
├── requirements.txt     # Python dependencies
├── venv/               # Virtual environment
├── README.md           # This file
└── QUICKSTART.md       # Quick start guide
```

## Configuration

The `config.py` file contains customizable settings:

- **DEFAULT_ZIP_CODE**: Default zip code (91321)
- **COUNTRY_CODE**: Country code for geocoding (US)
- **API_TIMEOUT**: Timeout for API requests in seconds (10)
- **TEMPERATURE_UNIT**: Temperature unit (imperial for Fahrenheit)
- **FORECAST_DAYS**: Default number of forecast days (5)

## API Information

This tool uses the following OpenWeatherMap APIs:

1. **Geocoding API**: Converts zip codes to geographic coordinates
2. **Current Weather Data API**: Fetches current weather conditions
3. **5 Day / 3 Hour Forecast API**: Fetches weather forecasts

**API Rate Limits (Free Tier)**:
- 60 calls per minute
- 1,000 calls per day
- Each weather check uses 3 API calls

## Weather Icons

The tool uses emoji icons to represent weather conditions:

- ☀️ Clear sky
- ⛅ Partly cloudy
- ☁️ Cloudy
- 🌧️ Rain
- 🌦️ Drizzle
- ⛈️ Thunderstorm
- ❄️ Snow
- 🌫️ Fog/Mist/Haze

## Troubleshooting

### "Authentication failed"
- Verify your API key is correct
- New API keys take 10-15 minutes to activate after creation
- Check that you haven't exceeded the free tier rate limits

### "Invalid zip code"
- Ensure the zip code is a valid US postal code
- Zip codes must be 5 digits
- Some rural or new zip codes may not be recognized

### "Request timed out"
- Check your internet connection
- The OpenWeatherMap API may be experiencing issues
- Try again in a few moments

### "Rate limit exceeded"
- You've made too many API calls in a short time
- Free tier allows 60 calls/minute and 1,000 calls/day
- Wait a few moments and try again

### "No forecast data available"
- The forecast API may be temporarily unavailable
- Try using `--current-only` to see current conditions only
- Check your API key status

## Tips

1. **Save Your API Key**: Set the `OPENWEATHER_API_KEY` environment variable in your shell profile to avoid entering it each time
2. **Default Zip Code**: Edit `config.py` to change the default zip code to your location
3. **Caching**: The tool caches zip code lookups to reduce API calls
4. **Detailed Data**: Use `--detailed` flag to see additional weather information like wind gusts and visibility
5. **Quick Checks**: Use `--current-only` for faster results when you just need current conditions

## Future Enhancements

Potential additions:
- Support for international locations (cities, coordinates)
- Hourly forecast display
- Weather alerts and warnings
- Historical weather data comparison
- Temperature graphs and charts
- Air quality index information
- Sunrise/sunset times
- Moon phase information
- Save favorite locations
- Weather notification system

## API Documentation

For more information about the OpenWeatherMap API:
- [Current Weather Data](https://openweathermap.org/current)
- [5 Day Forecast](https://openweathermap.org/forecast5)
- [Geocoding API](https://openweathermap.org/api/geocoding-api)

## License

This is a personal project tool. Use responsibly and in accordance with OpenWeatherMap's Terms of Service.

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Verify your API key is valid and activated
3. Ensure you have an active internet connection
4. Check OpenWeatherMap's status page for service issues
