#!/usr/bin/env python3
"""
get-catholic — Daily Catholic Wikipedia reading
"""

import os
import re
import sqlite3
import sys
import termios
import textwrap
import tty
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import requests

DIR          = Path(__file__).parent
DB_PATH      = DIR / "catholic.db"
WIDTH        = 80
UA           = "get-catholic/1.0 (terminal devotional app; https://github.com/coderanger76/currents)"
TIMEOUT      = 12
POOL_TTL_DAYS = 7
MAX_PARAS    = 5
MAX_CHARS    = 1400

CATEGORIES = [
    ("Doctors of the Church",  "Doctors_of_the_Church"),
    ("Church Fathers",         "Church_Fathers"),
    ("Popes",                  "Popes"),
    ("Ecumenical Councils",    "Ecumenical_councils"),
    ("Marian Apparitions",     "Marian_apparitions"),
    ("Catholic Mystics",       "Christian_mystics"),
    ("Patron Saints",          "Patron_saints"),
    ("Catholic Theology",      "Catholic_theology"),
    ("Catholic Martyrs",       "Catholic_martyrs"),
    ("Catholic Theologians",   "Catholic_theologians"),
]

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

def col(text, *codes):
    return "".join(codes) + str(text) + RESET

def visible_len(s):
    return len(ANSI_RE.sub('', s))

