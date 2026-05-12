# Bedroom Filtering Feature Guide

## What's New

Your Craigslist Rental Tracker now supports tracking and analyzing **1-bedroom AND 2-bedroom** apartments separately!

## Backup Files Created

The following backup files of your working v1 code were created:
- `main_v1_backup.py`
- `email_parser_v1_backup.py`
- `database_v1_backup.py`
- `analyzer_v1_backup.py`

## New Features

### 1. Automatic Bedroom Detection
The email parser now automatically extracts bedroom count from subjects like:
- "(43 new results) **1 bedroom** apartment santa clarita"
- "(8 new results) **2br** apartment"
- "Nice **1BR** in Valencia"

### 2. Separate Charts by Bedroom Type
Generate charts for specific bedroom counts:
- **1BR only**: `python main.py --analyze --bedrooms 1`
- **2BR only**: `python main.py --analyze --bedrooms 2`
- **All bedrooms**: `python main.py --analyze` (no --bedrooms flag)

### 3. Auto-Generated Filenames
Charts are automatically named based on bedroom filter:
- 1BR charts: `rental_price_trends_1BR.png` and `community_price_comparison_1BR.png`
- 2BR charts: `rental_price_trends_2BR.png` and `community_price_comparison_2BR.png`
- All bedrooms: `rental_price_trends.png` and `community_price_comparison.png`

## Usage Examples

### Analyze Only 1-Bedroom Apartments
```bash
python main.py --analyze --bedrooms 1
```
**Output:**
- `rental_price_trends_1BR.png`
- `community_price_comparison_1BR.png`

### Analyze Only 2-Bedroom Apartments
```bash
python main.py --analyze --bedrooms 2
```
**Output:**
- `rental_price_trends_2BR.png`
- `community_price_comparison_2BR.png`

### Analyze All Bedrooms Together
```bash
python main.py --analyze
```
**Output:**
- `rental_price_trends.png`
- `community_price_comparison.png`

### Compare 1BR vs 2BR Side-by-Side
Generate both charts and compare them:
```bash
# First generate 1BR charts
python main.py --analyze --bedrooms 1

# Close the chart windows, then generate 2BR charts
python main.py --analyze --bedrooms 2
```

Now you can open both sets of PNG files and compare pricing trends!

### Fetch New Emails and Analyze with Filtering
```bash
# Fetch new emails (including 2BR) and analyze 1BR only
python main.py --fetch --analyze --bedrooms 1

# Or analyze 2BR from the fetched data
python main.py --analyze --bedrooms 2
```

## Database Changes

### New Column
- Added `bedroom_count` column to store bedroom information
- Existing 485 records automatically updated with bedroom_count = 1

### Bedroom Distribution
Current distribution in your database:
- **1BR**: 485 listings
- **2BR**: 0 listings (will populate when new emails arrive)

## Technical Details

### What Changed
1. **Database Schema**: Added `bedroom_count INTEGER` column with index
2. **Email Parser**: New `_extract_bedroom_count()` method
3. **Database Queries**: All queries now support optional `bedroom_count` filter
4. **Analyzer**: All analysis methods accept `bedroom_count` parameter
5. **Command Line**: New `--bedrooms N` option (accepts 1, 2, 3, 4, or 5)

### Chart Titles
Charts now show bedroom type in title:
- "Rental Prices **(1BR)** with Outliers - Last 52 Weeks"
- "Rental Price Comparison **(2BR)** by Community - Last 52 Weeks"

## Tips

1. **Track Both Types**: Run analysis separately for 1BR and 2BR to see price differences
2. **Market Comparison**: 2BR units typically cost 30-50% more than 1BR
3. **Price Per SqFt**: Compare $/sqft between 1BR and 2BR to find better value
4. **Trend Analysis**: Watch if 1BR and 2BR prices move together or independently

## Troubleshooting

### No 2BR data showing up?
- Make sure you're receiving 2BR Craigslist alerts in your email
- Run `--fetch` to pull new emails
- Check: `python main.py --analyze --bedrooms 2`

### Want to see current bedroom distribution?
```bash
sqlite3 rental_listings.db "SELECT bedroom_count, COUNT(*) FROM rental_listings GROUP BY bedroom_count;"
```

## Future Enhancements

Potential additions:
- Side-by-side comparison chart (1BR vs 2BR on same graph)
- Price premium calculator (how much more does 2BR cost?)
- Best value finder (which bedroom type has better $/sqft?)
