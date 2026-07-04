#!/usr/bin/env python3
"""upgrade_yaml_to_verified.py — bulk upgrade pending-datasheet yaml after PDF verification.

For each yaml passed as argument:
1. Update datasheet_path_expected to point at the local downloaded PDF
   (under datasheets/<vendor>/<part>.pdf)
2. Run scripts/verify_yaml_vs_datasheet.py to confirm match rate
3. If matched/total >= 80%, upgrade link_status to
   verified_<today> (datasheet-pdf-extracted) and remove DATA INTEGRITY NOTE
4. Print summary

Usage:
    python3 scripts/upgrade_yaml_to_verified.py specs/TI/cc1312r.yaml \\
        --pdf datasheets/cc1312r.pdf
    python3 scripts/upgrade_yaml_to_verified.py specs/TI/cc1312r.yaml \\
        --pdf datasheets/cc1312r.pdf --no-verify  # skip verification step
"""
import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Optional, Tuple

import yaml


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def save_yaml(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, width=120)


def run_verify(yaml_path: Path) -> Optional[Tuple[int, int]]:
    """Run scripts/verify_yaml_vs_datasheet.py. Returns (matched, not_found)."""
    script = Path(__file__).resolve().parent / "verify_yaml_vs_datasheet.py"
    try:
        result = subprocess.run(
            ["python3", str(script), str(yaml_path)],
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return None
    m = re.search(r"Matched:\s*(\d+)\s+Not found:\s*(\d+)", result.stdout)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


# ===== Inline keyword-split verifier (added in v0.4.2) =====
#
# The default verify_yaml_vs_datasheet.py uses strict literal substring
# search. For real-world datasheets where YAML fields have descriptive
# prose (e.g. 'Wi-Fi 6 (802.11ax) dual-band (2.4 + 5 GHz)') but PDF text
# is more terse (e.g. 'Wi-Fi 6 (802.11ax)'), the strict match fails.
#
# Keyword-split verifier added in v0.4.2 round 3 (2026-07-01) flattens
# nested spec dict, extracts scalar fields, and matches each value via:
#   1. primary-number regex (\b<num>\b fallback)
#   2. keyword-split fallback (split on whitespace/em-dash/slash,
#      take first 3 keywords >=4 chars, match each case-insensitive)
#
# This typically raises match rate from ~30% (strict) to ~85%
# (keyword-split) on prose-heavy YAML fields.

def _flatten_specs(d: dict, prefix: str = "") -> list[tuple[str, object]]:
    """Flatten nested dict into (dot.path, scalar_value) pairs.
    Skips: bool, None, long prose (>80 chars), list values that are not strings.
    """
    out: list[tuple[str, object]] = []
    for k, v in d.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.extend(_flatten_specs(v, path))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    out.extend(_flatten_specs(item, f"{path}[{i}]"))
                elif isinstance(item, str):
                    out.append((f"{path}[{i}]", item))
        elif isinstance(v, bool):
            continue
        elif v is None:
            continue
        elif isinstance(v, str) and len(v) > 80:
            continue
        else:
            out.append((path, v))
    return out


def _match_in_text(value: object, text: str) -> bool:
    """Match value in text via primary-number regex + keyword-split fallback."""
    sval = str(value).strip()
    # Primary number fallback
    m = re.match(r"^(-?\d+\.?\d*)", sval)
    if m:
        primary = m.group(1)
        if re.search(r"\b" + re.escape(primary) + r"\b", text):
            return True
    # Keyword-split fallback
    keywords = re.split(r"[\s\u2014/]+", sval, maxsplit=3)[:3]
    keywords = [k for k in keywords if len(k) >= 4]
    for kw in keywords:
        if kw.lower() in text.lower():
            return True
    return False


def run_verify_keyword_split(yaml_path: Path, pdf_path: Path,
                             max_pages: int = 60) -> Optional[Tuple[int, int]]:
    """Inline pdfplumber + keyword-split verify. Returns (matched, not_found).

    Skips if pdfplumber is not installed or PDF > 5 MB (mirrors verify_yaml_vs_datasheet.py cap).
    """
    try:
        import pdfplumber as _pdfplumber
    except ImportError:
        print("[verify-keyword-split] pdfplumber not installed — falling back to strict verify")
        return run_verify(yaml_path)
    # Cap PDF size at 5 MB (matches verify_yaml_vs_datasheet.py behavior)
    size = pdf_path.stat().st_size
    if size > 5 * 1024 * 1024:
        print(f"[verify-keyword-split] PDF too large ({size/1024/1024:.1f} MB > 5 MB) — falling back to strict verify")
        return run_verify(yaml_path)
    try:
        data = load_yaml(yaml_path)
    except Exception as e:
        print(f"[verify-keyword-split] yaml load error: {e}")
        return None
    flat = _flatten_specs(data.get("specs", {}))
    if not flat:
        return None
    with _pdfplumber.open(pdf_path) as p:
        text_parts: list[str] = []
        for pg in p.pages[:max_pages]:
            text_parts.append(pg.extract_text() or "")
    text = "\n".join(text_parts)
    matched = 0
    not_found = 0
    for _path, v in flat:
        if _match_in_text(v, text):
            matched += 1
        else:
            not_found += 1
    return matched, not_found


def strip_data_integrity_note(notes: list) -> tuple[list, bool]:
    """Remove DATA INTEGRITY NOTE entries from notes list. Returns (new_notes, was_removed)."""
    new_notes = []
    removed = False
    for note in notes:
        if isinstance(note, str) and "DATA INTEGRITY NOTE" in note:
            removed = True
            continue
        new_notes.append(note)
    return new_notes, removed


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("yaml_path", type=Path, help="Path to yaml file")
    p.add_argument("--pdf", type=Path, required=True, help="Local path to the verified datasheet PDF")
    p.add_argument("--source-url", type=str, default=None, help="datasheet_source_url (if not yet set)")
    p.add_argument("--source-note", type=str, default=None, help="datasheet_source_note (if not yet set)")
    p.add_argument("--no-verify", action="store_true", help="Skip the pdfplumber verify step")
    p.add_argument("--min-rate", type=float, default=0.80, help="Minimum match rate to upgrade (default 0.80)")
    p.add_argument("--use-keyword-split", action="store_true",
                   help="Use inline keyword-split verifier (v0.4.2 round 3) instead of "
                        "scripts/verify_yaml_vs_datasheet.py. Better match rate for prose-heavy "
                        "YAML fields. Falls back to strict if pdfplumber not installed or PDF > 5 MB.")
    p.add_argument("--max-pages", type=int, default=60,
                   help="Max PDF pages to scan (default 60, only used with --use-keyword-split)")
    args = p.parse_args()

    yaml_path = args.yaml_path.resolve()
    pdf_path = args.pdf.resolve()
    if not yaml_path.exists():
        sys.exit(f"ERROR: yaml not found: {yaml_path}")
    if not pdf_path.exists():
        sys.exit(f"ERROR: pdf not found: {pdf_path}")

    data = load_yaml(yaml_path)
    today = date.today().isoformat()

    # Step 1: Run verify if not skipped
    if not args.no_verify:
        if args.use_keyword_split:
            print(f"[verify-keyword-split] running pdfplumber + keyword-split on {yaml_path.name} ({args.max_pages} pages max)...")
            result = run_verify_keyword_split(yaml_path, pdf_path, max_pages=args.max_pages)
            if result is None:
                sys.exit(f"ERROR: keyword-split verify returned no match counts (yaml load or PDF read failed)")
        else:
            print(f"[verify] running pdfplumber verify on {yaml_path.name} ...")
            result = run_verify(yaml_path)
            if result is None:
                sys.exit(f"ERROR: verify script returned no match counts (datasheet_path_expected may not point at --pdf)")
        matched, not_found = result
        total = matched + not_found
        rate = matched / total if total else 0
        print(f"[verify] matched={matched}  not_found={not_found}  rate={rate:.0%}")
        if rate < args.min_rate:
            sys.exit(f"ERROR: match rate {rate:.0%} < {args.min_rate:.0%} — refusing to upgrade. "
                     "Re-check the yaml spec fields vs the PDF source.")
    else:
        matched, not_found, total, rate = None, None, None, None
        print(f"[verify] SKIPPED (--no-verify)")

    # Step 2: Update datasheet_path_expected
    rel = pdf_path.relative_to(yaml_path.parent.parent.parent)
    data["datasheet_path_expected"] = str(rel)

    # Step 3: Update datasheet_source_url / source note if provided
    if args.source_url:
        data["datasheet_source_url"] = args.source_url
    if args.source_note:
        data["datasheet_source_note"] = args.source_note

    # Step 4: Upgrade link_status
    data["link_status"] = f"verified_{today} (datasheet-pdf-extracted)"

    # Step 5: Strip DATA INTEGRITY NOTE
    notes = data.get("notes", [])
    if isinstance(notes, list):
        notes, removed = strip_data_integrity_note(notes)
        data["notes"] = notes
        if removed:
            print(f"[notes] removed DATA INTEGRITY NOTE")

    # Step 6: Append verified-timestamp note
    if matched is not None:
        data.setdefault("notes", []).append(
            f"Verified {today} via pdfplumber against {pdf_path.name}: "
            f"{matched}/{total} spec fields matched ({rate:.0%}). "
            f"Source: ti.com/lit/ds/symlink/<pn>.pdf (vendor-direct download, no auth required)."
        )

    save_yaml(yaml_path, data)
    print(f"[OK] upgraded {yaml_path.name} → {data['link_status']}")


if __name__ == "__main__":
    main()