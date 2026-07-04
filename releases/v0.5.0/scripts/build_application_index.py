#!/usr/bin/env python3
"""build_application_index.py — Auto-generate application solution index.

Walks all solution.md files under `references/application-solution/*/solution.md`
AND all vendor system-solutions under
`references/semiconductor-vendor/*/system-solutions/*.md`, then produces
`references/application-solution/INDEX.md` summarising:

- All application topics catalogued
- For each topic: vendor solutions and BOM chips referenced
- Link status of each chip (✅/❌/⏳) inherited from the vendor's
  product_families.md

The output index is **derived** from existing markdown. No numerical specs
are written into INDEX.md — the index only lists *which* chips are referenced
by *which* application, plus their datasheet path. All numbers stay in the
per-chip YAMLs.

## Usage

    python3 scripts/build_application_index.py
    python3 scripts/build_application_index.py --dry-run
    python3 scripts/build_application_index.py --output /tmp/index.md

## Rules

- This script never invents a chip or application. If a topic is mentioned
  in a system-solutions README but no `solution.md` exists yet, it appears
  in INDEX.md under "⏳ planned" — with an empty BOM list.
- Chip names are extracted from `**BOM Candidates**` markdown tables
  (column 1 = function, column 2 = part number).
- Part numbers in BOMs are matched against
  `references/semiconductor-vendor/<Vendor>/product_families.md` to inherit
  the link status (✅/❌/⏳). Unknown parts get `unknown` status.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Optional

# === Paths ==============================================================
SCRIPT_DIR  = Path(__file__).resolve().parent
SKILL_DIR   = SCRIPT_DIR.parent
APP_DIR     = SKILL_DIR / "references" / "application-solution"
VENDOR_DIR  = SKILL_DIR / "references" / "semiconductor-vendor"
DEFAULT_OUT = APP_DIR / "INDEX.md"

# Pattern: matches a `| Part | ... |` row in a BOM Candidates table.
# Captures the part number (group 1) — typically a chip like DA14531, nRF52840.
# The part can be in column 1 (e.g. `| **DA14531** | ...`) OR column 2 of a
# `| Function | Part | ...` layout. We match either via two alternates.
BOM_ROW_RE = re.compile(
    r"^\|[^|\n]*\|\s*\*\*([^*]+?)\*\*\s*\|",
    re.MULTILINE,
)

# Pattern: matches the first column of a "Planned Topics" or "Solution"
# markdown table in a vendor's system-solutions README. Accepts both
# lower-case slugs ("smart-ring") and mixed-case solution names
# ("DA14531 BLE Beacon reference").
PLANNED_TOPIC_RE = re.compile(
    r"^\|\s*([A-Za-z][A-Za-z0-9 \-_./]+?)\s*\|",   # | <name> | ... |
    re.MULTILINE,
)

# Status tokens used in vendor product_families.md
LINK_STATUS_OK   = "✅"
LINK_STATUS_BAD  = "❌"
LINK_STATUS_PEND = "⏳"


# === Helpers =============================================================

def load_vendor_link_table() -> dict[str, dict[str, str]]:
    """Parse every vendor's product_families.md and return
    {part_number: {"vendor": <Vendor>, "status": <✅/❌/⏳>, "url": <main page>}}.

    Strikethrough parts (~~...~~) are recorded with status ❌. Lines without
    a recognised status token are recorded as ⏳ (pending verification).
    """
    table: dict[str, dict[str, str]] = {}
    if not VENDOR_DIR.exists():
        return table

    for vendor_md in sorted(VENDOR_DIR.glob("*/product_families.md")):
        vendor = vendor_md.parent.name
        text = vendor_md.read_text(encoding="utf-8")

        for line in text.splitlines():
            # Skip blank lines and non-table lines
            if "|" not in line or "---" in line:
                continue
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if not cells:
                continue

            # Row format: **Part** | Status | Main Page | Datasheet Path
            # Status cell is the one containing ✅/❌/⏳ or a strikethrough
            first_cell = cells[0]
            # Detect strikethrough: ~~DA14591~~
            strike = first_cell.startswith("~~") and first_cell.endswith("~~")
            # Part names may contain spaces (e.g. "i.MX RT1064"), dots,
            # and slashes. Capture everything up to the closing **.
            part_match = re.match(r"\*\*(?P<part>[^*]+?)\*\*", first_cell)
            if not part_match:
                continue
            part = part_match.group("part")
            if strike:
                status = LINK_STATUS_BAD
            else:
                # Find status token in any cell
                status = LINK_STATUS_PEND
                for cell in cells[1:4]:
                    if LINK_STATUS_OK in cell:
                        status = LINK_STATUS_OK
                        break
                    if LINK_STATUS_BAD in cell:
                        status = LINK_STATUS_BAD
                        break
            # Try to grab the main page URL (first http link after status)
            url = ""
            for cell in cells[1:4]:
                m = re.search(r"https?://\S+", cell)
                if m:
                    url = m.group(0)
                    break
            table[part] = {"vendor": vendor, "status": status, "url": url}

    return table


def find_solution_files() -> list[Path]:
    """Find all solution.md files under references/application-solution/."""
    if not APP_DIR.exists():
        return []
    return sorted(APP_DIR.glob("*/solution.md"))


def find_planned_topics(vendor: str) -> list[str]:
    """Read system-solutions/README.md for a vendor and extract the planned
    single-vendor solution list (the "Planned Topics" / "Solution" column).

    We only read rows in the section that starts with a heading named
    "Planned Topics" (case-insensitive). This avoids picking up table
    headers and template/usage examples further down the README.
    """
    readme = VENDOR_DIR / vendor / "system-solutions" / "README.md"
    if not readme.exists():
        return []

    text = readme.read_text(encoding="utf-8")

    # Find the start of the planned-topics section
    start_match = re.search(
        r"^#{1,3}\s+Planned\s+Topics\s*$",
        text, re.MULTILINE | re.IGNORECASE,
    )
    if not start_match:
        return []
    after = text[start_match.end():]
    end_match = re.search(r"^#{1,3}\s+", after, re.MULTILINE)
    section = after if not end_match else after[: end_match.start()]

    planned: list[str] = []
    for line in section.splitlines():
        if "|" not in line:
            continue
        if "---" in line:
            continue
        m = PLANNED_TOPIC_RE.match(line)
        if not m:
            continue
        name = m.group(1).strip()
        # Skip common header words that may appear in a Solution/Type/Source table
        if name.lower() in ("solution", "function", "type", "part", "topic",
                            "use case", "source", "hero part(s)", "vendor"):
            continue
        planned.append(name)
    return planned


def find_orphan_topic_dirs() -> list[str]:
    """Find application topic directories under APP_DIR that exist but have
    no `solution.md` yet. These are also 'planned' even if no vendor
    README explicitly lists them — they were created as part of the Phase 3
    framework setup and are awaiting Phase 5 content.
    """
    if not APP_DIR.exists():
        return []
    orphans: list[str] = []
    for sub in sorted(APP_DIR.iterdir()):
        if not sub.is_dir():
            continue
        if not (sub / "solution.md").exists():
            orphans.append(sub.name)
    return orphans


def find_implemented_system_solutions() -> dict[str, list[dict]]:
    """Find vendor-published system-solution markdown files that have been
    actually written (as opposed to just listed in the README's
    Planned Topics table). Returns a dict keyed by vendor; each value is
    a list of dicts with keys: path, title, bom_count.
    """
    out: dict[str, list[dict]] = {}
    if not VENDOR_DIR.exists():
        return out
    for vendor_dir in sorted(VENDOR_DIR.iterdir()):
        if not vendor_dir.is_dir():
            continue
        sys_dir = vendor_dir / "system-solutions"
        if not sys_dir.is_dir():
            continue
        vendor = vendor_dir.name
        items: list[dict] = []
        for md in sorted(sys_dir.glob("*.md")):
            if md.name.lower() == "readme.md":
                continue
            text = md.read_text(encoding="utf-8")
            # Title: first H1
            m = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
            title = m.group(1).strip() if m else md.stem
            # Count BOM rows (same regex as for application solutions)
            bom_count = 0
            in_bom = False
            for line in text.splitlines():
                if re.match(r"^##\s+(?:BOM|Recommended)\b", line, re.IGNORECASE):
                    in_bom = True
                    continue
                if in_bom and re.match(r"^##\s+", line):
                    in_bom = False
                if in_bom and BOM_ROW_RE.match(line):
                    if not re.match(r"^\|\s*(?:[-:]+|Function|Component)\b", line):
                        bom_count += 1
            items.append({
                "path": md,
                "title": title,
                "bom_count": bom_count,
            })
        if items:
            out[vendor] = items
    return out


def extract_bom_from_solution(solution_path: Path) -> dict:
    """Parse a solution.md file and return its metadata.

    Returns:
        {
            "topic": <str>,            # directory name
            "path": <str>,             # relative path from SKILL_DIR
            "overview": <str>,         # first paragraph after "## Overview"
            "source_class": <str|None>,# "Third-party teardowns ..." from quote block
            "bom": [(part, function), ...],  # parts mentioned in BOM tables
        }
    """
    topic = solution_path.parent.name
    text = solution_path.read_text(encoding="utf-8")

    # Overview
    overview = ""
    m = re.search(r"^##\s+Overview\s*$", text, re.MULTILINE)
    if m:
        # Take everything up to the next ## heading
        after = text[m.end():]
        nxt = re.search(r"^##\s+", after, re.MULTILINE)
        overview = after[: nxt.start()].strip() if nxt else after.strip()

    # BOM
    bom: list[tuple[str, str]] = []
    in_bom_section = False
    for line in text.splitlines():
        if re.match(r"^##\s+(?:BOM|Recommended)\b", line, re.IGNORECASE):
            in_bom_section = True
            continue
        if in_bom_section and re.match(r"^##\s+", line):
            in_bom_section = False
        if not in_bom_section:
            continue
        # Skip header row (Function | Part) and separator row (---|---)
        if re.match(r"^\|\s*(?:[-:]+|Function|Component)\b", line):
            continue
        m = BOM_ROW_RE.match(line)
        if m:
            # Find the function: it's the cell BEFORE the **part** cell.
            # If the part is in column 1, function is "—" (no preceding cell).
            # If the part is in column 2, function is the cell content before it.
            cells = [c.strip() for c in line.split("|") if c.strip()]
            part = m.group(1)
            func = ""
            for i, cell in enumerate(cells):
                if f"**{part}**" in cell:
                    if i > 0:
                        func = cells[i - 1].strip("* ")
                    break
            bom.append((part, func))

    # Source class — read the leading blockquote ("> **Source class:** ...")
    # if present. This tells the user whether the BOM is from a third-party
    # teardown (multi-vendor) or from a vendor's own reference design
    # (single-vendor, see system-solutions/ instead).
    source_class: Optional[str] = None
    m = re.search(
        r"^>\s+\*\*Source class:\*\*\s*(.+?)(?:\n|\Z)",
        text, re.MULTILINE,
    )
    if m:
        source_class = m.group(1).strip()

    return {
        "topic": topic,
        "path": str(solution_path.relative_to(SKILL_DIR)),
        "overview": overview,
        "source_class": source_class,
        "bom": bom,
    }


def render_index(solutions: list[dict], planned_by_vendor: dict[str, list[str]],
                 orphan_topics: list[str],
                 impl_system_solutions: dict[str, list[dict]],
                 link_table: dict[str, dict[str, str]],
                 out_path: Path) -> str:
    """Render INDEX.md from collected data. Pure function — no I/O."""
    lines: list[str] = []
    a = lines.append

    a("# Application Solutions Index")
    a("")
    a(f"> **Auto-generated by** `scripts/build_application_index.py` on "
      f"{dt.datetime.now().astimezone().isoformat(timespec='seconds')}.")
    a("> Do not edit by hand — re-run the script after adding or modifying "
      "solution files.")
    a("")
    a("---")
    a("")
    a("## How to read this index")
    a("")
    a("Each topic below points to a `solution.md` with the full BOM and "
      "rationale. The chip list here is just an at-a-glance summary; for any "
      "design decision open the linked `solution.md` and the vendor entry "
      "under `references/semiconductor-vendor/<Vendor>/product_families.md`. "
      "Numerical parameters must be verified against the official vendor "
      "datasheet (see `SKILL.md` → *Verification Before Responding*).")
    a("")
    a("Link status comes from each vendor's `product_families.md`:")
    a("")
    a(f"- {LINK_STATUS_OK}  Product page reachable (HTTP 200)")
    a(f"- {LINK_STATUS_BAD}  Part has been removed/renamed/relocated — do NOT use")
    a(f"- {LINK_STATUS_PEND}  Verification pending — recheck before recommending")
    a("")

    # Implemented solutions
    a("## Implemented Solutions")
    a("")
    if not solutions:
        a("_No `solution.md` files have been written yet. See \"Planned "
          "Solutions\" below for the topic list, and Phase 5 will populate "
          "this section._")
        a("")
    else:
        for sol in sorted(solutions, key=lambda s: s["topic"]):
            a(f"### `{sol['topic']}`")
            a("")
            a(f"- **Path:** `references/application-solution/{sol['topic']}/solution.md`")
            if sol["source_class"]:
                a(f"- **Source class:** {sol['source_class']}")
            a("")
            if sol["overview"]:
                # Indent the first paragraph for readability
                a(sol["overview"].splitlines()[0])
                a("")
            if not sol["bom"]:
                a("_BOM section not yet written — see solution.md_")
            else:
                a("| Function | Part | Vendor | Status | Datasheet |")
                a("|----------|------|--------|--------|-----------|")
                for part, func in sol["bom"]:
                    info = link_table.get(part)
                    if info:
                        vendor = info["vendor"]
                        status = info["status"]
                        ds_path = (VENDOR_DIR / vendor / "system-solutions" /
                                   "_shared").as_posix() + "/"  # placeholder
                        # Use the vendor's product_families.md datasheet path
                        ds_path = f"../../references/semiconductor-vendor/{vendor}/product_families.md"
                        a(f"| {func or '—'} | **{part}** | {vendor} | "
                          f"{status} | [link]({ds_path}) |")
                    else:
                        a(f"| {func or '—'} | **{part}** | _unknown_ | "
                          f"{LINK_STATUS_PEND} | — |")
            a("")

    # Implemented system-solutions (single-vendor)
    a("## Implemented System-Solutions (single-vendor)")
    a("")
    a("Reference designs published by the chip vendor themselves, with "
      "BOMs containing only that vendor's parts. Each entry below is a "
      "markdown file under `references/semiconductor-vendor/<Vendor>/system-solutions/`.")
    a("")
    if not impl_system_solutions:
        a("_No single-vendor system-solutions implemented yet._")
        a("")
    else:
        for vendor, items in sorted(impl_system_solutions.items()):
            a(f"### {vendor}")
            a("")
            for it in items:
                rel = it["path"].relative_to(SKILL_DIR).as_posix()
                a(f"- **{it['title']}** — {it['bom_count']} BOM rows  ")
                a(f"  [`{rel}`](../../{rel})")
            a("")

    # Planned solutions
    a("## Planned (single-vendor reference designs)")
    a("")
    a("Each vendor's `system-solutions/` directory may list planned "
      "single-vendor reference designs in its `README.md`. These are "
      "designs the vendor publishes themselves, with BOMs containing only "
      "that vendor's parts — **distinct** from the multi-vendor "
      "application solutions above.")
    a("")
    if not planned_by_vendor:
        a("_No vendor-specific system-solutions planned yet._")
        a("")
    else:
        for vendor, topics in sorted(planned_by_vendor.items()):
            a(f"### {vendor}")
            a("")
            for t in topics:
                a(f"- `{t}` — see [`{vendor}/system-solutions/README.md`]("
                  f"../../references/semiconductor-vendor/{vendor}/system-solutions/README.md)")
            a("")

    # Coverage summary
    # Two scopes:
    # - Multi-vendor application solutions: per-topic in `application-solution/`
    # - Single-vendor system-solutions: per-vendor in `semiconductor-vendor/<Vendor>/system-solutions/`
    a("## Coverage Summary")
    a("")
    a("**Multi-vendor application solutions** (third-party teardowns) live in "
      "`references/application-solution/<Topic>/solution.md`.")
    a("")
    a("**Single-vendor system-solutions** (vendor-published reference designs) "
      "live in `references/semiconductor-vendor/<Vendor>/system-solutions/<Name>.md`.")
    a("")
    a("| Scope | Implemented | Planned (in README) |")
    a("|-------|-------------|---------------------|")
    n_impl = len(solutions)
    n_plan = sum(len(t) for t in planned_by_vendor.values())
    n_sys_impl = sum(len(items) for items in impl_system_solutions.values())
    a(f"| Multi-vendor (application) | {n_impl} | 0 |")
    a(f"| Single-vendor (system) | {n_sys_impl} | {n_plan} |")
    if impl_system_solutions or planned_by_vendor:
        a("")
        a("**Per-vendor breakdown (single-vendor system-solutions):**")
        a("")
        a("| Vendor | Implemented | Planned |")
        a("|--------|-------------|---------|")
        all_vendors = set(impl_system_solutions.keys()) | set(planned_by_vendor.keys())
        for v in sorted(all_vendors):
            n_i = len(impl_system_solutions.get(v, []))
            n_p = len(planned_by_vendor.get(v, []))
            a(f"| {v} | {n_i} | {n_p} |")
    a("")
    a("---")
    a("")
    a("## Regenerating this index")
    a("")
    a("```bash")
    a("python3 scripts/build_application_index.py")
    a("python3 scripts/build_application_index.py --dry-run   # preview only")
    a("```")
    a("")
    a("The script does **not** invent parts or topics. If a topic is missing "
      "from the output, either no `solution.md` has been written yet, or the "
      "system-solutions README has not been updated. Both are intentional "
      "placeholders — Phase 5 will fill them in.")
    a("")

    text = "\n".join(lines)
    return text


# === Main ================================================================

def main():
    parser = argparse.ArgumentParser(description="Build application-solution INDEX.md")
    parser.add_argument("--output", default=str(DEFAULT_OUT),
                        help=f"Output path (default: {DEFAULT_OUT})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the index to stdout, do not write")
    args = parser.parse_args()

    link_table = load_vendor_link_table()
    print(f"[info] loaded {len(link_table)} chips from vendor product_families.md")

    solutions = []
    for sf in find_solution_files():
        sol = extract_bom_from_solution(sf)
        solutions.append(sol)
        print(f"[info] found solution: {sol['topic']} ({len(sol['bom'])} BOM rows)")

    planned_by_vendor: dict[str, list[str]] = {}
    for vendor_dir in sorted(VENDOR_DIR.glob("*/")):
        if not vendor_dir.is_dir():
            continue
        vendor = vendor_dir.name
        planned = find_planned_topics(vendor)
        if planned:
            planned_by_vendor[vendor] = planned
            print(f"[info] {vendor}: {len(planned)} planned topics")

    orphans = find_orphan_topic_dirs()
    if orphans:
        print(f"[info] orphan topic dirs (no solution.md): {orphans}")

    impl_sys = find_implemented_system_solutions()
    for v, items in impl_sys.items():
        print(f"[info] {v}: {len(items)} implemented system-solutions")

    rendered = render_index(solutions, planned_by_vendor, orphans, impl_sys, link_table, Path(args.output))

    if args.dry_run:
        sys.stdout.write(rendered)
        print("\n[info] --dry-run: nothing written", file=sys.stderr)
        return 0

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"[write] {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
