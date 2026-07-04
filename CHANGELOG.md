# Changelog

All notable changes to the `embedded-solution` skill, per release.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.5.0] — 2026-07-04 — First public release

### Layout

The release repository uses an **expanded layout** — each `releases/vX.Y.Z/` directory is the complete, deployable skill with every file at its install-time path. No tarball is committed to git; the git tree IS the artefact. This makes every file individually diffable, every SHA256 individually auditable, and `clawhub publish ./releases/vX.Y.Z/` a one-liner.

### Added

- HTML-first fast path (Tier 3 step 3d): vendor product pages render headline specs in 5-10 s instead of downloading a 30-MB PDF first. Validated against Nordic nRF5340, Renesas DA14706, TI CC2640R2F, ST STM32WB55, NXP NXH3675, Silicon Labs EFR32BG26, BlueTrum AB5602C.
- Capability-driven tool selection (Tier 3 step 3c/3d): any tool satisfying a capability contract qualifies at the corresponding tier. Removed hard-coded tool names (`web_fetch`, `tavily_extract`, `pdfplumber`).
- Step 2 routing for novel topics: **Option A** (fetch + cite inline, default), **Option B** (curate a new `solution.md` only when the topic recurs), **Option C** (disambiguate).
- Anti-pattern row: *"Create a new solution.md by default on every novel topic"* — points at Option A.
- Anti-pattern row: *"Always download the datasheet PDF to extract a single headline spec"* — points at HTML-first path.
- Anti-pattern row: *"Pick Tier 3 tool by brand name"* — points at capability contracts.
- 8 new application solutions in `references/application-solution/`: fitness-tracker, home-security-panel, industrial-gateway, motor-control-blcd, power-mgmt-pmic-bom, smart-watch, usb-bridge-adapter, wifi-smart-plug.

### Changed

- SKILL.md body reduced from 438 → 281 lines (-36%). Removed frontmatter `v0_4_X_highlights` blocks; removed `## Directory Layout`; removed `## Privacy / Publishing Notes` (now in `BUILD.md` of this release repo).
- Tier 4 mirror list consolidated to one paragraph (overseas + domestic CN both inline, all English).
- All bilingual Chinese vendor names → English brand transliteration.

### Security

- Removed 130 `firecrawl-snapshots/` maintenance-cache files from public git tracking (kept on disk for development).
- `.gitignore` extended to cover all maintenance cache paths.
- Tarball size after exclusions: 188 KB (down from 11 MB with leaked caches).

### Validation

- `scripts/build_application_index.py` — lists 11 application solutions and 110 chips across 11 vendors.
- Live test (HTML-first, 3 BLE SoCs): 12.3 s end-to-end with full `[D-HTML @ tier 2]` citations.
- Live test (capability ladder, ST STM32WB55): HTML × 3 timeouts → fell through to 3c Tier B (curl + pdfplumber, 2.4 s) per patch2 fallback rule; no retry on the same URL.
- Live test (Option A, novel topic): "wireless microphone SoC" query → 3-chip Top-3 comparison produced in 12 s, no `solution.md` created.

---

## [0.4.3] — 2026-07-02 — Last private release

Not published to GitHub or ClawHub. Internal development only.

### Added

- Out-of-catalog escalation rule (Tier 4 Tavily bridge): when a candidate part is not in the catalogue, the skill MUST escalate to Tier 4 with `[T4]` marker + URL + timestamp rather than silently dropping it.
- `scripts/test_outofcatalog.py` (fixture 19): regression test for the rule, enforces 5 rules against a 17-row BLE SoC comparison baseline.

---

## Earlier versions

See `~/.openclaw/workspace/embedded-solution-publish/RELEASE-v0.4.0.md`, `RELEASE-v0.4.1.md`, `RELEASE-v0.4.2.md` for development history.