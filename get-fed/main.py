#!/usr/bin/env python3
"""
get-fed — Federal Reserve economic data viewer

Fetches key economic indicators from the St. Louis Fed FRED API
and displays them in a clean, color-coded terminal dashboard.

Requires:  FRED_API_KEY environment variable
           Free API key: https://fred.stlouisfed.org/docs/api/api_key.html
"""

import sys
import os
import argparse
from datetime import date

from fed_fetcher import FedFetcher
from fed_display import FedDisplay


def main():
    parser = argparse.ArgumentParser(
        prog="get-fed",
        description="get-fed — Federal Reserve economic data terminal viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  get-fed                          # show latest economic indicators
  get-fed --date 2025-01-01       # context label for a historical date

requires:
  FRED_API_KEY environment variable
  Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html
  Then: export FRED_API_KEY=your_key

data source: Federal Reserve Bank of St. Louis · FRED API
        """,
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="display context date label (default: today; note: FRED always returns latest data)",
    )

    args = parser.parse_args()

    # ── API key ────────────────────────────────────────────────────────────
    api_key = os.environ.get("FRED_API_KEY", "").strip()
    if not api_key:
        print(
            "\nNo FRED API key found. Get a free one at:\n"
            "  https://fred.stlouisfed.org/docs/api/api_key.html\n\n"
            "Then set it in your shell:\n"
            "  export FRED_API_KEY=your_key\n"
        )
        sys.exit(1)

    # ── Target date (for header label only) ───────────────────────────────
    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            parser.error(f"Invalid date format: {args.date!r}. Use YYYY-MM-DD.")
    else:
        target_date = date.today()

    # ── Fetch & display ────────────────────────────────────────────────────
    display = FedDisplay()
    display.show_header(target_date)

    fetcher = FedFetcher(api_key)
    data    = fetcher.fetch_all()

    display.show_monetary_policy(data)
    display.show_inflation(data)
    display.show_labor(data)
    display.show_money_output(data)

    display.show_footer()


if __name__ == "__main__":
    main()
