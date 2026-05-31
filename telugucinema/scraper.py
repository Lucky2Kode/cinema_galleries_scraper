"""
Scraper for https://gallery.telugucinema.com/

Collects gallery listings (title + thumbnail + URL) from the home page
and optional category pages (actress, actor, general galleries).
"""

import csv
import os
from base import BaseScraper

BASE_URL = "https://gallery.telugucinema.com/"
OUTPUT_FILE = os.path.join("output", "telugucinema", "galleries.csv")

CATEGORY_URLS = {
    "home": BASE_URL,
    "actress": f"{BASE_URL}category/actress-galleries/",
    "actor": f"{BASE_URL}category/actor-galleries/",
}


class TeluguCinemaScraper(BaseScraper):

    def __init__(self, categories: list[str] = None, delay: float = 1.0):
        super().__init__(delay=delay)
        self.categories = categories or list(CATEGORY_URLS.keys())

    def get_gallery_items(self, url: str) -> list[dict]:
        soup = self.get_soup(url)
        items = []

        for a in soup.select("a[href]"):
            href = a.get("href", "").strip()
            if not href.startswith(BASE_URL) or href == BASE_URL:
                continue

            title_tag = a.find("h3") or a.find("h2")
            title = title_tag.get_text(strip=True) if title_tag else a.get_text(strip=True)

            img_tag = a.find("img")
            thumbnail = img_tag.get("src", "") if img_tag else ""

            if title:
                items.append({"title": title, "url": href, "thumbnail": thumbnail})

        # deduplicate by URL
        seen = set()
        unique = []
        for item in items:
            if item["url"] not in seen:
                seen.add(item["url"])
                unique.append(item)
        return unique

    def scrape(self):
        all_items = []
        for category in self.categories:
            url = CATEGORY_URLS.get(category)
            if not url:
                print(f"[telugucinema] Unknown category '{category}', skipping.")
                continue
            print(f"[telugucinema] Scraping category '{category}' ...")
            items = self.get_gallery_items(url)
            for item in items:
                item["category"] = category
            all_items.extend(items)
            print(f"[telugucinema] Found {len(items)} galleries in '{category}'")

        self._save(all_items)
        print(f"[telugucinema] Done. {len(all_items)} total galleries saved to {OUTPUT_FILE}")
        return all_items

    def _save(self, items: list[dict]):
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["category", "title", "url", "thumbnail"])
            writer.writeheader()
            writer.writerows(items)
