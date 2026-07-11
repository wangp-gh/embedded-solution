#!/usr/bin/env python3
"""
catalog_audit.py — walk every yaml under specs/ and bucket by trust tier.

Reproduces the 2026-07-08 catalog status report (CATALOG-STATUS-2026-07-08.md).

Usage:
    cd specs && python3 ../scripts/catalog_audit.py

Output sections (printed in order):
    1. Overall trust distribution
    2. Per-vendor trust breakdown
    3. Issues:
        A. source_pdf: (none)        — explicit unavailability marker
        B. no source_pdf field       — phase1-recovery didn't backfill
        C. DEAD                       — product page removed
        D. PARTIAL                    — frontpage-only
        E. FAMILY-ONLY                — not part-specific, design risk
        F. HTML-MIRROR                — lower trust than HTML-direct
        G. OLD LABEL                  — pre-trust-tier scheme
        H. DA BLE page-1              — inconsistent label scheme
        I. link_status field missing  — uses verified_by_human instead
    4. Recovery actions table
"""
from __future__ import annotations
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Optional


def categorize(link: str) -> str:
    """Map a link_status string to a trust-tier bucket."""
    if "datasheet-pdf-vendor-direct-extracted" in link:
        return "PDF-vendor-direct (HIGH)"
    if "datasheet-pdf-extracted" in link and "page-1 extractor" not in link:
        return "PDF-vendor-direct (HIGH)"
    if "datasheet-pdf-mirror-extracted" in link:
        return "PDF-mirror (HIGH-equiv)"
    if "datasheet-html-extracted" in link and "mirror" not in link:
        return "HTML-vendor-direct (MEDIUM-HIGH)"
    if "datasheet-html-mirror-extracted" in link:
        return "HTML-mirror (MEDIUM)"
    if "datasheet-pdf-extracted, dedicated page-1 extractor" in link:
        return "PDF-vendor-direct (HIGH) — page-1 extractor"
    if "family-overview-via-crawl" in link:
        return "Family-overview-crawl (MEDIUM-LOW, not part-specific)"
    if "family-page-extract" in link and "NOT-RECOMMENDED" in link:
        return "Family-page-extract (LOW, NOT-RECOMMENDED)"
    if "family-page-extract" in link:
        return "Family-page-extract (MEDIUM-LOW, not part-specific)"
    if "partial_verified" in link:
        return "PARTIAL (frontpage-only)"
    if "no-datasheet" in link:
        return "DEAD (no product page, no datasheet)"
    if "verified_2026-06-27" in link:
        return "verified_2026-06-27 (OLD label, pre-trust-tier)"
    if "pending-datasheet" in link:
        return "PENDING-DATASHEET (no source available, awaiting PDF)"
    return f"OTHER: {link[:60]}"


