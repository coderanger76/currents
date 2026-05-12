"""
Display and formatting module for get-stocks
"""

from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

WIDTH = 88
HEAVY = "═" * WIDTH
LIGHT = "─" * WIDTH

# ANSI color codes
RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
PACIFIC_TZ    = ZoneInfo("America/Los_Angeles")


def _color(text, code):
    return f"{code}{text}{RESET}"


def _trend(change):
    if change > 0:  return ("▲", GREEN)
    if change < 0:  return ("▼", RED)
    return              ("→", GRAY)


def _fmt_price(price):
    return f"{price:>12,.2f}"


def _fmt_change(change):
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:,.2f}"


def _pacific_str(dt):
    """Convert an aware datetime to a Pacific time string like '6:30 AM PDT'."""
    p    = dt.astimezone(PACIFIC_TZ)
    h12  = p.hour % 12 or 12
    ampm = "AM" if p.hour < 12 else "PM"
    return f"{h12}:{p.minute:02d} {ampm} {p.strftime('%Z')}"


def _market_status(index):
    """
    Return (is_open: bool, status_str: str) for the given index.
    Open/close times are always displayed in Pacific time.
    Does not account for local public holidays.
    """
    tz      = ZoneInfo(index["timezone"])
    now     = datetime.now(tz)
    weekday = now.weekday()
    t_now   = now.time().replace(tzinfo=None)
    open_t  = time(index["open"][0],  index["open"][1])
    close_t = time(index["close"][0], index["close"][1])

    # Build aware datetimes for today's open/close in the market's local timezone
    today    = now.date()
    open_dt  = datetime(today.year, today.month, today.day,
                        index["open"][0],  index["open"][1],  tzinfo=tz)
    close_dt = datetime(today.year, today.month, today.day,
                        index["close"][0], index["close"][1], tzinfo=tz)

    open_pac  = _pacific_str(open_dt)
    close_pac = _pacific_str(close_dt)

    def next_open_pac():
        """Pacific-time string for the next trading day's open."""
        days_ahead = 3 if weekday == 4 else 1   # Fri → +3 days = Mon
        return _pacific_str(open_dt + timedelta(days=days_ahead))

    def next_day_label():
        return "Mon" if weekday == 4 else WEEKDAY_NAMES[weekday + 1]

    if weekday >= 5:                # weekend
        days_ahead = (7 - weekday) % 7 or 7
        mon_open   = _pacific_str(open_dt + timedelta(days=days_ahead))
        return False, f"opens Mon {mon_open}"

    if t_now < open_t:              # before open (same day)
        return False, f"opens {open_pac}"

    if t_now < close_t:             # trading hours
        return True, f"closes {close_pac}"

    return False, f"opens {next_day_label()} {next_open_pac()}"  # after close


class StockDisplay:

    def show_header(self):
        ts = datetime.now().strftime("%a %b %d, %Y  %H:%M")
        padding = WIDTH - len("  GLOBAL STOCK INDICES") - len(ts)
        print()
        print(_color(HEAVY, YELLOW))
        print(_color(f"  GLOBAL STOCK INDICES{' ' * padding}{ts}", YELLOW))
        print(_color(f"  Source: Yahoo Finance (15-min delayed during market hours)", GRAY))
        print(_color(HEAVY, YELLOW))

    def show_footer(self):
        print()
        print(_color(HEAVY, YELLOW))
        print(_color(
            "  Index values are prior close when market is closed; "
            "current when open.", GRAY
        ))
        print(_color(
            "  Market hours are approximate and do not account for local holidays.", GRAY
        ))
        print(_color(HEAVY, YELLOW))
        print()

    def show_group_header(self, label):
        print()
        print(_color(f"  {label}", YELLOW + BOLD))
        print(_color(f"  {LIGHT}", GRAY))

    def show_no_data(self, flag, name):
        print(_color(f"  {flag} {name:<13}  (no data)", GRAY))

    def show_index_row(self, index, records):
        price  = float(records[0]["value"])
        prev   = float(records[1]["value"]) if len(records) > 1 else price
        change = price - prev
        pct    = (change / prev * 100) if prev else 0

        arrow, color = _trend(change)
        price_str  = _fmt_price(price)
        change_str = _fmt_change(change)
        pct_str    = f"({'+'  if pct >= 0 else ''}{pct:.2f}%)"

        is_open, status_str = _market_status(index)
        dot        = "🟢" if is_open else "🔴"
        status_col = GREEN if is_open else GRAY

        flag = index["flag"]
        name = index["name"]

        label      = f"  {flag} {name:<13}"
        price_part = _color(price_str, WHITE)
        trend_part = _color(f"   {arrow}  {change_str:>10}  {pct_str:>9}", color)
        stat_part  = _color(f"   {dot} {status_str}", status_col)

        print(f"{label}{price_part}{trend_part}{stat_part}")

    def show_history_table(self, index, records):
        days    = len(records) - 1   # records has days+1 entries
        display = records[:days]

        print()
        print(_color(f"    {index['flag']} {index['name']} — {days}-Day History", GRAY + BOLD))
        print(_color(f"    {'Date':<12}  {'Close':>12}  {'Change':>10}  {'% Chg':>9}", GRAY))
        print(_color(f"    {'─' * (WIDTH - 8)}", GRAY))

        for i, rec in enumerate(display):
            price  = float(rec["value"])
            period = rec["period"]

            if i + 1 < len(records):
                prev   = float(records[i + 1]["value"])
                delta  = price - prev
                pct    = (delta / prev * 100) if prev else 0
                arrow, clr = _trend(delta)
                d_str  = _fmt_change(delta)
                p_str  = f"{'+'  if pct >= 0 else ''}{pct:.2f}%"
                print(
                    f"    {period:<12}  {_fmt_price(price)}"
                    + _color(f"  {d_str:>10}  {p_str:>9}  {arrow}", clr)
                )
            else:
                print(_color(
                    f"    {period:<12}  {_fmt_price(price)}  {'—':>10}  {'—':>9}", GRAY
                ))
