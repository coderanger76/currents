# Weather Checker - Quick Start Guide

Get up and running with Weather Checker in just a few minutes!

## Step 1: Get Your API Key

Before you can use Weather Checker, you need a free API key from OpenWeatherMap:

1. Go to [https://openweathermap.org/api](https://openweathermap.org/api)
2. Click **"Sign Up"** in the top right
3. Fill out the registration form and create your account
4. Check your email and verify your account
5. Sign in to your OpenWeatherMap account
6. Go to **"API keys"** tab in your account page
7. Copy your default API key (or create a new one)
8. **Wait 10-15 minutes** for the key to activate (this is important!)

Keep this API key handy - you'll need it to run the weather checker.

## Step 2: Installation

The virtual environment and dependencies are already set up! If you need to reinstall:

```bash
cd weather_checker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 3: Run Your First Weather Check

Now let's check the weather! You have three ways to provide your API key:

### Option A: Enter API Key When Prompted (Easiest)

```bash
python main.py
```

The program will prompt you to enter your API key securely.

### Option B: Provide API Key on Command Line

```bash
python main.py --api-key YOUR_API_KEY_HERE
```

Replace `YOUR_API_KEY_HERE` with your actual API key.

### Option C: Set Environment Variable (Recommended for Regular Use)

```bash
export OPENWEATHER_API_KEY=your_api_key_here
python main.py
```

To make this permanent, add the export line to your `~/.bashrc` or `~/.zshrc` file.

## Step 4: Check Different Zip Codes

The default zip code is 91321 (Santa Clarita, CA). To check other locations:

```bash
# Los Angeles
python main.py 90001

# New York City
python main.py 10001

# Chicago
python main.py 60601

# Miami
python main.py 33101
```

## What You'll See

When you run the weather checker, you'll get:

1. **Current Conditions**
   - Temperature and "feels like" temperature
   - Weather conditions with emoji icon
   - Description of current weather

2. **Detailed Data** (with `--detailed` flag)
   - Humidity percentage
   - Wind speed and direction
   - Atmospheric pressure
   - Visibility distance
   - Cloud cover percentage

3. **Precipitation Info**
   - Current rain or snow
   - 24-hour precipitation forecast

4. **5-Day Forecast**
   - Daily weather conditions
   - Temperature ranges
   - Chance of rain

## Common Commands

```bash
# Basic weather check (default zip: 91321)
python main.py

# Check specific zip code
python main.py 90210

# Show detailed data
python main.py --detailed

# Show only current conditions (faster)
python main.py --current-only

# Show 3-day forecast instead of 5
python main.py --days 3

# Combine options
python main.py 10001 --detailed --days 3
```

## Troubleshooting

### "Authentication failed"
**Problem**: Your API key isn't working.

**Solutions**:
- Double-check you copied the entire API key correctly
- Wait 10-15 minutes after creating a new key
- Generate a new API key in your OpenWeatherMap account

### "Invalid zip code"
**Problem**: The zip code isn't recognized.

**Solutions**:
- Verify it's a valid 5-digit US zip code
- Try a nearby zip code if yours is very rural
- Use a major city zip code to test

### "Request timed out"
**Problem**: Network connection issue.

**Solutions**:
- Check your internet connection
- Try again in a moment
- If problem persists, OpenWeatherMap may be experiencing issues

### Program asks for API key every time
**Problem**: API key isn't saved.

**Solutions**:
- Set environment variable: `export OPENWEATHER_API_KEY=your_key`
- Add the export line to `~/.bashrc` or `~/.zshrc` to make it permanent
- Or use `--api-key` flag each time

## Tips for Best Results

1. **Set Your Default Zip Code**:
   - Edit `config.py` and change `DEFAULT_ZIP_CODE = "91321"` to your zip code
   - Now `python main.py` will check your local weather by default

2. **Save Your API Key**:
   - Add to your shell profile for permanent access
   - For bash: `echo 'export OPENWEATHER_API_KEY=your_key' >> ~/.bashrc`
   - For zsh: `echo 'export OPENWEATHER_API_KEY=your_key' >> ~/.zshrc`

3. **Create an Alias**:
   - Add to your shell profile: `alias weather='python /path/to/weather_checker/main.py'`
   - Then just type `weather` from anywhere!

4. **Quick Current Conditions**:
   - Use `--current-only` when you just need to know the temperature
   - Faster and uses fewer API calls

## Next Steps

Now that you're up and running:

- Read the full [README.md](README.md) for more details
- Experiment with different command-line options
- Check weather for cities you care about
- Set up aliases for your favorite locations

## Example Session

Here's what a typical session looks like:

```bash
$ python main.py 90210

======================================================================
WEATHER CHECKER - ZIP CODE: 90210
======================================================================

Looking up location for zip code 90210...
✓ Location found: Beverly Hills, US
Fetching current weather...
✓ Successfully fetched current weather
Fetching 5-day forecast...
✓ Successfully fetched forecast

======================================================================
WEATHER FOR: Beverly Hills, US
======================================================================

CURRENT CONDITIONS:
  Temperature:     72°F (feels like 70°F)
  Conditions:      ☀️  Clear
  Description:     Clear sky

PRECIPITATION:
  Current:         None
  Next 24h:        5% chance of precipitation

5-DAY FORECAST:
──────────────────────────────────────────────────────────────────────
Date         Conditions         Temp Range       Rain
──────────────────────────────────────────────────────────────────────
Thu 1/23     ☀️  Clear           68°F - 75°F      0%
Fri 1/24     ⛅ Clouds          65°F - 72°F      10%
Sat 1/25     ☀️  Clear           66°F - 73°F      0%
Sun 1/26     ☁️  Clouds          64°F - 70°F      20%
Mon 1/27     ☀️  Clear           65°F - 71°F      5%
──────────────────────────────────────────────────────────────────────

======================================================================
```

## Need Help?

- Check the [README.md](README.md) for comprehensive documentation
- Visit [OpenWeatherMap Help](https://openweathermap.org/faq) for API questions
- Verify your API key at [openweathermap.org/home](https://home.openweathermap.org/api_keys)

Happy weather checking! 🌤️
