"""
Data analysis and visualization module for rental trends
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
from database import RentalDatabase


class RentalAnalyzer:
    def __init__(self, db_path=None):
        """Initialize the analyzer with database"""
        self.db = RentalDatabase(db_path)

    def generate_weekly_report(self, weeks=52, bedroom_count=None):
        """
        Generate a comprehensive weekly rental price report

        Args:
            weeks: Number of weeks to analyze (default 52)
            bedroom_count: Filter by bedroom count (1, 2, etc.) or None for all (default None)
        """
        if not self.db.connect():
            return

        bedroom_label = f" - {bedroom_count}BR" if bedroom_count else ""
        print(f"\n{'='*70}")
        print(f"RENTAL PRICE ANALYSIS{bedroom_label} - Last {weeks} Weeks")
        print(f"{'='*70}\n")

        # Get overall statistics
        stats = self.db.get_statistics()
        if stats:
            print("Overall Statistics:")
            print(f"  Total listings: {stats['total_listings']}")
            print(f"  Unique locations: {stats['unique_locations']}")
            print(f"  Average price: ${stats['avg_price']:.2f}" if stats['avg_price'] else "  Average price: N/A")
            print(f"  Price range: ${stats['min_price']:.0f} - ${stats['max_price']:.0f}" if stats['min_price'] else "  Price range: N/A")
            print(f"  Average sqft: {stats['avg_sqft']:.0f} sqft" if stats['avg_sqft'] else "  Average sqft: N/A")
            print(f"  Date range: {stats['earliest_date']} to {stats['latest_date']}\n")

        # Get top locations
        print("Top 10 Locations by Listing Count:")
        top_locations = self.db.get_top_locations(10)
        if top_locations:
            print(f"  {'Location':<25} {'Count':<10} {'Avg Price':<15}")
            print(f"  {'-'*50}")
            for location, count, avg_price in top_locations:
                print(f"  {location:<25} {count:<10} ${avg_price:<14.2f}")
        else:
            print("  No location data available")

        # Get weekly averages
        print(f"\nWeekly Price Analysis (Last {weeks} weeks):")
        weekly_data = self.db.get_weekly_averages(weeks, bedroom_count=bedroom_count)

        if weekly_data:
            print(f"  {'Week':<12} {'Avg':<10} {'Min':<10} {'Max':<10} {'$/SqFt':<10} {'#':<8} {'Loc':<8}")
            print(f"  {'-'*68}")
            for week_start, avg_price, min_price, max_price, avg_psf, count, locations in weekly_data:
                psf_str = f"${avg_psf:.2f}" if avg_psf else "N/A"
                print(f"  {week_start:<12} ${avg_price:<9.0f} ${min_price:<9.0f} ${max_price:<9.0f} {psf_str:<10} {count:<8} {locations:<8}")
        else:
            print("  No weekly data available")

        self.db.close()

        return weekly_data

    def plot_price_trends(self, weeks=52, bedroom_count=None, output_file=None):
        """
        Create visualizations of rental price trends

        Args:
            weeks: Number of weeks to analyze (default 52)
            bedroom_count: Filter by bedroom count (1, 2, etc.) or None for all (default None)
            output_file: File path to save the plot (auto-generated if None)
        """
        if not self.db.connect():
            return

        # Auto-generate filename if not provided
        if output_file is None:
            if bedroom_count:
                output_file = f'rental_price_trends_{bedroom_count}BR.png'
            else:
                output_file = 'rental_price_trends.png'

        weekly_data = self.db.get_weekly_averages(weeks, bedroom_count=bedroom_count)
        self.db.close()

        if not weekly_data:
            print("✗ No data available for plotting")
            return

        # Convert to pandas DataFrame for easier plotting
        df = pd.DataFrame(weekly_data, columns=[
            'week_start', 'avg_price', 'min_price', 'max_price',
            'avg_price_per_sqft', 'listing_count', 'unique_locations'
        ])
        df['week_start'] = pd.to_datetime(df['week_start'])

        # Create figure with subplots - now 3 plots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 14))

        # Plot 1: Average Price Over Time with Min/Max Range
        # Show the range with shaded area
        ax1.fill_between(df['week_start'], df['min_price'], df['max_price'],
                         alpha=0.2, color='#B0B0B0', label='Min-Max Range')

        # Plot average line
        ax1.plot(df['week_start'], df['avg_price'], marker='o', linewidth=3,
                markersize=7, color='#2E86AB', label='Average Price', zorder=5)

        # Plot min and max as thinner lines
        ax1.plot(df['week_start'], df['min_price'], linestyle=':', linewidth=1.5,
                color='#E63946', label='Minimum', alpha=0.7)
        ax1.plot(df['week_start'], df['max_price'], linestyle=':', linewidth=1.5,
                color='#06A77D', label='Maximum', alpha=0.7)

        # Calculate trend line
        if len(df) > 1:
            z = np.polyfit(range(len(df)), df['avg_price'], 1)
            p = np.poly1d(z)
            trend_direction = "↓ Declining" if z[0] < 0 else "↑ Rising"
            ax1.plot(df['week_start'], p(range(len(df))), "--", linewidth=2,
                    color='#A23B72', label=f'Trend Line {trend_direction}')

        bedroom_label = f" ({bedroom_count}BR)" if bedroom_count else ""
        ax1.set_xlabel('Week', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Rent Price ($)', fontsize=12, fontweight='bold')
        ax1.set_title(f'Rental Prices{bedroom_label} with Outliers - Last {weeks} Weeks',
                     fontsize=14, fontweight='bold', pad=20)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(loc='upper right', fontsize=10)

        # Format y-axis as currency
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Format x-axis dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=4))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Plot 2: Price Per Square Foot Over Time
        ax2.plot(df['week_start'], df['avg_price_per_sqft'], marker='s', linewidth=2.5,
                markersize=6, color='#F18F01', label='Avg $/SqFt')
        ax2.fill_between(df['week_start'], df['avg_price_per_sqft'], alpha=0.3, color='#F18F01')

        # Calculate trend line for price per sqft
        if len(df) > 1:
            z_psf = np.polyfit(range(len(df)), df['avg_price_per_sqft'].fillna(0), 1)
            p_psf = np.poly1d(z_psf)
            trend_direction_psf = "↓ Declining" if z_psf[0] < 0 else "↑ Rising"
            ax2.plot(df['week_start'], p_psf(range(len(df))), "--", linewidth=2,
                    color='#C73E1D', label=f'Trend Line {trend_direction_psf}')

        ax2.set_xlabel('Week', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Price per SqFt ($)', fontsize=12, fontweight='bold')
        ax2.set_title('Price Per Square Foot Trends', fontsize=14, fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend(loc='upper right', fontsize=10)

        # Format y-axis as currency
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.2f}'))

        # Format x-axis dates
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=4))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Plot 3: Number of Listings Over Time
        ax3.bar(df['week_start'], df['listing_count'], width=5, color='#06A77D', alpha=0.7, label='Total Listings')
        ax3.plot(df['week_start'], df['unique_locations'], marker='s', linewidth=2, markersize=5, color='#5A189A', label='Unique Locations')

        ax3.set_xlabel('Week', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax3.set_title('Listing Volume Over Time', fontsize=14, fontweight='bold', pad=20)
        ax3.grid(True, alpha=0.3, linestyle='--', axis='y')
        ax3.legend()

        # Format x-axis dates
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax3.xaxis.set_major_locator(mdates.WeekdayLocator(interval=4))
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Add statistics text box
        stats_text = f"Period Averages:\n"
        stats_text += f"  Avg Price: ${df['avg_price'].mean():.2f}\n"
        stats_text += f"  Median: ${df['avg_price'].median():.2f}\n"
        stats_text += f"  Range: ${df['min_price'].min():.0f} - ${df['max_price'].max():.0f}\n"
        stats_text += f"  Avg $/SqFt: ${df['avg_price_per_sqft'].mean():.2f}\n"
        stats_text += f"  Total Listings: {df['listing_count'].sum():.0f}"

        props = dict(boxstyle='round', facecolor='wheat', alpha=0.6)
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=9,
                verticalalignment='top', bbox=props, family='monospace')

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Chart saved to: {output_file}")

        # Display the plot
        plt.show()

    def plot_community_comparison(self, weeks=52, bedroom_count=None, output_file=None):
        """
        Create a chart comparing price trends across different communities

        Args:
            weeks: Number of weeks to analyze (default 52)
            bedroom_count: Filter by bedroom count (1, 2, etc.) or None for all (default None)
            output_file: File path to save the plot (auto-generated if None)
        """
        if not self.db.connect():
            return

        # Auto-generate filename if not provided
        if output_file is None:
            if bedroom_count:
                output_file = f'community_price_comparison_{bedroom_count}BR.png'
            else:
                output_file = 'community_price_comparison.png'

        community_data = self.db.get_community_price_trends(weeks, min_listings=3, bedroom_count=bedroom_count)
        self.db.close()

        if not community_data:
            print("✗ No community data available for plotting")
            return

        # Color palette for different communities
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#06A77D',
                 '#5A189A', '#E63946', '#1D3557', '#F77F00', '#06FFA5']

        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

        # Plot 1: Average prices by community
        print(f"\nCommunity Price Trends:")
        print(f"  {'Community':<20} {'Avg Price':<12} {'Min':<10} {'Max':<10} {'Listings':<10}")
        print(f"  {'-'*70}")

        community_index = 0
        legend_entries = []

        for community, data in sorted(community_data.items()):
            if not data:
                continue

            # Convert to DataFrame for easier handling
            df = pd.DataFrame(data, columns=['week_start', 'avg_price', 'min_price', 'max_price', 'count'])
            df['week_start'] = pd.to_datetime(df['week_start'])

            color = colors[community_index % len(colors)]

            # Plot average price line
            ax1.plot(df['week_start'], df['avg_price'],
                    marker='o', linewidth=2.5, markersize=5,
                    color=color, label=f'{community}', alpha=0.9)

            # Plot min/max as shaded area (optional, can be lighter)
            ax1.fill_between(df['week_start'], df['min_price'], df['max_price'],
                           alpha=0.15, color=color)

            # Calculate stats for this community
            avg_price = df['avg_price'].mean()
            min_price = df['min_price'].min()
            max_price = df['max_price'].max()
            total_listings = df['count'].sum()

            print(f"  {community:<20} ${avg_price:<11.0f} ${min_price:<9.0f} ${max_price:<9.0f} {total_listings:<10.0f}")

            community_index += 1

        bedroom_label = f" ({bedroom_count}BR)" if bedroom_count else ""
        ax1.set_xlabel('Week', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Rent Price ($)', fontsize=12, fontweight='bold')
        ax1.set_title(f'Rental Price Comparison{bedroom_label} by Community - Last {weeks} Weeks',
                     fontsize=14, fontweight='bold', pad=20)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(loc='best', fontsize=10, framealpha=0.9)

        # Format y-axis as currency
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Format x-axis dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=4))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Plot 2: Price range (high-low spread) by community
        community_index = 0
        for community, data in sorted(community_data.items()):
            if not data:
                continue

            df = pd.DataFrame(data, columns=['week_start', 'avg_price', 'min_price', 'max_price', 'count'])
            df['week_start'] = pd.to_datetime(df['week_start'])
            df['price_range'] = df['max_price'] - df['min_price']

            color = colors[community_index % len(colors)]

            # Plot price range (spread between high and low)
            ax2.plot(df['week_start'], df['price_range'],
                    marker='s', linewidth=2, markersize=4,
                    color=color, label=f'{community}', alpha=0.8)

            community_index += 1

        ax2.set_xlabel('Week', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Price Range (Max - Min) ($)', fontsize=12, fontweight='bold')
        ax2.set_title('Price Volatility by Community (High-Low Spread)',
                     fontsize=14, fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend(loc='best', fontsize=10, framealpha=0.9)

        # Format y-axis as currency
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Format x-axis dates
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=4))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Community comparison chart saved to: {output_file}")

        # Display the plot
        plt.show()

    def export_to_csv(self, output_file='rental_listings.csv'):
        """Export all listings to CSV file"""
        if not self.db.connect():
            return

        listings = self.db.get_all_listings()
        self.db.close()

        if not listings:
            print("✗ No listings to export")
            return

        # Convert to DataFrame
        df = pd.DataFrame(listings, columns=['listing_id', 'location', 'price', 'sqft', 'received_date', 'subject', 'url'])

        # Export to CSV
        df.to_csv(output_file, index=False)
        print(f"✓ Exported {len(listings)} listings to: {output_file}")


# Import numpy for trend line calculation
import numpy as np


if __name__ == "__main__":
    # Test the analyzer
    analyzer = RentalAnalyzer()

    # Generate report
    analyzer.generate_weekly_report(weeks=52)

    # Create visualizations
    analyzer.plot_price_trends(weeks=52)

    # Export data
    analyzer.export_to_csv()
