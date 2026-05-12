"""
Yahoo Finance data fetching module for get-stocks
Fetches all tickers in parallel for speed.
"""

import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed


class StockFetcher:
    """
    Fetches index price history from Yahoo Finance, all tickers in parallel.
    """

    def __init__(self, indices, days):
        self._records = {}
        self._load(indices, days)

    def _load(self, indices, days):
        fetch_count = days + 1
        cal_days    = max(fetch_count * 3 + 10, 30)
        period      = f"{cal_days}d"

        def fetch_one(index):
            try:
                hist = yf.Ticker(index["ticker"]).history(period=period)
                if hist.empty:
                    return index["ticker"], None
                hist = hist.sort_index(ascending=False).head(fetch_count)
                records = [
                    {"period": idx.date().isoformat(), "value": str(row["Close"])}
                    for idx, row in hist.iterrows()
                ]
                return index["ticker"], records or None
            except Exception:
                return index["ticker"], None

        with ThreadPoolExecutor(max_workers=len(indices)) as pool:
            for ticker, records in pool.map(
                lambda i: fetch_one(i), indices
            ):
                self._records[ticker] = records

    def get(self, ticker):
        return self._records.get(ticker)
