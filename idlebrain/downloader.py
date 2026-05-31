"""
Image downloader for idlebrain galleries.

Reads output/idlebrain/idlebrain-format.txt and downloads every gallery to
downloads/idlebrain/<gallery-slug>/ (e.g. downloads/idlebrain/tamanna180/).

Algorithm (mirrors the Java IdlebrainHandler + DownloadOrchestrator):
  1. Parse format file → list of (person_name, [gallery_urls])
  2. For each gallery URL:
       a. Fetch gallery index page (e.g. tamanna180/index.html)
       b. Collect image-page links matching pages/imageN.html
       c. Visit each image page → extract full-size ../images/ src
       d. Download to <dest_dir>/<filename>, skip if already present
  3. Rewrite format.txt keeping only galleries with incomplete downloads.
"""

import os
import re
import time
from urllib.parse import unquote, urljoin

from base import BaseScraper

FORMAT_FILE = os.path.join("output", "idlebrain", "idlebrain-format.txt")
DAILY_FILE = os.path.join("output", "idlebrain", "idlebrain-daily.txt")
DAILY_HISTORY_FILE = os.path.join("output", "idlebrain", "idlebrain-daily-history.txt")
DOWNLOAD_DIR = os.path.join("downloads", "idlebrain")

_LOGO_KEYWORDS = ("th_", "thumb", "logo", "white", "/ads/", "banner")


def _is_logo_or_thumb(url_lower: str) -> bool:
    return any(kw in url_lower for kw in _LOGO_KEYWORDS)


def parse_format_file(filepath: str = FORMAT_FILE) -> list[tuple[str, list[str]]]:
    """Parse idlebrain-format.txt → [(person_name, [gallery_urls])]."""
    galleries: list[tuple[str, list[str]]] = []
    current_name: str | None = None
    current_urls: list[str] = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("### "):
                if current_name and current_urls:
                    galleries.append((current_name, current_urls))
                current_name = re.sub(r"\s*\(\d+ album\(s\)\)\s*$", "", line[4:]).strip()
                current_urls = []
            elif line.startswith('--url "'):
                url = line.removeprefix('--url "').rstrip('" \\').strip()
                if url:
                    current_urls.append(url)

    if current_name and current_urls:
        galleries.append((current_name, current_urls))

    return galleries


def gallery_slug(gallery_url: str) -> str:
    """Extract the download folder name from a gallery URL.

    tamanna180/index.html → tamanna180
    akshaya.html          → akshaya
    """
    base = "idlebrain.com/movie/photogallery/"
    path = gallery_url.split(base, 1)[-1].strip("/") if base in gallery_url else gallery_url
    if "/" in path:
        return path.split("/")[0]
    return path.replace(".html", "")


