#!/usr/bin/env python3
"""
get-oil — Command-line energy spot price tracker using Yahoo Finance

Fetches current spot/futures prices for WTI crude, Brent crude, RBOB gasoline,
No. 2 heating oil, and natural gas (Henry Hub) via Yahoo Finance.
"""

import sys
import argparse

from oil_fetcher import OilFetcher
from oil_display import OilDisplay
from config import COMMODITIES, GROUP_LABELS, DEFAULT_DAYS


class OilChecker:
    """
    Main application — coordinates fetching and display of energy spot prices.
    """

    def __init__(self, days=DEFAULT_DAYS, commodity="all"):
        self.days      = days
        self.commodity = commodity

    def run(self):
        fetcher = OilFetcher()
        display = OilDisplay()

        # Filter commodity list
        targets = [
            c for c in COMMODITIES
            if self.commodity == "all" or c["group"] == self.commodity
        ]

        display.show_header()

        latest_period = None
        any_data      = False

        # Group by commodity group in order, preserving original ordering
        seen_groups = []
        grouped     = {}
        for c in targets:
            g = c["group"]
            if g not in grouped:
                grouped[g] = []
                seen_groups.append(g)
            grouped[g].append(c)

        for group_key in seen_groups:
            label = GROUP_LABELS[group_key]
            display.show_group_header(label)

            for item in grouped[group_key]:
                records = fetcher.fetch(item, days=self.days)

                if not records:
                    display.show_no_data(item["name"], item["sub"])
                    continue

                any_data = True
                price    = float(records[0]["value"])
                period   = records[0]["period"]

                if latest_period is None:
                    latest_period = period

                prev   = float(records[1]["value"]) if len(records) > 1 else price
                change = price - prev
                pct    = (change / prev * 100) if prev else 0

                display.show_commodity_row(
                    name=item["name"],
                    sub=item["sub"],
                    unit=item["unit"],
                    price=price,
                    change=change,
                    pct=pct,
                )

                if self.days > 1:
                    display.show_history_table(
                        name=item["name"],
                        records=records,
                        unit=item["unit"],
                        days=self.days,
                    )

        display.show_footer(latest_period)
        return any_data


def main():
    parser = argparse.ArgumentParser(
        prog="get-oil",
        description="get-oil — energy spot price tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  get-oil                          # current prices for all commodities
  get-oil --days 7                 # show 7-day price history
  get-oil --commodity crude        # crude oil only
  get-oil --commodity refined      # gasoline & heating oil only
  get-oil --commodity natgas       # natural gas only

data source: Yahoo Finance (no API key required)
        """,
    )

    parser.add_argument(
        "--days", "-d",
        type=int,
        default=DEFAULT_DAYS,
        metavar="N",
        help=f"days of price history to show (1-30, default: {DEFAULT_DAYS})",
    )
    parser.add_argument(
        "--commodity", "-c",
        choices=["all", "crude", "refined", "natgas"],
        default="all",
        help="filter to a commodity group (default: all)",
    )

    args = parser.parse_args()

    if args.days < 1 or args.days > 30:
        parser.error("--days must be between 1 and 30")

    checker = OilChecker(
        days=args.days,
        commodity=args.commodity,
    )

    success = checker.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
