#!/usr/bin/env python3
"""
get-diocese — Random US Catholic Diocese Explorer
"""

import json
import os
import re
import sqlite3
import sys
import termios
import textwrap
import tty
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ── Config ────────────────────────────────────────────────────────────────────
DIR       = Path(__file__).parent
DB_PATH   = DIR / "diocese.db"
SEED_PATH = DIR / "dioceses.json"
WIDTH     = 80
UA        = "get-diocese/1.0 (terminal explorer; https://github.com/coderanger76/currents)"
TIMEOUT   = 10

# ── ANSI ──────────────────────────────────────────────────────────────────────
RESET      = "\033[0m"
BOLD       = "\033[1m"
BG_AMBER   = "\033[48;5;214m"
BG_DKGRAY  = "\033[100m"
FG_BLACK   = "\033[30m"
FG_AMBER   = "\033[38;5;214m"
FG_MAGENTA = "\033[95m"
FG_WHITE   = "\033[97m"
FG_LTGRAY  = "\033[37m"
FG_DKGRAY  = "\033[90m"
FG_RED     = "\033[91m"
FG_CYAN    = "\033[96m"

ANSI_RE = re.compile(r'\033\[[0-9;]*m')

def c(text, *codes):
    return "".join(codes) + str(text) + RESET

def visible_len(s):
    return len(ANSI_RE.sub('', s))

def rpad(s, width):
    diff = width - visible_len(s)
    return s + " " * max(diff, 0)

def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

