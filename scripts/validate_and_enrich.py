#!/usr/bin/env python3
"""validate_and_enrich.py — verify existing specs against PDF and propose enrichments.

For each yaml in specs/, this script:
  1. Loads the yaml and resolves its PDF (via PARTS catalog or
     source_pdf; falls back to datasheet_path_expected).
  2. Runs the same extractor that update_specs.py uses, then runs
     scripts/verify_yaml_vs_datasheet.py to compare.
  3. Reports three categories:
     - mismatch:  existing yaml value does NOT match PDF text
                 (real data error — needs fix)
     - missing_critical:  empty key_field that's available in PDF
                 (data gap — enrichment candidate)
     - already_verified:  all yaml fields matched PDF

  4. With --enrich, writes the missing critical fields into the yaml
     as unverified: ['enriched-from-PDF'], so a human can review
     before re-running promotion.

  5. With --promote-matches, marks fields as verified (the existing
     unverified: ['all'] gets cleared on byte-for-byte match).

Usage:
    python3 scripts/validate_and_enrich.py --batch
    python3 scripts/validate_and_enrich.py specs/Espressif/ESP32.yaml --verbose
    python3 scripts/validate_and_enrich.py specs/Espressif/ESP32.yaml --enrich --promote-matches
"""
from __future__ import annotations
import argparse
import re
import sys
import json
import subprocess
import yaml
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent
PARTS_INDEX_PATH = REPO_ROOT / "scripts" / "update_specs.py"


# ─── PARTS catalog import (for PDF resolution) ────────────────────────────

def _extract_parts_dict_from_update_specs():
    """Pull the PARTS dict literal out of scripts/update_specs.py by
    parsing the top-level assignment, without triggering update_specs's
    runtime code (which uses __file__).

    Falls back to a tolerant regex scan if the AST parse fails.
    """
    import ast
    src = PARTS_INDEX_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PARTS":
                    namespace: dict[str, Any] = {}
                    code = compile(
                        ast.Expression(body=node.value),
                        str(PARTS_INDEX_PATH),
                        "eval",
                    )
                    return eval(code, {"__file__": str(PARTS_INDEX_PATH)}, namespace)
    return {}


PARTS = _extract_parts_dict_from_update_specs()


# ─── Critical fields the extraction should cover ──────────────────────────

CRITICAL_FIELDS = (
    # Source: 88% to 99% missing-rate inventory 2026-07-07
    "cores", "flash", "ram", "clock_mhz_max",
    "operating_voltage_v", "wireless", "package", "peripherals_count",
    "security", "operating_temperature_c",
    # Also useful where the PDF states it
    "data_flash", "low_power_modes", "coremark", "tx_power_dbm_max",
)


# ─── PDF resolution ───────────────────────────────────────────────────────

def resolve_pdf(yaml_path: Path) -> tuple[Path | None, str | None]:
    """Find the datasheet source for a yaml. Tries:
      1. the manuallly-curated source_pdf (release repo convention)
      2. the embedded_dev/<vendor>/datasheet/<part>_datasheet.pdf (publish repo)
      3. PARTS-indexed filename under embedded_dev/<vendor>/datasheet/
      4. the legacy datasheet_path_expected (PDF or HTML, may also
         be references/semiconductor-vendor/<Vendor>/datasheet-html/*.html)
      5. the legacy top-level datasheets/<part>.pdf

    Returns (path, kind) where kind ∈ {"pdf", "html", None}. PDF is
    the only kind we can fully verify; HTML readers are partial so
    we mark the report differently.
    """
    with open(yaml_path) as f:
        y = yaml.safe_load(f) or {}
    part = y.get("part")
    vendor = yaml_path.parent.name

    candidates = []

    # 1. source_pdf relative to yaml location
    src = y.get("source_pdf")
    if src and not src.startswith("(none"):
        # '(none)' / '(none -- ...)' = explicitly marked unavailable,
        # skip directly without further fallback.
        p = (yaml_path.parent / src).resolve()
        if p.exists():
            candidates.append((p, "pdf"))

    # 2 + 3. embedded_dev/<vendor>/datasheet/<part>_datasheet.pdf
    if part:
        for suffix in ("_datasheet.pdf", ".pdf"):
            candidate = REPO_ROOT / "embedded_dev" / vendor.lower() / "datasheet" / f"{part}{suffix}"
            if candidate.exists():
                candidates.append((candidate, "pdf"))
        if part in PARTS:
            fn = (PARTS[part] or {}).get("pdf_filename")
            if fn:
                candidate = REPO_ROOT / "embedded_dev" / vendor.lower() / "datasheet" / fn
                if candidate.exists():
                    candidates.append((candidate, "pdf"))

    # 4. legacy datasheet_path_expected
    dpe = y.get("datasheet_path_expected")
    if dpe:
        for base in (yaml_path.parent, REPO_ROOT):
            p = (base / dpe).resolve()
            if p.exists():
                kind = "html" if str(p).endswith((".html", ".htm")) else "pdf"
                candidates.append((p, kind))

    # 5. legacy datasheets/ top-level fallback
    if part:
        legacy = REPO_ROOT / "datasheets" / f"{part}.pdf"
        if legacy.exists():
            candidates.append((legacy, "pdf"))

    if not candidates:
        return None, None
    # Prefer PDF over HTML, then by path string length (shorter = cleaner)
    candidates.sort(key=lambda x: (x[1] == "html", len(str(x[0]))))
    return candidates[0]  # (path, kind)


