#!/usr/bin/env python3
"""
currents — Bloomberg-style terminal information suite
"""

import os
import sys
import subprocess
import tty
import termios
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent   # repo root: …/claude/

# ── Terminal dimensions ────────────────────────────────────────────────────────
WIDTH = 80

# ── ANSI color codes ──────────────────────────────────────────────────────────
RESET      = "\033[0m"
BOLD       = "\033[1m"
DIM        = "\033[2m"
REVERSE    = "\033[7m"

# Bloomberg palette: black bg, amber/orange primaries, white text
BG_BLACK   = "\033[40m"
BG_DKGRAY  = "\033[100m"
BG_AMBER   = "\033[48;5;214m"    # amber fill for header
BG_PANEL   = "\033[48;5;232m"    # near-black panel

FG_BLACK   = "\033[30m"
FG_AMBER   = "\033[38;5;214m"    # primary accent
FG_ORANGE  = "\033[38;5;208m"    # secondary accent
FG_WHITE   = "\033[97m"
FG_LTGRAY  = "\033[37m"
FG_DKGRAY  = "\033[90m"
FG_CYAN    = "\033[96m"
FG_RED     = "\033[91m"
FG_GREEN   = "\033[92m"
FG_YELLOW  = "\033[93m"
FG_BLUE    = "\033[94m"
FG_MAGENTA = "\033[95m"

# Group accent colors (Bloomberg uses color-coded panels per sector)
GROUP_COLORS = {
    "NEWS":    FG_CYAN,
    "MARKETS": FG_GREEN,
    "SCIENCE": FG_BLUE,
    "FAITH":   FG_MAGENTA,
    "LOCAL":   FG_YELLOW,
}

GROUP_BG = {
    "NEWS":    "\033[48;5;23m",    # dark teal
    "MARKETS": "\033[48;5;22m",    # dark green
    "SCIENCE": "\033[48;5;17m",    # dark blue
    "FAITH":   "\033[48;5;53m",    # dark purple
    "LOCAL":   "\033[48;5;58m",    # dark olive
}


def c(text, *codes):
    return "".join(codes) + str(text) + RESET


def pad(s, width):
    """Pad/truncate a string to exactly width visible characters."""
    # strip ANSI to measure visible length
    import re
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    visible = ansi_escape.sub('', s)
    diff = width - len(visible)
    if diff > 0:
        return s + " " * diff
    elif diff < 0:
        return s[:width]   # rough trim (won't split mid-code)
    return s


# ── App registry ──────────────────────────────────────────────────────────────
# (key, name, description, path, group)
def _p(*parts):
    return str(BASE.joinpath(*parts))

APPS = [
    # News
    ("1", "GET-NEWS",    "NY Times · Top headlines",               _p("get-news",                "get-news"),    "NEWS"),
    ("2", "GET-HN",      "Hacker News · Top stories",              _p("get-hn",                  "get-hn"),      "NEWS"),
    # Markets
    ("3", "GET-OIL",     "Energy · Spot commodity prices",         _p("spot_oil",                "get-oil"),     "MARKETS"),
    ("4", "GET-STOCKS",  "Markets · Global indices",               _p("get-stocks",              "get-stocks"),  "MARKETS"),
    ("5", "GET-FED",     "Economy · Federal Reserve / FRED data",  _p("get-fed",                 "get-fed"),     "MARKETS"),
    # Weather & Science
    ("6", "GET-WEATHER", "Weather · Current conditions",           _p("weather_checker",         "weather"),     "SCIENCE"),
    ("7", "GET-APOD",    "NASA · Astronomy Pic of the Day",        _p("get-apod",                "get-apod"),    "SCIENCE"),
    # Faith
    ("8", "GET-SAINT",   "Liturgical · Daily calendar (API)",      _p("get-saint",               "get-saint"),   "FAITH"),
    ("9", "GET-SAINTS",  "Saints · Franciscan Media profiles",     _p("get-saints",              "get-saints"),  "FAITH"),
    ("d", "GET-DIOCESE", "Faith · Random US diocese explorer",     _p("get-diocese",             "get-diocese"), "FAITH"),
    ("c", "GET-CATHOLIC","Faith · Catholic daily reading",         _p("get-catholic",            "get-catholic"),"FAITH"),
    # Local
    ("0", "GET-RENTALS", "Housing · Craigslist rental listings",   _p("craigslist_rental_tracker","rentals"),    "LOCAL"),
]

GROUPS = ["NEWS", "MARKETS", "SCIENCE", "FAITH", "LOCAL"]

GROUP_LABELS = {
    "NEWS":    "NEWS & INFORMATION",
    "MARKETS": "MARKETS & ECONOMY",
    "SCIENCE": "SCIENCE & WEATHER",
    "FAITH":   "FAITH & LITURGY",
    "LOCAL":   "LOCAL & HOUSING",
}


