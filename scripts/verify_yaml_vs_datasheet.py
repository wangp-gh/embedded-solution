#!/usr/bin/env python3
"""verify_yaml_vs_datasheet.py — extract spec values from PDF and compare to yaml.

For each yaml in the pending-datasheet list:
1. Open the local datasheet PDF
2. Extract all text via pdfplumber
3. For each scalar spec field in the yaml, search the PDF text for a
   matching keyword/value
4. Output a comparison report showing match / mismatch / not-found

Usage:
    python3 scripts/verify_yaml_vs_datasheet.py specs/SGMicro/SGM3157.yaml
    python3 scripts/verify_yaml_vs_datasheet.py --batch
"""
from __future__ import annotations
import re
import sys
import json
import yaml
from pathlib import Path
from typing import Any, Iterator

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Run: pip install pdfplumber")
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent.parent


def _flat_spec_fields(specs: dict, prefix: str = "") -> Iterator[tuple[str, Any]]:
    """Flatten nested dict into (dot.path, scalar_value) pairs.
    Skips list values, dict values, None, bool, and sentinel/prose values.
    """
    for k, v in specs.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            yield from _flat_spec_fields(v, path)
        elif isinstance(v, list):
            # Skip list values — they're usually 'use_cases', 'protocols',
            # 'protocols_in_rom', etc. which need different verification
            continue
        elif v is None:
            continue
        elif isinstance(v, bool):
            # Skip bool — PDF can't directly verify True/False
            continue
        else:
            # Skip sentinel/prose fields per _skip_value rules
            if _skip_value(v, path):
                continue
            yield path, v


def _value_search_terms(value: Any) -> list[str]:
    """Generate candidate search terms for a given scalar value.

    For numbers: return both the raw int/float and common suffix variants
    (e.g. 5.5 -> ['5.5', '5.5V', '5.5 V', '+5.5', '5,5']).
    For strings: return the string itself + lowercase.
    """
    terms = []
    if isinstance(value, (int, float)):
        # Raw
        terms.append(f"{value}")
        # As float
        if isinstance(value, float):
            terms.append(f"{value:.1f}")
            terms.append(f"{value:g}")
        # Common suffix variants
        if "." in str(value):
            terms.append(f"{value}V")
            terms.append(f"{value} V")
        # Negative number: '+5.5' notation sometimes
        if value < 0:
            terms.append(f"{value:+}")
            terms.append(f"{abs(value)}")
    elif isinstance(value, str):
        terms.append(value)
        terms.append(value.lower())
        # If string contains numbers, also try those
        for num_match in re.findall(r"\d+\.?\d*", value):
            terms.append(num_match)
    return terms


def _extract_primary_number(value: str) -> str | None:
    """Extract the first numeric token from a value string.

    Examples:
      '5.0' -> '5.0'
      '2048 KB' -> '2048'
      '6468 (across both cores)' -> '6468'
      '118.75' -> '118.75'
      '-80 dBm' -> '-80'
      'Bluetooth 5' -> None (no leading number)
    """
    # Match a leading number (with optional sign and decimal)
    m = re.match(r"^(-?\d+\.?\d*)", str(value).strip())
    if m:
        return m.group(1)
    return None


def _skip_value(value: Any, path: str) -> bool:
    """Skip values that are sentinel / descriptive / don't have a numeric match."""
    if value is None:
        return True
    sval = str(value).strip()
    # Skip Yes/No/None sentinels (don't appear as strings in datasheets)
    if sval.lower() in ("none", "yes", "no", "true", "false", "n/a", "tbd"):
        return True
    # Skip descriptive / prose fields (long strings > 40 chars)
    if len(sval) > 50:
        return True
    # Skip fields whose name suggests prose/description
    if any(suffix in path for suffix in [".description", ".topology", ".function", ".notes"]):
        return True
    if path.endswith(("function", "topology", "rating")):
        return True
    return False


