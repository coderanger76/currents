"""
Database module for storing and retrieving rental listings
"""

import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH


class RentalDatabase:
    def __init__(self, db_path=None):
        """Initialize database connection"""
        self.db_path = db_path or DB_PATH
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            print(f"✓ Connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"✗ Database connection error: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")

    def create_tables(self):
        """Create the rental listings table"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS rental_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id TEXT UNIQUE NOT NULL,
            location TEXT,
            price INTEGER,
            sqft INTEGER,
            bedroom_count INTEGER,
            received_date TIMESTAMP NOT NULL,
            subject TEXT,
            url TEXT,
            email_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Create index on received_date for faster queries
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_received_date
        ON rental_listings(received_date);
        """

        # Create index on location
        create_location_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_location
        ON rental_listings(location);
        """

        # Create index on bedroom_count for filtering
        create_bedroom_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_bedroom_count
        ON rental_listings(bedroom_count);
        """

        try:
            self.cursor.execute(create_table_sql)

            # Migration: Add bedroom_count column if it doesn't exist (for existing databases)
            # Do this before creating the index on bedroom_count
            try:
                self.cursor.execute("ALTER TABLE rental_listings ADD COLUMN bedroom_count INTEGER")
                print("✓ Added bedroom_count column to existing database")
            except sqlite3.OperationalError as e:
                # Column already exists, that's fine
                if "duplicate column name" not in str(e).lower():
                    # Only pass if it's a duplicate column error, otherwise re-raise
                    pass

            # Now create indexes
            self.cursor.execute(create_index_sql)
            self.cursor.execute(create_location_index_sql)
            self.cursor.execute(create_bedroom_index_sql)

            self.connection.commit()
            print("✓ Database tables created/verified")
            return True
        except sqlite3.Error as e:
            print(f"✗ Error creating tables: {e}")
            return False

    def insert_listing(self, rental_data):
        """
        Insert a rental listing into the database

        Args:
            rental_data: Dictionary with rental information

        Returns:
            True if successful, False otherwise
        """
        insert_sql = """
        INSERT OR IGNORE INTO rental_listings
        (listing_id, location, price, sqft, bedroom_count, received_date, subject, url, email_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            self.cursor.execute(insert_sql, (
                rental_data['listing_id'],
                rental_data.get('location'),
                rental_data.get('price'),
                rental_data.get('sqft'),
                rental_data.get('bedroom_count'),
                rental_data['received_date'],
                rental_data.get('subject'),
                rental_data.get('url'),
                rental_data.get('email_id')
            ))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Error inserting listing {rental_data.get('listing_id')}: {e}")
            return False

    def insert_listings_bulk(self, rental_listings):
        """
        Insert multiple rental listings

        Args:
            rental_listings: List of rental data dictionaries

        Returns:
            Number of listings inserted
        """
        inserted = 0
        skipped = 0

        for rental_data in rental_listings:
            if self.insert_listing(rental_data):
                if self.cursor.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1

        print(f"✓ Inserted {inserted} new listings, skipped {skipped} duplicates")
        return inserted

    def get_all_listings(self):
        """Get all rental listings"""
        query = """
        SELECT listing_id, location, price, sqft, received_date, subject, url
        FROM rental_listings
        ORDER BY received_date DESC
        """

        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"✗ Error fetching listings: {e}")
            return []

    def get_listings_by_date_range(self, start_date, end_date):
        """Get listings within a date range"""
        query = """
        SELECT listing_id, location, price, sqft, received_date, subject, url
        FROM rental_listings
        WHERE received_date BETWEEN ? AND ?
        ORDER BY received_date DESC
        """

        try:
            self.cursor.execute(query, (start_date, end_date))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"✗ Error fetching listings: {e}")
            return []

    def get_weekly_averages(self, weeks=52, bedroom_count=None):
        """
        Calculate average rental prices by week with outliers and price per sqft

        Args:
            weeks: Number of weeks to analyze (default 52)
            bedroom_count: Filter by bedroom count (1, 2, etc.) or None for all (default None)

        Returns:
            List of tuples (week_start_date, avg_price, min_price, max_price,
                           avg_price_per_sqft, count, unique_locations)
        """
        # Build WHERE clause based on bedroom_count filter
        bedroom_filter = ""
        params = []

        days_back = -(weeks * 7)

        if bedroom_count is not None:
            bedroom_filter = "AND bedroom_count = ?"
            params = [days_back, bedroom_count]
        else:
            params = [days_back]

        query = f"""
        WITH weekly_data AS (
            SELECT
                DATE(received_date, 'weekday 0', '-6 days') as week_start,
                price,
                sqft,
                CAST(price AS REAL) / NULLIF(sqft, 0) as price_per_sqft,
                location
            FROM rental_listings
            WHERE price IS NOT NULL
                AND received_date >= DATE('now', ? || ' days')
                {bedroom_filter}
        )
        SELECT
            week_start,
            AVG(price) as avg_price,
            MIN(price) as min_price,
            MAX(price) as max_price,
            AVG(price_per_sqft) as avg_price_per_sqft,
            COUNT(*) as listing_count,
            COUNT(DISTINCT location) as unique_locations
        FROM weekly_data
        GROUP BY week_start
        ORDER BY week_start
        """

        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"✗ Error calculating weekly averages: {e}")
            return []

    def get_statistics(self):
        """Get overall statistics about the data"""
        stats_query = """
        SELECT
            COUNT(*) as total_listings,
            COUNT(DISTINCT location) as unique_locations,
            AVG(price) as avg_price,
            MIN(price) as min_price,
            MAX(price) as max_price,
            AVG(sqft) as avg_sqft,
            MIN(received_date) as earliest_date,
            MAX(received_date) as latest_date
        FROM rental_listings
        WHERE price IS NOT NULL
        """

        try:
            self.cursor.execute(stats_query)
            result = self.cursor.fetchone()
            return {
                'total_listings': result[0],
                'unique_locations': result[1],
                'avg_price': result[2],
                'min_price': result[3],
                'max_price': result[4],
                'avg_sqft': result[5],
                'earliest_date': result[6],
                'latest_date': result[7]
            }
        except sqlite3.Error as e:
            print(f"✗ Error fetching statistics: {e}")
            return {}

    def get_top_locations(self, limit=10):
        """Get most common locations"""
        query = """
        SELECT location, COUNT(*) as count, AVG(price) as avg_price
        FROM rental_listings
        WHERE location != 'Unknown' AND location != 'UNDETERMINED' AND price IS NOT NULL
        GROUP BY location
        ORDER BY count DESC
        LIMIT ?
        """

        try:
            self.cursor.execute(query, (limit,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"✗ Error fetching top locations: {e}")
            return []

    def get_community_price_trends(self, weeks=52, min_listings=3, bedroom_count=None):
        """
        Get weekly price trends for each community

        Args:
            weeks: Number of weeks to analyze (default 52)
            min_listings: Minimum number of listings for a community to be included (default 3)
            bedroom_count: Filter by bedroom count (1, 2, etc.) or None for all (default None)

        Returns:
            Dictionary with location as key and list of weekly data as value
            Format: {location: [(week_start, avg_price, min_price, max_price, count), ...]}
        """
        # Build WHERE clause based on bedroom_count filter
        bedroom_filter = ""
        params = []

        days_back = -(weeks * 7)

        if bedroom_count is not None:
            bedroom_filter = "AND bedroom_count = ?"
            params = [days_back, bedroom_count, min_listings]
        else:
            params = [days_back, min_listings]

        query = f"""
        WITH weekly_location_data AS (
            SELECT
                DATE(received_date, 'weekday 0', '-6 days') as week_start,
                location,
                price
            FROM rental_listings
            WHERE price IS NOT NULL
                AND location NOT IN ('Unknown', 'UNDETERMINED')
                AND received_date >= DATE('now', ? || ' days')
                {bedroom_filter}
        ),
        location_counts AS (
            SELECT location, COUNT(*) as total_count
            FROM weekly_location_data
            GROUP BY location
            HAVING total_count >= ?
        )
        SELECT
            wld.week_start,
            wld.location,
            AVG(wld.price) as avg_price,
            MIN(wld.price) as min_price,
            MAX(wld.price) as max_price,
            COUNT(*) as listing_count
        FROM weekly_location_data wld
        INNER JOIN location_counts lc ON wld.location = lc.location
        GROUP BY wld.week_start, wld.location
        ORDER BY wld.location, wld.week_start
        """

        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()

            # Organize by location
            community_data = {}
            for row in results:
                week_start, location, avg_price, min_price, max_price, count = row
                if location not in community_data:
                    community_data[location] = []
                community_data[location].append((week_start, avg_price, min_price, max_price, count))

            return community_data
        except sqlite3.Error as e:
            print(f"✗ Error fetching community trends: {e}")
            return {}


if __name__ == "__main__":
    # Test the database
    db = RentalDatabase()
    if db.connect():
        db.create_tables()

        # Test insert
        test_listing = {
            'listing_id': 'test_123',
            'location': 'West LA',
            'price': 2500,
            'sqft': 750,
            'received_date': datetime.now(),
            'subject': 'Test listing',
            'url': 'http://test.com',
            'email_id': 'test_email'
        }
        db.insert_listing(test_listing)

        # Test statistics
        stats = db.get_statistics()
        print("\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        db.close()
