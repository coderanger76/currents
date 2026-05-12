"""
Display and formatting module for get-fed.
Renders Federal Reserve / FRED economic data beautifully in the terminal.
"""

from datetime import datetime, date

WIDTH = 72
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


def _c(text, code):
    return f"{code}{text}{RESET}"


def _trend(value):
    """Return (arrow, color) for a numeric change."""
    if value > 0:
        return "▲", GREEN
    if value < 0:
        return "▼", RED
    return "→", GRAY


def _fmt_date(date_str):
    """
    Format a YYYY-MM-DD date string into a short human-readable label.
    Examples: '2026-03-22' -> 'Mar 22', '2026-02-01' -> 'Feb 2026'
    If the year differs from today's year, always show year.
    If it's the same month+year and day is 1 (monthly series), show month+year.
    """
    if not date_str:
        return ""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = date.today()
        if d.day == 1:
            # Monthly or quarterly — show "Mon YYYY"
            return d.strftime("%b %Y")
        if d.year != today.year:
            return d.strftime("%b %-d, %Y")
        return d.strftime("%b %-d")
    except ValueError:
        return date_str


def _fmt_quarter(date_str):
    """Convert a YYYY-MM-DD to a quarter label like 'Q4 2025'."""
    if not date_str:
        return ""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        q = (d.month - 1) // 3 + 1
        return f"Q{q} {d.year}"
    except ValueError:
        return date_str


def _latest_valid(observations):
    """Return the first observation whose value is not '.' ."""
    for obs in (observations or []):
        if obs.get("value", ".") != ".":
            return obs
    return None


def _prev_valid(observations):
    """Return the second non-'.' observation (for period-over-period change)."""
    found = 0
    for obs in (observations or []):
        if obs.get("value", ".") != ".":
            found += 1
            if found == 2:
                return obs
    return None


