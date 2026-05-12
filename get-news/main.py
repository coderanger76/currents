#!/usr/bin/env python3
"""
get-news — NY Times breaking news in your terminal

Pulls top stories, searches articles, or shows most-popular from the
NY Times API and renders them in a clean, readable feed.
"""

import sys
import os
import argparse
import getpass

from news_fetcher  import NewsFetcher
from news_display  import NewsDisplay
from config        import DEFAULT_SECTION, DEFAULT_LIMIT, SECTIONS


class NewsChecker:
    """
    Main application — coordinates fetching and display of NYT news.
    """

    def __init__(self, api_key=None, section=DEFAULT_SECTION, limit=DEFAULT_LIMIT,
                 search=None, popular=None, popular_period=1, no_abstract=False):
        self.api_key        = (
            api_key
            or os.environ.get("NYT_API_KEY")
            or self._prompt_for_key()
        )
        self.section        = section
        self.limit          = limit
        self.search         = search
        self.popular        = popular          # 'viewed' | 'emailed' | 'shared' | None
        self.popular_period = popular_period
        self.show_abstract  = not no_abstract

    def _prompt_for_key(self):
        print("\nNo NYT API key found. You can set it via:")
        print("  1. Command line:    --api-key YOUR_KEY")
        print("  2. Environment var: export NYT_API_KEY=YOUR_KEY")
        print("  3. Enter it now (input hidden)\n")
        return getpass.getpass("Enter NYT API key: ")

    def run(self):
        fetcher = NewsFetcher(self.api_key)
        display = NewsDisplay()

        try:
            if self.search:
                articles, last_updated = fetcher.search(self.search, limit=self.limit)
                mode_label = f'Search: "{self.search}"  ·  {len(articles)} results'
                if not articles:
                    display.show_header(mode_label)
                    display.show_no_results(self.search)
                    display.show_footer(0)
                    return False

            elif self.popular:
                articles, last_updated = fetcher.most_popular(
                    period=self.popular_period, mode=self.popular
                )
                period_label = {1: "Today", 7: "This Week", 30: "This Month"}.get(
                    self.popular_period, f"{self.popular_period}d"
                )
                mode_label = f"Most {self.popular.capitalize()}  ·  {period_label}"
                articles = articles[: self.limit]

            else:
                articles, last_updated = fetcher.top_stories(self.section)
                section_label = self.section.replace("-", " ").title()
                mode_label = f"Top Stories  ·  {section_label}"
                articles = articles[: self.limit]

        except RuntimeError as e:
            display.show_error(str(e))
            return False

        display.show_header(mode_label, last_updated)

        if not articles:
            display.show_error("No articles returned from API.")
            return False

        for i, article in enumerate(articles, start=1):
            display.show_article(i, article, show_abstract=self.show_abstract)

        display.show_footer(len(articles), last_updated)
        return True


def main():
    parser = argparse.ArgumentParser(
        prog="get-news",
        description="get-news — NY Times breaking news in your terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
examples:
  get-news                          # top stories (home feed)
  get-news --section technology     # tech section
  get-news --section world          # world news
  get-news --search "ukraine"       # search articles
  get-news --popular                # most viewed today
  get-news --popular --period 7     # most viewed this week
  get-news --popular emailed        # most emailed today
  get-news --limit 20               # show more stories
  get-news --no-abstract            # headlines only (compact)

available sections:
  {", ".join(SECTIONS)}

environment:
  NYT_API_KEY    set your API key here to skip --api-key every time
        """,
    )

    parser.add_argument(
        "--api-key", "-k",
        metavar="KEY",
        help="NYT API key (or set NYT_API_KEY env var)",
    )
    parser.add_argument(
        "--section", "-s",
        default=DEFAULT_SECTION,
        metavar="SECTION",
        help=f"top stories section (default: {DEFAULT_SECTION})",
    )
    parser.add_argument(
        "--search", "-q",
        metavar="QUERY",
        help="search articles by keyword",
    )
    parser.add_argument(
        "--popular", "-p",
        nargs="?",
        const="viewed",
        choices=["viewed", "emailed", "shared"],
        metavar="MODE",
        help="most popular articles: viewed (default), emailed, or shared",
    )
    parser.add_argument(
        "--period",
        type=int,
        default=1,
        choices=[1, 7, 30],
        metavar="DAYS",
        help="popularity window in days: 1 (default), 7, or 30",
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=DEFAULT_LIMIT,
        metavar="N",
        help=f"max number of stories to show (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--no-abstract",
        action="store_true",
        help="show headlines only, skip article abstracts",
    )

    args = parser.parse_args()

    # Validate section if not using search/popular
    if not args.search and not args.popular:
        if args.section not in SECTIONS:
            parser.error(
                f"Unknown section '{args.section}'. "
                f"Choose from: {', '.join(SECTIONS)}"
            )

    checker = NewsChecker(
        api_key=args.api_key,
        section=args.section,
        limit=args.limit,
        search=args.search,
        popular=args.popular,
        popular_period=args.period,
        no_abstract=args.no_abstract,
    )

    success = checker.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
