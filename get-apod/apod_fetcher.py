"""
NASA APOD data fetcher for get-apod.
"""

import os
import requests
from datetime import date

APOD_URL = "https://api.nasa.gov/planetary/apod"
TIMEOUT  = 15

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


class APODFetcher:

    def __init__(self):
        self._api_key = os.environ.get("NASA_API_KEY", "DEMO_KEY").strip() or "DEMO_KEY"

    def fetch(self, target_date=None):
        """
        Fetch the APOD for the given date (date object) or today.
        Returns a dict with keys: date, title, explanation, media_type,
        url, hdurl (optional), copyright (optional).
        Raises on network or API errors.
        """
        if target_date is None:
            target_date = date.today()

        params = {
            "api_key": self._api_key,
            "date":    target_date.isoformat(),
            "thumbs":  "True",   # request thumbnail URL for videos
        }

        resp = requests.get(APOD_URL, params=params, headers=HEADERS, timeout=TIMEOUT)

        if resp.status_code == 400:
            try:
                msg = resp.json().get("msg", resp.text)
            except Exception:
                msg = resp.text
            raise ValueError(f"NASA API error: {msg}")

        resp.raise_for_status()
        data = resp.json()

        return {
            "date":        data.get("date", target_date.isoformat()),
            "title":       data.get("title", "Unknown"),
            "explanation": data.get("explanation", ""),
            "media_type":  data.get("media_type", "image"),
            "url":         data.get("url", ""),
            "hdurl":       data.get("hdurl", ""),
            "copyright":   data.get("copyright", "").strip(),
            "thumbnail":   data.get("thumbnail_url", ""),
            "api_key_used": self._api_key,
        }