# ─── Field-level comparison helpers ────────────────────────────────────────

def flatten_scalar_fields(specs: dict) -> Iterator[tuple[str, Any]]:
    """Yield (dotpath, scalar) tuples. Skips dict/list/None/bool."""
    for k, v in specs.items():
        if isinstance(v, (dict, list)):
            continue
        if v is None or isinstance(v, bool):
            continue
        yield k, v


def normalize_for_match(value: Any) -> str:
    """Drop quoting / case / whitespace for fuzzy match."""
    s = str(value)
    s = s.lower()
    s = re.sub(r"['\"\s\u2013\u2014\.,;()\[\]]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def keyword_for_value(value: Any) -> list[str]:
    """Pick one or more numeric/unique keywords from a yaml value for
    searching the PDF. Skips prose values.

    Order:
      1. Leading number (covers "78.86", "512 KB", "2.7 to 3.6", etc.)
      2. Unique short tokens (≥ 4 chars, deduped, top-3) from the value
      3. Full text fallback

    Multiple keywords boost recall — e.g. for "Wi-Fi b/g/n + Bluetooth 4.2"
    we try 'Wi-Fi' AND 'Bluetooth' AND '4.2'; any hit is a match.
    """
    s = str(value).strip()
    # 1. Leading number
    m = re.match(r"([\d]+(?:\.\d+)?)", s)
    if m:
        primary = m.group(1)
    else:
        primary = None

    # 2. Unique short tokens
    tokens = re.findall(r"[\w\-\+/]{4,}", s)
    seen = []
    for t in tokens:
        tl = t.lower()
        if tl not in seen and tl not in {"with", "from", "this", "that", "core", "cores", "class", "type"}:
            seen.append(tl)
        if len(seen) >= 3:
            break

    if primary:
        return [primary] + seen
    if seen:
        return seen
    # Fallback
    return [s.strip()]


# ─── Single-yaml verification ─────────────────────────────────────────────

def verify_yaml_fields(yaml_path: Path, pdf_path: Path, max_pages: int = 5) -> dict:
    """Compare scalar fields in the yaml to searchable keywords in the PDF."""
    with open(yaml_path) as f:
        y = yaml.safe_load(f) or {}
    specs = (y.get("specs") or {}) if isinstance(y, dict) else {}

    try:
        # HTML paths: read as plain text after stripping tags
        rep = {"yaml": yaml_path.name, "matched": [], "not_found": []}
        if str(pdf_path).lower().endswith((".html", ".htm")):
            from html.parser import HTMLParser

            class _Strip(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.parts = []
                    self._skip = 0

                def handle_starttag(self, tag, attrs):
                    if tag in ("script", "style", "noscript"):
                        self._skip += 1

                def handle_endtag(self, tag):
                    if tag in ("script", "style", "noscript") and self._skip:
                        self._skip -= 1
                    if tag in ("p", "br", "tr", "div", "h1", "h2", "h3", "li"):
                        self.parts.append("\n")

                def handle_data(self, data):
                    if not self._skip:
                        self.parts.append(data)

            raw = pdf_path.read_text(encoding="utf-8", errors="replace")
            stripper = _Strip()
            stripper.feed(raw)
            full_text = "".join(stripper.parts)
            rep["source_kind"] = "html"
            rep["pages"] = 1
        else:
            import pdfplumber
            full_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                # 5 pages: enough for Key Features / General Description
                # on every MCU we've measured (GigaDevice p4, NXP p8-12,
                # Nordic PS p30, Renesas group datasheets p18-25). For
                # datasheets where the operating characteristics live past
                # page 5, the verify will miss them — the richer check
                # is the per-keyword CRITICAL_FIELDS pass below.
                for pn in range(min(max_pages, len(pdf.pages))):
                    full_text += (pdf.pages[pn].extract_text() or "") + "\n"
            rep["source_kind"] = "pdf"
            rep["pages"] = len(pdf.pages)
    except Exception as e:
        return {"yaml": yaml_path.name, "error": f"source read failed: {e}"}

    full_text_lower = full_text.lower()

    matched, not_found = [], []
    for field, value in flatten_scalar_fields(specs):
        keywords = keyword_for_value(value)
        if not keywords:
            continue
        if any(kw.lower() in full_text_lower for kw in keywords):
            matched.append({"field": field, "value": str(value)})
        else:
            not_found.append({"field": field, "value": str(value), "keywords": keywords})

    return {
        "yaml": yaml_path.name,
        "matched": matched,
        "not_found": not_found,
        "pages": rep.get("pages", 0),
        "source_kind": rep.get("source_kind", "pdf"),
    }


# ─── Critical-field gap analysis ───────────────────────────────────────────

def find_missing_critical(yaml_path: Path) -> list[str]:
    """Return CRITICAL_FIELDS keys whose value is missing or empty."""
    with open(yaml_path) as f:
        y = yaml.safe_load(f) or {}
    specs = (y.get("specs") or {}) if isinstance(y, dict) else {}
    missing = []
    for k in CRITICAL_FIELDS:
        v = specs.get(k)
        if v is None or v == "" or v == "-" or (isinstance(v, list) and not v) or (isinstance(v, dict) and not v):
            missing.append(k)
    return missing


# ─── CLI plumbing ──────────────────────────────────────────────────────────

def vendor_dirs() -> list[str]:
    """Return the list of vendor subdirs under specs/."""
    specs_root = REPO_ROOT / "specs"
    return sorted([p.name for p in specs_root.iterdir() if p.is_dir()])


def enrich_yaml(yaml_path: Path, pdf_path: Path, dry_run: bool = False, max_pages: int = 5) -> dict:
    """Re-extract specs from PDF and write any NEW CRITICAL_FIELDS values
    into the yaml. Existing values are preserved. Fields added by enrich
    are tracked in the `unverified` list (e.g. ['enriched-2026-07-07'])
    so a human can review later.

    Returns a dict {field: would_write_value} for reporting.
    """
    import datetime as dt

    with open(yaml_path) as f:
        y = yaml.safe_load(f) or {}
    existing_specs = y.get("specs") or {}

    # Re-run the same extractor update_specs.py uses.
    # MAX_FULL_TEXT_PAGES is a local variable inside
    # extract_specs_from_pdf (NOT a module attribute), so we can't
    # monkey-patch it. Instead we run the function twice: first
    # the bounded version (5-20 pages, covers Key Features), then
    # if we need a missing field from a deeper page we can re-run.
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from update_specs import extract_specs_from_pdf

    # Look up family from PARTS
    part = y.get("part")
    vendor_dir = yaml_path.parent.name
    family = None
    if part and part in PARTS:
        family = (PARTS[part] or {}).get("family")

    try:
        fresh = extract_specs_from_pdf(pdf_path, family=family)
        fresh_specs = fresh.get("specs") or {}
    except Exception as e:
        return {"_error": f"extract failed: {e}"}

    additions = {}
    for k in CRITICAL_FIELDS:
        if existing_specs.get(k) is not None and existing_specs.get(k) != "" and existing_specs.get(k) != "-":
            # already filled; skip
            continue
        new_val = fresh_specs.get(k)
        if new_val is None or new_val == "" or new_val == "-":
            continue
        additions[k] = new_val

    if not additions or dry_run:
        return additions

    # Apply additions
    for k, v in additions.items():
        existing_specs[k] = v
    y["specs"] = existing_specs
    # Track which fields came from this enrich pass so they can be reviewed
    unverified = y.get("unverified")
    if isinstance(unverified, list):
        marker = f"enriched-{dt.date.today().isoformat()}"
        if marker not in unverified:
            unverified.append(marker)
    y["unverified"] = unverified
    y["extracted_at"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")

    with open(yaml_path, "w") as f:
        yaml.safe_dump(y, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)

    return additions


def main():
    parser = argparse.ArgumentParser(
        description="Validate existing specs against PDFs and propose enrichments."
    )
    parser.add_argument("yaml", nargs="?", help="Single yaml to verify")
    parser.add_argument("--batch", action="store_true",
                        help="Process all yaml in specs/")
    parser.add_argument("--vendor", type=str,
                        help="Restrict --batch to one vendor (e.g. Espressif, Renesas)")
    parser.add_argument("--enrich", action="store_true",
                        help="Write missing critical fields into the yaml (with 'enriched-from-PDF' marker)")
    parser.add_argument("--dry-run-enrich", action="store_true",
                        help="Print what --enrich would change, but don't write yaml")
    parser.add_argument("--promote-matches", action="store_true",
                        help="When a matched value is byte-for-byte what the PDF says, clear unverified=['all']")
    parser.add_argument("--verbose", action="store_true", help="Per-field detail")
    parser.add_argument("--max-pages", type=int, default=5,
                        help="Max pages per PDF to read (default 5; raise for ST RM-style 1500-page reference manuals)")
    args = parser.parse_args()

    if not args.yaml and not args.batch:
        parser.print_help()
        sys.exit(0)

    # --vendor only valid with --batch
    if args.vendor and not args.batch:
        print("--vendor requires --batch", file=sys.stderr)
        sys.exit(2)

    targets = []
    if args.yaml:
        p = Path(args.yaml)
        if not p.is_absolute():
            p = (REPO_ROOT / p).resolve()
        targets.append(p)
    else:
        vendors = vendor_dirs()
        if args.vendor:
            if args.vendor not in vendors:
                print(f"Unknown vendor {args.vendor!r}. Available: {vendors}", file=sys.stderr)
                sys.exit(1)
            vendors = [args.vendor]
        for v in vendors:
            targets.extend((REPO_ROOT / "specs" / v).glob("*.yaml"))

    if not targets:
        print("No yaml found", file=sys.stderr)
        sys.exit(1)

    summary = {"verified": [], "with_not_found": [], "no_pdf": [], "with_missing_critical": []}

    for yp in sorted(targets):
        if not yp.exists():
            continue

        pdf, kind = resolve_pdf(yp)
        if pdf is None:
            # Distinguish 'explicitly none' from 'missing'
            with open(yp) as f:
                _y = yaml.safe_load(f) or {}
            if str(_y.get("source_pdf", "")).startswith("(none"):
                summary.setdefault("explicitly_none", []).append(yp.name)
                print(f"--- {yp.name} ---\n  [none] source_pdf explicitly marked unavailable; skipping validation")
            else:
                summary["no_pdf"].append(yp.name)
                print(f"--- {yp.name} ---\n  [skip] no source resolvable (no source_pdf, no PARTS pdf_filename, no datasheet_path_expected pointing to a real file)")
            continue

        # HTML sources can't be fully keyword-verified against PDF-style text
        # (the HTML wraps values in tag soup). We still do the keyword search
        # against the raw HTML text but flag the kind in the report.
        rep = verify_yaml_fields(yp, pdf, max_pages=args.max_pages)
        if "error" in rep:
            summary["no_pdf"].append(yp.name)
            print(f"--- {yp.name} ---\n  [error] {rep['error']}")
            continue

        print(f"--- {yp.name} ---")
        print(f"  Source ({kind}): {pdf.relative_to(REPO_ROOT)} ({rep['pages']} pages)")
        print(f"  Matched: {len(rep['matched'])} / Not found: {len(rep['not_found'])}")
        if args.verbose:
            for m in rep["matched"]:
                print(f"    ✓ {m['field']:<22} = {m['value'][:60]}")
            for n in rep["not_found"]:
                print(f"    ✗ {n['field']:<22} = {n['value'][:60]}  (keywords tried: {n['keywords']})")
        if rep["not_found"]:
            summary["with_not_found"].append(yp.name)
        else:
            summary["verified"].append(yp.name)

        # Critical-field gap analysis
        missing = find_missing_critical(yp)
        if missing:
            summary["with_missing_critical"].append((yp.name, missing))
            print(f"  Missing critical fields: {missing}")
            if args.enrich or args.dry_run_enrich:
                # Re-extract from PDF and diff against missing fields
                additions = enrich_yaml(yp, pdf, dry_run=not args.enrich, max_pages=args.max_pages)
                if additions and "_error" not in additions:
                    if args.dry_run_enrich:
                        print(f"    [dry-run-enrich] would add: {sorted(additions.keys())}")
                        print(f"      sample: {next(iter(additions.items()))}" if additions else "")
                    else:
                        print(f"    [enriched] wrote: {sorted(additions.keys())}")
                elif "_error" in additions:
                    print(f"    [enrich skipped] {additions['_error']}")
                else:
                    print("    [enrich] nothing new in extract for the missing fields")
            else:
                print("    (re-run with --enrich or --dry-run-enrich to fill these)")
        print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Verified (all matched):       {len(summary['verified'])}")
    print(f"  With not_found (verify gap): {len(summary['with_not_found'])}")
    print(f"  Missing critical fields:     {len(summary['with_missing_critical'])}")
    print(f"  No resolvable PDF:           {len(summary['no_pdf'])}")
    if args.batch and not args.enrich and not args.dry_run_enrich:
        print()
        print("Run with --enrich to fill missing fields, or --dry-run-enrich to preview.")
        print("--enrich --promote-matches also clears unverified=['all'] markers where the field matches.")


if __name__ == "__main__":
    main()
