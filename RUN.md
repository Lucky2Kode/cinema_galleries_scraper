# How to Run

## 1. Setup

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

## 2. Interactive Menu

The easiest way to run — no need to remember commands:

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
  4. Download       (123telugu-format.txt → downloads/123telugu/)
==================================================
Choose an option (1-4):
```

---

## 3. Telugu123 Scraper

### Daily run — pick up new galleries only

Reads the checkpoint, skips already-seen galleries, writes only new ones.

```bash
python main.py telugu123
```

```
[123telugu] Checkpoint found.
  Last run : 2026-05-22 12:54:40
  Last URL : https://gallery.123telugu.com/.../Faria-Abdullah-022/...
[123telugu] Scraping page 1 ...
[123telugu] Page 1: 8 new galleries.
[123telugu] Checkpoint updated to: https://gallery.123telugu.com/.../NewGallery/...
[123telugu] Done. 8 new items written to output/telugu123/123telugu-galleries.txt
```

---

### Scrape specific pages

```bash
# Single page
python main.py telugu123 3

# Multiple specific pages
python main.py telugu123 1 5 10

# A range of pages
python main.py telugu123 1-10
```

---

### Full scrape — all 199 pages

Clears `123telugu-galleries.txt` and scrapes everything from page 1 to 199.
Takes around 10 minutes.

```bash
python main.py telugu123 fullscrape
```

```
[123telugu] Full scrape: pages 1–199
[123telugu] Output → output/telugu123/123telugu-galleries.txt

[123telugu] Page 1/199 ... 20 galleries
[123telugu] Page 2/199 ... 20 galleries
[123telugu] Page 3/199 ... 18 galleries
...
[123telugu] Scrape complete.
  Pages scraped  : 199/199
  Total galleries: 3842
  Output file    : output/telugu123/123telugu-galleries.txt
[123telugu] Checkpoint updated to: https://gallery.123telugu.com/.../LatestGallery/...
```

Custom page range:

```bash
python main.py telugu123 fullscrape 1 50    # pages 1 to 50
python main.py telugu123 fullscrape 50 100  # pages 50 to 100
```

---

### Resume after interruption

If `fullscrape` is interrupted (Ctrl+C, network drop, etc.), just run it again — it automatically resumes from the last completed page:

```bash
python main.py telugu123 fullscrape
```

```
[123telugu] Resuming from page 88 (last completed: page 87)
[123telugu] Page 88/199 ... 20 galleries
...
```

---

### Format the scraped URLs

Reads `123telugu-galleries.txt`, groups by person name, writes `123telugu-format.txt`.
Run this after every scrape.

```bash
python main.py telugu123 fullformat
```

```
[formatter] 3842 unique URLs grouped into 412 names.
[formatter] Output written to output/telugu123/123telugu-format.txt
```

**Output format (`123telugu-format.txt`):**

```
### Aishwarya-Rajesh (3 album(s))

--url "https://gallery.123telugu.com/content/slideshows/2026/5/Aishwarya-Rajesh-22/imgpages/" \
--url "https://gallery.123telugu.com/content/slideshows/2026/4/Aishwarya-Rajesh-21/imgpages/" \
--url "https://gallery.123telugu.com/content/slideshows/2026/3/Aishwarya-Rajesh-20/imgpages/"

### Niharika-Konidela (2 album(s))

--url "https://gallery.123telugu.com/content/slideshows/2026/5/Niharika-Konidela22/imgpages/" \
--url "https://gallery.123telugu.com/content/slideshows/2026/4/Niharika-Konidela21/imgpages/"
```

---

### Download images

Reads `123telugu-format.txt` and downloads every gallery to `downloads/123telugu/<gallery-slug>/`.
Already-downloaded images are skipped — safe to interrupt and resume.

```bash
python main.py telugu123 download
```

```
[download] 20 person(s), 20 total album(s) to download.

[download] ══ Anu-Emmanuel (1 album(s)) ══

[download] Gallery : Anu-Emmanuel31
[download] URL     : https://gallery.123telugu.com/content/slideshows/2026/5/Anu-Emmanuel31/imgpages/
[download] 25 image pages found.
  [1/25] ✓ image1.jpg
  [2/25] ✓ image2.jpg
  ...
[download] Done: 25/25 images → downloads/123telugu/Anu-Emmanuel31

[download] All done. 487 total images downloaded.
```

**Folder structure:**
```
downloads/
  123telugu/
    Anu-Emmanuel31/
    Rukshar-Dhillon-31/
    Samyuktha-031/
    ...
```

---

### Full workflow (first time or monthly refresh)

```bash
# Step 1 — scrape all pages + format
python main.py telugu123 fullscrape

# Step 2 — download images
python main.py telugu123 download
```

### Daily workflow (pick up new galleries)

```bash
# Picks up only new galleries since last run
python main.py telugu123

# Download the new ones (existing images are skipped)
python main.py telugu123 download
```

---

## 4. TeluguCinema Scraper

Scrapes home, actress, and actor gallery categories. Saves to a CSV file.

```bash
python main.py telugucinema
```

```
[telugucinema] Scraping category 'home' ...
[telugucinema] Found 24 galleries in 'home'
[telugucinema] Scraping category 'actress' ...
[telugucinema] Found 18 galleries in 'actress'
[telugucinema] Scraping category 'actor' ...
[telugucinema] Found 12 galleries in 'actor'
[telugucinema] Done. 54 total galleries saved to output/telugucinema/galleries.csv
```

Output CSV columns: `category`, `title`, `url`, `thumbnail`

---

## 5. Output Files Explained

| File | Cleared each run? | Description |
|---|---|---|
| `123telugu-galleries.txt` | Yes | Raw scraped titles + URLs from the last run |
| `123telugu-format.txt` | Yes (on fullformat) | Grouped `--url` lines ready for downloader |
| `123telugu-checkpoint.txt` | No — updated | Last scraped URL + resume page number |
| `123telugu-history.txt` | No — appended | Log of every run with timestamp and count |

---

## 6. History Log

Every run appends an entry to `123telugu-history.txt`:

```
=== 2026-05-31 10:00:00 | incremental ===
Pages          : [1]
New galleries  : 8
Started from   : https://gallery.123telugu.com/.../Faria-Abdullah-022/... (2026-05-22 12:54:40)
Checkpoint set : https://gallery.123telugu.com/.../NewGallery/...

=== 2026-05-31 10:30:00 | full ===
Pages          : 1–199
New galleries  : 3842
Started from   : fresh start (pages 1–199)
Checkpoint set : https://gallery.123telugu.com/.../LatestGallery/...
```

---

## 7. Reset checkpoint (scrape everything fresh)

```bash
rm output/telugu123/123telugu-checkpoint.txt
python main.py telugu123 fullscrape
```
