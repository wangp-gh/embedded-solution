#!/usr/bin/env python3
"""upgrade_yaml_html_source.py — upgrade pending-datasheet yaml when only HTML source is available.

For vendors like Renesas, Espressif, NXP where the "datasheet" is published
as HTML (not PDF), this script:
1. Loads yaml + the local firecrawl-scraped HTML file
2. For each scalar spec field, searches the HTML text for matching keyword
3. If matched/total >= 60% (lower threshold for HTML since whitespace/formatting
   is more variable than PDFs), upgrade link_status to
   verified_<today> (datasheet-html-extracted) and remove DATA INTEGRITY NOTE
4. Uses text search (case-insensitive + \b<num>\b regex)

Usage:
    python3 scripts/upgrade_yaml_html_source.py specs/NXP/KW47.yaml \\
        --html references/semiconductor-vendor/NXP/datasheet-html/kw47.html \\
        --source-url "https://www.nxp.com/products/KW47"
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Iterator, Tuple

import yaml


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def save_yaml(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, width=120)


def flatten(d: dict, prefix: str = "") -> Iterator[Tuple[str, object]]:
    """Flatten nested dict into (dot.path, scalar_value) pairs."""
    for k, v in d.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            yield from flatten(v, path)
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    yield from flatten(item, f"{path}[{i}]")
                elif isinstance(item, str):
                    yield f"{path}[{i}]", item
        elif isinstance(v, bool):
            continue
        elif v is None:
            continue
        elif isinstance(v, str) and len(v) > 80:
            continue
        else:
            yield path, v


def search_in_html(value, html: str) -> bool:
    sval = str(value).strip()
    # primary-number fallback
    m = re.match(r"^(-?\d+\.?\d*)", sval)
    if m:
        primary = m.group(1)
        if re.search(r"\b" + re.escape(primary) + r"\b", html):
            return True
    # substring fallback (case-insensitive)
    return sval.lower() in html.lower()


def strip_data_integrity_note(notes):
    new = [n for n in notes if not (isinstance(n, str) and "DATA INTEGRITY NOTE" in n)]
    return new, len(notes) - len(new)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("yaml_path", type=Path)
    p.add_argument("--html", type=Path, required=True)
    p.add_argument("--source-url", type=str, required=True)
    p.add_argument("--source-note", type=str, default=None)
    p.add_argument("--min-rate", type=float, default=0.60)
    args = p.parse_args()

    if not args.yaml_path.exists():
        sys.exit(f"yaml not found: {args.yaml_path}")
    if not args.html.exists():
        sys.exit(f"html not found: {args.html}")

    data = load_yaml(args.yaml_path)
    html = args.html.read_text(encoding="utf-8", errors="replace")

    flat = list(flatten(data.get("specs", {})))
    if not flat:
        sys.exit(f"no flatten-able spec fields in {args.yaml_path}")

    matched = sum(1 for _, v in flat if search_in_html(v, html))
    not_found = len(flat) - matched
    rate = matched / len(flat) if flat else 0
    print(f"[verify] {args.yaml_path.name}: matched={matched}  not_found={not_found}  rate={rate:.0%}  (n={len(flat)} fields)")

    if rate < args.min_rate:
        sys.exit(f"ERROR: match rate {rate:.0%} < {args.min_rate:.0%} — refusing to upgrade")

    today = date.today().isoformat()

    # compute rel path from yaml to html
    yaml_dir = args.yaml_path.parent.parent.parent
    try:
        rel_html = args.html.resolve().relative_to(yaml_dir)
    except ValueError:
        rel_html = args.html

    data["datasheet_path_expected"] = str(rel_html)
    data["datasheet_source_url"] = args.source_url
    if args.source_note:
        data["datasheet_source_note"] = args.source_note
    data["link_status"] = f"verified_{today} (datasheet-html-extracted)"

    notes = data.get("notes", [])
    if isinstance(notes, list):
        notes, removed = strip_data_integrity_note(notes)
        if removed:
            print(f"[notes] removed {removed} DATA INTEGRITY NOTE entries")
    else:
        notes, removed = [], 0
    data["notes"] = notes + [
        f"Verified {today} via firecrawl-html-extract against {args.html.name}: "
        f"{matched}/{len(flat)} spec fields matched ({rate:.0%}). "
        f"Source: {args.source_url} (vendor product page scraped as HTML; no separate PDF available)."
    ]
    save_yaml(args.yaml_path, data)
    print(f"[OK] upgraded {args.yaml_path.name} → {data['link_status']}")


if __name__ == "__main__":
    main()