# ── Terminal helpers ──────────────────────────────────────────────────────────

def clear():
    os.system("clear")


def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch


def pause(msg="  <PRESS ANY KEY TO RETURN>"):
    print()
    print(c(msg, FG_DKGRAY))
    getch()


# ── Display ───────────────────────────────────────────────────────────────────

def header_bar():
    """Bloomberg-style amber top bar."""
    now      = datetime.now()
    date_str = now.strftime("%a %d %b %Y  %H:%M:%S").upper()
    title    = " CURRENTS "
    tagline  = "TERMINAL INFORMATION SUITE"

    # Full-width amber bar
    bar = BG_AMBER + FG_BLACK + BOLD
    left  = f" {title} │ {tagline}"
    right = f"{date_str} "
    gap   = WIDTH - len(left) - len(right)
    line  = left + " " * max(gap, 1) + right
    print(bar + line[:WIDTH] + RESET)


def sub_bar():
    """Dark subtitle bar with session info."""
    session = "SESSION ACTIVE"
    hint    = "ENTER CODE TO LAUNCH  │  Q QUIT"
    gap     = WIDTH - len(session) - len(hint) - 2
    print(
        c(f" {session}" + " " * max(gap, 1) + f"{hint} ",
          BG_DKGRAY, FG_AMBER)
    )


def divider(label="", color=FG_AMBER):
    if label:
        label_str = f"─── {label} "
        trail     = "─" * max(0, WIDTH - len(label_str) - 1)
        print(c(f" {label_str}{trail}", color))
    else:
        print(c(" " + "─" * (WIDTH - 2), FG_DKGRAY))


def app_row(key, name, desc, accent):
    """Single app entry row."""
    key_cell  = c(f" {key} ", BG_AMBER, FG_BLACK, BOLD)
    name_cell = c(f"  {name:<13}", accent, BOLD)
    desc_cell = c(f"  {desc}", FG_LTGRAY)
    row = f"  {key_cell}{name_cell}{desc_cell}"

    # right-pad to WIDTH for clean background fill
    import re
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    visible_len = len(ansi_escape.sub('', row))
    padding = max(0, WIDTH - visible_len)
    print(row + " " * padding)


def footer_bar():
    """Bloomberg-style function key footer."""
    keys = [
        ("1-9/0/C/D", "LAUNCH"),
        ("Q",       "QUIT  "),
        ("↵",       "SELECT"),
    ]
    bar = BG_DKGRAY + FG_WHITE
    parts = []
    for k, label in keys:
        parts.append(
            BG_AMBER + FG_BLACK + BOLD + f" {k} " + RESET +
            BG_DKGRAY + FG_LTGRAY + f" {label}  " + RESET
        )
    line  = "  " + "".join(parts)
    import re
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    visible_len = len(ansi_escape.sub('', line))
    padding = max(0, WIDTH - visible_len)
    print(bar + line + " " * padding + RESET)


def show_menu():
    clear()

    # ── Header ────────────────────────────────────────────────────────────────
    print()
    header_bar()
    sub_bar()
    print()

    # ── Grouped app list ──────────────────────────────────────────────────────
    grouped = {}
    for app in APPS:
        grouped.setdefault(app[4], []).append(app)

    for group in GROUPS:
        apps = grouped.get(group, [])
        if not apps:
            continue
        accent = GROUP_COLORS[group]
        divider(GROUP_LABELS[group], accent)
        for key, name, desc, path, _ in apps:
            app_row(key, name, desc, accent)
        print()

    # ── Footer ────────────────────────────────────────────────────────────────
    footer_bar()
    print()


def run_app(app):
    key, name, desc, path, group = app
    clear()

    accent = GROUP_COLORS[group]
    now    = datetime.now().strftime("%H:%M:%S")
    print()
    print(c(f" ▶ LAUNCHING {name}  │  {desc}  │  {now} ", BG_AMBER, FG_BLACK, BOLD))
    print(c(" " + "─" * (WIDTH - 2), FG_DKGRAY))
    print()

    try:
        subprocess.run([path], check=False)
    except FileNotFoundError:
        print()
        print(c(f"  ✗  NOT FOUND: {path}", FG_RED, BOLD))
    except Exception as e:
        print()
        print(c(f"  ✗  ERROR: {e}", FG_RED))

    pause()


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    key_map = {app[0]: app for app in APPS}

    while True:
        show_menu()
        ch = getch()

        if ch in ("q", "Q", "\x03"):
            clear()
            print()
            print(c("  CURRENTS TERMINAL CLOSED.\n", FG_DKGRAY))
            break

        if ch in key_map:
            run_app(key_map[ch])


if __name__ == "__main__":
    main()