class IdlebrainDownloader(BaseScraper):

    def __init__(
        self,
        format_file: str = FORMAT_FILE,
        download_dir: str = DOWNLOAD_DIR,
        delay: float = 0.5,
    ):
        super().__init__(delay=delay)
        self.format_file = format_file
        self.download_dir = download_dir

    # ------------------------------------------------------------------
    # Gallery crawling
    # ------------------------------------------------------------------

    def _crawl_gallery(self, gallery_url: str) -> list[str]:
        """Return ordered list of image-page URLs from the gallery index."""
        soup = self.get_soup(gallery_url)
        seen: set[str] = set()
        pages: list[str] = []

        for a in soup.select("a[href]"):
            href = a.get("href", "")
            abs_href = urljoin(gallery_url, href)
            if re.search(r"/pages/image\d+\.html", abs_href):
                if abs_href not in seen:
                    seen.add(abs_href)
                    pages.append(abs_href)

        # Fallback: linked images (older flat-HTML galleries)
        if not pages:
            for a in soup.select("a[href]:has(img)"):
                href = a.get("href", "")
                abs_href = urljoin(gallery_url, href)
                if abs_href not in seen and "idlebrain.com" in abs_href:
                    seen.add(abs_href)
                    pages.append(abs_href)

        return pages

    def _extract_image_url(self, image_page_url: str) -> str | None:
        """Return the full-size image URL from a pages/imageN.html page."""
        soup = self.get_soup(image_page_url)

        # Primary: relative ../images/ or ./images/ path
        for img in soup.select("img[src]"):
            src = img.get("src", "")
            if src.startswith("../images/") or src.startswith("./images/"):
                return urljoin(image_page_url, src)

        # Fallback: any non-logo image with a recognisable extension
        for img in soup.select("img[src]"):
            src = img.get("src", "")
            abs_src = urljoin(image_page_url, src)
            lower = abs_src.lower()
            if _is_logo_or_thumb(lower):
                continue
            if re.search(r"\.(jpg|jpeg|png|webp)(\?.*)?$", lower):
                return abs_src

        return None

    # ------------------------------------------------------------------
    # Downloading
    # ------------------------------------------------------------------

    def _download_image(
        self,
        image_url: str,
        referer: str,
        dest_dir: str,
        idx: int,
        total: int,
    ) -> bool:
        filename = unquote(image_url.split("?")[0].split("/")[-1]) or "image.jpg"
        filepath = os.path.join(dest_dir, filename)

        if os.path.exists(filepath):
            print(f"  [{idx}/{total}] Already exists: {filename}")
            return True

        try:
            resp = self.session.get(image_url, headers={"Referer": referer}, timeout=60)
            resp.raise_for_status()
            os.makedirs(dest_dir, exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(resp.content)
            print(f"  [{idx}/{total}] ✓ {filename}")
            time.sleep(self.delay)
            return True
        except Exception as e:
            print(f"  [{idx}/{total}] Error: {e}")
            return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def download_gallery(self, gallery_url: str) -> tuple[int, int]:
        """Download all images from one gallery URL. Returns (downloaded, total).

        total=0 means the gallery index couldn't be crawled.
        """
        slug = gallery_slug(gallery_url)
        dest_dir = os.path.join(self.download_dir, slug)

        print(f"\n[download] Gallery : {slug}")
        print(f"[download] URL     : {gallery_url}")

        try:
            image_pages = self._crawl_gallery(gallery_url)
        except Exception as e:
            print(f"[download] Failed to crawl: {e}")
            return 0, 0

        if not image_pages:
            print("[download] No image pages found.")
            return 0, 0

        total = len(image_pages)
        print(f"[download] {total} image pages found.")
        downloaded = 0

        for idx, page_url in enumerate(image_pages, start=1):
            try:
                image_url = self._extract_image_url(page_url)
                if not image_url:
                    print(f"  [{idx}/{total}] No image found on {page_url}")
                    continue
                if self._download_image(image_url, page_url, dest_dir, idx, total):
                    downloaded += 1
            except Exception as e:
                print(f"  [{idx}/{total}] Error: {e}")

        print(f"[download] Done: {downloaded}/{total} images → {dest_dir}")
        return downloaded, total

    def _rewrite_format_file(self, galleries: list[tuple[str, list[str]]]) -> None:
        """Overwrite format.txt with only the given galleries (failed ones)."""
        with open(self.format_file, "w", encoding="utf-8") as f:
            for name, urls in galleries:
                f.write(f"### {name} ({len(urls)} album(s))\n\n")
                for i, url in enumerate(urls):
                    continuation = "" if i == len(urls) - 1 else " \\"
                    f.write(f'--url "{url}"{continuation}\n')
                f.write("\n")

        if galleries:
            kept = sum(len(u) for _, u in galleries)
            print(
                f"[download] {kept} gallery/ies kept in "
                f"{os.path.basename(self.format_file)} — download incomplete."
            )
        else:
            print(f"[download] All galleries downloaded. {os.path.basename(self.format_file)} cleared.")

    def download_all(self) -> None:
        """Download every gallery in format.txt, then rewrite it keeping only failures."""
        if not os.path.exists(self.format_file):
            print(f"[download] Format file not found: {self.format_file}")
            print("[download] Run: python main.py idlebrain format")
            return

        galleries = parse_format_file(self.format_file)
        if not galleries:
            print("[download] No galleries found in format file.")
            return

        total_albums = sum(len(urls) for _, urls in galleries)
        print(f"[download] {len(galleries)} person(s), {total_albums} total album(s) to download.")

        total_images = 0
        failed: list[tuple[str, list[str]]] = []

        for name, urls in galleries:
            print(f"\n[download] ══ {name} ({len(urls)} album(s)) ══")
            failed_urls: list[str] = []
            for url in urls:
                downloaded, total = self.download_gallery(url)
                total_images += downloaded
                if downloaded < total or total == 0:
                    failed_urls.append(url)
            if failed_urls:
                failed.append((name, failed_urls))

        self._rewrite_format_file(failed)

        failed_count = sum(len(u) for _, u in failed)
        if failed_count:
            print(
                f"\n[download] Done. {total_images} images downloaded. "
                f"{failed_count} gallery/ies had errors — kept in format file for retry."
            )
        else:
            print(f"\n[download] All done. {total_images} total images downloaded.")

    def download_daily(
        self,
        daily_file: str = DAILY_FILE,
        history_file: str = DAILY_HISTORY_FILE,
    ) -> None:
        """Download galleries listed in idlebrain-daily.txt (one URL per line).

        After each run:
          - Successfully completed URLs are removed from daily.txt and
            appended to idlebrain-daily-history.txt.
          - Failed or partial URLs remain in daily.txt for retry.
        """
        if not os.path.exists(daily_file):
            print(f"[download] Daily file not found: {daily_file}")
            return

        urls = [
            line.strip()
            for line in open(daily_file, encoding="utf-8")
            if line.strip().startswith("http")
        ]

        if not urls:
            print("[download] No URLs found in daily file.")
            return

        print(f"[download] {len(urls)} URL(s) in {os.path.basename(daily_file)}")

        total_images = 0
        failed_urls: list[str] = []
        done_urls: list[str] = []

        for url in urls:
            downloaded, total = self.download_gallery(url)
            total_images += downloaded
            if downloaded == total and total > 0:
                done_urls.append(url)
            else:
                failed_urls.append(url)

        # Rewrite daily.txt with only failed URLs
        with open(daily_file, "w", encoding="utf-8") as f:
            for url in failed_urls:
                f.write(url + "\n")

        # Append successful slugs to history with a run timestamp
        if done_urls:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(history_file, "a", encoding="utf-8") as f:
                f.write(f"=== {timestamp} ===\n")
                for url in done_urls:
                    f.write(gallery_slug(url) + "\n")
                f.write("\n")

        if failed_urls:
            print(
                f"\n[download] Done. {total_images} images downloaded. "
                f"{len(failed_urls)} URL(s) kept in daily file for retry."
            )
        else:
            print(
                f"\n[download] All done. {total_images} images downloaded. "
                f"Daily file cleared ({len(done_urls)} URL(s) moved to history)."
            )
