"""
Terminal display and formatting for get-news
"""

import textwrap
from datetime import datetime, timezone
from config import SECTION_COLORS, DEFAULT_SECTION_COLOR

WIDTH        = 72
HEAVY        = "═" * WIDTH
LIGHT        = "─" * WIDTH
THIN         = "·" * WIDTH

# ANSI codes
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
GRAY    = "\033[90m"
NYT_RED = "\033[38;5;196m"   # Close to NYT brand red


def _c(text, code):
    return f"{code}{text}{RESET}"


def _section_color(section):
    key = (section or "").lower()
    return SECTION_COLORS.get(key, DEFAULT_SECTION_COLOR)


def _relative_time(date_str):
    """Return a human-friendly relative time string."""
    if not date_str:
        return ""
    try:
        # Handle both 'Z' and '+00:00' suffixes
        clean = date_str.replace("Z", "+00:00")
        dt    = datetime.fromisoformat(clean)
        now   = datetime.now(timezone.utc)
        delta = now - dt
        secs  = int(delta.total_seconds())

        if secs < 0:
            return "just now"
        if secs < 60:
            return "just now"
        if secs < 3600:
            m = secs // 60
            return f"{m}m ago"
        if secs < 86400:
            h = secs // 3600
            return f"{h}h ago"
        if secs < 604800:
            d = secs // 86400
            return f"{d}d ago"
        return dt.strftime("%-m/%-d/%Y")
    except Exception:
        return date_str[:10]


def _wrap(text, indent=6, max_width=WIDTH):
    """Wrap text to fit within terminal width."""
    if not text:
        return ""
    available = max_width - indent
    lines = textwrap.wrap(text, width=available)
    prefix = " " * indent
    return ("\n" + prefix).join(lines)


class NewsDisplay:
    """Renders NY Times news to the terminal."""

    def show_header(self, mode_label, last_updated=""):
        ts = datetime.now().strftime("%a %b %d, %Y  %H:%M")
        print()
        print(_c(HEAVY, NYT_RED))
        # NYT masthead
        nyt = "  THE NEW YORK TIMES"
        right = ts
        pad = WIDTH - len(nyt) - len(right)
        print(_c(f"{nyt}{' ' * pad}{right}", NYT_RED + BOLD))
        # Mode label
        print(_c(f"  {mode_label}", GRAY))
        print(_c(HEAVY, NYT_RED))

    def show_article(self, index, article, show_abstract=True):
        """Render a single article row."""
        title    = article.get("title", "(no title)")
        abstract = article.get("abstract", "")
        url      = article.get("url", "")
        byline   = article.get("byline", "")
        section  = (article.get("section") or article.get("subsection") or "").upper()
        pub_date = article.get("updated_date") or article.get("published_date", "")
        rel_time = _relative_time(pub_date)

        sec_color = _section_color(section.lower())

        # ── Index + section badge + time ──────────────────────────────
        idx_str  = _c(f"  [{index:>2}]", DIM)
        sec_str  = _c(f" {section:<14}" if section else " " * 15, sec_color + BOLD)
        time_str = _c(rel_time, GRAY)
        print(f"{idx_str}{sec_str} {time_str}")

        # ── Headline ──────────────────────────────────────────────────
        # Wrap headline to width, indented
        wrapped_title = _wrap(title, indent=7, max_width=WIDTH)
        print(_c(f"       {wrapped_title}", WHITE + BOLD))

        # ── Byline ────────────────────────────────────────────────────
        if byline:
            print(_c(f"       {byline}", GRAY))

        # ── Abstract ──────────────────────────────────────────────────
        if show_abstract and abstract:
            wrapped_abs = _wrap(abstract, indent=7, max_width=WIDTH)
            print(_c(f"       {wrapped_abs}", DIM))

        # ── URL ───────────────────────────────────────────────────────
        if url:
            short = url.replace("https://www.nytimes.com", "nytimes.com")
            # Trim long URLs
            if len(short) > WIDTH - 10:
                short = short[:WIDTH - 13] + "..."
            print(_c(f"       → {short}", CYAN + DIM))

        print()

    def show_section_break(self, label):
        """A thin separator with optional label for subsections."""
        if label:
            pad   = WIDTH - len(label) - 6
            print(_c(f"  ── {label} {'─' * pad}", GRAY))
        else:
            print(_c(f"  {LIGHT}", GRAY))

    def show_footer(self, count, last_updated=""):
        rel = _relative_time(last_updated) if last_updated else ""
        updated_str = f"  Updated {rel}  ·  " if rel else "  "
        attr = "Data © The New York Times"
        print(_c(HEAVY, NYT_RED))
        print(_c(f"{updated_str}{count} stories  ·  {attr}", GRAY))
        print(_c(HEAVY, NYT_RED))
        print()

    def show_error(self, msg):
        print()
        print(_c(f"  ✗  {msg}", RED))
        print()

    def show_no_results(self, query):
        print()
        print(_c(f"  No results found for: {query}", YELLOW))
        print()
