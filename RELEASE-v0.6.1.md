# RELEASE v0.6.1 — Sync I

**Date:** 2026-07-11
**Codename:** Sync I (post-v0.6.0 maintenance release)
**Commit:** `5287675`
**Tag:** `v0.6.1` (annotated)
**Mirror:** Both `embedded-solution-publish/` (local) and
`embedded-solution-release/` (github.com/wangp-gh/embedded-solution) tagged.

## Summary

First maintenance release after v0.6.0. Closes the catalog-drift gap between
the private source-of-truth (`publish/`) and the public mirror (`release/`).
No spec semantics changed — this is a sync, not a feature release.

## Highlights

- **7 new spec yamls** spanning previously-unsupported vendor categories:
  - `Ambiq/Apollo4.yaml` — ultra-low-power Cortex-M4 MCU
  - `Microchip/SAMD21.yaml` — Cortex-M0+ MCU
  - `Microchip/dsPIC33CK.yaml` — dsPIC33 DSC family
  - `Bosch/BMI270.yaml` — IMU sensor
  - `Nuvoton/M480.yaml` — Cortex-M4 MCU
  - `WIZnet/W5500.yaml` — hardwired TCP/IP Ethernet controller
  - `RaspberryPi/RP2040.yaml` — dual Cortex-M0+ MCU
- **`update_specs.py`** — widened Renesas RA extractor to **any Arm Cortex-M
  variant** (was M33-only; now covers M0+/M23/M4/M33/M85 etc.). This was the
  root cause of the 2026-07-05 RX72N factory-error → 2026-07-07 phase2 cleanup
  on RA6M2/RA6M3 (Cortex-M4) parts.
- **76 spec updates** across Nordic, NXP, WCH, Silergy, ST, SGMicro,
  GigaDevice, Renesas, Espressif, TI — Phase2 Rounds 3-5 + post-phase2 cleanup.
- **2 new validation tools**:
  - `scripts/validate_and_enrich.py` — catalog field validation + enrichment
  - `scripts/catalog_audit.py` — link_status / datasheet-coverage audit
  - `scripts/VALIDATE_AND_ENRICH_REPORT.md` — reference output

## Catalog

- **Total yamls:** 132 (was 125 in v0.6.0; +7)
- **Vendors:** 16 (was 15; added Ambiq, Bosch, Microchip, Nuvoton, WIZnet; Raspberry Pi was already in publish/)
- **`pending-datasheet-*`:** 0 (target met)
- **`needs-re-extraction-factory-error-*`:** 0 (post-phase2 cleanup complete)

## Round-by-round provenance (publish/ side)

| Round | Date | Scope | Vendors |
|---|---|---|---|
| Phase2 R1 | 2026-07-04 | Renesas phase1-recovery (25 parts) | Renesas |
| Phase2 R2 | 2026-07-05 | TX/RX/RA family re-extract | Renesas |
| Phase2 R3 | 2026-07-10 | vendor-direct backfills (batches 2-5) | NXP, ST, Renesas |
| Phase2 R4 | 2026-07-10 | STM32 + TI vendor-direct backfills complete | ST, TI |
| Phase2 R5 | 2026-07-10 | status updates, 3 new yamls (Ambiq, Bosch, Nuvoton) | Ambiq, Bosch, Nuvoton |
| Cleanup | 2026-07-10 | redundant unverified entries pruned | various |

## Tools Inventory

### Mirror
- `scripts/update_specs.py` (universal Cortex-M RA extraction)
- 7 `specs/<Vendor>/<Part>.yaml` new
- 76 `specs/<Vendor>/<Part>.yaml` updated

### Validation (NEW in this release)
- `scripts/validate_and_enrich.py` — catalog field validator
- `scripts/catalog_audit.py` — coverage / status auditor

## Deferred to v0.7.0

- `.github/workflows/ci.yml` (Tier 1 CI scaffold). Local file exists in working
  tree but cannot be pushed: current GitHub OAuth App lacks the `workflow`
  scope required to create/modify `.github/workflows/*.yml`. Grant the scope
  in GitHub Developer settings, then a v0.7.0 commit will lift the CI
  scaffold into the repo.

## Risks & Mitigations

- **Mirror drift recurrence:** Same root cause as v0.6.0 → v0.6.1 drift.
  *Mitigation:* consider a periodic (`cron` or `sessionStatus` heartbeat)
  publish→release diff check after the CI scaffold lands in v0.7.0.
- **OAuth `workflow` scope blocker:** blocks CI push. *Mitigation:*
  v0.7.0 will include a single-line instruction in its RELEASE notes for
  the owner to grant the scope before CI can run.

## Provenance

- publish/ HEAD at v0.6.1 tag: `027364d chore: bump specs to e5b6038`
- release/ HEAD at v0.6.1 tag: `5287675 mirror(publish): v0.6.1 — SKILL/scripts/specs sync from publish/`
- Mirror strategy: `cp -R` (per-publish-file) then `git add -A`, per MEMORY.
- Anti-patterns avoided: no `rsync --delete` (per MEMORY anti-pattern entry).