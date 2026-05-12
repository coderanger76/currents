#!/usr/bin/env python3
"""
get-hn — Hacker News top stories in your terminal.

Fetches the top, new, or best stories from Hacker News and displays them
in a clean, colourful feed. No API key required.
"""

import sys
import argparse

from hn_fetcher import HNFetcher
from hn_display  import HNDisplay

FEED_LABELS = {
    "top":  "TOP STORIES",
    "new":  "NEW STORIES",
    "best": "BEST STORIES",
}


def main():
    parser = argparse.ArgumentParser(
        prog="get-hn",
        description="get-hn — Hacker News top stories in your terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  get-hn                  # top 30 stories
  get-hn -n 10            # top 10 stories
  get-hn --type new       # newest stories
  get-hn --type best -n 20  # best 20 stories

no API key required — uses the public Hacker News Firebase API.
        """,
    )

    parser.add_argument(
        "--count", "-n",
        type=int,
        default=30,
        metavar="N",
        help="number of stories to display (default: 30, max: 50)",
    )
    parser.add_argument(
        "--type", "-t",
        default="top",
        choices=["top", "new", "best"],
        metavar="FEED",
        help="story feed: top (default), new, or best",
    )

    args = parser.parse_args()
    count = max(1, min(args.count, 50))
    feed  = args.type

    display = HNDisplay()
    fetcher = HNFetcher(feed_type=feed)

    display.show_header(feed_label=FEED_LABELS.get(feed, "TOP STORIES"), count=count)

    try:
        stories = fetcher.fetch_top(n=count)
    except Exception as e:
        display.show_error(f"Failed to fetch stories: {e}")
        sys.exit(1)

    if not stories:
        display.show_error("No stories returned from API.")
        sys.exit(1)

    for story in stories:
        display.show_story(story)

    display.show_footer(len(stories))
    sys.exit(0)


if __name__ == "__main__":
    main()
