# Idlebrain Scraper

Scrapes all heroine gallery listings from [idlebrain.com/movie/photogallery/heroines.html](https://www.idlebrain.com/movie/photogallery/heroines.html), formats them into grouped output, and downloads images into `downloads/idlebrain/<gallery-slug>/`.

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

## Commands

| Command | What it does |
|---|---|
| `python main.py idlebrain` | Scrape heroines.html for new galleries + auto-format |
| `python main.py idlebrain format` | Format only (galleries.txt → format.txt) |
| `python main.py idlebrain download` | Download images from idlebrain-format.txt |
| `python main.py idlebrain daily` | Download images from idlebrain-daily.txt |
| `python main.py` | Interactive menu (options 5–8) |

---

## 1. Scrape — New Galleries Only

Fetches `heroines.html`, compares against the checkpoint, and appends only new gallery URLs to `idlebrain-galleries.txt`. Also auto-formats at the end.

```bash
python main.py idlebrain
```

**Sample output:**
```
[idlebrain] Fetching https://www.idlebrain.com/movie/photogallery/heroines.html ...
[idlebrain] Parsed 5842 total gallery entries from listing page.
[idlebrain] 12 new galleries written to output/idlebrain/idlebrain-galleries.txt
[formatter] 12 unique URLs grouped into 8 names.
[formatter] Output written to output/idlebrain/idlebrain-format.txt
[formatter] Cleared 12 formatted URLs from idlebrain-galleries.txt
```

Re-running after a previous scrape only picks up genuinely new albums added to the site since the last run.

---

## 2. Format Only

Groups `idlebrain-galleries.txt` by person name and writes `idlebrain-format.txt`.
Clears `idlebrain-galleries.txt` after formatting.

```bash
python main.py idlebrain format
```

**Sample output:**
```
[formatter] 5842 unique URLs grouped into 412 names.
[formatter] Output written to output/idlebrain/idlebrain-format.txt
[formatter] Cleared 5842 formatted URLs from idlebrain-galleries.txt
```

---

## 3. Download — From Format File

Downloads every gallery in `idlebrain-format.txt` to `downloads/idlebrain/<gallery-slug>/`.
After the run, fully downloaded galleries are removed from `format.txt`; failed/partial ones stay for retry.

```bash
python main.py idlebrain download
```

**Sample output:**
```
[download] 412 person(s), 5842 total album(s) to download.

[download] ══ Adah-Sharma (51 album(s)) ══

[download] Gallery : adahsharma
[download] URL     : https://www.idlebrain.com/movie/photogallery/adahsharma/index.html
[download] 25 image pages found.
  [1/25] ✓ adahsharma1.jpg
  [2/25] ✓ adahsharma2.jpg
  ...
  [25/25] ✓ adahsharma25.jpg
[download] Done: 25/25 images → downloads/idlebrain/adahsharma

[download] All galleries downloaded. idlebrain-format.txt cleared.
[download] All done. 124850 total images downloaded.
```

---

## 4. Daily Download — From Daily File

The quickest way to download a handful of specific galleries. Paste URLs (one per line) into `output/idlebrain/idlebrain-daily.txt`, then run:

```bash
python main.py idlebrain daily
```

**idlebrain-daily.txt** (before run):
```
https://www.idlebrain.com/movie/photogallery/anikhasurendran5/index.html
https://www.idlebrain.com/movie/photogallery/kajaltiwari/index.html
https://www.idlebrain.com/movie/photogallery/rashisingh26/index.html
```

**Sample output:**
```
[download] 3 URL(s) in idlebrain-daily.txt

[download] Gallery : anikhasurendran5
[download] URL     : https://www.idlebrain.com/movie/photogallery/anikhasurendran5/index.html
[download] 30 image pages found.
  [1/30] ✓ anikhasurendran5_1.jpg
  ...
[download] Done: 30/30 images → downloads/idlebrain/anikhasurendran5

[download] Gallery : kajaltiwari
...

[download] All done. 87 images downloaded. Daily file cleared (3 URL(s) moved to history).
```

After the run:
- `idlebrain-daily.txt` — cleared (or retains any failed URLs)
- `idlebrain-daily-history.txt` — latest run prepended at the top

**idlebrain-daily-history.txt** (after run):
```
=== 2026-05-31 15:39:34 ===
anikhasurendran5
kajaltiwari
rashisingh26

=== 2026-05-31 10:39:08 ===
someoldgallery
```

---

## Output Files

| File | Cleared? | Description |
|---|---|---|
| `idlebrain-galleries.txt` | Yes — after format | Raw scrape output: name + URL pairs |
| `idlebrain-format.txt` | Yes — after full download | Grouped `--url` lines ready for download |
| `idlebrain-checkpoint.txt` | No — grows over time | All gallery URLs ever scraped (prevents duplicates) |
| `idlebrain-daily.txt` | Yes — after daily download | Ad-hoc queue: paste URLs here, run daily command |
| `idlebrain-daily-history.txt` | No — prepended each run | Log of every daily run with timestamp and slugs |

---

## Output Format Examples

### idlebrain-galleries.txt

```
Adah Sharma
https://www.idlebrain.com/movie/photogallery/adahsharma/index.html

Adah Sharma
https://www.idlebrain.com/movie/photogallery/adahsharma1/index.html

Aadeen Khan
https://www.idlebrain.com/movie/photogallery/aadeenkhan/index.html
```

### idlebrain-format.txt

```
### Adah-Sharma (51 album(s))

--url "https://www.idlebrain.com/movie/photogallery/adahsharma/index.html" \
--url "https://www.idlebrain.com/movie/photogallery/adahsharma1/index.html" \
--url "https://www.idlebrain.com/movie/photogallery/adahsharma2/index.html"

### Aadeen-Khan (1 album(s))

--url "https://www.idlebrain.com/movie/photogallery/aadeenkhan/index.html"
```

### idlebrain-daily-history.txt

```
=== 2026-05-31 15:39:34 ===
anikhasurendran5
kajaltiwari
rashisingh26

=== 2026-05-28 09:15:00 ===
tamanna180
anushka143
```

---

## Download Folder Structure

```
downloads/
  idlebrain/
    adahsharma/
      adahsharma1.jpg
      adahsharma2.jpg
      ...
    adahsharma1/
      adahsharma1_1.jpg
      ...
    anikhasurendran5/
      anikhasurendran5_1.jpg
      ...
    kajaltiwari/
      ...
```

Each gallery URL produces one folder named after the slug extracted from the URL (the segment between `photogallery/` and `/index.html`).
Already-downloaded images are skipped — safe to interrupt and resume any command.

---

## Typical Workflows

### First time — download everything

```bash
python main.py idlebrain           # scrape all + format
python main.py idlebrain download  # download all
```

### Weekly — pick up new galleries

```bash
python main.py idlebrain           # scrape new + format
python main.py idlebrain download  # download new (existing images skipped)
```

### Daily — a few specific galleries

```bash
# 1. Paste gallery URLs into output/idlebrain/idlebrain-daily.txt
# 2. Run:
python main.py idlebrain daily
```

### Retry failed downloads

Just re-run the same command — failed galleries stay in their respective file:

```bash
python main.py idlebrain download  # retries format.txt failures
python main.py idlebrain daily     # retries daily.txt failures
```
