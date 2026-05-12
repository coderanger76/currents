"""
Liturgical calendar fetcher for get-saint
"""

import requests
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor

API_BASE = "http://calapi.inadiutorium.cz/api/v0/en/calendars/general-en"


class SaintFetcher:

    def fetch_range(self, start: date, count: int = 7):
        """Fetch `count` days starting from `start`, in parallel."""
        dates = [start + timedelta(days=i) for i in range(count)]

        def fetch_one(d):
            url = f"{API_BASE}/{d.year}/{d.month}/{d.day}"
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                return resp.json()
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=count) as pool:
            results = list(pool.map(fetch_one, dates))

        return [r for r in results if r is not None]
