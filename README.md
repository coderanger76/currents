# Currents

A Bloomberg-style terminal information suite for macOS. One launcher, twelve modules — news, markets, weather, science, faith, and local data, all displayed in a consistent amber-on-black dashboard aesthetic.

> Built for daily use. Press a key, read, press any key to return.

---

## Screenshot

*(screenshots coming)*

---

## Modules

Navigate the dashboard with a single keypress. Press `Q` to quit.

### NEWS
| Key | Module | Description |
|-----|--------|-------------|
| `1` | **GET-NEWS** | NY Times top headlines via the Times API. Displays title, section, byline, and summary for the top stories. |
| `2` | **GET-HN** | Hacker News top stories. Shows rank, score, comment count, and domain for the front page. |

### MARKETS
| Key | Module | Description |
|-----|--------|-------------|
| `3` | **GET-OIL** | Energy spot prices — WTI crude, Brent crude, natural gas, and gasoline futures with day-over-day change. |
| `4` | **GET-STOCKS** | Global market indices — US, Europe, and Asia — with price, change, and percentage via Yahoo Finance. |
| `5` | **GET-FED** | Federal Reserve economic data via FRED — GDP, CPI, unemployment, federal funds rate, and more. |

### SCIENCE & WEATHER
| Key | Module | Description |
|-----|--------|-------------|
| `6` | **GET-WEATHER** | Current conditions and multi-day forecast via OpenWeatherMap. Temperature, humidity, wind, UV index. |
| `7` | **GET-APOD** | NASA Astronomy Picture of the Day with full title, explanation, and credit. |

### FAITH & LITURGY
| Key | Module | Description |
|-----|--------|-------------|
| `8` | **GET-SAINT** | Daily liturgical calendar — feast days, saint of the day, and liturgical season via API. |
| `9` | **GET-SAINTS** | Saint profiles scraped from Franciscan Media — biography, feast day, patronage, and reflection. |
| `D` | **GET-DIOCESE** | Randomly explores one of 183 US Catholic dioceses. Pulls bishop, statistics (Catholics, priests, parishes), history, and a best-effort crawl of the diocese's own website. Caches results in SQLite. Press `L` to reroll. |
| `C` | **GET-CATHOLIC** | Daily Catholic reading drawn from a curated Wikipedia pool — Doctors of the Church, Popes, Church Fathers, Ecumenical Councils, Marian Apparitions, and more. Same article all day (date-seeded), refreshes at midnight. Pool rebuilds weekly. Press `L` for a bonus read. |

### LOCAL
| Key | Module | Description |
|-----|--------|-------------|
| `0` | **GET-RENTALS** | Craigslist rental listing tracker. Pulls and parses rental alert emails from iCloud, stores listings in SQLite, and displays current inventory with price trends. |

---

## Requirements

- macOS (uses `termios`/`tty` for raw keypress handling)
- Python 3.10+ (tested on 3.14)
- [Homebrew](https://brew.sh/) for installing Python if needed

---

## Installation

**1. Clone the repo**

```bash
git clone https://github.com/coderanger76/currents.git
cd currents
```

**2. Run the setup script**

This creates a virtual environment and installs dependencies for each module:

```bash
chmod +x setup.sh
./setup.sh
```

**3. Set your API keys**

Copy the example env file and follow the links inside to get each free key:

```bash
cp .env.example .env
```

Then add your keys to `~/.zshrc` (or `~/.bash_profile`):

```bash
export NYT_API_KEY=your_key_here
export FRED_API_KEY=your_key_here
export NASA_API_KEY=your_key_here
export OPENWEATHER_API_KEY=your_key_here
```

Reload your shell: `source ~/.zshrc`

**4. Launch**

```bash
./currents/currents
```

---

## API Keys

Four modules require a free API key. The others (GET-HN, GET-OIL, GET-DIOCESE, GET-CATHOLIC, GET-SAINT, GET-SAINTS) need no key at all.

| Key | Service | Free tier |
|-----|---------|-----------|
| `NYT_API_KEY` | [NY Times Developer](https://developer.nytimes.com/get-started) | 500 req/day |
| `FRED_API_KEY` | [St. Louis Fed / FRED](https://fred.stlouisfed.org/docs/api/api_key.html) | Unlimited |
| `NASA_API_KEY` | [NASA APIs](https://api.nasa.gov/) | 1,000 req/day (`DEMO_KEY` works with lower limits) |
| `OPENWEATHER_API_KEY` | [OpenWeatherMap](https://openweathermap.org/api) | 1,000 req/day |

---

## How It Works

Each module is a self-contained directory with its own virtual environment and a shell launcher script. The `currents` launcher is a Python script that renders the dashboard menu and spawns the selected module as a subprocess — so each app runs independently and returns cleanly when you press any key.

```
currents/               ← launcher (main menu)
get-news/               ← NY Times module
get-hn/                 ← Hacker News module
get-stocks/             ← Markets module
spot_oil/               ← Oil prices module
get-fed/                ← Federal Reserve module
weather_checker/        ← Weather module
get-apod/               ← NASA module
get-saint/              ← Liturgical calendar module
get-saints/             ← Franciscan Media module
get-diocese/            ← US Diocese explorer module
get-catholic/           ← Catholic daily reading module
craigslist_rental_tracker/  ← Rental listings module
setup.sh                ← One-shot venv installer
.env.example            ← API key template
```

**GET-DIOCESE** maintains a SQLite database of all 183 US Catholic dioceses (Latin and Eastern rites), fetches bishop and statistical data from Wikipedia's structured infoboxes, and does a best-effort crawl of each diocese's official website for history and about text. The database self-corrects stale URLs on each visit.

**GET-CATHOLIC** bootstraps a reading pool from ten curated Wikipedia categories on first run, stores article titles in SQLite, and uses the date as a seed so the same article appears all day. The pool refreshes every seven days.

---

## Tech Stack

- **Python 3** — all modules
- **requests** — HTTP across all modules
- **BeautifulSoup4** — scraping (saints, diocese websites, oil prices)
- **yfinance** — stock and market data
- **SQLite** (stdlib `sqlite3`) — local caching for diocese, Catholic reading, and rentals
- **Wikipedia MediaWiki API** — diocese and Catholic reading data (no key required)
- **ANSI escape codes** — all terminal formatting, no third-party TUI library

---

## Notes

- All paths are relative, so the repo works from any directory on any machine.
- Virtual environments are gitignored — `setup.sh` recreates them after cloning.
- SQLite databases are gitignored — they're generated at runtime and are personal to your machine.
- The craigslist module requires an iCloud email account configured to receive Craigslist alerts. Copy `craigslist_rental_tracker/config.example.py` to `config.py` and fill in your details.

---

*Built on macOS. Inspired by Bloomberg Terminal aesthetics.*
