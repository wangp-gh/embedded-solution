# embedded-solution

Recommend embedded system solutions: chip selection, BOM design, vendor
comparison, and reference design matching across multiple semiconductor vendors.

## What this skill does

When you ask a question about embedded systems — chips, MCUs, BLE / WiFi / LoRa
SoCs, sensor selection, BOM design, reference designs — this skill:

1. Checks its catalogue of chip indexes (`references/semiconductor-vendor/<Vendor>/product_families.md`)
2. Cross-references application-solution templates (`references/application-solution/<topic>/solution.md`)
3. Returns **top 3 candidates + comparison table** by default (not a single pick)
4. Cites vendor URLs for every recommendation
5. Says **"not verified"** for any parameter it cannot confirm against official sources

It does **not** fabricate part numbers, specs, prices, or stock counts.

## Quick start

```text
You: "I'm designing a smart ring with BLE and 1-week battery life."

Skill: (asks Step 5 clarifying questions — battery capacity, size, sensor set, ...)
You: (answers)

Skill: (returns top 3 BLE SoC candidates + comparison table + trade-offs,
        each linked to vendor URL and marked with verification status)
```

## When this skill triggers

Triggers for: BLE SoC selection, WiFi+BLE combo, BOM design, vendor
comparison, datasheet parameter verification, application-solution matching,
matter / thread / lorawan design, industrial IoT, smart home / ring / glasses /
lock design, motor control BOM.

