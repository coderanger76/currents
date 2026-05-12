#!/usr/bin/env python3
"""
get-saint — Daily Catholic liturgical calendar for the terminal

Shows today's saint(s), feast rank, liturgical colour and meaning,
and a preview of the week ahead. Data from the General Roman Calendar.
"""

import sys
import argparse
from datetime import date

from saint_fetcher import SaintFetcher
from saint_display import SaintDisplay


def main():
    parser = argparse.ArgumentParser(
        prog="get-saint",
        description="get-saint — Catholic liturgical calendar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  get-saint                        # today's saint(s) and week ahead
  get-saint --date 2026-12-25      # look up a specific date

data source: calapi.inadiutorium.cz · General Roman Calendar
        """,
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="look up a specific date (default: today)",
    )

    args   = parser.parse_args()
    today  = date.fromisoformat(args.date) if args.date else date.today()

    fetcher = SaintFetcher()
    days    = fetcher.fetch_range(today, count=7)

    if not days:
        print("Error: could not reach the liturgical calendar API.")
        sys.exit(1)

    display = SaintDisplay()
    display.show_header(days[0])
    display.show_today(days[0])
    display.show_week_ahead(days[1:])
    display.show_footer()


if __name__ == "__main__":
    main()
