"""
Franciscan Media scraper for get-saints
"""

import re
import json
import requests
from pathlib import Path
from datetime import date
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

CALENDAR_URL = "https://www.franciscanmedia.org/saint-of-the-day/calendar/"


class SaintsFetcher:

    def get_saints_for_date(self, target_date=None):
        """
        Return a list of {url, title} dicts for the given date's feast day(s).
        Results are de-duplicated (the same saint appears across multiple years).
        Calendar page is cached in /tmp per calendar-fetch date.
        """
        if target_date is None:
            target_date = date.today()

        cache = Path(f"/tmp/franciscan_calendar_{date.today()}.json")
        if cache.exists():
            entries = json.loads(cache.read_text())
        else:
            r = requests.get(CALENDAR_URL, headers=HEADERS, timeout=20)
            r.raise_for_status()
            entries = _parse_calendar(r.text)
            cache.write_text(json.dumps(entries))

        # Match month-day regardless of year (same feast day recurs annually)
        month_day = f"-{target_date.month:02d}-{target_date.day:02d}T"
        seen, results = set(), []
        for e in entries:
            if month_day in e["start"] and e["url"] not in seen:
                seen.add(e["url"])
                results.append({"url": e["url"], "title": e["title"]})
        return results

    def get_saint_detail(self, url):
        """Scrape a saint page and return structured data dict."""
        soup = BeautifulSoup(
            requests.get(url, headers=HEADERS, timeout=10).text, "lxml"
        )

        name = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Unknown"

        feast_date = born = died = None
        story_paras = []
        reflection_paras = []

        for h4 in soup.find_all("h4"):
            section = h4.get_text(strip=True)
            paras   = _extract_paras(h4)

            if "Saint of the Day" in section:
                feast_date = (
                    section.replace("Saint of the Day for", "")
                           .replace("Feast of the Day for", "")
                           .strip()
                )
                if paras:
                    born, died = _parse_dates(paras[0])

            elif "Story" in section or "Life" in section:
                story_paras = paras

            elif "Reflection" in section:
                reflection_paras = paras

        patron = _extract_patron(story_paras)

        return {
            "name":       name,
            "feast_date": feast_date,
            "born":       born,
            "died":       died,
            "story":      _clean_paras(story_paras),
            "reflection": _clean_paras(reflection_paras),
            "patron":     patron,
            "url":        url,
        }


# ── helpers ───────────────────────────────────────────────────────────

def _parse_calendar(html):
    """Extract (url, title, start) triples from the embedded calendar JSON."""
    pattern = (
        r'"url":"(https://www\.franciscanmedia\.org/saint-of-the-day/[^"]+)"'
        r'[^}]*?"title":"([^"]+)"'
        r'[^}]*?"start":"([^"]+)"'
    )
    return [
        {"url": u, "title": t, "start": s}
        for u, t, s in re.findall(pattern, html)
    ]


def _extract_paras(h4_tag):
    """Collect sibling paragraph texts immediately following an h4."""
    paras, node = [], h4_tag.find_next_sibling()
    while node and node.name not in ("h4", "h3", "h2", "h1"):
        text = node.get_text(separator=" ", strip=True)
        if text:
            paras.append(text)
        node = node.find_next_sibling()
    return paras


def _parse_dates(raw):
    """
    Parse '(November 16, 1538 – March 23, 1606)' → ('November 16, 1538', 'March 23, 1606').
    Handles en-dash, em-dash, and plain hyphen separators.
    """
    raw = raw.strip("()")
    for sep in ("\u2013", "\u2014", " - "):   # en-dash, em-dash, spaced hyphen
        if sep in raw:
            parts = raw.split(sep, 1)
            b = parts[0].strip() or "Unknown"
            d = parts[1].strip() or "Unknown"
            return b, d
    return raw.strip() or "Unknown", "Unknown"


def _extract_patron(paras):
    """Try to find 'patron of X' or 'patroness of X' in the story text."""
    text = " ".join(paras)
    m = re.search(
        r"[Pp]atron(?:ess)?\s+(?:saint\s+)?of\s+([^.;,\n]{3,80}?)(?:[.,;]|\s{2}|$)",
        text,
    )
    return m.group(1).strip() if m else None


def _clean_paras(paras):
    """Strip captions, link-only lines, and noise from paragraph list."""
    noise = re.compile(
        r"^(Click here|Photo:|CNS photo|\(CNS|\(Photo|©|Subscribe|Sign up|"
        r"The Catholic Saints|A banner of|hangs from)",
        re.IGNORECASE,
    )
    cleaned = []
    for p in paras:
        p = re.sub(r"\s+", " ", p).strip()
        if len(p) < 25:
            continue
        if noise.match(p):
            continue
        cleaned.append(p)
    return cleaned