def rpad(s, width):
    return s + " " * max(0, width - visible_len(s))

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
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id           INTEGER PRIMARY KEY,
            title        TEXT NOT NULL,
            slug         TEXT NOT NULL UNIQUE,
            category     TEXT,
            visited      INTEGER DEFAULT 0,
            last_visited TEXT,
            extract      TEXT,
            wiki_cats    TEXT,
            cached_at    TEXT
        );
        CREATE TABLE IF NOT EXISTS daily (
            date         TEXT PRIMARY KEY,
            article_id   INTEGER
        );
        CREATE TABLE IF NOT EXISTS meta (
            key          TEXT PRIMARY KEY,
            value        TEXT
        );
    """)
    conn.commit()
    return conn

def pool_needs_rebuild(conn):
    count = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    if count == 0:
        return True
    row = conn.execute("SELECT value FROM meta WHERE key='pool_built_at'").fetchone()
    if not row:
        return True
    age = (datetime.now() - datetime.fromisoformat(row['value'])).days
    return age >= POOL_TTL_DAYS

# ── Network ───────────────────────────────────────────────────────────────────

SESSION = requests.Session()
SESSION.headers['User-Agent'] = UA


def fetch_category_members(cat_slug, limit=300):
    try:
        r = SESSION.get('https://en.wikipedia.org/w/api.php', params={
            'action':  'query',
            'list':    'categorymembers',
            'cmtitle': f'Category:{cat_slug}',
            'cmlimit': min(limit, 500),
            'cmtype':  'page',
            'format':  'json',
        }, timeout=TIMEOUT)
        if r.ok:
            return [(m['title'], m['title'].replace(' ', '_'))
                    for m in r.json().get('query', {}).get('categorymembers', [])]
    except Exception:
        pass
    return []


def build_pool(conn):
    os.system('clear')
    print()
    print(col("  Building Catholic reading pool from Wikipedia...", FG_AMBER, BOLD))
    print()
    conn.execute("DELETE FROM articles")
    conn.commit()
    total = 0
    for label, cat_slug in CATEGORIES:
        print(col(f"  ↳ {label:<28}", FG_DKGRAY), end='', flush=True)
        members = fetch_category_members(cat_slug)
        if members:
            conn.executemany(
                "INSERT OR IGNORE INTO articles (title, slug, category) VALUES (?,?,?)",
                [(title, slug, label) for title, slug in members]
            )
            conn.commit()
            total += len(members)
            print(col(f"{len(members):>4} articles", FG_AMBER))
        else:
            print(col("  —", FG_DKGRAY))
    conn.execute("INSERT OR REPLACE INTO meta (key,value) VALUES ('pool_built_at',?)",
                 (datetime.now().isoformat(),))
    conn.commit()
    real_count = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    print()
    print(col(f"  Pool ready: {real_count} articles across {len(CATEGORIES)} categories.", FG_AMBER))
    import time; time.sleep(1.5)


def fetch_article_content(slug):
    """Fetch intro extract + categories via MediaWiki API."""
    data = {}
    try:
        r = SESSION.get('https://en.wikipedia.org/w/api.php', params={
            'action':      'query',
            'prop':        'extracts|categories',
            'exintro':     1,
            'explaintext': 1,
            'titles':      slug.replace('_', ' '),
            'cllimit':     20,
            'format':      'json',
        }, timeout=TIMEOUT)
        if not r.ok:
            return data
        pages = r.json().get('query', {}).get('pages', {})
        for page in pages.values():
            data['title']   = page.get('title', slug.replace('_', ' '))
            data['extract'] = page.get('extract', '').strip()
            skip_prefixes = (
                'Articles', 'CS1', 'Wikipedia', 'All ', 'Pages', 'Use ',
                'Harv', 'Webarchive', 'Short description', 'Cleanup',
            )
            skip_patterns = re.compile(
                r'^\d+s?\s+(births|deaths|disestablishments|establishments)'
                r'|\d+(st|nd|rd|th)-century'
                r'|^\d{4}\s+in\s'
                r'|^(January|February|March|April|May|June|July|August'
                r'|September|October|November|December)\s+\d{4}'
                r'|Commons category'
                r'|^(AC|BC)\s'
            )
            raw_cats = [
                entry['title'].replace('Category:', '')
                for entry in page.get('categories', [])
                if not any(entry['title'].startswith(f'Category:{pfx}') for pfx in skip_prefixes)
                and not skip_patterns.search(entry['title'].replace('Category:', ''))
            ]
            data['wiki_cats'] = ' · '.join(raw_cats[:7])
    except Exception:
        pass
    return data


def get_or_fetch(conn, article_id):
    row = conn.execute("SELECT * FROM articles WHERE id=?", (article_id,)).fetchone()
    if not row:
        return None
    a = dict(row)
    if not a.get('extract'):
        fresh = fetch_article_content(a['slug'])
        a.update(fresh)
        conn.execute("""
            UPDATE articles
            SET extract=?, wiki_cats=?, cached_at=?, visited=visited+1, last_visited=?
            WHERE id=?
        """, (a.get('extract',''), a.get('wiki_cats',''),
              datetime.now().isoformat(), datetime.now().isoformat(), article_id))
        conn.commit()
    return a


def get_daily_article(conn):
    today = datetime.now().strftime('%Y-%m-%d')
    row   = conn.execute("SELECT article_id FROM daily WHERE date=?", (today,)).fetchone()
    if row:
        return get_or_fetch(conn, row['article_id'])
    pick = (
        conn.execute("SELECT id FROM articles WHERE visited=0 ORDER BY RANDOM() LIMIT 1").fetchone() or
        conn.execute("SELECT id FROM articles ORDER BY RANDOM() LIMIT 1").fetchone()
    )
    if not pick:
        return None
    conn.execute("INSERT OR REPLACE INTO daily (date, article_id) VALUES (?,?)",
                 (today, pick['id']))
    conn.commit()
    return get_or_fetch(conn, pick['id'])


def get_lucky_article(conn):
    today      = datetime.now().strftime('%Y-%m-%d')
    daily_row  = conn.execute("SELECT article_id FROM daily WHERE date=?", (today,)).fetchone()
    exclude_id = daily_row['article_id'] if daily_row else -1
    pick = (
        conn.execute("SELECT id FROM articles WHERE visited=0 AND id!=? ORDER BY RANDOM() LIMIT 1",
                     (exclude_id,)).fetchone() or
        conn.execute("SELECT id FROM articles WHERE id!=? ORDER BY RANDOM() LIMIT 1",
                     (exclude_id,)).fetchone()
    )
    if not pick:
        return None
    return get_or_fetch(conn, pick['id'])

# ── Display ───────────────────────────────────────────────────────────────────

def divider(label='', color=FG_AMBER):
    if label:
        inner = f"─── {label} "
        trail = "─" * max(0, WIDTH - len(inner) - 1)
        print(col(f" {inner}{trail}", color))
    else:
        print(col(" " + "─" * (WIDTH - 2), FG_DKGRAY))


def wrap_para(text, indent=2, color=FG_LTGRAY):
    for line in textwrap.wrap(text.strip(), WIDTH - indent - 1):
        print(col(" " * indent + line, color))


def render(article, is_lucky=False):
    os.system('clear')

    raw_title = (article.get('title') or article.get('slug','').replace('_',' '))
    category  = article.get('category') or ''
    extract   = article.get('extract') or ''
    wiki_cats = article.get('wiki_cats') or ''
    slug      = article.get('slug') or ''
    today_str = datetime.now().strftime('%a %d %b %Y').upper()
    mode      = "FEELING LUCKY" if is_lucky else "DAILY READ"

    # Fit title into header — truncate if needed
    tag        = f"FAITH · {mode} "
    max_t_len  = WIDTH - len(tag) - 2
    title      = raw_title.upper()
    if len(title) > max_t_len:
        title = title[:max_t_len - 1] + '…'

    # ── Header ────────────────────────────────────────────────────────────────
    print()
    left = f" {title}"
    gap  = WIDTH - visible_len(left) - len(tag)
    print(col(rpad(left + " " * max(gap, 1) + tag, WIDTH), BG_AMBER, FG_BLACK, BOLD))

    # Sub-bar: category · date
    sub_parts = [p for p in [category, today_str] if p]
    print(col(rpad("  " + "  ·  ".join(sub_parts), WIDTH), BG_DKGRAY, FG_AMBER))
    print()

    # ── Article text ──────────────────────────────────────────────────────────
    if extract:
        paragraphs  = [p.strip() for p in extract.split('\n') if len(p.strip()) > 40]
        char_count  = 0
        para_count  = 0
        for para in paragraphs:
            if para_count >= MAX_PARAS or char_count >= MAX_CHARS:
                print(col("  […]", FG_DKGRAY))
                break
            wrap_para(para)
            print()
            char_count += len(para)
            para_count += 1
    else:
        print(col("  (No content available for this article.)", FG_DKGRAY))
        print()

    # ── Topics ────────────────────────────────────────────────────────────────
    if wiki_cats:
        divider("TOPICS", FG_MAGENTA)
        wrap_para(wiki_cats, color=FG_CYAN)
        print()

    # ── Source ────────────────────────────────────────────────────────────────
    divider("SOURCE", FG_DKGRAY)
    print(col("  Wikipedia  ", FG_DKGRAY) + col(f"en.wikipedia.org/wiki/{slug}", FG_CYAN))
    print()

    # ── Footer ────────────────────────────────────────────────────────────────
    footer = (
        col(" L ", BG_AMBER, FG_BLACK, BOLD) +
        col(" FEELING LUCKY  ", BG_DKGRAY, FG_LTGRAY) +
        col(" ANY KEY ", BG_AMBER, FG_BLACK, BOLD) +
        col(" RETURN  ", BG_DKGRAY, FG_LTGRAY) +
        col(f"  {today_str}", FG_DKGRAY)
    )
    print(col(rpad(footer, WIDTH), BG_DKGRAY))


def status(msg):
    os.system('clear')
    print()
    print(col(f"  {msg}", FG_DKGRAY))

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    conn = init_db()

    if pool_needs_rebuild(conn):
        build_pool(conn)

    status("Loading today's Catholic reading...")
    article  = get_daily_article(conn)
    is_lucky = False

    if not article:
        os.system('clear')
        print()
        print(col("  No articles available. Check your connection and try again.", FG_RED))
        getch()
        conn.close()
        return

    while True:
        render(article, is_lucky=is_lucky)
        ch = getch()
        if ch.lower() == 'l':
            status("Finding another article...")
            lucky = get_lucky_article(conn)
            if lucky:
                article  = lucky
                is_lucky = True
        else:
            break

    conn.close()


if __name__ == '__main__':
    main()
