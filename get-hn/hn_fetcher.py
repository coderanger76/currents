"""
Hacker News data fetcher — no API key required.
Uses the official Firebase REST API.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests

BASE_URL = "https://hacker-news.firebaseio.com/v0"
TIMEOUT  = 10

FEED_ENDPOINTS = {
    "top":  "topstories",
    "new":  "newstories",
    "best": "beststories",
}


def _time_ago(unix_ts):
    """Convert a Unix timestamp to a human-readable relative string."""
    if not unix_ts:
        return ""
    delta = int(time.time()) - int(unix_ts)
    if delta < 0:
        return "just now"
    if delta < 60:
        return f"{delta}s ago"
    if delta < 3600:
        m = delta // 60
        return f"{m}m ago"
    if delta < 86400:
        h = delta // 3600
        return f"{h}h ago"
    d = delta // 86400
    return f"{d}d ago"


def _extract_domain(url):
    """Return the bare domain of a URL, without www. prefix."""
    if not url:
        return "news.ycombinator.com"
    try:
        netloc = urlparse(url).netloc
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or "news.ycombinator.com"
    except Exception:
        return "news.ycombinator.com"


def _fetch_item(item_id):
    """Fetch a single HN item by ID. Returns dict or None."""
    try:
        r = requests.get(f"{BASE_URL}/item/{item_id}.json", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


class HNFetcher:
    """Fetches stories from the Hacker News Firebase API."""

    def __init__(self, feed_type="top"):
        endpoint = FEED_ENDPOINTS.get(feed_type, "topstories")
        self.feed_url = f"{BASE_URL}/{endpoint}.json"

    def fetch_top(self, n=30):
        """
        Fetch the top n stories, returned as a list of story dicts sorted by rank.
        Uses parallel requests for speed.
        """
        n = min(n, 50)

        # 1. Get ranked story IDs
        r = requests.get(self.feed_url, timeout=TIMEOUT)
        r.raise_for_status()
        all_ids = r.json()
        ids = all_ids[:n]

        # 2. Fetch all story details in parallel
        raw_items = {}
        with ThreadPoolExecutor(max_workers=20) as pool:
            future_map = {pool.submit(_fetch_item, sid): (rank, sid)
                          for rank, sid in enumerate(ids, start=1)}
            for future in as_completed(future_map):
                rank, sid = future_map[future]
                data = future.result()
                if data:
                    raw_items[rank] = data

        # 3. Build normalised story dicts, preserving rank order
        stories = []
        for rank in range(1, n + 1):
            data = raw_items.get(rank)
            if not data:
                continue
            url      = data.get("url", "")
            title    = data.get("title", "(no title)")
            stories.append({
                "rank":     rank,
                "title":    title,
                "url":      url,
                "domain":   _extract_domain(url),
                "score":    data.get("score", 0),
                "by":       data.get("by", ""),
                "time":     data.get("time", 0),
                "time_ago": _time_ago(data.get("time")),
                "comments": data.get("descendants", 0),
                "type":     data.get("type", "story"),
            })

        return stories
