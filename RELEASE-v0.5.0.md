# Release v0.5.0 — Concision Cycle + Initial Public Release

**Tag:** `v0.5.0`
**Date:** 2026-07-04
**Codename:** "Lean Public Body — Behavioural Contract, Not Catalogue of History"
**Supersedes:** v0.4.3 (annotated tag on commit `cff01db`)
**Type:** Minor bump — first GitHub-published release

---

## TL;DR

- **First public release** prepared for GitHub + ClawHub (no previous tag was a GitHub release)
- **5 SKILL.md revisions consolidated** since v0.4.3 — total **438 → 281 lines** (-36%)
- **3 new behavioural modes** (HTML-first, capability-driven fetches, fetch-and-cite inline)
- **1 new Anti-pattern** (don't create solution.md by default)
- **8 new application solutions** added to catalogue (11 total; v0.4.3 had 3)
- **110 chips** in catalogue (Renesas / ST / NXP / Nordic / TI / Espressif / GigaDevice / SGMicro / Silergy / SiliconLabs / WCH)
- **Runtime-agnostic** — works with any agent capability matrix (web_fetch, tavily, firecrawl, jina, exec+curl+pdfplumber, etc.)

---

## What This Release Adds

### 1. v0.4.4-patch1 — HTML-first fast path (Tier 3 step 3d)

Vendor product pages (`renesas.com/<part>`, `st.com/...`, `nxp.com/products/<part>`) render headline spec blocks without requiring a 35 MB PDF download. The skill now prefers this fast path for "compare 3-7 chips on headline specs" tasks.

| Old (PDF path) | New (HTML-first) |
|----------------|------------------|
| 30-90 s / part | 5-10 s / part |
| 6-35 MB / part | 1 MB markdown text |
| Triggers pdfplumber | Tavily basic / web_fetch text |

Validated live: 3 BLE SoCs (Nordic nRF5340, Renesas DA14706, TI CC2640R2F) fetched in **12.3 s** total, with 17+ headline specs per chip, fully cited as `[D-HTML @ tier 2]`.

### 2. v0.4.4-patch2 — Capability-driven tool selection

The previous SKILL.md hard-coded `web_fetch`, `tavily_extract`, and `pdfplumber` by name, which broke when an agent runtime lacked one of them. v0.4.4-patch2 replaces these with **4-tier capability ladders** for both PDF fetch (3c: Tier A/B/C) and HTML fetch (3d: Tier 1-4). Any tool satisfying the capability contract qualifies at that tier.

| Capability | Tools that qualify (any one) |
|------------|------------------------------|
| URL → markdown directly | web_fetch extractMode=markdown, Firecrawl MCP, Jina Reader, r.jina.ai CLI |
| Keyword-routed page extraction | tavily_extract extract_depth=basic, web_fetch text + HTML-strip |
| Raw HTTP body | exec curl, exec wget |
| Server-side PDF repair (truncated downloads) | tavily_extract advanced, Firecrawl scrape, Jina Reader |
| Direct PDF download + local parse | curl + pdfplumber, curl + pdftotext |

Verified live: a partial tool stack (no web_fetch, but tavily_extract + exec curl + pdfplumber) successfully ran the full Step 4 4-tier walk on ST STM32WB55. When the HTML path failed (3× Tavily timeouts), the skill **did not** retry the same URL — it fell through to 3c Tier B (curl + pdfplumber) per the patch2 3d → 3c fallback rule.

### 3. v0.4.5 — Skill concision rewrite (438 → 369 lines)

The skill body had accumulated narrative redundancy. v0.4.5 collapsed six rounds of incremental edits:

- Anti-patterns table deduplicated (19 → 15 rows)
- Step 4 (tier-by-tier commands) compressed 93 → ~50 lines, capability-driven 3c/3d preserved
- Step 5 (decision table + 7-dimension defaults + three example blockquotes) merged
- Tier 4 mirror list consolidated to one paragraph (overseas + domestic CN both inline)
- All bilingual Chinese vendor names → English (no Chinese brand fragments anywhere)

Result: **438 → 369 lines (-15.8%)** with no loss of behavioural coverage.

### 4. v0.4.6 — Step 2 no-matching-solution routing (Option A / B / C)

Previously, when `references/application-solution/INDEX.md` had no matching topic, the skill defaulted to "create a new `solution.md`" — which took 20-60 minutes per topic. v0.4.6 introduces three explicit options:

- **Option A — fetch + cite inline (default, recommended).** Generate the answer directly using the Tier 1-4 search path (Step 4) and present it as a comparison table with citations. **Don't create a new solution.md unless explicitly asked.**
- **Option B — curate a new solution file.** Only when the topic recurs or the user asks for a reusable reference design.
- **Option C — disambiguate.** Last-resort one-question ask only when no Step 5 default can be assumed.

A new Anti-pattern added: *"Create a new solution.md by default on every novel topic"* — points at Option A instead.

Validated live on a "wireless microphone SoC" query (catalogue had no match): the skill produced a 3-chip Top-3 comparison in **12 seconds**, citing NXP NXH3675 (fact sheet PDF p.1), Silicon Labs EFR32BG26 (HTML-first), and BlueTrum AB5602C (HTML-first), each cell with a tier marker. **No solution.md was created** — the comparison was complete as a direct response.

### 5. v0.4.7 — Lean public release (369 → 281 lines)

The skill body still described publication / install / changelog metadata. v0.4.7 stripped it down to behaviour only:

- Frontmatter `v0_4_X_highlights` blocks (4 of them) removed → release history belongs in `RELEASE-v0.5.0.md`, not the public skill body
- `## Directory Layout` removed → directory tree is visible after `ls` on install
- `## Privacy / Publishing Notes` removed (5 H3 sub-sections, ~50 lines, including the 4-install-mode matrix and Maintainer note) → behaviour is now driven by the capability-aware Tier 3 fetcher (v0.4.5), so the matrix becomes user-irrelevant
- Two Chinese vendor brand fragments in Tier 4 region-aware rules replaced with Latin transliteration (e.g. "兆易GD / WCH-CH" → "GD / QH")

Result: **369 → 281 lines (-24%)**; 100% English prose; v0.4.4-v0.4.6 behavioural changes still operative.

### 6. v0.4.7-chore — `.gitignore` cleanup

While building the v0.5.0 tarball, a tar-payload check revealed that `references/semiconductor-vendor/*/firecrawl-snapshots/` had been accidentally committed in earlier rounds (130 markdown files). These are maintenance caches regenerated by `scripts/update_specs.py` on demand — they should never ship in a public release.

The `.gitignore` was extended:
```gitignore
references/semiconductor-vendor/*/datasheet/
references/semiconductor-vendor/*/datasheet-html/
references/semiconductor-vendor/*/firecrawl-snapshots/
references/application-solution/.DS_Store
datasheets/   # top-level scratch, alternative cache location
```

130 firecrawl-snapshots files were `git rm --cached`'d (kept on disk for maintenance, removed from the git index). Result: tracked file count 274 → 144.

Tarball size impact: a tarball with the leaked caches was **11 MB**; after this fix it is **178 KB** (-98%).

### 7. New catalogue content (3 → 11 application solutions)

Between v0.4.3 and v0.5.0, eight new `references/application-solution/<topic>/solution.md` files were added:

| Topic | Path | First lines |
|-------|------|-------------|
| fitness-tracker | `references/application-solution/fitness-tracker/solution.md` | Fitness / activity tracker wearable |
| home-security-panel | `references/application-solution/home-security-panel/solution.md` | Home alarm / security control panel |
| industrial-gateway | `references/application-solution/industrial-gateway/solution.md` | Industrial IoT gateway |
| motor-control-blcd | `references/application-solution/motor-control-blcd/solution.md` | BLDC motor controller |
| power-mgmt-pmic-bom | `references/application-solution/power-mgmt-pmic-bom/solution.md` | Multi-rail PMIC BOM |
| smart-watch | `references/application-solution/smart-watch/solution.md` | Multi-function smart watch |
| usb-bridge-adapter | `references/application-solution/usb-bridge-adapter/solution.md` | USB-to-UART / SPI bridge |
| wifi-smart-plug | `references/application-solution/wifi-smart-plug/solution.md` | Wi-Fi smart plug / outlet |

INDEX.md regenerated by `scripts/build_application_index.py` lists all 11 topics. Catalogue touches 110 chips across 11 vendors.

---

## Behavioural Compatibility Matrix (v0.4.3 → v0.5.0)

| Feature | v0.4.3 | v0.5.0 |
|---------|--------|--------|
| Hard-coded tool names (`web_fetch`, `tavily_extract`, `pdfplumber`) | ✅ | ❌ — replaced with capability contracts |
| Step 2 default on novel topic | "Create new solution.md" (20-60 min) | **Option A — fetch + cite inline (60-90 s)** |
| 3d HTML-first fast path | ❌ | ✅ — 5-10 s/headline-spec |
| Tier markers in citation | `[T1]` / `[T4]` only | `[T1]` / `[T4]` / `[D]` / `[D-HTML @ tier N]` / `[~]` |
| Verify-against-datasheet checklist items | 8 | 8 (no behavioural regression) |
| `scripts/test_outofcatalog.py` regression | ✅ | ✅ (untouched) |
| `scripts/build_application_index.py` output | 3 application solutions | 11 application solutions |
| Public release body | 324 lines | 281 lines |

---

## What's NOT in this release

These items stay in the developer's `embedded-solution-publish/` repo but are **never** shipped in the public tarball:

- `specs/` — per-chip YAML database (submodule; private repository)
- `embedded_dev/<v>/datasheet/*.pdf` — downloaded datasheets (~197 MB gzipped), available as a separate `datasheets plug-in`
- `references/semiconductor-vendor/<v>/datasheet/` — vendor-specific mirror PDFs (e.g. Silergy 17 MB)
- `references/semiconductor-vendor/<v>/datasheet-html/` — mirror HTML caches
- `references/semiconductor-vendor/<v>/firecrawl-snapshots/` — firecrawl scrape caches
- `datasheets/` — top-level scratch directory
- `.DS_Store`, `__pycache__/`, `*.pyc`, `scripts/.firecrawl_key`

All of these are `.gitignore`'d at the publish repo level and excluded from the release tarball via `tar czf` exclusion rules.

---

## Validation

This release was validated end-to-end on 2026-07-04:

1. **`scripts/build_application_index.py`** — regenerated INDEX.md, lists 11 application solutions and 110 chips across 11 vendors
2. **HTML-first live test** — 3 BLE SoC product pages fetched in 12.3 s with full `[D-HTML @ tier 2]` citations
3. **Capability-ladder live test** — STM32WB55 HTML failed 3× (Tavily timeouts); fell through to 3c Tier B (curl + pdfplumber, 2.4 s); 9 headline specs extracted from PDF p.1
4. **Option A live test** — "wireless microphone SoC" query (no catalogue match); 3-chip Top-3 comparison produced in 12 s, no `solution.md` created
5. **Top-3 table live test** — Smart-watch comparison (catalogue match); 3-chip Top-3 with tier markers in 28 s total

---

## Rollback

Old `~/.openclaw/workspace/skills/embedded-solution/` (v0.3.3) was backed up at install time as:

```
~/.openclaw/workspace/skills/embedded-solution-bak-v0.3.3-20260704-173925/
```

To roll back:
```bash
cd ~/.openclaw/workspace/skills
rm -rf embedded-solution
mv embedded-solution-bak-v0.3.3-20260704-173925 embedded-solution
```

---

## Commit list (v0.4.4-patch1 → v0.5.0)

```
988e2a5  release(v0.5.0): marketing minor bump after 5-commit concision cycle
9d9ad77  chore(gitignore): exclude maintenance caches from release tarball
36cd052  release(v0.4.7): skill body stripped of changelog + install-mode docs
076d0e6  release(v0.4.6): Step 2 no-matching-solution routing — Option A/B/C
9c1083b  release(v0.4.5): skill concision rewrite — 438 -> 369 lines, all English
6d59999  release(v0.4.4-patch2): capability-driven tool selection in 3c + 3d
e7e9517  release(v0.4.4-patch1): add HTML-first fast path (Tier 3 step 3d)
```