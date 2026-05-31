"""
Scraper for https://www.idlebrain.com/movie/photogallery/heroines.html

Reads the single alphabetical listing page, extracts every gallery URL
with the corresponding person name, and appends new galleries (not seen
in a previous run) to output/idlebrain/idlebrain-galleries.txt.

Checkpoint (idlebrain-checkpoint.txt) stores all gallery URLs ever
written, so repeated scrapes only emit genuinely new galleries.
"""

import os
import re
from urllib.parse import urljoin

from base import BaseScraper

ROOT_URL = "https://www.idlebrain.com/movie/photogallery/heroines.html"
BASE_URL = "https://www.idlebrain.com/movie/photogallery/"
OUTPUT_FILE = os.path.join("output", "idlebrain", "idlebrain-galleries.txt")
CHECKPOINT_FILE = os.path.join("output", "idlebrain", "idlebrain-checkpoint.txt")

_NAV_PAGES = {"index.html", "heroines.html", "heroes.html"}


def _is_gallery_link(href: str) -> bool:
    """Return True if href points to a gallery page (not a nav link)."""
    if not href:
        return False
    if href.startswith("..") or href.startswith("/") or href.startswith("#"):
        return False
    if href.startswith("javascript"):
        return False
    if href.startswith("http"):
        if "idlebrain.com/movie/photogallery/" not in href:
            return False
        path = href.split("idlebrain.com/movie/photogallery/", 1)[-1].strip("/")
        return bool(path) and path not in _NAV_PAGES
    return href not in _NAV_PAGES and href.endswith(".html")


class IdlebrainScraper(BaseScraper):

    def __init__(self, delay: float = 1.0):
        super().__init__(delay=delay)

    def scrape(self) -> int:
        """Fetch heroines.html, append new galleries to galleries.txt. Returns new count."""
        print(f"[idlebrain] Fetching {ROOT_URL} ...")
        soup = self.get_soup(ROOT_URL)
        pairs = self._parse_listing(soup)
        print(f"[idlebrain] Parsed {len(pairs)} total gallery entries from listing page.")

        checkpoint = self._load_checkpoint()
        new_pairs = [(n, u) for n, u in pairs if u not in checkpoint]

        if not new_pairs:
            print("[idlebrain] No new galleries found.")
            return 0

        self._append_galleries(new_pairs)
        self._update_checkpoint(checkpoint, new_pairs)
        print(f"[idlebrain] {len(new_pairs)} new galleries written to {OUTPUT_FILE}")
        return len(new_pairs)

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse_listing(self, soup) -> list[tuple[str, str]]:
        """Parse heroines.html → [(person_name, absolute_url)] preserving order."""
        pairs: list[tuple[str, str]] = []
        seen_urls: set[str] = set()

        for p_tag in soup.select('div[align="left"] p'):
            raw_html = p_tag.decode_contents()
            # Split the paragraph at each <br> to get individual listing lines
            chunks = re.split(r"<br\s*/?>", raw_html, flags=re.IGNORECASE)

            for chunk in chunks:
                from bs4 import BeautifulSoup as _BS
                chunk_soup = _BS(chunk, "lxml")

                # Person name: first <b> or <strong> that is not purely numeric
                name: str | None = None
                for tag in chunk_soup.find_all(["b", "strong"]):
                    text = tag.get_text(strip=True).rstrip(":").strip()
                    if text and not text.isdigit():
                        name = text
                        break

                # Collect gallery links; use link text as name for single galleries
                for a in chunk_soup.find_all("a", href=True):
                    href = a.get("href", "").strip()
                    if not _is_gallery_link(href):
                        continue

                    link_name = name
                    if not link_name:
                        link_text = a.get_text(strip=True)
                        if link_text and not link_text.isdigit():
                            link_name = link_text

                    if not link_name:
                        continue

                    abs_url = urljoin(BASE_URL, href)
                    if abs_url not in seen_urls:
                        seen_urls.add(abs_url)
                        pairs.append((link_name, abs_url))

        return pairs

    # ------------------------------------------------------------------
    # I/O helpers
    # ------------------------------------------------------------------

    def _load_checkpoint(self) -> set[str]:
        if not os.path.exists(CHECKPOINT_FILE):
            return set()
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}

    def _update_checkpoint(self, existing: set[str], new_pairs: list[tuple[str, str]]) -> None:
        os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
        updated = existing | {u for _, u in new_pairs}
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            for url in sorted(updated):
                f.write(url + "\n")

    def _append_galleries(self, pairs: list[tuple[str, str]]) -> None:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            for name, url in pairs:
                f.write(f"{name}\n{url}\n\n")
