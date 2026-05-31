# 123Telugu Scraper

Scrapes photo gallery listings from [123telugu.com/category/gallery](https://www.123telugu.com/category/gallery/) and formats the URLs into grouped output ready for downloading.

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

## Options

| Command | What it does |
|---|---|
| `python main.py telugu123` | Scrape page 1 — new galleries only (uses checkpoint) |
| `python main.py telugu123 fullscrape` | Scrape all 199 pages + auto format |
| `python main.py telugu123 fullscrape 1 50` | Scrape pages 1–50 + auto format |
| `python main.py telugu123 fullformat` | Format only (no scrape) |
| `python main.py telugu123 download` | Download images from 123telugu-format.txt |
| `python main.py telugu123 1` | Scrape a single page |
| `python main.py telugu123 1 5 10` | Scrape specific pages |
| `python main.py telugu123 1-10` | Scrape a range of pages |
| `python main.py` | Interactive menu |

---

## 1. Daily Run — New Galleries Only

Reads the checkpoint, skips already-seen galleries, writes only new ones.
Use this for day-to-day updates.

```bash
python main.py telugu123
```

**Sample output:**
```
[123telugu] Checkpoint found.
  Last run : 2026-05-22 12:54:40
  Last URL : https://gallery.123telugu.com/.../Faria-Abdullah-022/...
[123telugu] Scraping page 1 ...
[123telugu] Page 1: 8 new galleries.
[123telugu] Skipped 12 already-seen item(s).
[123telugu] Checkpoint updated to: https://gallery.123telugu.com/.../NewGallery/...
[123telugu] Done. 8 new items written to output/telugu123/123telugu-galleries.txt
```

---

## 2. Full Scrape — All 199 Pages

Scrapes every page and automatically formats the results at the end.

```bash
python main.py telugu123 fullscrape
```

**Sample output:**
```
[123telugu] Full scrape: pages 1–199
[123telugu] Output → output/telugu123/123telugu-galleries.txt

[123telugu] Page 1/199 ... 20 galleries
[123telugu] Page 2/199 ... 20 galleries
[123telugu] Page 3/199 ... 18 galleries
...
[123telugu] Page 199/199 ... 15 galleries

[123telugu] Scrape complete.
  Pages scraped  : 199/199
  Total galleries: 3842
  Output file    : output/telugu123/123telugu-galleries.txt
[123telugu] Checkpoint updated to: https://gallery.123telugu.com/.../LatestGallery/...

[formatter] 3842 unique URLs grouped into 412 names.
[formatter] Output written to output/telugu123/123telugu-format.txt
```

---

## 3. Full Scrape — Custom Page Range

```bash
python main.py telugu123 fullscrape 1 50     # pages 1 to 50
python main.py telugu123 fullscrape 50 100   # pages 50 to 100
python main.py telugu123 fullscrape 100 199  # pages 100 to 199
```

---

## 4. Scrape Specific Pages

```bash
# Single page
python main.py telugu123 3

# Multiple specific pages
python main.py telugu123 1 5 10

# Range of pages
python main.py telugu123 1-10

# Mix (not supported — use range or list)
```

---

## 5. Format Only

Reads `123telugu-galleries.txt`, groups by person name, writes `123telugu-format.txt`.
Use this if you want to re-format without scraping again.

```bash
python main.py telugu123 fullformat
```

**Sample output:**
```
[formatter] 3842 unique URLs grouped into 412 names.
[formatter] Output written to output/telugu123/123telugu-format.txt
```

---

## 6. Resume After Interruption

If `fullscrape` is interrupted (Ctrl+C, network drop), just run it again.
It automatically resumes from the last completed page.

```bash
python main.py telugu123 fullscrape
```

```
[123telugu] Resuming from page 88 (last completed: page 87)
[123telugu] Page 88/199 ... 20 galleries
[123telugu] Page 89/199 ... 19 galleries
...
```

---

## 7. Interactive Menu

```bash
python main.py
```

```
==================================================
  Telugu Gallery Scraper
==================================================
  1. Scrape URLs    (selected pages → 123telugu-galleries.txt)
  2. Full scrape    (pages 1–199   → 123telugu-galleries.txt)
  3. Format URLs    (123telugu-galleries.txt → 123telugu-format.txt)
==================================================
Choose an option (1-3):
```

---

## Output Files

| File | Cleared each run? | Description |
|---|---|---|
| `123telugu-galleries.txt` | Yes | Raw scraped titles + URLs from last run |
| `123telugu-format.txt` | Yes (on format) | Grouped `--url` lines ready for downloader |
| `123telugu-checkpoint.txt` | No — updated | Last scraped URL + resume page number |
| `123telugu-history.txt` | No — appended | Log of every run |

---

## Output Format Examples

### 123telugu-galleries.txt

```
=== Page 1 ===

Latest Photos : Niharika Konidela
https://gallery.123telugu.com/content/slideshows/2026/5/Niharika-Konidela22/imgpages/image0.html

Photos : Glamourous Vaishnavi Chaitanya
https://gallery.123telugu.com/content/slideshows/2026/5/Vaishnavi-Chaitanya22/imgpages/image0.html

=== Page 2 ===

New Photos : Saanve Megghana
https://gallery.123telugu.com/content/slideshows/2026/5/Saanve-Megghana21/imgpages/image0.html
```

### 123telugu-format.txt

```
### Aishwarya-Rajesh (3 album(s))

--url "https://gallery.123telugu.com/content/slideshows/2026/5/Aishwarya-Rajesh-22/imgpages/" \
--url "https://gallery.123telugu.com/content/slideshows/2026/4/Aishwarya-Rajesh-21/imgpages/" \
--url "https://gallery.123telugu.com/content/slideshows/2026/3/Aishwarya-Rajesh-20/imgpages/"

### Niharika-Konidela (2 album(s))

--url "https://gallery.123telugu.com/content/slideshows/2026/5/Niharika-Konidela22/imgpages/" \
--url "https://gallery.123telugu.com/content/slideshows/2026/4/Niharika-Konidela21/imgpages/"
```

### 123telugu-history.txt

```
=== 2026-05-22 12:54:40 | incremental ===
Pages          : [1]
New galleries  : 15
Started from   : fresh run (no checkpoint)
Checkpoint set : https://gallery.123telugu.com/.../Faria-Abdullah-022/...

=== 2026-05-31 10:00:00 | full ===
Pages          : 1–199
New galleries  : 3842
Started from   : fresh start (pages 1–199)
Checkpoint set : https://gallery.123telugu.com/.../LatestGallery/...
```

---

## 8. Download Images

Downloads every gallery listed in `123telugu-format.txt` into `downloads/123telugu/<gallery-slug>/`.
Run `fullformat` first if you haven't already.

```bash
python main.py telugu123 download
```

**Sample output:**
```
[download] 20 person(s), 20 total album(s) to download.

[download] ══ Anu-Emmanuel (1 album(s)) ══

[download] Gallery : Anu-Emmanuel31
[download] URL     : https://gallery.123telugu.com/content/slideshows/2026/5/Anu-Emmanuel31/imgpages/
[download] 25 image pages found.
  [1/25] ✓ image1.jpg
  [2/25] ✓ image2.jpg
  ...
  [25/25] ✓ image25.jpg
[download] Done: 25/25 images → downloads/123telugu/Anu-Emmanuel31

[download] ══ Rukshar-Dhillon (1 album(s)) ══
...

[download] All done. 487 total images downloaded.
```

**Folder structure created:**
```
downloads/
  123telugu/
    Anu-Emmanuel31/
      image1.jpg
      image2.jpg
      ...
    Rukshar-Dhillon-31/
      image1.jpg
      ...
    Samyuktha-031/
      image1.jpg
      ...
```

Already-downloaded images are skipped on re-run — safe to interrupt and resume.

---

## Reset and Scrape Everything Fresh

```bash
rm output/telugu123/123telugu-checkpoint.txt
python main.py telugu123 fullscrape
```

---

## Typical Workflows

### First time setup
```bash
python main.py telugu123 fullscrape   # scrape all 199 pages + format
python main.py telugu123 download     # download all images
```

### Daily update
```bash
python main.py telugu123              # scrape + format new galleries
python main.py telugu123 download     # download only the new ones (skips existing)
```

### Missed a few days (new galleries may be on pages 2–3)
```bash
python main.py telugu123 1-3
python main.py telugu123 fullformat
python main.py telugu123 download
```

### Monthly full refresh
```bash
python main.py telugu123 fullscrape
python main.py telugu123 download
```
