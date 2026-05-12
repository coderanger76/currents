"""
Display and formatting module for get-saint
"""

from datetime import datetime

WIDTH = 72
HEAVY = "═" * WIDTH
LIGHT = "─" * WIDTH

# ANSI codes
RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"
PURPLE = "\033[35m"
CYAN   = "\033[96m"

# Liturgical colour → (ANSI code, meaning)
LIT_COLOUR = {
    "white":  (WHITE,              "joy & purity"),
    "red":    (RED,                "Holy Spirit & martyrdom"),
    "violet": (PURPLE,             "penance & preparation"),
    "green":  ("\033[32m",         "hope & growth"),
    "rose":   ("\033[95m",         "joy amid penance"),
    "black":  (GRAY,               "mourning"),
    "gold":   ("\033[33m",         "highest solemnity"),
}

RANK_LABELS = {
    "primary liturgical days": "Primary Liturgical Day",
    "triduum":                 "Easter Triduum",
    "solemnity":               "Solemnity",
    "feast":                   "Feast",
    "memorial":                "Memorial",
    "optional memorial":       "Optional Memorial",
    "commemoration":           "Commemoration",
    "ferial":                  "Ferial",
}

SEASON_LABELS = {
    "advent":    "Advent",
    "christmas": "Christmas Season",
    "ordinary":  "Ordinary Time",
    "lent":      "Lent",
    "easter":    "Easter Season",
    "triduum":   "Easter Triduum",
}

SAINT_PREFIXES = ("Saints ", "Saint ", "Blesseds ", "Blessed ", "Venerable ")


def _c(text, code):
    return f"{code}{text}{RESET}"


def _rank_label(rank):
    return RANK_LABELS.get(rank.lower(), rank.title())


def _colour_swatch(colour):
    """Return a coloured ■ swatch with the colour name."""
    ansi, meaning = LIT_COLOUR.get(colour.lower(), (GRAY, ""))
    return _c(f"■ {colour.title()}", ansi)


def _ordinal(n):
    if 11 <= n <= 13:
        return f"{n}th"
    return f"{n}{['th','st','nd','rd','th','th','th','th','th','th'][n % 10]}"


def _is_saint(title):
    return any(title.startswith(p) for p in SAINT_PREFIXES)


def _parse_saint(title):
    """
    Split 'Saint Foo of Bar, bishop' into (full_name, role).
    Returns (title, None) if no comma-separated role found.
    """
    if ", " in title:
        name, role = title.split(", ", 1)
        return name, role.title()
    return title, None


def _season_line(data):
    season  = SEASON_LABELS.get(data.get("season", ""), data.get("season", "").title())
    sw      = data.get("season_week", 0)
    if sw:
        return f"{season}  ·  {_ordinal(sw)} Week"
    return season


class SaintDisplay:

    def show_header(self, today):
        date_str = datetime.strptime(today["date"], "%Y-%m-%d").strftime("%A, %B %-d, %Y")
        padding  = WIDTH - len("  LITURGICAL CALENDAR  ✝") - len(date_str) - 2
        print()
        print(_c(HEAVY, YELLOW))
        print(_c(f"  LITURGICAL CALENDAR  ✝{' ' * padding}{date_str}", YELLOW))
        print(_c(f"  {_season_line(today)}", GRAY))
        print(_c(HEAVY, YELLOW))

    def show_today(self, today):
        celebrations = sorted(today.get("celebrations", []), key=lambda x: x.get("rank_num", 9))
        print()
        print(_c(f"  TODAY'S OBSERVANCES", YELLOW + BOLD))
        print(_c(f"  {LIGHT}", GRAY))

        for cel in celebrations:
            title   = cel["title"]
            rank    = _rank_label(cel["rank"])
            colour  = cel.get("colour", "")
            swatch  = _colour_swatch(colour)

            # Rank badge + colour swatch on same line
            badge_line = f"  [{rank.upper()}]"
            padding    = WIDTH - len(f"  [{rank.upper()}]") - len(f"  {colour.title()}") - 3
            print()
            print(f"{_c(badge_line, BOLD)}{'  ' + swatch:>{len(str(swatch)) + padding}}")

            if _is_saint(title):
                name, role = _parse_saint(title)
                print(_c(f"  {name}", WHITE + BOLD))
                if role:
                    print(_c(f"  Role:  {role}", CYAN))
            else:
                print(_c(f"  {title}", WHITE))

            # Colour meaning
            _, meaning = LIT_COLOUR.get(colour.lower(), (GRAY, None))
            if meaning:
                ansi, _ = LIT_COLOUR[colour.lower()]
                print(_c(f"  Liturgical Colour:  {colour.title()} — {meaning}", ansi))

    def show_week_ahead(self, week_days):
        """week_days: list of API dicts for the next 6 days (excluding today)."""
        print()
        print()
        print(_c(f"  WEEK AHEAD", YELLOW + BOLD))
        print(_c(f"  {LIGHT}", GRAY))
        print()

        for day in week_days:
            d           = datetime.strptime(day["date"], "%Y-%m-%d")
            date_str    = d.strftime("%a  %b %-d")
            celebrations = sorted(day.get("celebrations", []), key=lambda x: x.get("rank_num", 9))

            # Show the primary celebration (lowest rank_num = highest importance)
            primary = celebrations[0] if celebrations else None
            if not primary:
                continue

            rank   = _rank_label(primary["rank"])
            colour = primary.get("colour", "")
            title  = primary["title"]
            swatch = _colour_swatch(colour)

            # Additional saints on same day (commemorations etc.)
            extras = [
                c["title"] for c in celebrations[1:]
                if _is_saint(c["title"])
            ]

            rank_col = YELLOW if primary.get("rank_num", 9) <= 1.5 else (
                       CYAN   if primary.get("rank_num", 9) <= 2.5 else GRAY)

            line = f"  {_c(date_str, WHITE)}  ·  {_c(f'{rank:<22}', rank_col)}  {title}"
            swatch_pad = max(0, WIDTH - len(f"  {date_str}  ·  {rank:<22}  {title}") - 5)
            print(f"{line}  {swatch}")

            for extra in extras:
                name, role = _parse_saint(extra)
                role_str   = f", {role}" if role else ""
                print(_c(f"              + {name}{role_str}", GRAY))

        print()

    def show_footer(self):
        print(_c(HEAVY, YELLOW))
        print(_c("  Source: Liturgical Calendar API · calapi.inadiutorium.cz", GRAY))
        print(_c("  General Roman Calendar · Roman Rite", GRAY))
        print(_c(HEAVY, YELLOW))
        print()
