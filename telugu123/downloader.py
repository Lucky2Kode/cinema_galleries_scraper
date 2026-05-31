"""
Image downloader for 123telugu galleries.

Reads output/telugu123/123telugu-format.txt and downloads every gallery to
downloads/123telugu/<gallery-slug>/ (e.g. downloads/123telugu/Samyuktha-031/).

Algorithm (ported from the Java Telugu123Handler + DownloadOrchestrator):
  1. Parse format file → list of (person_name, [gallery_urls])
  2. For each gallery URL:
       a. Strip "imgpages/" suffix → gallery index URL
       b. Crawl index page for image-page links (imgpages/imageN.html)
       c. Visit each image page → extract full-size image src
       d. Download image to <dest_dir>/<filename>, skip if already present
"""

import os
import re
import time
from urllib.parse import unquote, urljoin

from base import BaseScraper

FORMAT_FILE = os.path.join("output", "telugu123", "123telugu-format.txt")
DOWNLOAD_DIR = os.path.join("downloads", "123telugu")

_LOGO_KEYWORDS = ("th_", "thumb", "logo", "white", "/ads/", "banner")


def _is_logo_or_thumb(url_lower: str) -> bool:
    return any(kw in url_lower for kw in _LOGO_KEYWORDS)


def parse_format_file(filepath: str = FORMAT_FILE) -> list[tuple[str, list[str]]]:
    """Parse 123telugu-format.txt → [(person_name, [gallery_urls])]."""
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
    """Extract the folder name from a gallery URL (segment before imgpages/)."""
    url = gallery_url.rstrip("/")
    for suffix in ["/imgpages", "/pages"]:
        idx = url.find(suffix)
        if idx != -1:
            url = url[:idx]
    return unquote(url.split("/")[-1])


def _resolve_index_url(gallery_url: str) -> str:
    """Strip imgpages/ or pages/ to get the gallery root index URL."""
    for sub in ["imgpages/", "pages/"]:
        idx = gallery_url.find(sub)
        if idx != -1:
            return gallery_url[:idx]
    return gallery_url.rstrip("/") + "/"


class Telugu123Downloader(BaseScraper):

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
        index_url = _resolve_index_url(gallery_url)
        soup = self.get_soup(index_url)
        seen: set[str] = set()
        pages: list[str] = []
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            abs_href = urljoin(index_url, href)
            if re.search(r"/(imgpages?|pages?)/image\d+\.html", abs_href):
                if abs_href not in seen:
                    seen.add(abs_href)
                    pages.append(abs_href)
        return pages

    def _extract_image_url(self, image_page_url: str) -> str | None:
        """Return the full-size image URL from an imgpages/imageN.html page."""
        soup = self.get_soup(image_page_url)

        # Primary: relative ../images/ or ./images/ path (site's canonical pattern)
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
            resp = self.session.get(
                image_url,
                headers={"Referer": referer},
                timeout=60,
            )
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

    def download_gallery(self, gallery_url: str) -> int:
        """Download all images from one gallery URL. Returns count saved."""
        slug = gallery_slug(gallery_url)
        dest_dir = os.path.join(self.download_dir, slug)

        print(f"\n[download] Gallery : {slug}")
        print(f"[download] URL     : {gallery_url}")

        try:
            image_pages = self._crawl_gallery(gallery_url)
        except Exception as e:
            print(f"[download] Failed to crawl: {e}")
            return 0

        if not image_pages:
            print("[download] No image pages found.")
            return 0

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
        return downloaded

    def download_all(self) -> None:
        """Download every gallery listed in the format file."""
        if not os.path.exists(self.format_file):
            print(f"[download] Format file not found: {self.format_file}")
            print("[download] Run: python main.py telugu123 fullformat")
            return

        galleries = parse_format_file(self.format_file)
        if not galleries:
            print("[download] No galleries found in format file.")
            return

        total_albums = sum(len(urls) for _, urls in galleries)
        print(
            f"[download] {len(galleries)} person(s), "
            f"{total_albums} total album(s) to download."
        )

        total_images = 0
        for name, urls in galleries:
            print(f"\n[download] ══ {name} ({len(urls)} album(s)) ══")
            for url in urls:
                total_images += self.download_gallery(url)

        print(f"\n[download] All done. {total_images} total images downloaded.")
