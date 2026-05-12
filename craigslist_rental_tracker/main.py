#!/usr/bin/env python3
"""
Craigslist Rental Tracker - Main Application
Fetches, parses, stores, and analyzes Craigslist rental listings from email
"""

import argparse
import sys
from datetime import datetime, timedelta
from email_fetcher import EmailFetcher
from email_parser import RentalParser
from database import RentalDatabase
from analyzer import RentalAnalyzer


class RentalTracker:
    def __init__(self, app_password=None):
        """Initialize the rental tracker"""
        self.fetcher = EmailFetcher(app_password)
        self.parser = RentalParser()
        self.db = RentalDatabase()
        self.analyzer = RentalAnalyzer()

    def fetch_and_store(self, since_days=None):
        """
        Fetch emails and store rental listings in database

        Args:
            since_days: Only fetch emails from last N days (default: all emails)
        """
        print("\n" + "="*70)
        print("CRAIGSLIST RENTAL TRACKER - Fetch & Store")
        print("="*70 + "\n")

        # Connect to email
        if not self.fetcher.connect():
            print("✗ Failed to connect to email. Please check your credentials.")
            return False

        # Determine date range
        since_date = None
        if since_days:
            since_date = datetime.now() - timedelta(days=since_days)
            print(f"Fetching emails from the last {since_days} days...")
        else:
            print("Fetching all Craigslist emails...")

        # Fetch emails
        emails = self.fetcher.fetch_craigslist_emails(since_date)
        self.fetcher.disconnect()

        if not emails:
            print("\n✗ No emails found")
            return False

        print(f"\nParsing {len(emails)} emails...")

        # Parse emails and extract rental data
        rental_listings = []
        parsed_count = 0
        failed_count = 0

        for idx, email_data in enumerate(emails, 1):
            print(f"  Parsing {idx}/{len(emails)}...", end='\r')
            rental_data = self.parser.parse_rental_email(email_data)

            if rental_data and rental_data.get('price'):
                rental_listings.append(rental_data)
                parsed_count += 1
            else:
                failed_count += 1

        print(f"\n✓ Successfully parsed {parsed_count} listings")
        if failed_count > 0:
            print(f"  ⚠ Failed to extract price from {failed_count} emails")

        # Store in database
        print("\nStoring listings in database...")
        if not self.db.connect():
            print("✗ Failed to connect to database")
            return False

        self.db.create_tables()
        inserted = self.db.insert_listings_bulk(rental_listings)
        self.db.close()

        print(f"\n{'='*70}")
        print("Summary:")
        print(f"  Emails fetched: {len(emails)}")
        print(f"  Listings parsed: {parsed_count}")
        print(f"  New listings added: {inserted}")
        print(f"  Duplicates skipped: {parsed_count - inserted}")
        print(f"{'='*70}\n")

        return True

    def analyze(self, weeks=52, bedroom_count=None):
        """Run analysis and generate visualizations"""
        bedroom_label = f" - {bedroom_count}BR" if bedroom_count else ""
        print("\n" + "="*70)
        print(f"CRAIGSLIST RENTAL TRACKER{bedroom_label} - Analysis")
        print("="*70 + "\n")

        # Generate weekly report
        self.analyzer.generate_weekly_report(weeks, bedroom_count=bedroom_count)

        # Create visualizations
        print("\nGenerating overall price trend visualizations...")
        self.analyzer.plot_price_trends(weeks, bedroom_count=bedroom_count)

        # Create community comparison chart
        print("\nGenerating community comparison chart...")
        self.analyzer.plot_community_comparison(weeks, bedroom_count=bedroom_count)

        # Export data
        print("\nExporting data to CSV...")
        self.analyzer.export_to_csv()

        print(f"\n{'='*70}")
        print("Analysis complete!")
        print(f"{'='*70}\n")

    def run_full_pipeline(self, since_days=None, weeks=52, bedroom_count=None):
        """Run the complete fetch, store, and analyze pipeline"""
        # Fetch and store
        if not self.fetch_and_store(since_days):
            return False

        # Analyze
        self.analyze(weeks, bedroom_count=bedroom_count)

        return True


def main():
    """Main entry point with command-line interface"""
    parser = argparse.ArgumentParser(
        description='Craigslist Rental Tracker - Track rental prices over time',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch all emails and run analysis
  python main.py --fetch --analyze

  # Fetch only emails from last 30 days
  python main.py --fetch --since-days 30

  # Just run analysis on existing data
  python main.py --analyze

  # Full pipeline with custom weeks for analysis
  python main.py --fetch --analyze --weeks 52
        """
    )

    parser.add_argument('--fetch', action='store_true',
                       help='Fetch and store rental emails')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze stored data and generate visualizations')
    parser.add_argument('--since-days', type=int, metavar='N',
                       help='Only fetch emails from last N days (default: fetch all)')
    parser.add_argument('--weeks', type=int, default=52, metavar='N',
                       help='Number of weeks to analyze (default: 52)')
    parser.add_argument('--bedrooms', type=int, metavar='N', choices=[1, 2, 3, 4, 5],
                       help='Filter by bedroom count (1, 2, 3, 4, or 5). Omit to see all bedrooms.')
    parser.add_argument('--password', type=str, metavar='PASSWORD',
                       help='Apple app password (will prompt if not provided)')

    args = parser.parse_args()

    # If no arguments provided, show help
    if not args.fetch and not args.analyze:
        parser.print_help()
        sys.exit(0)

    # Initialize tracker
    tracker = RentalTracker(app_password=args.password)

    # Run requested operations
    if args.fetch and args.analyze:
        tracker.run_full_pipeline(since_days=args.since_days, weeks=args.weeks, bedroom_count=args.bedrooms)
    elif args.fetch:
        tracker.fetch_and_store(since_days=args.since_days)
    elif args.analyze:
        tracker.analyze(weeks=args.weeks, bedroom_count=args.bedrooms)


if __name__ == "__main__":
    main()