class FedDisplay:

    # ── Header / Footer ────────────────────────────────────────────────────

    def show_header(self, target_date=None):
        if target_date is None:
            target_date = date.today()
        date_str = target_date.strftime("%a %b %-d, %Y")
        title    = "FEDERAL RESERVE  ECONOMIC DATA"
        padding  = WIDTH - len(f"  {title}") - len(date_str)
        print()
        print(_c(HEAVY, YELLOW))
        print(_c(f"  {title}{' ' * max(padding, 1)}{date_str}", YELLOW))
        print(_c(f"  Source: Federal Reserve Bank of St. Louis · FRED API", GRAY))
        print(_c(HEAVY, YELLOW))

    def show_footer(self):
        print()
        print(_c(HEAVY, YELLOW))
        print(_c(
            "  Source: Federal Reserve Bank of St. Louis · FRED API",
            GRAY,
        ))
        print(_c(
            "  https://fred.stlouisfed.org  ·  Data may lag by 1–5 days",
            GRAY,
        ))
        print(_c(HEAVY, YELLOW))
        print()

    # ── Group header ───────────────────────────────────────────────────────

    def show_group_header(self, label):
        print()
        print(_c(f"  {label}", YELLOW + BOLD))
        print(_c(f"  {LIGHT}", GRAY))

    # ── Row helpers ────────────────────────────────────────────────────────

    def _row(self, label, value_str, date_tag, change_str=""):
        """
        Print one data row.

        Layout (total WIDTH = 72):
          col 0-1:   "  " (indent)
          col 2-29:  label (28 chars)
          col 30-49: value (20 chars, right-aligned within its section)
          change_str: optional trend indicator
          date_tag:  gray, right side
        """
        # We assemble the printable (non-ANSI) widths manually so alignment
        # is correct regardless of how many invisible ANSI bytes are present.
        label_part  = f"  {label:<28}"
        value_part  = f"{value_str}"
        change_part = f"  {change_str}" if change_str else ""

        # Right-align the date tag to fill WIDTH
        # Measure visible lengths
        visible_len = len(label_part) + len(value_str) + (2 + len(change_str) if change_str else 0)
        date_visible = len(date_tag)
        gap = WIDTH - visible_len - date_visible
        gap = max(gap, 2)

        print(f"{label_part}{value_part}{change_part}{' ' * gap}{_c(date_tag, GRAY)}")

    # ── Section renderers ──────────────────────────────────────────────────

    def show_monetary_policy(self, data):
        self.show_group_header("MONETARY POLICY")

        # ── Fed Funds Target Range ─────────────────────────────────────────
        lo_obs = _latest_valid(data.get("DFEDTARL"))
        hi_obs = _latest_valid(data.get("DFEDTARU"))
        if lo_obs and hi_obs:
            lo  = float(lo_obs["value"])
            hi  = float(hi_obs["value"])
            val = _c(f"{lo:.2f}% – {hi:.2f}%", WHITE)
            self._row("Fed Funds Target", val, _fmt_date(lo_obs["date"]))
        else:
            self._row("Fed Funds Target", _c("(no data)", GRAY), "")

        # ── Effective Fed Funds Rate ───────────────────────────────────────
        obs  = _latest_valid(data.get("FEDFUNDS"))
        prev = _prev_valid(data.get("FEDFUNDS"))
        if obs:
            v       = float(obs["value"])
            val_str = _c(f"{v:.2f}%", WHITE)
            chg_str = ""
            if prev:
                delta     = v - float(prev["value"])
                arrow, clr = _trend(delta)
                sign       = "+" if delta >= 0 else ""
                chg_str    = _c(f"{arrow} {sign}{delta:.2f}%", clr)
            self._row("Effective Fed Funds", val_str, _fmt_date(obs["date"]), chg_str)
        else:
            self._row("Effective Fed Funds", _c("(no data)", GRAY), "")

        # ── Treasuries ─────────────────────────────────────────────────────
        treasury_specs = [
            ("DGS2",  "2-Year Treasury"),
            ("DGS10", "10-Year Treasury"),
            ("DGS30", "30-Year Treasury"),
        ]
        treasury_values = {}
        for sid, label in treasury_specs:
            obs  = _latest_valid(data.get(sid))
            prev = _prev_valid(data.get(sid))
            if obs:
                v       = float(obs["value"])
                treasury_values[sid] = v
                val_str = _c(f"{v:.2f}%", WHITE)
                chg_str = ""
                if prev:
                    delta      = v - float(prev["value"])
                    arrow, clr = _trend(delta)
                    sign       = "+" if delta >= 0 else ""
                    chg_str    = _c(f"{arrow} {sign}{delta:.2f}%", clr)
                self._row(label, val_str, _fmt_date(obs["date"]), chg_str)
            else:
                self._row(label, _c("(no data)", GRAY), "")

        # ── 10Y–2Y Yield Curve Spread ──────────────────────────────────────
        if "DGS10" in treasury_values and "DGS2" in treasury_values:
            spread = treasury_values["DGS10"] - treasury_values["DGS2"]
            sign   = "+" if spread >= 0 else ""
            # Green = normal (positive), Red = inverted (negative)
            clr    = GREEN if spread >= 0 else RED
            val_str  = _c(f"{sign}{spread:.2f}%", clr)
            note_str = _c("(yield curve spread)", GRAY)
            self._row("10Y–2Y Spread", val_str, "calculated", note_str)

        # ── 30-Year Fixed Mortgage ─────────────────────────────────────────
        obs  = _latest_valid(data.get("MORTGAGE30US"))
        prev = _prev_valid(data.get("MORTGAGE30US"))
        if obs:
            v       = float(obs["value"])
            val_str = _c(f"{v:.2f}%", WHITE)
            chg_str = ""
            if prev:
                delta      = v - float(prev["value"])
                arrow, clr = _trend(delta)
                sign       = "+" if delta >= 0 else ""
                chg_str    = _c(f"{arrow} {sign}{delta:.2f}%", clr)
            self._row("30-Yr Fixed Mortgage", val_str, _fmt_date(obs["date"]), chg_str)
        else:
            self._row("30-Yr Fixed Mortgage", _c("(no data)", GRAY), "")

    def show_inflation(self, data):
        self.show_group_header("INFLATION")

        inflation_specs = [
            ("CPIAUCSL",  "CPI (All Items)"),
            ("CPILFESL",  "Core CPI ex Food/Energy"),
            ("PCEPI",     "PCE Price Index"),
        ]

        for sid, label in inflation_specs:
            observations = data.get(sid) or []
            valid = [o for o in observations if o.get("value", ".") != "."]

            if len(valid) < 13:
                self._row(label, _c("(insufficient data)", GRAY), "")
                continue

            latest   = valid[0]
            prior_12 = valid[12]
            prior_1  = valid[1]

            v_now   = float(latest["value"])
            v_then  = float(prior_12["value"])
            v_prev  = float(prior_1["value"])

            yoy     = (v_now - v_then)  / v_then  * 100
            mom     = (v_now - v_prev)  / v_prev  * 100

            sign_yoy = "+" if yoy >= 0 else ""
            # YoY is shown as the primary value
            val_str  = _c(f"{sign_yoy}{yoy:.1f}% Y/Y", WHITE)

            # MoM as the change indicator in percentage points
            sign_mom  = "+" if mom >= 0 else ""
            arrow, clr = _trend(mom)
            chg_str    = _c(f"{arrow} {sign_mom}{mom:.2f}pp mom", clr)

            self._row(label, val_str, _fmt_date(latest["date"]), chg_str)

    def show_labor(self, data):
        self.show_group_header("LABOR MARKET")

        # ── Unemployment Rate ──────────────────────────────────────────────
        obs  = _latest_valid(data.get("UNRATE"))
        prev = _prev_valid(data.get("UNRATE"))
        if obs:
            v       = float(obs["value"])
            val_str = _c(f"{v:.1f}%", WHITE)
            chg_str = ""
            if prev:
                delta      = v - float(prev["value"])
                arrow, clr = _trend(delta)
                sign       = "+" if delta >= 0 else ""
                chg_str    = _c(f"{arrow} {sign}{delta:.1f}pp", clr)
            self._row("Unemployment Rate", val_str, _fmt_date(obs["date"]), chg_str)
        else:
            self._row("Unemployment Rate", _c("(no data)", GRAY), "")

        # ── Initial Jobless Claims ─────────────────────────────────────────
        obs  = _latest_valid(data.get("ICSA"))
        prev = _prev_valid(data.get("ICSA"))
        if obs:
            v       = float(obs["value"]) / 1000
            val_str = _c(f"{v:.0f}k/wk", WHITE)
            chg_str = ""
            if prev:
                pv         = float(prev["value"]) / 1000
                delta      = v - pv
                arrow, clr = _trend(delta)
                sign       = "+" if delta >= 0 else ""
                chg_str    = _c(f"{arrow} {sign}{delta:.0f}k", clr)
            self._row("Initial Jobless Claims", val_str, _fmt_date(obs["date"]), chg_str)
        else:
            self._row("Initial Jobless Claims", _c("(no data)", GRAY), "")

    def show_money_output(self, data):
        self.show_group_header("MONEY & OUTPUT")

        # ── M2 Money Supply ────────────────────────────────────────────────
        observations = data.get("M2SL") or []
        valid = [o for o in observations if o.get("value", ".") != "."]
        if valid:
            latest = valid[0]
            v      = float(latest["value"])     # billions
            t      = v / 1_000                  # trillions
            val_str = _c(f"${t:.1f}T", WHITE)
            chg_str = ""
            if len(valid) >= 13:
                # YoY growth
                v_then = float(valid[12]["value"])
                yoy    = (v - v_then) / v_then * 100
                arrow, clr = _trend(yoy)
                sign       = "+" if yoy >= 0 else ""
                chg_str    = _c(f"{arrow} {sign}{yoy:.1f}% Y/Y", clr)
            self._row("M2 Money Supply", val_str, _fmt_date(latest["date"]), chg_str)
        else:
            self._row("M2 Money Supply", _c("(no data)", GRAY), "")

        # ── Real GDP Growth Rate ───────────────────────────────────────────
        obs  = _latest_valid(data.get("A191RL1Q225SBEA"))
        prev = _prev_valid(data.get("A191RL1Q225SBEA"))
        if obs:
            v       = float(obs["value"])
            sign    = "+" if v >= 0 else ""
            val_str = _c(f"{sign}{v:.1f}% ann.", WHITE)
            chg_str = ""
            if prev:
                pv         = float(prev["value"])
                delta      = v - pv
                arrow, clr = _trend(delta)
                dsign      = "+" if delta >= 0 else ""
                chg_str    = _c(f"{arrow} {dsign}{delta:.1f}pp prior qtr", clr)
            self._row("Real GDP Growth", val_str, _fmt_quarter(obs["date"]), chg_str)
        else:
            self._row("Real GDP Growth", _c("(no data)", GRAY), "")
