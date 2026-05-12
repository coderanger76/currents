"""
FRED API data fetching module for get-fed.
Fetches all series in parallel for speed.
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

# All series IDs to fetch
ALL_SERIES = [
    # Monetary Policy
    "DFEDTARL",
    "DFEDTARU",
    "FEDFUNDS",
    "DGS2",
    "DGS10",
    "DGS30",
    "MORTGAGE30US",
    # Inflation (need 14 obs for YoY: 13 months back + latest)
    "CPIAUCSL",
    "CPILFESL",
    "PCEPI",
    # Labor
    "UNRATE",
    "ICSA",
    # Money & Output
    "M2SL",
    "A191RL1Q225SBEA",
]


def calc_yoy(observations):
    """
    Given a list of observations (newest first), compute year-over-year
    percentage change: (latest - value_12_periods_ago) / value_12_periods_ago * 100.

    Skips observations with "." (FRED's missing-data sentinel).
    Returns (yoy_pct, latest_date, latest_value) or (None, None, None).
    """
    valid = [o for o in observations if o.get("value", ".") != "."]
    if len(valid) < 13:
        return None, None, None
    latest    = valid[0]
    prior_12  = valid[12]
    try:
        v_now  = float(latest["value"])
        v_then = float(prior_12["value"])
    except (ValueError, TypeError):
        return None, None, None
    if v_then == 0:
        return None, None, None
    yoy = (v_now - v_then) / v_then * 100
    return yoy, latest["date"], v_now


class FedFetcher:
    """
    Fetches FRED economic series for get-fed.
    All series are fetched in parallel.
    """

    def __init__(self, api_key):
        self._api_key = api_key

    def _fetch_series(self, series_id):
        """Fetch up to 14 observations (newest first) for one series."""
        params = {
            "series_id":  series_id,
            "api_key":    self._api_key,
            "file_type":  "json",
            "sort_order": "desc",
            "limit":      14,
        }
        try:
            resp = requests.get(
                FRED_BASE_URL,
                params=params,
                headers=HEADERS,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            observations = data.get("observations", [])
            return series_id, observations if observations else None
        except Exception:
            return series_id, None

    def fetch_all(self):
        """
        Fetch all series in parallel.
        Returns dict: series_id -> list of observations (newest first),
        or None if the fetch failed.
        """
        results = {}
        with ThreadPoolExecutor(max_workers=len(ALL_SERIES)) as pool:
            futures = {pool.submit(self._fetch_series, sid): sid for sid in ALL_SERIES}
            for future in as_completed(futures):
                series_id, observations = future.result()
                results[series_id] = observations
        return results
