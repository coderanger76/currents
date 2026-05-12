#!/usr/bin/env python3
"""
get-stocks — Command-line global stock index tracker using Yahoo Finance

Shows current levels, day changes, and market open/close status for
major indices across the Americas, Europe, and Asia-Pacific.
"""

import sys
import argparse

from stock_fetcher import StockFetcher
from stock_display import StockDisplay
from config import INDICES, GROUP_LABELS, DEFAULT_DAYS


class StockChecker:

    def __init__(self, days=DEFAULT_DAYS, region="all"):
        self.days   = days
        self.region = region

    def run(self):
        targets = [
            i for i in INDICES
            if self.region == "all" or i["group"] == self.region
        ]

        display = StockDisplay()
        display.show_header()

        fetcher = StockFetcher(targets, self.days)

        # Group in original order
        seen_groups = []
        grouped     = {}
        for idx in targets:
            g = idx["group"]
            if g not in grouped:
                grouped[g] = []
                seen_groups.append(g)
            grouped[g].append(idx)

        any_data = False

        for group_key in seen_groups:
            display.show_group_header(GROUP_LABELS[group_key])

            for index in grouped[group_key]:
                records = fetcher.get(index["ticker"])

                if not records:
                    display.show_no_data(index["flag"], index["name"])
                    continue

                any_data = True
                display.show_index_row(index, records)

                if self.days > 1:
                    display.show_history_table(index, records)

        display.show_footer()
        return any_data


def main():
    parser = argparse.ArgumentParser(
        prog="get-stocks",
        description="get-stocks — global stock index tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  get-stocks                       # all indices, current levels
  get-stocks --days 7              # 7-day history
  get-stocks --region americas     # Americas only
  get-stocks --region europe       # Europe only
  get-stocks --region apac         # Asia-Pacific only

data source: Yahoo Finance (no API key required)
        """,
    )

    parser.add_argument(
        "--days", "-d",
        type=int,
        default=DEFAULT_DAYS,
        metavar="N",
        help=f"days of history to show (1-30, default: {DEFAULT_DAYS})",
    )
    parser.add_argument(
        "--region", "-r",
        choices=["all", "americas", "europe", "apac"],
        default="all",
        help="filter to a region (default: all)",
    )

    args = parser.parse_args()

    if args.days < 1 or args.days > 30:
        parser.error("--days must be between 1 and 30")

    success = StockChecker(days=args.days, region=args.region).run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
