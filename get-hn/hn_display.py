"""
Terminal display and formatting for get-hn.
"""

from datetime import datetime

WIDTH = 80
HEAVY = "═" * WIDTH
LIGHT = "─" * WIDTH

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
ORANGE  = "\033[38;5;208m"   # HN orange-ish accent

# Special-story prefixes and their display colours
SPECIAL_PREFIXES = {
    "Ask HN:":  CYAN,
    "Show HN:": CYAN,
    "Tell HN:": CYAN,
    "Launch HN:": CYAN,
}


def _c(text, code):
    return f"{code}{text}{RESET}"


def _strip_special(title):
    """
    If title starts with a known prefix, return (prefix, rest_of_title).
    Otherwise return (None, title).
    """
    for prefix in SPECIAL_PREFIXES:
        if title.startswith(prefix):
            rest = title[len(prefix):].lstrip()
            return prefix, rest
    return None, title


class HNDisplay:
    """Renders Hacker News stories to the terminal."""

    def show_header(self, feed_label="TOP STORIES", count=30):
        ts = datetime.now().strftime("%a %b %d, %Y  %H:%M")
        masthead = "  HACKER NEWS  " + feed_label
        pad = WIDTH - len(masthead) - len(ts)
        print()
        print(_c(HEAVY, YELLOW))
        print(_c(f"{masthead}{' ' * max(pad, 1)}{ts}", YELLOW + BOLD))
        print(_c(HEAVY, YELLOW))

    def show_story(self, story):
        rank     = story["rank"]
        title    = story["title"]
        score    = story["score"]
        domain   = story["domain"]
        comments = story["comments"]
        time_ago = story["time_ago"]
        by       = story["by"]

        # ── Rank colour: bold red for top 3, yellow otherwise ────────
        if rank <= 3:
            rank_str = _c(f"{rank:>3}", RED + BOLD)
        else:
            rank_str = _c(f"{rank:>3}", YELLOW)

        # ── Score ─────────────────────────────────────────────────────
        score_str = _c(f"▲{score:>5}", GREEN)

        # ── Title — detect and colour special prefixes ─────────────
        prefix, rest = _strip_special(title)
        max_title = WIDTH - 3 - 8 - 2   # rank(3) + " " + "▲NNNNN "(8) + spaces
        if prefix:
            prefix_colored = _c(prefix, CYAN + BOLD)
            # Account for the visible prefix length when truncating the rest
            max_rest = max_title - len(prefix) - 1
            if len(rest) > max_rest:
                rest = rest[:max_rest - 1] + "…"
            title_str = f"{prefix_colored} {_c(rest, WHITE + BOLD)}"
        else:
            if len(title) > max_title:
                title = title[:max_title - 1] + "…"
            title_str = _c(title, WHITE + BOLD)

        # Line 1:  " 1  ▲ 2847  Title of the story"
        print(f"{rank_str} {score_str}  {title_str}")

        # ── Line 2: domain · comments · time · by ────────────────────
        comments_str = _c(f"💬 {comments}", CYAN)
        meta = (
            f"          "
            f"{_c(domain, GRAY)}  ·  "
            f"{comments_str}  ·  "
            f"{_c(time_ago, GRAY)}  ·  "
            f"{_c('by ' + by, GRAY)}"
        )
        print(meta)

    def show_separator(self):
        print(_c(f"  {LIGHT}", GRAY))

    def show_footer(self, count):
        source = "Source: Hacker News API  ·  hacker-news.firebaseio.com  ·  news.ycombinator.com"
        print(_c(HEAVY, YELLOW))
        print(_c(f"  {count} stories  ·  {source}", GRAY))
        print(_c(HEAVY, YELLOW))
        print()

    def show_error(self, msg):
        print()
        print(_c(f"  ✗  {msg}", RED))
        print()