Does NOT trigger for: pure software / learning ("how to write Hello World
in Rust"), web / cloud / database questions, math without hardware context.

See [`SKILL.md`](SKILL.md) for full trigger conditions and workflow.

## Install

```bash
clawhub install embedded-solution
```

## Repository layout

```
embedded-solution/
├── SKILL.md                                       # Skill contract — read this first
├── README.md                                      # This file
├── VERIFICATION.md                                # Trust hierarchy and per-vendor upgrade paths
├── RELEASE-v0.5.0.md                             # Release notes for v0.5.0
├── SHA256SUMS.txt                                 # File-by-file integrity hashes
├── requirements.txt                               # Python dependencies for development
├── scripts/                                       # Helper scripts (10 entries)
│   ├── build_application_index.py                # Regenerate references/application-solution/INDEX.md
│   ├── check_no_specs_dead_refs.sh               # CI guard for stale user-facing specs/ path refs
│   ├── clean_markdown.py                         # Markdown normalisation
│   ├── firecrawl_extract.py                      # Firecrawl SDK wrapper (keyed + keyless)
│   ├── test_outofcatalog.py                      # Regression test fixture 19 — out-of-catalog escalation rule
│   ├── update_specs.py                           # Maintainer: extract specs from datasheet PDFs
│   ├── upgrade_yaml_html_source.py               # Maintainer: re-verify yaml from HTML sources
│   ├── upgrade_yaml_to_verified.py                # Maintainer: bulk-verify yaml fields
│   └── verify_yaml_vs_datasheet.py               # Maintainer: cross-check yaml vs datasheet PDF
└── references/
    ├── semiconductor-vendor/                     # Per-vendor chip indexes (11 vendors)
    │   ├── Renesas/product_families.md
    │   ├── Renesas/system-solutions/
    │   ├── Nordic/, NXP/, ST/, TI/, Espressif/,
    │   ├── GigaDevice/, SGMicro/, Silergy/,
    │   ├── SiliconLabs/, WCH/
    │   └── ...
    ├── application-solution/                     # Multi-vendor application BOM templates (11 topics)
    │   ├── INDEX.md                              # Auto-generated catalog
    │   ├── smart-ring/solution.md
    │   ├── smart-glasses/solution.md
    │   ├── robot-gripper/solution.md
    │   ├── smart-watch/solution.md
    │   ├── fitness-tracker/solution.md
    │   ├── home-security-panel/solution.md
    │   ├── industrial-gateway/solution.md
    │   ├── motor-control-blcd/solution.md
    │   ├── power-mgmt-pmic-bom/solution.md
    │   ├── usb-bridge-adapter/solution.md
    │   └── wifi-smart-plug/solution.md
    └── testing/                                  # Regression test fixtures (18 fixtures + 19 expected outputs)
        ├── README.md
        ├── evaluation-rubric.md
        ├── fixtures/                             # 18 user prompt templates
        └── expected-outputs/                     # Structural skeletons per fixture
```

## Install modes

This skill supports four install modes transparently:

| Install state | Behaviour |
|---|---|
| **Public release** (this repo, public) | No `specs/`, no `embedded_dev/` PDFs. Skill uses Tier 3 (product page fetch) and Tier 4 (mirror) for all parameters. |
| **Public release + datasheets plug-in** | Tier 2 local PDFs available. Faster, offline-capable. |
| **Public release + specs plug-in** | Tier 1 YAML field cache available. Fewest network calls. |
| **Dev clone** (`git submodule update --init`) | All plug-ins loaded. Includes the private `specs/` submodule with curated YAML data. |

Each tier is conditionally enabled based on what the host environment has installed. The skill transparently falls back when a tier is unavailable — see `SKILL.md` Search Priority section.

## For maintainers

### Adding a new vendor

1. Create `references/semiconductor-vendor/<VendorName>/product_families.md`
   following the existing format (see `Renesas/product_families.md` for full example).
2. Add at least one product URL and verification status.
3. Run `bash scripts/check_no_specs_dead_refs.sh` to verify no broken paths.

### Adding a new application-solution

1. Create `references/application-solution/<topic>/solution.md`.
2. Follow the structure of `smart-ring/solution.md` (Overview / BOM Candidates
   / Reference Designs / Selection Matrix / Verification Status / Caveat).
3. Run `python3 scripts/build_application_index.py` to refresh `INDEX.md`.

### Adding a regression test fixture

1. Add `references/testing/fixtures/<NN>-<topic>.md` with verbatim prompt +
   workflow path + acceptance criteria.
2. Add `references/testing/expected-outputs/<NN>-<topic>.expected.md` with
   structural skeleton (table headers, citation anchors, anti-patterns).
3. Optionally extend `evaluation-rubric.md` if a new scoring axis is needed.

### Cutting a new public release

1. Bump `version:` in `SKILL.md`
2. Write `RELEASE-v<version>.md` following the structure of `RELEASE-v0.5.0.md`
3. Regenerate `SHA256SUMS.txt` (`find . -type f | xargs sha256sum > SHA256SUMS.txt`)
4. Run `python3 scripts/build_application_index.py` to refresh `references/application-solution/INDEX.md`
5. `git tag -a v<version> -m "<release notes>"`
6. `gh release create v<version> --notes-file RELEASE-v<version>.md --public --target main`
7. `clawhub publish .` (one dot — repo root is the skill root)

## Testing

18 regression fixtures cover the main `SKILL.md` workflow paths. Run manual
evaluation by feeding a fixture's "Input prompt" to the skill and scoring
the response against `evaluation-rubric.md` (5 axes × 5 pts = 25 max,
pass = 20+).

```bash
# Run the dead-reference guard
bash scripts/check_no_specs_dead_refs.sh

# Run the out-of-catalog escalation regression
python3 scripts/test_outofcatalog.py

# (Optional) Run all 18 fixtures against the skill and score manually
# See references/testing/README.md for the script template
```

## License

MIT. See `SKILL.md` header for full license.

## Contributing

Issues and PRs welcome. For major changes (new vendor, new application domain,
new top-level `SKILL.md` section), please open an issue first to discuss.

---

**Full skill definition:** [`SKILL.md`](SKILL.md)
**Test suite:** [`references/testing/`](references/testing/)
**Evaluation rubric:** [`references/testing/evaluation-rubric.md`](references/testing/evaluation-rubric.md)