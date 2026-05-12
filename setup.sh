#!/bin/bash
# setup.sh — create venvs and install dependencies for all currents apps

set -e

PYTHON=$(which python3)
ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo "  CURRENTS — setup"
echo "  Using Python: $PYTHON"
echo ""

setup_app() {
    local dir="$1"
    local packages="$2"
    local path="$ROOT/$dir"

    if [ ! -d "$path" ]; then
        echo "  ✗  $dir not found, skipping"
        return
    fi

    printf "  %-32s" "$dir"
    "$PYTHON" -m venv "$path/venv" --quiet
    "$path/venv/bin/pip" install $packages --quiet
    echo "✓"
}

setup_app "currents"                 ""
setup_app "get-news"                 "requests"
setup_app "get-hn"                   "requests"
setup_app "spot_oil"                 "requests beautifulsoup4 yfinance pandas peewee"
setup_app "get-stocks"               "requests beautifulsoup4 yfinance pandas peewee"
setup_app "get-fed"                  "requests"
setup_app "weather_checker"          "requests python-dateutil"
setup_app "get-apod"                 "requests"
setup_app "get-saint"                "requests beautifulsoup4 lxml"
setup_app "get-saints"               "requests beautifulsoup4 lxml"
setup_app "get-diocese"              "requests beautifulsoup4"
setup_app "get-catholic"             "requests"
setup_app "craigslist_rental_tracker" "requests beautifulsoup4 pandas matplotlib pillow"

echo ""
echo "  All done. Next: copy .env.example to .env and add your API keys."
echo "  Then run: ./currents/currents"
echo ""
