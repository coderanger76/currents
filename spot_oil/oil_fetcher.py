"""
Yahoo Finance data fetching module for get-oil
"""

import yfinance as yf


class OilFetcher:
    """
    Fetches energy spot/futures price data from Yahoo Finance.
    """

    def fetch(self, commodity, days=1):
        """
        Fetch price records for a single commodity.

        Fetches one extra record beyond `days` so callers can compute
        a day-over-day change for every displayed row.

        Args:
            commodity: dict from config.COMMODITIES (must have "ticker" key)
            days:      number of trading days to return

        Returns:
            List of record dicts {"period": "YYYY-MM-DD", "value": str}
            sorted newest-first, or None on failure.
        """
        fetch_count = days + 1
        # Request enough calendar days to always cover fetch_count trading days
        # (weekends + holidays buffer)
        cal_days = max(fetch_count * 3 + 10, 30)

        try:
            ticker = yf.Ticker(commodity["ticker"])
            hist = ticker.history(period=f"{cal_days}d")
            if hist.empty:
                return None
            hist = hist.sort_index(ascending=False).head(fetch_count)
            records = [
                {
                    "period": idx.date().isoformat(),
                    "value":  str(row["Close"]),
                }
                for idx, row in hist.iterrows()
            ]
            return records if records else None
        except Exception:
            return None
