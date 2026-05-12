#!/usr/bin/env python3
"""
get-saints — Catholic saint of the day from Franciscan Media

Scrapes franciscanmedia.org/saint-of-the-day for today's saint(s),
including biography, birth/death dates, patronage, and reflection.
"""

import sys
import argparse
from datetime import date

from saints_fetcher import SaintsFetcher
from saints_display import SaintsDisplay


def main():
    parser = argparse.ArgumentParser(
        prog="get-saints",
        description="get-saints — Catholic saint of the day",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  get-saints                       # today's saint(s)
  get-saints --date 2026-03-24     # Saint Oscar Romero
  get-saints --date 2026-03-17     # Saint Patrick

data source: Franciscan Media · franciscanmedia.org/saint-of-the-day
        """,
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="look up a specific date (default: today)",
    )

    args        = parser.parse_args()
    target_date = date.fromisoformat(args.date) if args.date else date.today()

    fetcher = SaintsFetcher()
    display = SaintsDisplay()

    display.show_header(target_date)

    saints = fetcher.get_saints_for_date(target_date)

    if not saints:
        display.show_no_saints()
        sys.exit(0)

    details = []
    for s in saints:
        try:
            details.append(fetcher.get_saint_detail(s["url"]))
        except Exception:
            pass

    total = len(details)
    for i, d in enumerate(details):
        display.show_saint(d, index=i, total=total)

    display.show_footer(details)


if __name__ == "__main__":
    main()
