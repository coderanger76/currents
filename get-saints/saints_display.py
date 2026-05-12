"""
Display and formatting module for get-saints
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


class SaintsDisplay:

    def show_header(self, target_date):
        date_str = target_date.strftime("%A, %B %-d, %Y")
        padding  = WIDTH - len("  SAINT OF THE DAY  ✝") - len(date_str) - 2
        print()
        print(_c(HEAVY, YELLOW))
        print(_c(f"  SAINT OF THE DAY  ✝{' ' * padding}{date_str}", YELLOW))
        print(_c("  Source: Franciscan Media · franciscanmedia.org", GRAY))
        print(_c(HEAVY, YELLOW))

    def show_no_saints(self):
        print()
        print(_c("  No saint entry found for this date.", GRAY))
        print()

    def show_saint(self, detail, index=0, total=1):
        print()

        # ── Name ────────────────────────────────────────────────────────
        label = detail["name"].upper()
        if total > 1:
            label += f"   ({index + 1} of {total})"
        print(_c(f"  ✝  {label}", WHITE + BOLD))
        print()

        # ── Metadata ─────────────────────────────────────────────────────
        if detail.get("feast_date"):
            print(_c(f"     Feast Day  ·  {detail['feast_date']}", CYAN))

        born = detail.get("born", "Unknown")
        died = detail.get("died", "Unknown")
        if born and born != "Unknown":
            print(_c(f"     Born       ·  {born}", GRAY))
        if died and died != "Unknown":
            print(_c(f"     Died       ·  {died}", GRAY))
        if detail.get("patron"):
            print(_c(f"     Patron of  ·  {detail['patron']}", GREEN))

        # ── Story ────────────────────────────────────────────────────────
        if detail.get("story"):
            print()
            print(_c(f"  STORY", YELLOW + BOLD))
            print(_c(f"  {LIGHT}", GRAY))
            print()
            for para in detail["story"]:
                print(_wrap(para))
                print()

        # ── Reflection ───────────────────────────────────────────────────
        if detail.get("reflection"):
            print(_c(f"  REFLECTION", YELLOW + BOLD))
            print(_c(f"  {LIGHT}", GRAY))
            print()
            for para in detail["reflection"]:
                print(_wrap(para))
                print()

        # ── Divider between multiple saints ──────────────────────────────
        if total > 1 and index < total - 1:
            print(_c(f"  {LIGHT}", GRAY))

    def show_footer(self, details):
        print(_c(HEAVY, YELLOW))
        for d in details:
            print(_c(f"  {d['url']}", GRAY))
        print(_c(HEAVY, YELLOW))
        print()
