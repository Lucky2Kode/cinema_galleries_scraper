import time
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BaseScraper:
    """Shared HTTP + parsing utilities for all site scrapers."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    TIMEOUT = 45  # seconds — slow sites need more time

    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        retry = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get_soup(self, url: str) -> BeautifulSoup:
        response = self.session.get(url, timeout=self.TIMEOUT)
        response.raise_for_status()
        time.sleep(self.delay)
        return BeautifulSoup(response.text, "lxml")

    def scrape(self):
        raise NotImplementedError("Each scraper must implement scrape()")
