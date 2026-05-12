"""
Terminal display for get-apod.
"""

import textwrap
from datetime import datetime

WIDTH = 74
HEAVY = "═" * WIDTH
LIGHT = "─" * WIDTH

RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"


def _c(text, code):
    return f"{code}{text}{RESET}"


def _wrap(text, indent="  ", width=WIDTH - 4):
    return textwrap.fill(
        text,
        width=width,
        initial_indent=indent,
        subsequent_indent=indent,
        break_long_words=False,
        break_on_hyphens=False,
    )


class APODDisplay:

    def show(self, apod):
        date_str  = apod["date"]
        title     = apod["title"]
        media     = apod["media_type"]
        url       = apod.get("hdurl") or apod.get("url", "")
        thumb     = apod.get("thumbnail", "")
        copyright = apod.get("copyright", "")
        explain   = apod.get("explanation", "")
        api_key   = apod.get("api_key_used", "DEMO_KEY")

        # ── Parse and reformat date ────────────────────────────────────
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            friendly_date = d.strftime("%A, %B %-d, %Y")
        except ValueError:
            friendly_date = date_str

        # ── Header ────────────────────────────────────────────────────
        label   = "  NASA · ASTRONOMY PICTURE OF THE DAY  ✦"
        padding = WIDTH - len(label) - len(friendly_date) - 2
        print()
        print(_c(HEAVY, YELLOW))
        print(_c(f"{label}{' ' * max(padding, 1)}{friendly_date}", YELLOW))
        print(_c(HEAVY, YELLOW))
        print()

        # ── Title ─────────────────────────────────────────────────────
        print(_c(f"  ✦  {title.upper()}", WHITE + BOLD))
        print()

        # ── Media type badge ──────────────────────────────────────────
        if media == "video":
            print(_c("     Media    ·  🎬 Video", CYAN))
            if thumb:
                print(_c(f"     Thumbnail ·  {thumb}", GRAY))
        else:
            print(_c("     Media    ·  📷 Image", CYAN))

        if copyright:
            print(_c(f"     Credit   ·  {copyright}", GREEN))
        if url:
            print(_c(f"     URL      ·  {url}", GRAY))

        # ── Explanation ───────────────────────────────────────────────
        if explain:
            print()
            print(_c("  EXPLANATION", YELLOW + BOLD))
            print(_c(f"  {LIGHT}", GRAY))
            print()
            # Split on double newlines, then wrap each paragraph
            paragraphs = [p.strip() for p in explain.split("  ") if p.strip()]
            if not paragraphs:
                paragraphs = [explain]
            for para in paragraphs:
                print(_wrap(para))
                print()

        # ── Footer ────────────────────────────────────────────────────
        print(_c(HEAVY, YELLOW))
        key_label = "DEMO_KEY (30 req/hr — set NASA_API_KEY for more)" if api_key == "DEMO_KEY" else "NASA API"
        print(_c(f"  Source: NASA APOD  ·  api.nasa.gov/planetary/apod  ·  {key_label}", GRAY))
        print(_c(HEAVY, YELLOW))
        print()

    def show_error(self, msg):
        print()
        print(_c(f"  ✗  {msg}", RED))
        print()
