# scripts/

This directory contains automation scripts for the embedded-solution skill.

## build_application_index.py

Auto-generates `references/application-solution/INDEX.md` by:

1. Reading every `references/semiconductor-vendor/<Vendor>/product_families.md`
   to build a chip → (vendor, link-status, main-page) lookup table.
2. Walking every `references/application-solution/<Topic>/solution.md` and
   extracting the **BOM Candidates** table.
3. Walking every `references/semiconductor-vendor/<Vendor>/system-solutions/README.md`
   for the **planned** topic list (topics that no `solution.md` covers yet).
4. Looking for orphan topic directories (folders under `references/application-solution/`
   that have no `solution.md` yet — these are the framework-only placeholders
   from the Phase 3 setup).
5. Rendering `INDEX.md` with three sections:
   - **Implemented Solutions** — BOM tables, link status inherited from vendor
   - **Planned Solutions** — topics awaiting Phase 5
   - **Coverage Summary** — implemented vs planned per vendor

### Usage

```bash
python3 scripts/build_application_index.py
python3 scripts/build_application_index.py --dry-run
python3 scripts/build_application_index.py --output /tmp/index.md
```

### No Fabrication

The script **never** invents parts, vendors, or topics. Every row in INDEX.md
is derived from existing markdown in the skill. If a topic is missing, it is
either:

- Not yet mentioned in any `system-solutions/README.md`, OR
- Has no `solution.md` written yet (orphan topic dir)

Both are intentional placeholders; Phase 5 will fill them in.

### Output Example

A topic that has a `solution.md`:

```
### `smart-ring`
- **Path:** `references/application-solution/smart-ring/solution.md`
- **Recommended vendor (hint):** Renesas
... (overview excerpt) ...

| Function | Part | Vendor | Status | Datasheet |
|----------|------|--------|--------|-----------|
| BLE SoC  | **DA1470x** | Renesas | ✅ | [link](../../references/semiconductor-vendor/Renesas/product_families.md) |
| ... |
```

A planned topic:

```
### Renesas
- `ble-beacon` — see [Renesas/system-solutions/README.md](../../references/semiconductor-vendor/Renesas/system-solutions/README.md)
```

## update_specs.py (Phase 4 next, not yet implemented)

This is the planned multi-vendor counterpart to the single-vendor
`update_specs.py` in `renesas-search-publish/scripts/`. When written, it will:

- For every chip in `specs/<Vendor>/*.yaml` whose `link_status: unverified`:
  1. Probe the `main_page` URL for HTTP status.
  2. On 200, attempt to download the datasheet PDF to
     `embedded_dev/<vendor>/datasheet/<PartNumber>_datasheet.pdf`.
  3. Use `pdfplumber` to extract Key Features, BLE/WiFi version, RAM, Flash,
     operating voltage, package, etc.
  4. Merge the extracted data into the YAML.
  5. On 404, mark the chip `link_status: removed` (or delete it).
  6. Commit the changes to the local `specs/` git submodule only.

The Renesas reference implementation lives in
`../../renesas-search-publish/scripts/update_specs.py` and can be ported with
family-specific extractors for Nordic (nRF52/53/54/91), NXP (i.MX RT / KW / K /
LPC), ST (STM32 families), and TI (CC/MSP).

## test_outofcatalog.py (fixture 19, added v0.4.3)

Regression test for the **out-of-catalog escalation rule** (SKILL.md Step 4 v0.4.3 + Anti-patterns).

Validates that a BLE SoC comparison table built by the skill:

1. Includes **all 17 candidate parts** (no silent drops) — R1
2. Marks every out-of-catalog part with a `[T4]` tier marker — R2
3. Anchors every in-catalog part to `[T1]` (yaml source) — R3
4. Marks missing fields explicitly (no fabrication by silent blank) — R4
5. Maintains schema consistency (exactly 4 markers per row) — R5

The baseline is frozen — it does not re-fetch live datasheets, so the test runs offline and deterministically.

### Usage

```bash
python3 scripts/test_outofcatalog.py
# Expected: ✅ All rules passed. Out-of-catalog escalation rule is enforced.
# Exit 0 on pass, 1 on fail.
```

### When the test fails

| Failing rule | Likely cause |
|--------------|--------------|
| R1 | Baseline row count is wrong (parts added/removed without updating fixture) |
| R2 | Out-of-catalog part was missing `[T4]` marker (regression of escalation rule) |
| R3 | In-catalog part lost its `[T1]` yaml anchor (yaml data corruption) |
| R4 | Cell became silently blank (fabrication risk) |
| R5 | Schema drift (markers per row changed) |
