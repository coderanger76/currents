"""
Configuration and commodity definitions for get-oil
"""

# Default number of history days to show
DEFAULT_DAYS = 1

# Commodity definitions
COMMODITIES = [
    {
        "group":  "crude",
        "name":   "WTI Crude Oil",
        "sub":    "Cushing, OK",
        "ticker": "CL=F",
        "unit":   "$/bbl",
    },
    {
        "group":  "crude",
        "name":   "Brent Crude Oil",
        "sub":    "Europe",
        "ticker": "BZ=F",
        "unit":   "$/bbl",
    },
    {
        "group":  "refined",
        "name":   "RBOB Gasoline",
        "sub":    "NYMEX",
        "ticker": "RB=F",
        "unit":   "$/gal",
    },
    {
        "group":  "refined",
        "name":   "No. 2 Heating Oil",
        "sub":    "New York Harbor",
        "ticker": "HO=F",
        "unit":   "$/gal",
    },
    {
        "group":  "natgas",
        "name":   "Natural Gas",
        "sub":    "Henry Hub, LA",
        "ticker": "NG=F",
        "unit":   "$/MMBtu",
    },
]

GROUP_LABELS = {
    "crude":   "CRUDE OIL",
    "refined": "REFINED PRODUCTS",
    "natgas":  "NATURAL GAS",
}
