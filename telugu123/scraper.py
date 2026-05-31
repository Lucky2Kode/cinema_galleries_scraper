"""
Scraper for https://www.123telugu.com/category/gallery/

Collects each gallery card title + URL and writes results to a text file
grouped by page number. Both incremental and full scrapes write to
123telugu-galleries.txt.

Checkpoint: the last scraped URL is saved to checkpoint.txt.
On the next run, all items up to and including that URL are skipped.

Usage (via main.py):
    python main.py telugu123            # current page only (page 1)
    python main.py telugu123 1          # page 1 only
    python main.py telugu123 1 3 5      # pages 1, 3 and 5
    python main.py telugu123 1-10       # pages 1 through 10
"""

import os
import time
from datetime import datetime
from lxml import html as lxml_html
from base import BaseScraper

BASE_URL = "https://www.123telugu.com/category/gallery/"
FULL_OUTPUT_FILE = os.path.join("output", "telugu123", "123telugu-galleries.txt")
CHECKPOINT_FILE = os.path.join("output", "telugu123", "123telugu-checkpoint.txt")
HISTORY_FILE = os.path.join("output", "telugu123", "123telugu-history.txt")

# Title + link lives in: div.pcsl-title > a
TITLE_LINK_XPATH = '//div[contains(@class,"pcsl-title")]//a[contains(@href,"gallery.123telugu.com")]'


def _page_url(page: int) -> str:
    return BASE_URL if page == 1 else f"{BASE_URL}page/{page}/"


def _load_checkpoint() -> tuple[str | None, str | None, int | None]:
    """Return (last_url, last_run_datetime, last_page) from checkpoint."""
    if not os.path.exists(CHECKPOINT_FILE):
        return None, None, None
    lines = open(CHECKPOINT_FILE, encoding="utf-8").read().splitlines()
    url = lines[0].strip() if len(lines) > 0 else None
    ran_at = lines[1].strip() if len(lines) > 1 else None
    last_page = None
    for line in lines[2:]:
        if line.startswith("last_page:"):
            try:
                last_page = int(line.split(":", 1)[1])
            except ValueError:
                pass
    return (url or None), (ran_at or None), last_page


def _save_checkpoint(url: str):
    """Save the latest gallery URL. Clears any in-progress page marker."""
    os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
    ran_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(f"{url}\n{ran_at}\n")


def _save_checkpoint_url_only(url: str):
    """Update the checkpoint URL and timestamp but keep the last_page resume marker."""
    os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
    lines = []
    if os.path.exists(CHECKPOINT_FILE):
        lines = open(CHECKPOINT_FILE, encoding="utf-8").read().splitlines()
    ran_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Preserve any last_page line
    last_page_line = next((l for l in lines if l.startswith("last_page:")), None)
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(f"{url}\n{ran_at}\n")
        if last_page_line:
            f.write(f"{last_page_line}\n")


def _save_progress_page(page: int):
    """Record the last successfully scraped page so scrape_full() can resume."""
    os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
    lines = []
    if os.path.exists(CHECKPOINT_FILE):
        lines = open(CHECKPOINT_FILE, encoding="utf-8").read().splitlines()
    while len(lines) < 2:
        lines.append("")
    lines = [l for l in lines if not l.startswith("last_page:")]
    lines.append(f"last_page:{page}")
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _ensure_output_file():
    """Create 123telugu-galleries.txt if it doesn't exist yet."""
    os.makedirs(os.path.dirname(FULL_OUTPUT_FILE), exist_ok=True)
    if not os.path.exists(FULL_OUTPUT_FILE):
        open(FULL_OUTPUT_FILE, "w", encoding="utf-8").close()


