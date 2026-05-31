"""
Web scraping entry point.

Usage:
    python main.py                           # interactive menu
    python main.py telugu123                 # scrape page 1 (current page)
    python main.py telugu123 1 3 5           # scrape specific pages
    python main.py telugu123 1-10            # scrape a range of pages
    python main.py telugu123 fullscrape      # scrape all pages 1-199
    python main.py telugu123 fullscrape 1 50 # scrape pages 1-50
    python main.py telugu123 fullformat      # format 123telugu-galleries.txt → 123telugu-format.txt
    python main.py telugucinema              # run telugucinema scraper
"""

import sys
from telugu123.scraper import Telugu123Scraper
from telugu123.formatter import format_full_urls
from telugucinema.scraper import TeluguCinemaScraper


def parse_pages(args: list[str]) -> list[int] | None:
    if not args:
        return None
    pages = set()
    for arg in args:
        if "-" in arg:
            parts = arg.split("-", 1)
            try:
                start, end = int(parts[0]), int(parts[1])
                pages.update(range(start, end + 1))
            except ValueError:
                print(f"Invalid range '{arg}', skipping.")
        else:
            try:
                pages.add(int(arg))
            except ValueError:
                print(f"Invalid page number '{arg}', skipping.")
    return sorted(pages) if pages else None


def run_telugu123(pages: list[int] | None):
    scraper = Telugu123Scraper(pages=pages)
    scraper.scrape()
    print()
    format_full_urls()


def run_telugu123_full(start: int = 1, end: int = 199):
    scraper = Telugu123Scraper()
    scraper.scrape_full(start=start, end=end)
    print()
    format_full_urls()


def run_telugucinema():
    scraper = TeluguCinemaScraper()
    scraper.scrape()


def show_menu():
    print("\n" + "=" * 50)
    print("  Telugu Gallery Scraper")
    print("=" * 50)
    print("  1. Scrape URLs    (selected pages → 123telugu-galleries.txt)")
    print("  2. Full scrape    (pages 1–199   → 123telugu-galleries.txt)")
    print("  3. Format URLs    (123telugu-galleries.txt → 123telugu-format.txt)")
    print("=" * 50)

    choice = input("Choose an option (1-3): ").strip()

    if choice == "1":
        print("\nEnter page numbers to scrape.")
        print("Examples:  1        → page 1 only")
        print("           1 3 5    → pages 1, 3 and 5")
        print("           1-10     → pages 1 through 10")
        print("(Press Enter to scrape current page only)")
        raw = input("Pages: ").strip()
        pages = parse_pages(raw.split()) if raw else None
        print()
        run_telugu123(pages)

    elif choice == "2":
        print()
        run_telugu123_full(start=1, end=199)

    elif choice == "3":
        print()
        format_full_urls()

    else:
        print(f"Invalid choice '{choice}'. Please enter 1, 2, or 3.")
        sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        show_menu()
    elif args[0] == "telugu123":
        if len(args) > 1 and args[1] == "fullformat":
            format_full_urls()
        elif len(args) > 1 and args[1] == "fullscrape":
            start = int(args[2]) if len(args) > 2 else 1
            end = int(args[3]) if len(args) > 3 else 199
            run_telugu123_full(start=start, end=end)
        else:
            pages = parse_pages(args[1:])
            run_telugu123(pages)
    elif args[0] == "telugucinema":
        run_telugucinema()
    else:
        pages = parse_pages(args)
        if pages:
            run_telugu123(pages)
        else:
            print(f"Unknown argument '{args[0]}'.")
            print("Usage: python main.py [telugu123|telugucinema] [pages|fullscrape|fullformat]")
            sys.exit(1)