def main(root: str = ".") -> int:
    ALL = []
    PER_VENDOR = defaultdict(Counter)

    SOURCE_NONE = []
    NO_SP = []
    DEAD = []
    PARTIAL = []
    FAMILY_RISK = []
    HTML_ONLY = []
    MIRROR_HTML = []
    PAGE1_DA = []
    OLD_LABEL = []
    LINK_MISSING = []
    OTHER_CAT = []

    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".yaml"):
                continue
            p = os.path.join(dirpath, fn)
            with open(p) as f:
                text = f.read()
            parts = p.split(os.sep)
            vendor = parts[1] if len(parts) > 2 else "?"
            link_m = re.search(r"^link_status:\s*(.+)$", text, re.M)
            sp_m = re.search(r"^source_pdf:\s*(.+)$", text, re.M)
            link = link_m.group(1).strip() if link_m else "(missing)"
            sp = sp_m.group(1).strip() if sp_m else None
            cat = categorize(link)
            PER_VENDOR[vendor][cat] += 1
            ALL.append((p, vendor, link, cat, sp))

            if link_m is None:
                LINK_MISSING.append(p)
            if sp and sp.startswith("(none"):
                SOURCE_NONE.append(p)
            elif sp is None:
                NO_SP.append((p, link))
            if "no-datasheet" in link:
                DEAD.append(p)
            if "partial_verified" in link:
                PARTIAL.append(p)
            if "family-" in link:
                FAMILY_RISK.append((p, link))
            if "datasheet-html-extracted" in link and "mirror" not in link:
                HTML_ONLY.append(p)
            if "datasheet-html-mirror-extracted" in link:
                MIRROR_HTML.append(p)
            if "page-1 extractor" in link:
                PAGE1_DA.append(p)
            if "verified_2026-06-27" in link:
                OLD_LABEL.append(p)
            if cat.startswith("OTHER:") and "missing" not in link:
                OTHER_CAT.append((p, link))

    # --- Output ---
    print("=" * 82)
    print("EMBEDDED-SOLUTION CATALOG: 125 YAML ANALYSIS")
    print("=" * 82)
    print()
    print("OVERALL TRUST DISTRIBUTION")
    print("-" * 82)
    ALL_CATS = Counter([x[3] for x in ALL])
    for cat, c in ALL_CATS.most_common():
        print(f"  {c:3d}  {cat}")
    print(f"  ---")
    print(f"  {sum(ALL_CATS.values()):3d}  TOTAL")
    print()

    print("=" * 82)
    print("PER-VENDOR TRUST BREAKDOWN")
    print("=" * 82)
    header = f"{'vendor':14s}  {'PDF-HI':>7} {'PDF-MIR':>7} {'PDF-DA':>6} {'HTML-HI':>7} {'HTML-MIR':>8} {'FAM':>4} {'PART':>4} {'DEAD':>4} {'OLD':>4} {'PEND':>5}  total"
    print(header)
    print("-" * 82)
    grand = Counter()
    for v, ctr in sorted(PER_VENDOR.items()):
        pdf_hi = ctr.get("PDF-vendor-direct (HIGH)", 0)
        pdf_mir = ctr.get("PDF-mirror (HIGH-equiv)", 0)
        pdf_da = ctr.get("PDF-vendor-direct (HIGH) — page-1 extractor", 0)
        html_hi = ctr.get("HTML-vendor-direct (MEDIUM-HIGH)", 0)
        html_mir = ctr.get("HTML-mirror (MEDIUM)", 0)
        fam = (
            ctr.get("Family-overview-crawl (MEDIUM-LOW, not part-specific)", 0)
            + ctr.get("Family-page-extract (MEDIUM-LOW, not part-specific)", 0)
            + ctr.get("Family-page-extract (LOW, NOT-RECOMMENDED)", 0)
        )
        part = ctr.get("PARTIAL (frontpage-only)", 0)
        dead = ctr.get("DEAD (no product page, no datasheet)", 0)
        old = ctr.get("verified_2026-06-27 (OLD label, pre-trust-tier)", 0)
        pending = ctr.get("PENDING-DATASHEET (no source available, awaiting PDF)", 0)
        tot = sum(ctr.values())
        print(
            f"{v:14s}  {pdf_hi:>7} {pdf_mir:>7} {pdf_da:>6} {html_hi:>7} {html_mir:>8} {fam:>4} {part:>4} {dead:>4} {old:>4} {pending:>4}  {tot:>5}"
        )
        for k, v2 in ctr.items():
            grand[k] += v2
    print("-" * 82)

    def g(k):
        return grand.get(k, 0)

    fam_total = (
        g("Family-overview-crawl (MEDIUM-LOW, not part-specific)")
        + g("Family-page-extract (MEDIUM-LOW, not part-specific)")
        + g("Family-page-extract (LOW, NOT-RECOMMENDED)")
    )
    print(
        f"{'TOTAL':14s}  {g('PDF-vendor-direct (HIGH)'):>7} {g('PDF-mirror (HIGH-equiv)'):>7} {g('PDF-vendor-direct (HIGH) — page-1 extractor'):>6} {g('HTML-vendor-direct (MEDIUM-HIGH)'):>7} {g('HTML-mirror (MEDIUM)'):>8} {fam_total:>4} {g('PARTIAL (frontpage-only)'):>4} {g('DEAD (no product page, no datasheet)'):>4} {g('verified_2026-06-27 (OLD label, pre-trust-tier)'):>4} {g('PENDING-DATASHEET (no source available, awaiting PDF)'):>5}  {sum(grand.values()):>5}"
    )
    print()
    print("=" * 82)
    print("ISSUES — must address before next release")
    print("=" * 82)
    print()

    # A
    print(f"### A. SOURCE_PDF: (none) — explicit unavailability marker ({len(SOURCE_NONE)} yaml)")
    for p in SOURCE_NONE:
        print(f"  - {p}")
    print()

    # B
    print(f"### B. NO source_pdf field at all ({len(NO_SP)} yaml)")
    print(f"   Field is OPTIONAL (introduced 2026-07-05 phase1-recovery). Working 'on honor'.")
    print(f"   {len(NO_SP)} files; samples (first 20):")
    for p, link in NO_SP[:20]:
        print(f"  - {p}    [{link[:60]}]")
    if len(NO_SP) > 20:
        print(f"  ... ({len(NO_SP) - 20} more)")
    print()

    # C
    print(f"### C. DEAD: {len(DEAD)} yaml")
    for p in DEAD:
        print(f"  - {p}")
    print()

    # D
    print(f"### D. PARTIAL: {len(PARTIAL)} yaml")
    for p in PARTIAL:
        print(f"  - {p}")
    print()

    # E
    print(f"### E. FAMILY-ONLY: {len(FAMILY_RISK)} yaml")
    for p, l in FAMILY_RISK:
        print(f"  - {p}")
        print(f"      {l[:90]}")
    print()

    # F
    print(f"### F. HTML-MIRROR: {len(MIRROR_HTML)} yaml")
    for p in MIRROR_HTML:
        print(f"  - {p}")
    print()

    # G
    print(f"### G. OLD LABEL: {len(OLD_LABEL)} yaml")
    for p in OLD_LABEL:
        print(f"  - {p}")
    print()

    # H
    print(f"### H. DA BLE page-1 extractor: {len(PAGE1_DA)} yaml with inconsistent label")
    for p in PAGE1_DA:
        print(f"  - {p}")
    print()

    # I
    print(f"### I. LINK_STATUS field missing: {len(LINK_MISSING)} yaml")
    for p in LINK_MISSING:
        print(f"  - {p}")
    print()

    # PENDING-DATASHEET
    pending = [x for x in ALL if "pending-datasheet" in x[2]]
    print(f"### J. PENDING-DATASHEET (no source available, awaiting PDF): {len(pending)} yaml")
    for p, _, link, _, _ in pending:
        print(f"  - {p}    [{link[:80]}]")
    print()

    # OTHER_CAT (unrecognized link_status)
    if OTHER_CAT:
        print(f"### K. OTHER (unrecognized link_status): {len(OTHER_CAT)} yaml")
        for p, link in OTHER_CAT:
            print(f"  - {p}  →  {link[:80]}")
        print()

    # Summary
    print("=" * 82)
    print("RECOVERY ACTIONS — prioritized")
    print("=" * 82)
    print(f"  A. {len(SOURCE_NONE)} source_pdf=none:  DONE (5fcc341, awaiting publish bump)")
    print(f"  B. {len(NO_SP)} yaml without source_pdf field:  backfill, low priority")
    print(f"  C. {len(DEAD)} DEAD:  acknowledge as EOL in catalog README")
    print(f"  D. {len(PARTIAL)} PARTIAL:  re-run validate_and_enrich with MAX_FULL_TEXT_PAGES=0")
    print(f"  E. {len(FAMILY_RISK)} FAMILY-ONLY:  mark with design-risk note in catalog README")
    print(f"  F. {len(MIRROR_HTML)} HTML-MIRROR:  retry round 1 vendor-direct")
    print(f"  G. {len(OLD_LABEL)} OLD LABEL:  re-label to 2026-07-XX")
    print(f"  H. {len(PAGE1_DA)} DA BLE page-1:  label-normalize to 2026-07-07")
    print(f"  I. {len(LINK_MISSING)} LINK_MISSING:  uses verified_by_human, NOT an issue")
    print(f"  J. {len([x for x in ALL if 'pending-datasheet' in x[2]])} PENDING-DATASHEET:  waiting on vendor-published PDF, NOT an issue (correctly labeled)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
