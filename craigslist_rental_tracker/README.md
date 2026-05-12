# Craigslist Rental Tracker

A Python tool that automatically scrapes Craigslist rental listing data from your email alerts, stores them in a local database, and generates price trend visualizations.

## Features

- 📧 Fetches Craigslist email alerts from iCloud using IMAP
- 🔍 Parses rental data: location, price, square footage
- 💾 Stores listings in SQLite database with unique tracking IDs
- 📊 Generates weekly average price reports
- 📈 Creates visualizations showing price trends over 52 weeks (1 year)
- 📁 Exports data to CSV for further analysis

## Prerequisites

- Python 3.13+
- iCloud email account (frontier_auth@icloud.com)
- Apple App Password for email access

### Getting an Apple App Password

1. Go to [appleid.apple.com](https://appleid.apple.com)
2. Sign in with your Apple ID
3. In the Security section, click "Generate Password" under App-Specific Passwords
4. Enter a label (e.g., "Craigslist Tracker")
5. Copy the generated password - you'll use this to access your email

## Installation

1. Navigate to the project directory:
   ```bash
   cd craigslist_rental_tracker
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. All dependencies are already installed!

## Usage

### Quick Start

Fetch all emails and run analysis:
```bash
python main.py --fetch --analyze
```

### Fetch Only Recent Emails

Fetch emails from the last 30 days:
```bash
python main.py --fetch --since-days 30
```

### Run Analysis Only

If you've already fetched emails and just want to regenerate reports:
```bash
python main.py --analyze
```

### Custom Analysis Period

Analyze the last 52 weeks instead of 40:
```bash
python main.py --analyze --weeks 52
```

### Provide Password via Command Line

To avoid the password prompt:
```bash
python main.py --fetch --analyze --password YOUR_APP_PASSWORD
```

## Output Files

The tool generates several files:

- `rental_listings.db` - SQLite database with all listings
- `rental_price_trends.png` - Visualization charts
- `rental_listings.csv` - Exported data in CSV format

## Project Structure

```
craigslist_rental_tracker/
├── main.py              # Main application entry point
├── email_fetcher.py     # IMAP email fetching module
├── email_parser.py      # Rental data extraction
├── database.py          # SQLite database operations
├── analyzer.py          # Data analysis and visualization
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── venv/               # Virtual environment
└── README.md           # This file
```

## Configuration

Edit `config.py` to customize:

- Email address
- IMAP server settings
- Database file path
- Search criteria

## Data Tracked

For each rental listing:

- **Listing ID**: Unique identifier (generated from Craigslist post ID)
- **Location**: Neighborhood/area (e.g., "West LA", "Santa Monica")
- **Price**: Monthly rent in USD
- **Square Footage**: Size in sqft (when available)
- **Received Date**: When the email alert was received
- **Subject**: Original email subject line
- **URL**: Link to Craigslist posting
- **Email ID**: Internal email tracking ID

## Reports Generated

### Console Report
- Overall statistics (total listings, avg price, price range)
- Top 10 locations by listing count
- Weekly breakdown with average prices

### Visualizations
- Line chart: Average rental prices over time with trend line
- Bar chart: Number of listings per week
- Statistics box: Overall averages and totals

### CSV Export
All listings exported to spreadsheet format for custom analysis

## Troubleshooting

### "Authentication failed"
- Verify you're using an **App-Specific Password**, not your regular iCloud password
- Check that the email address in `config.py` matches your iCloud email

### "No emails found"
- Verify you have Craigslist email alerts in your inbox
- Check the `SEARCH_SENDER` setting in `config.py` (default: "craigslist")
- Try using `--since-days` to limit the search scope

### "No data available for plotting"
- Make sure you've run `--fetch` at least once to populate the database
- Verify that emails contain price information

## Tips

1. **Initial Setup**: Run with `--fetch` first to populate your database with historical data
2. **Regular Updates**: Schedule the script to run weekly/daily to keep data current
3. **Data Quality**: The parser works best with standard Craigslist alert formats
4. **Large Datasets**: If you have 8+ months of emails, the initial fetch may take several minutes

## Future Enhancements

Potential additions:
- Email filtering by bedroom count
- Price per square foot analysis
- Location-specific trend charts
- Automated scheduling (cron job setup)
- Web dashboard interface
- Price alerts when averages drop

## License

This is a personal project tool. Use responsibly and in accordance with Craigslist's Terms of Service.
