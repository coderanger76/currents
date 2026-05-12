"""
Configuration for get-news (NY Times API)
"""

NYT_BASE_URL = "https://api.nytimes.com/svc"

DEFAULT_SECTION = "home"
DEFAULT_LIMIT   = 12

# All available Top Stories sections
SECTIONS = [
    "home", "arts", "automobiles", "books", "business", "fashion",
    "food", "health", "insider", "magazine", "movies", "national",
    "nyregion", "obituaries", "opinion", "politics", "realestate",
    "science", "sports", "sundayreview", "technology", "theater",
    "travel", "upshot", "us", "world",
]

# Section → color code (ANSI) for the section label badge
SECTION_COLORS = {
    "politics":    "\033[91m",   # bright red
    "us":          "\033[91m",
    "national":    "\033[91m",
    "world":       "\033[94m",   # bright blue
    "technology":  "\033[96m",   # cyan
    "science":     "\033[96m",
    "health":      "\033[95m",   # magenta
    "business":    "\033[92m",   # green
    "arts":        "\033[93m",   # yellow
    "books":       "\033[93m",
    "movies":      "\033[93m",
    "theater":     "\033[93m",
    "sports":      "\033[92m",
    "opinion":     "\033[90m",   # dark gray
    "food":        "\033[33m",   # orange-ish
    "travel":      "\033[33m",
    "fashion":     "\033[35m",   # purple
    "obituaries":  "\033[90m",
}

DEFAULT_SECTION_COLOR = "\033[37m"  # white/light gray
