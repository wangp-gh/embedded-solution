#!/usr/bin/env python3
"""
Rewrite datasheet references from local paths (embedded_dev/...) to either:
  - Real vendor PDF URLs (for the 4 priority chips the user just compared)
  - 'product page → Documents & Downloads' placeholder for the rest

Usage:
    python3 scripts/rewrite_datasheet_refs.py [--dry-run] [--files <paths>]

Default scope: references/semiconductor-vendor/**/*.md
Excludes:      references/testing/** (test fixtures kept as-is)

Three local-path formats are handled:
  1. `<cwd>/embedded_dev/<vendor>/datasheet/<pn>.pdf`
  2. `embedded_dev/<vendor>/datasheet/<pn>.pdf`  (backticked)
  3. `../../embedded_dev/<vendor>/datasheet/<pn>.pdf`  (markdown relative link)
"""

from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Real vendor PDF URLs (verified 2026-07-05 by Tavily + curl HEAD).
# These four are the priority chips from the v0.5.0 BLE comparison work.
# ---------------------------------------------------------------------------
REAL_PDF_URLS: dict[str, str] = {
    # Renesas DA14592 — errata page is publicly linkable; the datasheet itself
    # is one click deeper on the same product-page "Documents & Downloads" tab
    "DA14592":  "https://www.renesas.com/en/document/dst/da14592-datasheet",

    # Nordic nRF54L15 — official docs bundle page (PDF is server-rendered).
    # Direct PDF download is gated by Cloudflare; product docs page is public.
    "nRF54L15": "https://docs.nordicsemi.com/bundle/ps_nrf54L15",

    # Espressif ESP32-C6 — direct stable PDF URL on Espressif CDN
    "ESP32-C6": "https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf",

    # Telink TLSR8258 — direct stable PDF URL on Telink public wiki
    "TLSR8258": "https://wiki.telink-semi.cn/doc/ds/DS_TLSR8258-E_Datasheet%20for%20Telink%20BLE+IEEE802.15.4%20Multi-Standard%20Wireless%20SoC%20TLSR8258.pdf",
}

PLACEHOLDER = "product page → Documents & Downloads"

# ---------------------------------------------------------------------------
# PartNumber extraction from path
# ---------------------------------------------------------------------------
PATH_RE = re.compile(
    r"`?(?:<cwd>/|../../)?embedded_dev/(?P<vendor>[a-z0-9_]+)/datasheet/(?P<pn>[A-Za-z0-9_\-]+)\.pdf`?",
    re.IGNORECASE,
)


def replacement_for(pn: str) -> str:
    """Return the URL/placeholder string to substitute for this part number."""
    if pn in REAL_PDF_URLS:
        return REAL_PDF_URLS[pn]
    # Case-insensitive match for part numbers we have URLs for
    for key, url in REAL_PDF_URLS.items():
        if key.lower() == pn.lower():
            return url
    return PLACEHOLDER


def rewrite_text(text: str) -> tuple[str, int]:
    """Rewrite all local datasheet paths. Returns (new_text, num_replacements)."""
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        pn = m.group("pn")
        return replacement_for(pn)

    new_text = PATH_RE.sub(repl, text)
    return new_text, count


def rewrite_file(path: Path, dry_run: bool) -> int:
    original = path.read_text(encoding="utf-8")
    new_text, n = rewrite_text(original)
    if n == 0:
        return 0
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="show what would change without writing")
    ap.add_argument("--files", nargs="+", help="restrict to these files (default: all under references/semiconductor-vendor)")
    args = ap.parse_args()

    if args.files:
        paths = [Path(p) for p in args.files]
    else:
        root = Path(__file__).resolve().parent.parent / "references" / "semiconductor-vendor"
        paths = list(root.rglob("*.md"))

    total_files = 0
    total_subs = 0
    for p in sorted(paths):
        n = rewrite_file(p, dry_run=args.dry_run)
        if n > 0:
            total_files += 1
            total_subs += n
            tag = "[dry-run]" if args.dry_run else "[ok]"
            print(f"{tag} {p}: {n} replacement(s)")

    print(f"\nTotal: {total_files} files, {total_subs} substitutions"
          + (" (dry-run, nothing written)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())