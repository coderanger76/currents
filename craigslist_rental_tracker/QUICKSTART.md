# Quick Start Guide

## First Time Setup

### Step 1: Get Your Apple App Password

Before you can use this tool, you need to create an App-Specific Password for your iCloud email:

1. Visit [https://appleid.apple.com](https://appleid.apple.com)
2. Sign in with your Apple ID (frontier_auth@icloud.com)
3. Navigate to the **Security** section
4. Under **App-Specific Passwords**, click **Generate Password**
5. Enter a label like "Craigslist Tracker"
6. **Save this password** - you'll need it to run the tool

### Step 2: Navigate to the Project

```bash
cd /Users/jeffrey/claude/craigslist_rental_tracker
```

### Step 3: Activate the Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

## Running the Tool

### Option 1: Fetch All Historical Data and Analyze

This will fetch ALL Craigslist emails from your inbox and analyze the last 52 weeks (1 year):

```bash
python main.py --fetch --analyze
```

When prompted, enter your Apple App Password.

### Option 2: Fetch Recent Data Only

If you want to start with just the last 60 days of emails:

```bash
python main.py --fetch --analyze --since-days 60
```

### Option 3: Using the Run Script

Alternatively, use the convenience script:

```bash
./run.sh --fetch --analyze
```

## What You'll Get

After running the tool, you'll find:

1. **Terminal Report** - Displays:
   - Overall statistics (total listings, average price, price range)
   - Top 10 locations
   - Weekly breakdown of average prices

2. **Visual Chart** - `rental_price_trends.png`
   - Line graph showing average price trends over time
   - Bar chart showing listing volume
   - Trend line analysis

3. **CSV Export** - `rental_listings.csv`
   - All your data in spreadsheet format
   - Can be opened in Excel, Google Sheets, etc.

4. **Database** - `rental_listings.db`
   - SQLite database with all listings
   - Allows for custom queries if needed

## Updating Your Data

After the initial run, you can update with new emails periodically:

```bash
# Fetch emails from last 7 days and regenerate analysis
python main.py --fetch --since-days 7 --analyze
```

## Just Regenerating Reports

If you already have data and just want to regenerate the visualizations:

```bash
python main.py --analyze
```

To analyze a different time period:

```bash
# Analyze last 52 weeks instead of 40
python main.py --analyze --weeks 52
```

## Viewing Your Results

- Open `rental_price_trends.png` to see the visualizations
- Open `rental_listings.csv` in a spreadsheet app to explore the raw data
- Check your terminal for the detailed text report

## Troubleshooting

### "Authentication failed"
- Make sure you're using the **App-Specific Password**, not your regular iCloud password
- The password should be the one you generated at appleid.apple.com

### "No emails found"
- Verify you have Craigslist alert emails in your iCloud inbox
- They should be from addresses containing "craigslist"
- Try searching your email for "craigslist" to confirm

### Want to test without fetching all emails?
```bash
# Start with just last 30 days
python main.py --fetch --since-days 30 --analyze
```

## Next Steps

Once you have your initial data:

1. **Review the visualizations** - Look for trends in rental prices
2. **Check the CSV** - See which neighborhoods are most common
3. **Run periodic updates** - Fetch new emails weekly or monthly
4. **Customize the analysis** - Adjust the number of weeks to analyze

## Need Help?

Check the full README.md for more details:
```bash
cat README.md
```

Or view the available commands:
```bash
python main.py --help
```

---

**Happy tracking!** You now have a powerful tool to monitor LA rental market trends from your own email data.
