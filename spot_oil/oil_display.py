"""
Display and formatting module for get-oil
"""

from datetime import datetime, date, timedelta
from itertools import groupby

WIDTH = 68
HEAVY = "═" * WIDTH
LIGHT = "─" * WIDTH

# ANSI color codes
RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"
DIM    = "\033[2m"


def _trend(change):
    if change > 0:  return ("▲", GREEN)
    if change < 0:  return ("▼", RED)
    return              ("→", GRAY)


def _fmt_price(price, unit):
    if unit == "$/bbl":
        return f"{price:8.2f}"
    return f"{price:8.3f}"


def _fmt_change(change, unit):
    if unit == "$/bbl":
        sign = "+" if change >= 0 else ""
        return f"{sign}{change:.2f}"
    else:
        sign = "+" if change >= 0 else ""
        return f"{sign}{change:.3f}"


def _color(text, code):
    return f"{code}{text}{RESET}"


def _trading_days_ago(period_str):
    """Return the number of weekdays between period_str and today, or None on parse error."""
    try:
        data_date = datetime.strptime(period_str, "%Y-%m-%d").date()
    except ValueError:
        return None
    today = date.today()
    if data_date >= today:
        return 0
    count = 0
    d = data_date + timedelta(days=1)
    while d <= today:
        if d.weekday() < 5:  # Mon–Fri
            count += 1
        d += timedelta(days=1)
    return count


class OilDisplay:
    """
    Renders oil price data to the terminal.
    """

    def show_header(self):
        ts = datetime.now().strftime("%a %b %d, %Y  %H:%M")
        padding = WIDTH - len("  OIL & ENERGY SPOT PRICES") - len(ts)
        print()
        print(_color(HEAVY, YELLOW))
        print(_color(f"  OIL & ENERGY SPOT PRICES{' ' * padding}{ts}", YELLOW))
        print(_color(f"  Source: Yahoo Finance (15-min delayed)", GRAY))
        print(_color(HEAVY, YELLOW))

    def show_footer(self, latest_period=None):
        print()
        print(_color(HEAVY, YELLOW))
        if latest_period:
            staleness = _trading_days_ago(latest_period)
            if staleness is not None and staleness > 2:
                warn = f"  ⚠  Data is {staleness} trading days old — EIA publish delay"
                print(_color(warn, RED))
            print(_color(f"  Latest data: {latest_period}", GRAY))
        print(_color(f"  Prices are front-month futures (USD). Change vs. prior trading day.", GRAY))
        print(_color(HEAVY, YELLOW))
        print()

    def show_group_header(self, label):
        print()
        print(_color(f"  {label}", YELLOW + BOLD))
        print(_color(f"  {LIGHT}", GRAY))

    def show_commodity_row(self, name, sub, unit, price, change, pct):
        arrow, color = _trend(change)
        price_str  = _fmt_price(price, unit)
        change_str = _fmt_change(change, unit)
        pct_str    = f"({'+'  if pct >= 0 else ''}{pct:.2f}%)"

        label  = f"  {name:<22} {sub:<18}"
        price_part  = _color(f"$ {price_str.strip()}", WHITE)
        unit_part   = _color(f"  {unit}", GRAY)
        trend_part  = _color(f"  {arrow}  {change_str:<9} {pct_str}", color)

        print(f"{label}{price_part}{unit_part}{trend_part}")

    def show_no_data(self, name, sub):
        print(_color(f"  {name:<22} {sub:<18}  (no data available)", GRAY))

    def show_history_table(self, name, records, unit, days):
        """
        Print a multi-day price history table for one commodity.
        records is newest-first; we have days+1 entries so we can show a delta
        for every displayed row.
        """
        display = records[:days]

        print()
        print(_color(f"    {name} — {days}-Day History", CYAN))
        print(_color(f"    {'Date':<12}  {'Price':>10}  {'Change':>10}  {'% Chg':>9}", GRAY))
        print(_color(f"    {'─' * (WIDTH - 8)}", GRAY))

        for i, rec in enumerate(display):
            price  = float(rec["value"])
            period = rec["period"]

            if i + 1 < len(records):
                prev   = float(records[i + 1]["value"])
                delta  = price - prev
                pct    = (delta / prev * 100) if prev else 0
                arrow, color = _trend(delta)
                d_str = _fmt_change(delta, unit)
                p_str = f"{'+'  if pct >= 0 else ''}{pct:.2f}%"
                print(
                    f"    {period:<12}  {_fmt_price(price, unit):>10}"
                    + _color(f"  {d_str:>10}  {p_str:>9}  {arrow}", color)
                )
            else:
                # Oldest row — no prior record for delta
                print(_color(f"    {period:<12}  {_fmt_price(price, unit):>10}  {'—':>10}  {'—':>9}", GRAY))