def _is_keyword_in_text(keyword: str, full_text: str, full_text_lower: str) -> bool:
    """Loose matching: case-insensitive, allows +/- whitespace."""
    kw = keyword.strip()
    if not kw:
        return False
    if kw in full_text:
        return True
    if kw.lower() in full_text_lower:
        return True
    # Try with various whitespace
    kw_flex = re.escape(kw).replace(r"\ ", r"\s*")
    if re.search(kw_flex, full_text, re.IGNORECASE):
        return True
    # Try primary-number search: extract first number from value, search
    primary = _extract_primary_number(kw)
    if primary:
        # Exact number boundary: \b<num>\b
        if re.search(r"\b" + re.escape(primary) + r"\b", full_text):
            return True
    # Last resort: loose substring of the raw value (covers 'Bluetooth 5'
    # matching for ble_version '5.0' due to 'Bluetooth 5' having the number 5)
    # This is intentionally loose — we want presence-not-precision here.
    return False


def verify_yaml(yaml_path: Path) -> dict:
    """Extract PDF + check yaml fields. Return report dict."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    specs = data.get("specs", {})
    if not specs:
        return {"yaml": str(yaml_path), "error": "no specs block", "results": []}

    # Find PDF
    ds_rel = data.get("datasheet_path_expected", "")
    if ds_rel:
        # Resolve relative path (relative to yaml file dir)
        yaml_dir = yaml_path.parent
        ds_path = (yaml_dir / ds_rel).resolve()
    else:
        ds_path = None
    if not ds_path or not ds_path.exists():
        return {
            "yaml": str(yaml_path.relative_to(REPO_ROOT)),
            "datasheet": str(ds_path) if ds_path else "(missing datasheet_path_expected)",
            "error": "datasheet PDF not found",
            "results": [],
        }

    # Skip overly large PDFs (>5 MB) to avoid hangs
    size_mb = ds_path.stat().st_size / 1024 / 1024
    if size_mb > 5.0:
        return {
            "yaml": str(yaml_path.relative_to(REPO_ROOT)),
            "datasheet": str(ds_path.relative_to(REPO_ROOT)),
            "size_mb": round(size_mb, 1),
            "error": f"PDF too large ({size_mb:.1f} MB > 5 MB) — skipped",
            "results": [],
        }

    # Extract PDF text (limit to first 20 pages to avoid hangs on huge PDFs)
    with pdfplumber.open(ds_path) as pdf:
        page_count = len(pdf.pages)
        pages_to_use = pdf.pages[: min(page_count, 20)]
        full_text = "\n".join(p.extract_text() or "" for p in pages_to_use)
    full_text_lower = full_text.lower()

    # Verify each scalar field
    results = []
    matched = 0
    not_found = 0
    for path, value in _flat_spec_fields(specs):
        terms = _value_search_terms(value)
        # Also try the original raw value
        raw_match = _is_keyword_in_text(str(value), full_text, full_text_lower)
        if raw_match:
            results.append({"path": path, "value": value, "status": "match", "term": str(value)})
            matched += 1
        else:
            # Try alternative terms
            alt_match = None
            for term in terms[1:]:
                if _is_keyword_in_text(term, full_text, full_text_lower):
                    alt_match = term
                    break
            if alt_match:
                results.append({"path": path, "value": value, "status": "match", "term": alt_match})
                matched += 1
            else:
                results.append({"path": path, "value": value, "status": "not_found", "term": None})
                not_found += 1

    return {
        "yaml": str(yaml_path.relative_to(REPO_ROOT)),
        "datasheet": str(ds_path.relative_to(REPO_ROOT)),
        "pages": page_count,
        "pages_used": len(pages_to_use),
        "matched": matched,
        "not_found": not_found,
        "results": results,
    }


def format_report(report: dict, verbose: bool = False) -> str:
    out = []
    out.append(f"=== {report['yaml']} ===")
    if "error" in report:
        out.append(f"  ERROR: {report['error']}")
        return "\n".join(out)
    out.append(f"  Datasheet: {report['datasheet']} ({report['pages']} pages)")
    out.append(f"  Matched: {report['matched']}    Not found: {report['not_found']}")
    if verbose:
        for r in report["results"]:
            status_marker = "✓" if r["status"] == "match" else "✗"
            term_info = f"  (term: {r['term']})" if r["term"] and r["term"] != str(r["value"]) else ""
            out.append(f"    {status_marker}  {r['path']:40s} = {r['value']!r}{term_info}")
    return "\n".join(out)


def _verify_with_timeout(yaml_path: Path, timeout_sec: int = 30, verbose: bool = False) -> dict:
    """Run verify_yaml in a subprocess with hard timeout to avoid hangs."""
    import subprocess
    cmd = ["python3", str(Path(__file__).absolute()), str(yaml_path)]
    if verbose:
        cmd.append("--verbose")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=timeout_sec
        )
        # Re-parse the script's output
        out = result.stdout
        # The script outputs the report, then SUMMARY
        # Re-parse the matched/not_found
        import re
        m = re.search(r"Matched:\s*(\d+)\s+Not found:\s*(\d+)", out)
        ds_name = re.search(r"Datasheet:\s*(\S+)\s+\((\d+)\s+pages", out)
        if m:
            return {
                "yaml": yaml_path.name,
                "matched": int(m.group(1)),
                "not_found": int(m.group(2)),
                "pages": int(ds_name.group(2)) if ds_name else None,
                "output": out,
            }
        # Check for error
        if "ERROR:" in out or "datasheet PDF not found" in out:
            return {"yaml": yaml_path.name, "error": out.split("ERROR:")[-1].strip()[:100] if "ERROR:" in out else "no datasheet"}
        return {"yaml": yaml_path.name, "error": f"no parse: {out[:200]}"}
    except subprocess.TimeoutExpired:
        return {"yaml": yaml_path.name, "error": f"TIMEOUT (> {timeout_sec}s)"}
    except Exception as e:
        return {"yaml": yaml_path.name, "error": str(e)[:100]}


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    if args[0] == "--batch":
        # Verify all yaml in specs/ that have datasheet
        vendor_dirs = ["ST", "NXP", "TI", "Espressif", "WCH", "GigaDevice", "SGMicro", "Silergy", "SiliconLabs", "Nordic", "Renesas"]
        yaml_paths = []
        for vd in vendor_dirs:
            yaml_paths.extend(REPO_ROOT.glob(f"specs/{vd}/*.yaml"))
        verbose = "--verbose" in args
    else:
        yaml_paths = [Path(args[0])]
        verbose = "--verbose" in args

    total_matched = 0
    total_not_found = 0
    yaml_with_results = []
    yaml_with_errors = []

    for yp in sorted(yaml_paths):
        if not yp.exists():
            print(f"SKIP: {yp} (not found)")
            continue
        yp = yp.resolve()
        # For batch mode, use subprocess with timeout to avoid hangs
        if args[0] == "--batch":
            result = _verify_with_timeout(yp, timeout_sec=30, verbose=verbose)
            if "error" in result:
                yaml_with_errors.append(yp.name)
                print(f"=== {yp.name} ===\n  ERROR: {result['error']}")
                continue
            yaml_with_results.append(yp.name)
            print(f"=== {yp.name} ===")
            print(f"  Pages: {result.get('pages')}  Matched: {result['matched']}  Not found: {result['not_found']}")
            if verbose:
                print(result['output'])
            total_matched += result['matched']
            total_not_found += result['not_found']
            print()
        else:
            report = verify_yaml(yp)
            if "error" in report:
                yaml_with_errors.append(report["yaml"])
                print(format_report(report))
                continue
            print(format_report(report, verbose=verbose))
            total_matched += report["matched"]
            total_not_found += report["not_found"]
            print()

    print("=" * 60)
    print(f"SUMMARY: {total_matched} matched, {total_not_found} not found across {len(yaml_with_results)} yamls")
    if yaml_with_errors:
        print(f"  Errors ({len(yaml_with_errors)}): {yaml_with_errors}")


if __name__ == "__main__":
    main()
