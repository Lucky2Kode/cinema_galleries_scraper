"""
Formats URLs from idlebrain-galleries.txt into grouped --url lines.

Groups all albums for the same person under one ### header, then
clears idlebrain-galleries.txt (formatted entries are now in format.txt).
"""

import os
import re

GALLERIES_FILE = os.path.join("output", "idlebrain", "idlebrain-galleries.txt")
FORMAT_FILE = os.path.join("output", "idlebrain", "idlebrain-format.txt")


def _normalize_name(name: str) -> str:
    """Turn 'Adah Sharma' → 'Adah-Sharma', 'Anasuya (new)' → 'Anasuya-new'."""
    name = re.sub(r"\s*\bNew\b\s*$", "", name, flags=re.IGNORECASE).strip()
    name = name.rstrip(":").strip()
    name = re.sub(r"[\s()\[\]]+", "-", name)
    return name.strip("-")


def _extract_pairs(filepath: str) -> list[tuple[str, str]]:
    """Read galleries.txt → [(person_name, url)]."""
    pairs: list[tuple[str, str]] = []
    if not os.path.exists(filepath):
        return pairs
    lines = open(filepath, encoding="utf-8").read().splitlines()
    i = 0
    while i < len(lines):
        name_line = lines[i].strip()
        if name_line and i + 1 < len(lines):
            url_line = lines[i + 1].strip()
            if url_line.startswith("http"):
                pairs.append((name_line, url_line))
                i += 2
                continue
        i += 1
    return pairs


def format_idlebrain_urls() -> None:
    pairs = _extract_pairs(GALLERIES_FILE)
    if not pairs:
        print(f"[formatter] No URLs found in {GALLERIES_FILE}")
        return

    # Group by normalized person name, preserving insertion order
    seen_urls: set[str] = set()
    groups: dict[str, list[str]] = {}
    name_map: dict[str, str] = {}  # normalised_key → display name

    for raw_name, url in pairs:
        if url in seen_urls:
            continue
        seen_urls.add(url)
        key = _normalize_name(raw_name)
        if key not in name_map:
            name_map[key] = key  # use normalised form as display
        groups.setdefault(key, []).append(url)

    os.makedirs(os.path.dirname(FORMAT_FILE), exist_ok=True)
    with open(FORMAT_FILE, "w", encoding="utf-8") as f:
        for key in sorted(groups):
            urls = groups[key]
            f.write(f"### {key} ({len(urls)} album(s))\n\n")
            for i, url in enumerate(urls):
                continuation = "" if i == len(urls) - 1 else " \\"
                f.write(f'--url "{url}"{continuation}\n')
            f.write("\n")

    print(f"[formatter] {len(seen_urls)} unique URLs grouped into {len(groups)} names.")
    print(f"[formatter] Output written to {FORMAT_FILE}")

    # Clear galleries.txt — all URLs are now in format.txt
    with open(GALLERIES_FILE, "w", encoding="utf-8") as f:
        pass
    print(f"[formatter] Cleared {len(seen_urls)} formatted URLs from {os.path.basename(GALLERIES_FILE)}")