# ── Database ──────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dioceses (
            id             INTEGER PRIMARY KEY,
            name           TEXT NOT NULL,
            diocese_type   TEXT,
            state          TEXT,
            city           TEXT,
            wikipedia      TEXT,
            url            TEXT,
            url_verified   INTEGER DEFAULT 0,
            visited        INTEGER DEFAULT 0,
            last_visited   TEXT,
            bishop         TEXT,
            founded        TEXT,
            catholics      TEXT,
            parishes       TEXT,
            priests        TEXT,
            deacons        TEXT,
            population     TEXT,
            area           TEXT,
            cathedral      TEXT,
            summary        TEXT,
            website_excerpt TEXT,
            cached_at      TEXT
        )
    """)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM dioceses").fetchone()[0]
    if count == 0 and SEED_PATH.exists():
        with open(SEED_PATH) as f:
            seed = json.load(f)
        conn.executemany(
            "INSERT INTO dioceses (name, diocese_type, state, city, wikipedia, url) VALUES (?,?,?,?,?,?)",
            [(d['name'], d.get('type','diocese'), d.get('state',''), d.get('city',''),
              d.get('wikipedia',''), d.get('url','')) for d in seed]
        )
        conn.commit()
    return conn


def pick_random(conn):
    row = conn.execute(
        "SELECT * FROM dioceses WHERE visited = 0 ORDER BY RANDOM() LIMIT 1"
    ).fetchone()
    if not row:
        row = conn.execute(
            "SELECT * FROM dioceses ORDER BY RANDOM() LIMIT 1"
        ).fetchone()
    return dict(row)


def save_result(conn, diocese_id, data):
    conn.execute("""
        UPDATE dioceses SET
            visited         = visited + 1,
            last_visited    = ?,
            bishop          = COALESCE(NULLIF(?, ''), bishop),
            founded         = COALESCE(NULLIF(?, ''), founded),
            catholics       = COALESCE(NULLIF(?, ''), catholics),
            parishes        = COALESCE(NULLIF(?, ''), parishes),
            priests         = COALESCE(NULLIF(?, ''), priests),
            deacons         = COALESCE(NULLIF(?, ''), deacons),
            population      = COALESCE(NULLIF(?, ''), population),
            area            = COALESCE(NULLIF(?, ''), area),
            cathedral       = COALESCE(NULLIF(?, ''), cathedral),
            summary         = COALESCE(NULLIF(?, ''), summary),
            website_excerpt = COALESCE(NULLIF(?, ''), website_excerpt),
            cached_at       = ?,
            url             = COALESCE(NULLIF(?, ''), url),
            url_verified    = 1
        WHERE id = ?
    """, (
        datetime.now().isoformat(),
        data.get('bishop',''), data.get('founded',''), data.get('catholics',''),
        data.get('parishes',''), data.get('priests',''), data.get('deacons',''),
        data.get('population',''), data.get('area',''), data.get('cathedral',''),
        data.get('summary',''), data.get('website_excerpt',''),
        datetime.now().isoformat(), data.get('url',''),
        diocese_id,
    ))
    conn.commit()

# ── Network helpers ───────────────────────────────────────────────────────────

SESSION = requests.Session()
SESSION.headers['User-Agent'] = UA


def validate_url(url):
    if not url:
        return url
    try:
        r = SESSION.head(url, allow_redirects=True, timeout=TIMEOUT)
        return r.url
    except Exception:
        try:
            r = SESSION.get(url, allow_redirects=True, timeout=TIMEOUT, stream=True)
            r.close()
            return r.url
        except Exception:
            return url


def clean(text):
    text = re.sub(r'\[.*?\]', '', text)       # strip [1], [note 1]
    text = text.replace('\xa0', ' ')          # non-breaking spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def fetch_wikipedia(slug):
    data = {}
    if not slug:
        return data

    encoded = quote(slug, safe='')

    # REST summary — clean paragraph
    try:
        r = SESSION.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            timeout=TIMEOUT
        )
        if r.ok:
            j = r.json()
            data['summary'] = j.get('extract', '')
    except Exception:
        pass

    # Full page HTML — infobox scrape
    try:
        r = SESSION.get(f"https://en.wikipedia.org/wiki/{encoded}", timeout=TIMEOUT)
        if not r.ok:
            return data
        soup = BeautifulSoup(r.text, 'html.parser')
        infobox = soup.find('table', class_=re.compile(r'\binfobox\b'))
        if not infobox:
            return data

        for row in infobox.find_all('tr'):
            th = row.find('th')
            td = row.find('td')
            if not th or not td:
                continue
            key = th.get_text(' ', strip=True).lower()
            val = clean(td.get_text(' ', strip=True))
            if not val:
                continue

            if any(k in key for k in ('bishop', 'archbishop', 'ordinary', 'administrator')):
                data.setdefault('bishop', val)
            elif any(k in key for k in ('founded', 'established', 'erected', 'created')):
                data.setdefault('founded', val)
            elif 'cathedral' in key:
                data.setdefault('cathedral', val)
            elif 'parish' in key:
                data.setdefault('parishes', val)
            elif 'priest' in key and 'deacon' not in key:
                data.setdefault('priests', val)
            elif 'deacon' in key:
                data.setdefault('deacons', val)
            elif 'population' in key and ('total' in key or 'catholic' in key):
                # Combined row e.g. "Population Total Catholics" -> split both out
                val_clean = re.sub(r'\(as of \d{4}\)', '', val)
                nums = [n for n in re.findall(r'[\d,]+', val_clean)
                        if len(n.replace(',', '')) >= 4]
                pct = re.search(r'\([\d.]+%\)', val)
                pct_str = f' {pct.group()}' if pct else ''
                if len(nums) >= 2:
                    data.setdefault('population', nums[0])
                    data.setdefault('catholics', nums[1] + pct_str)
                elif nums:
                    data.setdefault('catholics', nums[0] + pct_str)
            elif 'member' in key or 'catholic' in key:
                data.setdefault('catholics', val)
            elif 'population' in key:
                data.setdefault('population', val)
            elif 'area' in key and 'sq' in val.lower():
                data.setdefault('area', val)
    except Exception:
        pass

    return data


def fetch_website_excerpt(url):
    if not url:
        return ''
    try:
        r = SESSION.get(url, timeout=TIMEOUT)
        if not r.ok:
            return ''
        soup = BeautifulSoup(r.text, 'html.parser')

        # Hunt for an about/history page link
        target = None
        for a in soup.find_all('a', href=True):
            text = a.get_text(strip=True).lower()
            href = a['href']
            if any(kw in text for kw in ('about', 'history', 'our diocese', 'who we are', 'overview')):
                if href.startswith('http'):
                    target = href
                elif href.startswith('/'):
                    target = urljoin(url, href)
                if target:
                    break

        fetch_url = target or url
        if target:
            try:
                r = SESSION.get(fetch_url, timeout=TIMEOUT)
                if not r.ok:
                    fetch_url = url
                    r = SESSION.get(url, timeout=TIMEOUT)
            except Exception:
                fetch_url = url
                r = SESSION.get(url, timeout=TIMEOUT)

        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()

        main = (soup.find('main') or
                soup.find('article') or
                soup.find('div', class_=re.compile(r'content|main|body', re.I)))
        text = (main or soup).get_text(' ', strip=True)
        text = re.sub(r'\s+', ' ', text)

        sentences = re.split(r'(?<=[.!?])\s+', text)
        good = [s for s in sentences if len(s) > 50][:5]
        return ' '.join(good)[:700]
    except Exception:
        return ''

# ── Display ───────────────────────────────────────────────────────────────────

def divider(label='', color=FG_AMBER):
    if label:
        inner = f"─── {label} "
        trail = "─" * max(0, WIDTH - len(inner) - 1)
        print(c(f" {inner}{trail}", color))
    else:
        print(c(" " + "─" * (WIDTH - 2), FG_DKGRAY))


def wrap_print(text, indent=2, color=FG_LTGRAY, max_lines=6):
    if not text:
        return
    lines = textwrap.wrap(text, WIDTH - indent - 1)
    for line in lines[:max_lines]:
        print(c(" " * indent + line, color))


def stat_pair(label1, val1, label2='', val2=''):
    if not val1:
        return
    left = c(f"  {label1:<18}", FG_AMBER, BOLD) + c(val1, FG_WHITE)
    if label2 and val2:
        pad = " " * max(0, 42 - visible_len(left))
        right = c(f"{label2:<14}", FG_AMBER, BOLD) + c(val2, FG_WHITE)
        print(left + pad + c("│  ", FG_DKGRAY) + right)
    else:
        print(left)


def render(diocese, data, total):
    os.system('clear')
    name  = diocese['name'].upper()
    dtype = (diocese['diocese_type'] or 'diocese').upper()
    state = diocese.get('state', '')
    city  = diocese.get('city', '')

    # ── Header bar ────────────────────────────────────────────────────────────
    print()
    tag  = f"FAITH · {dtype} "
    left = f" {name}"
    gap  = WIDTH - visible_len(left) - len(tag)
    print(c(rpad(left + " " * max(gap, 1) + tag, WIDTH), BG_AMBER, FG_BLACK, BOLD))

    # Sub bar: city/state + founded
    founded = data.get('founded') or diocese.get('founded') or ''
    parts = []
    if city and state:
        parts.append(f"{city}, {state}")
    elif state:
        parts.append(state)
    if founded:
        parts.append(f"Founded {founded}")
    sub = "  " + "  ·  ".join(parts) if parts else ''
    if sub:
        print(c(rpad(sub, WIDTH), BG_DKGRAY, FG_AMBER))
    print()

    # ── Bishop / Cathedral ────────────────────────────────────────────────────
    bishop   = data.get('bishop') or diocese.get('bishop') or ''
    cathedral = data.get('cathedral') or diocese.get('cathedral') or ''
    leader   = "ARCHBISHOP" if dtype == 'ARCHDIOCESE' else ("BISHOP" if dtype != 'EPARCHY' else "BISHOP/EPARCH")
    if bishop:
        print(c(f"  {leader:<18}", FG_AMBER, BOLD) + c(bishop, FG_WHITE))
    if cathedral:
        print(c(f"  {'CATHEDRAL':<18}", FG_AMBER, BOLD) + c(cathedral, FG_WHITE))
    if bishop or cathedral:
        print()

    # ── Statistics ────────────────────────────────────────────────────────────
    catholics  = data.get('catholics')  or diocese.get('catholics')  or ''
    parishes   = data.get('parishes')   or diocese.get('parishes')   or ''
    priests    = data.get('priests')    or diocese.get('priests')    or ''
    deacons    = data.get('deacons')    or diocese.get('deacons')    or ''
    population = data.get('population') or diocese.get('population') or ''
    area       = data.get('area')       or diocese.get('area')       or ''

    if any([catholics, parishes, priests, deacons, population, area]):
        divider("STATISTICS", FG_MAGENTA)
        stat_pair("Catholics",        catholics)
        stat_pair("Total Population", population)
        stat_pair("Parishes",         parishes,  "Priests",  priests)
        stat_pair("Deacons",          deacons,   "Area",     area)
        print()

    # ── About ─────────────────────────────────────────────────────────────────
    summary = data.get('summary') or diocese.get('summary') or ''
    if summary:
        divider("ABOUT", FG_MAGENTA)
        wrap_print(summary)
        print()

    # ── From the Diocese ──────────────────────────────────────────────────────
    excerpt = data.get('website_excerpt') or diocese.get('website_excerpt') or ''
    if excerpt and excerpt[:80] not in (summary or '')[:80]:
        divider("FROM THE DIOCESE", FG_MAGENTA)
        wrap_print(excerpt)
        print()

    # ── Sources ───────────────────────────────────────────────────────────────
    divider("SOURCES", FG_DKGRAY)
    if diocese.get('wikipedia'):
        slug_disp = diocese['wikipedia']
        print(c("  Wikipedia  ", FG_DKGRAY) + c(f"en.wikipedia.org/wiki/{slug_disp}", FG_CYAN))
    site = data.get('url') or diocese.get('url') or ''
    if site:
        domain = re.sub(r'^https?://(www\.)?', '', site).rstrip('/')
        print(c("  Website    ", FG_DKGRAY) + c(domain, FG_CYAN))
    print()

    # ── Footer ────────────────────────────────────────────────────────────────
    visited = diocese.get('visited', 0) + 1
    footer  = rpad(
        c(" L ", BG_AMBER, FG_BLACK, BOLD) + c(" FEELING LUCKY  ", BG_DKGRAY, FG_LTGRAY) +
        c(" ANY KEY ", BG_AMBER, FG_BLACK, BOLD) + c(" RETURN  ", BG_DKGRAY, FG_LTGRAY) +
        c(f"  {visited}/{total} visited", FG_DKGRAY),
        WIDTH
    )
    print(c(footer, BG_DKGRAY))

# ── Status line ───────────────────────────────────────────────────────────────

def status(msg):
    os.system('clear')
    print()
    print(c(f"  {msg}", FG_DKGRAY))

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    conn  = init_db()
    total = conn.execute("SELECT COUNT(*) FROM dioceses").fetchone()[0]

    while True:
        diocese = pick_random(conn)

        status(f"Loading {diocese['name']}...")

        url = diocese.get('url', '')
        if not diocese.get('url_verified'):
            print(c("  Validating URL...", FG_DKGRAY))
            url = validate_url(url) or url

        data = {'url': url}

        if diocese.get('wikipedia'):
            print(c("  Fetching Wikipedia...", FG_DKGRAY))
            data.update(fetch_wikipedia(diocese['wikipedia']))

        print(c("  Fetching diocese website...", FG_DKGRAY))
        data['website_excerpt'] = fetch_website_excerpt(url)

        save_result(conn, diocese['id'], data)

        # Merge fresh data over the db row for display
        diocese.update({k: v for k, v in data.items() if v})

        render(diocese, data, total)

        ch = getch()
        if ch.lower() == 'l':
            continue
        break

    conn.close()


if __name__ == '__main__':
    main()
