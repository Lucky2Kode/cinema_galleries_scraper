# Telugu Gallery Scraper

A Python web scraping tool that collects photo gallery listings from Telugu entertainment websites and formats the results for bulk downloading.

---

## What It Does

- Scrapes gallery titles and URLs from two Telugu websites
- Groups galleries by person/name
- Formats URLs ready for a download tool
- Tracks run history and resumes from where it left off

---

## Supported Sites

| Scraper | Website | Output |
|---|---|---|
| `telugu123` | 123telugu.com/category/gallery | Text file grouped by page |
| `telugucinema` | gallery.telugucinema.com | CSV with title, URL, thumbnail |

---

## Project Structure

```
main.py                        # entry point — CLI + interactive menu
base.py                        # shared HTTP session, retry, rate limiting
telugu123/
  scraper.py                   # 123telugu scraper + checkpoint logic
  formatter.py                 # groups and formats scraped URLs
telugucinema/
  scraper.py                   # telugucinema scraper → CSV
output/
  telugu123/
    123telugu-galleries.txt    # raw scrape output (cleared each run)
    123telugu-format.txt       # formatted --url lines (cleared each format)
    123telugu-checkpoint.txt   # last scraped URL + resume state
    123telugu-history.txt      # log of every run (never cleared)
```

---

## Setup

**Prerequisites:** Python 3.9+

### First time (do once)

```bash
# 1. Navigate to the project directory
cd cinema_galleries_scraper

# 2. Create a virtual environment
python3 -m venv .venv

# 3. Activate it
source .venv/bin/activate

# 4. Install dependencies
pip install requests beautifulsoup4 lxml
```

### Every session (after setup is done)

```bash
cd cinema_galleries_scraper
source .venv/bin/activate
```

---

## Quick Start

```bash
# Daily incremental scrape (picks up new galleries since last run)
python main.py telugu123

# Full scrape of all 199 pages + format
python main.py telugu123 fullscrape
python main.py telugu123 fullformat
```

---

## Output Files

| File | Description |
|---|---|
| `123telugu-galleries.txt` | Raw scraped titles + URLs, grouped by page |
| `123telugu-format.txt` | Formatted `--url` lines grouped by person name |
| `123telugu-checkpoint.txt` | Tracks last seen URL and last completed page |
| `123telugu-history.txt` | Appended log of every scrape run |

---

## Key Features

- **Checkpoint resume** — incremental scrape skips already-seen galleries
- **Full scrape resume** — if interrupted at page 87, next run continues from page 88
- **Run history** — every run is logged with timestamp, pages, and gallery count
- **Auto retry** — retries failed pages with exponential backoff (429, 500, 502, 503, 504)
- **Rate limiting** — 1 second delay between requests

---

See [RUN.md](RUN.md) for detailed usage instructions and examples.