def _append_history(
    mode: str,
    pages_info: str,
    new_count: int,
    start_info: str,
    new_checkpoint: str | None,
    failed_pages: list[int] | None = None,
):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    ran_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_entry = f"=== {ran_at} | {mode} ===\n"
    new_entry += f"Pages          : {pages_info}\n"
    new_entry += f"New galleries  : {new_count}\n"
    new_entry += f"Started from   : {start_info}\n"
    new_entry += f"Checkpoint set : {new_checkpoint or 'unchanged'}\n"
    if failed_pages:
        new_entry += f"Failed pages   : {failed_pages}\n"
    new_entry += "\n"

    existing = ""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            existing = f.read()

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(new_entry + existing)


class Telugu123Scraper(BaseScraper):

    FULL_SCRAPE_DELAY = 2.0   # seconds between pages for full scrape
    FULL_SCRAPE_PAUSE_EVERY = 25  # pages between long pauses
    FULL_SCRAPE_PAUSE_DURATION = 5  # seconds for long pause

    def __init__(self, pages: list[int] | None = None, delay: float = 1.0):
        super().__init__(delay=delay)
        # None → only the current/first page
        self.pages = pages if pages is not None else [1]

    def get_gallery_items(self, page: int) -> list[dict]:
        url = _page_url(page)
        response = self.session.get(url, timeout=self.TIMEOUT)
        response.raise_for_status()

        tree = lxml_html.fromstring(response.content)
        anchors = tree.xpath(TITLE_LINK_XPATH)

        seen = set()
        items = []
        for a in anchors:
            href = (a.get("href") or "").strip()
            title = (a.text_content() or "").strip()
            if href and href not in seen:
                seen.add(href)
                items.append({"page": page, "title": title, "url": href})

        return items

    def scrape(self) -> list[dict]:
        _ensure_output_file()
        # Clear the file at the start of every run
        open(FULL_OUTPUT_FILE, "w", encoding="utf-8").close()

        last_url, last_ran, _ = _load_checkpoint()
        if last_url:
            print(f"[123telugu] Checkpoint found.")
            print(f"  Last run : {last_ran}")
            print(f"  Last URL : {last_url}")
        else:
            print("[123telugu] No checkpoint found. Scraping from scratch.")

        all_items = []
        found_checkpoint = last_url is None  # no checkpoint = take everything

        for page in self.pages:
            print(f"[123telugu] Scraping page {page} ...")
            items = self.get_gallery_items(page)

            if not found_checkpoint:
                # Collect items that appear BEFORE the checkpoint URL (these are new)
                # Stop as soon as we hit the checkpoint — everything from there is old
                new_items = []
                for item in items:
                    if item["url"] == last_url:
                        found_checkpoint = True
                        break  # hit the checkpoint — rest is already seen
                    new_items.append(item)
                items = new_items
                if found_checkpoint:
                    break  # no need to scrape further pages

            if not items:
                print(f"[123telugu] Page {page}: no new galleries.")
            else:
                print(f"[123telugu] Page {page}: {len(items)} new galleries.")
            all_items.extend(items)

        if not found_checkpoint and last_url:
            print(f"[123telugu] WARNING: checkpoint URL was not found in the scraped pages.")
            print(f"  The site may have updated. Writing all scraped items as new.")
            all_items = []
            for page in self.pages:
                all_items.extend(self.get_gallery_items(page))

        new_checkpoint = None
        if all_items:
            self._write(all_items)
            new_checkpoint = all_items[0]["url"]
            _save_checkpoint(new_checkpoint)  # newest item is always first on page 1
            print(f"[123telugu] Checkpoint updated to: {new_checkpoint}")
        else:
            print("[123telugu] Nothing new to save.")

        start_info = f"{last_url} ({last_ran})" if last_url else "fresh run (no checkpoint)"
        _append_history(
            mode="incremental",
            pages_info=str(self.pages),
            new_count=len(all_items),
            start_info=start_info,
            new_checkpoint=new_checkpoint,
        )

        print(f"[123telugu] Done. {len(all_items)} new items written to {FULL_OUTPUT_FILE}")
        return all_items

    def scrape_full(self, start: int = 1, end: int = 199) -> None:
        """Scrape pages start→end in order, write to FULL_OUTPUT_FILE page by page.
        Resumes automatically from the last completed page if interrupted.
        Checkpoint is updated only after all pages complete successfully."""
        _ensure_output_file()

        _, _, last_page = _load_checkpoint()

        # Resume from the page after the last completed one, if applicable
        resume_from = start
        if last_page is not None and start <= last_page < end:
            resume_from = last_page + 1
            print(f"[123telugu] Resuming from page {resume_from} (last completed: page {last_page})")
        else:
            print(f"[123telugu] Full scrape: pages {start}–{end}")

        file_mode = "a" if resume_from > start else "w"
        total_pages = end - resume_from + 1
        total_items = 0
        failed_pages = []

        print(f"[123telugu] Output → {FULL_OUTPUT_FILE}\n")

        with open(FULL_OUTPUT_FILE, file_mode, encoding="utf-8") as f:
            for page in range(resume_from, end + 1):
                print(f"[123telugu] Page {page}/{end} ...", end=" ", flush=True)
                try:
                    items = self.get_gallery_items(page)
                    if items:
                        f.write(f"=== Page {page} ===\n\n")
                        for item in items:
                            f.write(f"{item['title']}\n{item['url']}\n\n")
                        f.flush()
                        total_items += len(items)
                        print(f"{len(items)} galleries")
                    else:
                        print("0 galleries (skipped)")
                    _save_progress_page(page)  # track progress for resume
                    # longer pause every N pages to avoid rate limiting
                    if page % self.FULL_SCRAPE_PAUSE_EVERY == 0:
                        print(f"[123telugu] Pausing {self.FULL_SCRAPE_PAUSE_DURATION}s ...")
                        time.sleep(self.FULL_SCRAPE_PAUSE_DURATION)
                    else:
                        time.sleep(self.FULL_SCRAPE_DELAY)
                except Exception as e:
                    failed_pages.append(page)
                    print(f"FAILED ({e})")

        print(f"\n[123telugu] Scrape complete.")
        print(f"  Pages scraped  : {total_pages - len(failed_pages)}/{total_pages}")
        print(f"  Total galleries: {total_items}")
        print(f"  Output file    : {FULL_OUTPUT_FILE}")

        # Always update checkpoint URL from page 1 so daily runs stay accurate
        first_items = self.get_gallery_items(1)
        new_checkpoint = first_items[0]["url"] if first_items else None

        if failed_pages:
            print(f"  Failed pages   : {failed_pages}")
            # Save URL but keep last_page so resume still works
            if new_checkpoint:
                _save_progress_page(last_page or end)
                _save_checkpoint_url_only(new_checkpoint)
                print(f"[123telugu] Checkpoint URL updated to: {new_checkpoint}")
                print(f"[123telugu] Resume marker kept at page {last_page or end}.")
        else:
            # All pages succeeded — update checkpoint and clear resume marker
            if new_checkpoint:
                _save_checkpoint(new_checkpoint)
                print(f"[123telugu] Checkpoint updated to: {new_checkpoint}")

        start_info = (
            f"resumed from page {resume_from} (last completed: page {last_page})"
            if resume_from > start
            else f"fresh start (pages {start}–{end})"
        )
        _append_history(
            mode="full",
            pages_info=f"{resume_from}–{end}",
            new_count=total_items,
            start_info=start_info,
            new_checkpoint=new_checkpoint,
            failed_pages=failed_pages or None,
        )

    def _write(self, items: list[dict]):
        """Write scraped items to 123telugu-galleries.txt (file already cleared before call)."""
        with open(FULL_OUTPUT_FILE, "w", encoding="utf-8") as f:
            current_page = None
            for item in items:
                if item["page"] != current_page:
                    current_page = item["page"]
                    f.write(f"=== Page {current_page} ===\n\n")
                f.write(f"{item['title']}\n{item['url']}\n\n")
        print(f"[123telugu] Output written to {FULL_OUTPUT_FILE}")
