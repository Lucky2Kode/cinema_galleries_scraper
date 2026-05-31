"""
Formats URLs from 123telugu-galleries.txt into grouped --url lines.

Groups by the slug name (part before the trailing digits),
e.g. Vithika-Sheru-20 and Vithika-Sheru-21 both go under "Vithika-Sheru".
"""

import re
import os

FULL_OUTPUT_FILE = os.path.join("output", "telugu123", "123telugu-galleries.txt")
FULL_FORMATTED_FILE = os.path.join("output", "telugu123", "123telugu-format.txt")


def _extract_urls(filepath: str) -> list[tuple[str, str]]:
    pairs = []
    if not os.path.exists(filepath):
        print(f"[formatter] File not found: {filepath}")
        return pairs

    lines = open(filepath, encoding="utf-8").read().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("===") or line.startswith("---"):
            i += 1
            continue
        if line.startswith("https://"):
            title = lines[i - 1].strip() if i > 0 else ""
            pairs.append((title, line))
        i += 1
    return pairs


def _to_imgpages_base(url: str) -> str:
    return re.sub(r'image\d+\.html$', '', url)


def _group_key(url: str) -> str:
    match = re.search(r'/slideshows/\d+/\d+/([^/]+)/imgpages/', url)
    if not match:
        return "Other"
    slug = match.group(1)
    group = re.sub(r'[-_]?\d+$', '', slug)
    return group or slug


def _format(source: str, dest: str) -> None:
    pairs = _extract_urls(source)
    if not pairs:
        print(f"[formatter] No URLs found in {source}")
        return

    seen_urls: set[str] = set()
    groups: dict[str, list[str]] = {}
    for _title, url in pairs:
        base = _to_imgpages_base(url)
        if base in seen_urls:
            continue
        seen_urls.add(base)
        key = _group_key(url)
        groups.setdefault(key, []).append(base)

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        for group, urls in sorted(groups.items()):
            f.write(f"### {group} ({len(urls)} album(s))\n\n")
            for i, base_url in enumerate(urls):
                continuation = "" if i == len(urls) - 1 else " \\"
                f.write(f'--url "{base_url}"{continuation}\n')
            f.write("\n")

    print(f"[formatter] {len(seen_urls)} unique URLs grouped into {len(groups)} names.")
    print(f"[formatter] Output written to {dest}")

    # Clear galleries.txt — all URLs are now in format.txt
    with open(source, "w", encoding="utf-8") as f:
        pass
    print(f"[formatter] Cleared {len(seen_urls)} formatted URLs from {os.path.basename(source)}")


def format_full_urls() -> None:
    _format(source=FULL_OUTPUT_FILE, dest=FULL_FORMATTED_FILE)
