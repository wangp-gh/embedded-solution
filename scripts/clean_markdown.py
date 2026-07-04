#!/usr/bin/env python3
"""clean_markdown.py — strip nav/footer/ad noise from Firecrawl-scrape output.

Firecrawl-scrape'd vendor product pages typically come back with a lot
of site chrome mixed into the markdown: language switchers, country
selectors, "Save to myST", "Order Direct", navigation, "Quick links",
search widgets, etc. Those inflate file size 5-20× and make downstream
spec extraction noisier.

This script applies a sequence of well-tested, vendor-agnostic
heuristics to keep only the "content" sections:

1. **Repeated-line dedup**: if the same line appears 3+ times in the
   file, drop all but the first occurrence (catches repeating nav
   blocks and "English / 中文 / 日本語" headers).
2. **URL-only lines**: drop lines that are just a markdown link with
   no surrounding prose (`[foo](https://...)` with no other words).
3. **Country/locale lists**: detect and drop the "WorldwideAfricaAsia
   Europe...Afghanistan...Zimbabwe" mega-list that st.com, nxp.com,
   ti.com etc. all emit.
4. **Section anchors below the fold**: identify the "Product overview
   → Description" heading and truncate everything before it (typical
   preamble is just nav + metadata).
5. **Trailing noise**: drop anything after a final "##" heading that
   looks like footer ("Related links", "Support", "Community", etc.).

The output is NOT a perfect semantic extractor. It's a "shrink 678KB
to ~30-80KB of useful content" filter that makes the file readable for
both humans and regex/LLM downstream consumers.

## Usage

    # As a library:
    from clean_markdown import clean
    cleaned = clean(open('/tmp/stm32wb55rg_test.md').read())

    # As a CLI:
    python3 scripts/clean_markdown.py /path/to/input.md -o /path/to/output.md

The cleaner is **idempotent** — running it twice produces the same
output as running it once.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


# ===== Tunables (vendor-agnostic, empirically chosen) =====

_URL_ONLY_LINE = re.compile(r"^\s*(\[[^\]]*\]\([^)]+\)\s*)+$")

_FOOTER_SECTIONS = (
    "related links",
    "support",
    "community",
    "downloads",
    "tools & software",
    "tools and software",
    "cad resources",
    "quality & reliability",
    "quality and reliability",
    "sample & buy",
    "sample and buy",
    "get started",
    "partner products",
    "sales briefcase",
    "quick links",
    "search tools",
    "search documents",
    "served country",
)

_COUNTRY_WORDS = (
    "Worldwide", "Africa", "Asia", "Europe", "North America", "South America",
    "Oceania", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola",
    "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria",
    "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus",
    "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia",
    "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina", "Burma",
    "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African",
    "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica",
    "Croatia", "Cuba", "Cyprus", "Czech", "Democratic Republic",
    "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor",
    "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea",
    "Estonia", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia",
    "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala",
    "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary",
    "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Israel", "Italy",
    "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
    "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho",
    "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
    "Macedonia", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali",
    "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico",
    "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco",
    "Mozambique", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand",
    "Nicaragua", "Niger", "Nigeria", "Norway", "Oman", "Pakistan", "Palau",
    "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines",
    "Poland", "Portugal", "Qatar", "Romania", "Russian Federation",
    "Rwanda", "Saint Kitts", "Saint Lucia", "Saint Vincent", "Samoa",
    "San Marino", "Sao Tome", "Saudi Arabia", "Senegal", "Serbia",
    "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia",
    "Solomon Islands", "Somalia", "South Africa", "South Korea", "Spain",
    "Sri Lanka", "Sudan", "Suriname", "Swaziland", "Sweden", "Switzerland",
    "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo",
    "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan",
    "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom",
    "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican",
    "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe",
)
_COUNTRY_COUNT_RE = re.compile(
    r"(" + "|".join(re.escape(c) for c in _COUNTRY_WORDS) + r")"
)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

_CONTENT_ANCHOR_HEADINGS = (
    "product overview",
    "description",
    "features",
    "all features",
    "key features",
    "highlights",
    "specifications",
    "datasheet",
    "overview",
)


# ===== Helpers =====

def _is_url_only_line(line: str) -> bool:
    return bool(_URL_ONLY_LINE.match(line))


def _is_country_list(line: str) -> bool:
    matches = _COUNTRY_COUNT_RE.findall(line)
    return len(matches) >= 20


def _is_footer_heading(text: str) -> bool:
    """Match footer headings using WORD-BOUNDARY regex, not substring.

    Substring matching caused false positives like 'support' matching
    'supporting' (Bluetooth SoC descriptions) — see Gap #1 in
    .planning/v0.4.0-resume.md. The fix uses word boundaries so 'support'
    only matches the standalone word.
    """
    tl = text.strip().lower()
    for sec in _FOOTER_SECTIONS:
        # Match the phrase as a whole word/phrase; for multi-word phrases
        # like 'tools & software' require the '&' or 'and' to be present.
        # Use regex with word boundaries; for '&' inside phrase, just
        # check substring + word boundary at start/end.
        pattern = r"(?:^|\b)" + re.escape(sec) + r"(?:$|\b)"
        if re.search(pattern, tl):
            return True
    return False


def _drop_repeats(lines: list[str]) -> list[str]:
    """Drop all but the first occurrence of any line that appears 3+ times."""
    counts = Counter(lines)
    seen_repeats: set[str] = set()
    out = []
    for ln in lines:
        if counts[ln] >= 3:
            if ln in seen_repeats:
                continue
            seen_repeats.add(ln)
            out.append(ln)
        else:
            out.append(ln)
    return out


def _drop_url_only(lines: list[str]) -> list[str]:
    return [ln for ln in lines if not _is_url_only_line(ln)]


def _drop_country_lists(lines: list[str]) -> list[str]:
    return [ln for ln in lines if not _is_country_list(ln)]


def _truncate_before_content(lines: list[str]) -> list[str]:
    """Drop everything before the first 'Product overview' / 'Description' heading."""
    for i, ln in enumerate(lines):
        m = _HEADING_RE.match(ln)
        if not m:
            continue
        heading_text = m.group(2).strip().lower()
        for anchor in _CONTENT_ANCHOR_HEADINGS:
            if heading_text == anchor:
                return lines[i:]
    return lines


def _truncate_after_footer(lines: list[str]) -> list[str]:
    """Drop everything from the first footer heading onward."""
    for i, ln in enumerate(lines):
        m = _HEADING_RE.match(ln)
        if m and _is_footer_heading(m.group(2)):
            return lines[:i]
    return lines


def _collapse_blank_runs(lines: list[str]) -> list[str]:
    out = []
    blank_run = 0
    for ln in lines:
        if not ln.strip():
            blank_run += 1
            if blank_run > 1:
                continue
            out.append(ln)
        else:
            blank_run = 0
            out.append(ln)
    return out


# ===== Main entry =====

def clean(text: str) -> str:
    """Apply the cleaning pipeline to the given markdown text."""
    lines = text.splitlines()
    lines = _drop_repeats(lines)
    lines = _drop_url_only(lines)
    lines = _drop_country_lists(lines)
    lines = _truncate_before_content(lines)
    lines = _truncate_after_footer(lines)
    lines = _collapse_blank_runs(lines)
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n"


# ===== CLI =====

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    in_path = Path(sys.argv[1])
    out_path = None
    if "-o" in sys.argv:
        out_path = Path(sys.argv[sys.argv.index("-o") + 1])
    elif "--out" in sys.argv:
        out_path = Path(sys.argv[sys.argv.index("--out") + 1])
    text = in_path.read_text()
    original_len = len(text)
    cleaned = clean(text)
    cleaned_len = len(cleaned)
    if out_path:
        out_path.write_text(cleaned)
    else:
        sys.stdout.write(cleaned)
    print(
        f"[clean_markdown] {in_path}: "
        f"{original_len} → {cleaned_len} chars "
        f"({100 * cleaned_len / max(original_len, 1):.1f}% retained)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()