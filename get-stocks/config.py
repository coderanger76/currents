"""
Configuration and index definitions for get-stocks
"""

DEFAULT_DAYS = 1

INDICES = [
    # ── Americas ──────────────────────────────────────────────────────
    {
        "group":    "americas",
        "flag":     "🇺🇸",
        "name":     "S&P 500",
        "ticker":   "^GSPC",
        "timezone": "America/New_York",
        "open":     (9, 30),
        "close":    (16, 0),
    },
    {
        "group":    "americas",
        "flag":     "🇺🇸",
        "name":     "Dow Jones",
        "ticker":   "^DJI",
        "timezone": "America/New_York",
        "open":     (9, 30),
        "close":    (16, 0),
    },
    {
        "group":    "americas",
        "flag":     "🇺🇸",
        "name":     "NASDAQ",
        "ticker":   "^IXIC",
        "timezone": "America/New_York",
        "open":     (9, 30),
        "close":    (16, 0),
    },
    {
        "group":    "americas",
        "flag":     "🇨🇦",
        "name":     "TSX Composite",
        "ticker":   "^GSPTSE",
        "timezone": "America/Toronto",
        "open":     (9, 30),
        "close":    (16, 0),
    },
    {
        "group":    "americas",
        "flag":     "🇧🇷",
        "name":     "Bovespa",
        "ticker":   "^BVSP",
        "timezone": "America/Sao_Paulo",
        "open":     (10, 0),
        "close":    (17, 30),
    },
    # ── Europe ────────────────────────────────────────────────────────
    {
        "group":    "europe",
        "flag":     "🇬🇧",
        "name":     "FTSE 100",
        "ticker":   "^FTSE",
        "timezone": "Europe/London",
        "open":     (8, 0),
        "close":    (16, 30),
    },
    {
        "group":    "europe",
        "flag":     "🇩🇪",
        "name":     "DAX",
        "ticker":   "^GDAXI",
        "timezone": "Europe/Berlin",
        "open":     (9, 0),
        "close":    (17, 30),
    },
    {
        "group":    "europe",
        "flag":     "🇫🇷",
        "name":     "CAC 40",
        "ticker":   "^FCHI",
        "timezone": "Europe/Paris",
        "open":     (9, 0),
        "close":    (17, 30),
    },
    {
        "group":    "europe",
        "flag":     "🇪🇺",
        "name":     "Euro Stoxx 50",
        "ticker":   "^STOXX50E",
        "timezone": "Europe/Berlin",
        "open":     (9, 0),
        "close":    (17, 30),
    },
    # ── Asia-Pacific ──────────────────────────────────────────────────
    {
        "group":    "apac",
        "flag":     "🇯🇵",
        "name":     "Nikkei 225",
        "ticker":   "^N225",
        "timezone": "Asia/Tokyo",
        "open":     (9, 0),
        "close":    (15, 30),
    },
    {
        "group":    "apac",
        "flag":     "🇭🇰",
        "name":     "Hang Seng",
        "ticker":   "^HSI",
        "timezone": "Asia/Hong_Kong",
        "open":     (9, 30),
        "close":    (16, 0),
    },
    {
        "group":    "apac",
        "flag":     "🇨🇳",
        "name":     "Shanghai Comp.",
        "ticker":   "000001.SS",
        "timezone": "Asia/Shanghai",
        "open":     (9, 30),
        "close":    (15, 0),
    },
    {
        "group":    "apac",
        "flag":     "🇦🇺",
        "name":     "ASX 200",
        "ticker":   "^AXJO",
        "timezone": "Australia/Sydney",
        "open":     (10, 0),
        "close":    (16, 0),
    },
    {
        "group":    "apac",
        "flag":     "🇮🇳",
        "name":     "BSE Sensex",
        "ticker":   "^BSESN",
        "timezone": "Asia/Kolkata",
        "open":     (9, 15),
        "close":    (15, 30),
    },
]

GROUP_LABELS = {
    "americas": "AMERICAS",
    "europe":   "EUROPE",
    "apac":     "ASIA-PACIFIC",
}
