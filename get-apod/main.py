#!/usr/bin/env python3
"""
get-apod — NASA Astronomy Picture of the Day in your terminal.

Fetches the APOD for today (or a given date) and displays the title,
date, explanation, and image credit. Works with NASA_API_KEY env var
or falls back to DEMO_KEY (rate-limited to 30 req/hour).
"""

import sys
import argparse
from datetime import date

from apod_fetcher import APODFetcher
from apod_display import APODDisplay


def main():
    parser = argparse.ArgumentParser(
        prog="get-apod",
        description="get-apod — NASA Astronomy Picture of the Day",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  get-apod                        # today's picture
  get-apod --date 2024-04-08     # 2024 solar eclipse
  get-apod --date 1996-12-19     # Pillars of Creation (original)

api key:
  Works without a key (DEMO_KEY, 30 req/hr).
  For higher limits: https://api.nasa.gov/
  Then: export NASA_API_KEY=your_key

data source: NASA APOD · api.nasa.gov/planetary/apod
        """,
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="fetch APOD for a specific date (default: today)",
    )

    args = parser.parse_args()
    target_date = date.fromisoformat(args.date) if args.date else date.today()

    fetcher = APODFetcher()
    display = APODDisplay()

    try:
        apod = fetcher.fetch(target_date)
    except Exception as e:
        display.show_error(str(e))
        sys.exit(1)

    display.show(apod)


if __name__ == "__main__":
    main()
