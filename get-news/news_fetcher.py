"""
NY Times API fetching module for get-news
"""

import requests
from config import NYT_BASE_URL


class NewsFetcher:
    """
    Fetches news data from the NY Times API.
    Supports Top Stories, Article Search, and Most Popular.
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _get(self, url, params=None):
        params = params or {}
        params["api-key"] = self.api_key
        try:
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                raise RuntimeError("Rate limit hit — try again in a minute (10 calls/min max).")
            if e.response is not None and e.response.status_code == 401:
                raise RuntimeError(
                    "Unauthorized (401). This API may not be enabled for your key.\n"
                    "  Enable it at: https://developer.nytimes.com/my-apps/"
                )
            raise RuntimeError(f"API error: {e}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error: {e}")

    def top_stories(self, section="home"):
        """
        Fetch top stories for a given section.
        Returns list of article dicts.
        """
        url  = f"{NYT_BASE_URL}/topstories/v2/{section}.json"
        data = self._get(url)
        return data.get("results", []), data.get("last_updated", "")

    def search(self, query, limit=10):
        """
        Search articles by keyword using the Article Search API.
        Returns list of article dicts.
        """
        url    = f"{NYT_BASE_URL}/search/v2/articlesearch.json"
        params = {
            "q":    query,
            "sort": "newest",
            "page": 0,
        }
        data    = self._get(url, params)
        docs    = data.get("response", {}).get("docs", [])

        # Normalize search results to match top-stories shape
        normalized = []
        for d in docs[:limit]:
            headline = d.get("headline", {})
            byline   = d.get("byline", {})
            multi    = d.get("multimedia", [])
            normalized.append({
                "title":          headline.get("main", ""),
                "abstract":       d.get("abstract") or d.get("snippet", ""),
                "url":            d.get("web_url", ""),
                "byline":         byline.get("original", ""),
                "section":        d.get("section_name", ""),
                "subsection":     d.get("subsection_name", ""),
                "published_date": d.get("pub_date", ""),
                "updated_date":   d.get("pub_date", ""),
                "multimedia":     [{"url": m.get("url", ""), "format": m.get("subtype", "")} for m in multi],
                "_source":        "search",
            })
        return normalized, ""

    def most_popular(self, period=1, mode="viewed"):
        """
        Fetch most popular articles.
        mode: 'viewed' | 'emailed' | 'shared'
        period: 1 | 7 | 30
        """
        url  = f"{NYT_BASE_URL}/mostpopular/v2/{mode}/{period}.json"
        data = self._get(url)
        results = data.get("results", [])

        # Normalize to top-stories shape
        normalized = []
        for r in results:
            multi = r.get("media", [])
            images = []
            for m in multi:
                for meta in m.get("media-metadata", []):
                    images.append({"url": meta.get("url", ""), "format": meta.get("format", "")})

            normalized.append({
                "title":          r.get("title", ""),
                "abstract":       r.get("abstract", ""),
                "url":            r.get("url", ""),
                "byline":         r.get("byline", ""),
                "section":        r.get("section", ""),
                "subsection":     r.get("subsection", ""),
                "published_date": r.get("published_date", ""),
                "updated_date":   r.get("updated", ""),
                "multimedia":     images,
                "_source":        f"popular:{mode}:{period}d",
            })
        return normalized, ""
