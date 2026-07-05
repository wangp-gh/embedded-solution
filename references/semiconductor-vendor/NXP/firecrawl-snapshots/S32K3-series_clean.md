# NXP S32K3 — Automotive Arm Cortex-M7 MCU (ASIL-D capable)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/NXP/firecrawl-snapshots/S32K3-series_raw.md`
(193,622 bytes). Captured from `https://www.nxp.com/products/S32K3`.

## Family Identity

- **Family:** S32K3 — Automotive General-Purpose MCUs
- **Marketing tagline:** "S32K3 Microcontrollers for Automotive General Purpose"
- **Position:** Upgrade of S32K1 family. Arm Cortex-M7-based, with
  ASIL-D capable safety.

## Core

- **Arm Cortex-M7** (32-bit) — base of S32K3 family
- Higher performance than S32K1 (M0+ / M4F)

## Family Sub-Series

- **S32K3** — general-purpose MCUs
- **S32K39/37/36** — electrification MCUs (BMS, motor, OBC)

## Package (visible from chip image)

- HDQFP (LFBGA also available)

## Application

- Automotive body & chassis ECUs
- Electrification (BMS, motor control, on-board charger)
- ADAS domain controllers (subordinate ECUs)

## Use-Case Tier Hint

- Higher-tier upgrade of S32K1 for applications needing Cortex-M7 compute
  headroom + ASIL-D compliance.
- Use S32K3 (general-purpose) for body/chassis; S32K39/37/36 (electrification)
  for BMS / motor control / OBC.

## Notes

- Detailed feature breakdown (peripherals, safety details, operating
  conditions) is in raw — see `S32K3-series_raw.md` for full content.
- Family level marketing page; per-variant subseries data not enumerated
  in fetched raw.
- Companion to S32K1 (added in previous round).

unverified:
- exact core count (single / dual)
- exact flash range
- exact safety level per sub-series
- exact operating temperature range
- exact peripheral count per sub-series
notes:
- 'New yaml entry on 2026-06-30 — extracted from nxp.com S32K3 family
  page via Firecrawl (193,622 bytes raw).'
- 'Family differentiator vs S32K1 (existing yaml): S32K3 is Cortex-M7
  (more compute) vs S32K1 Cortex-M0+/M4F. S32K3 is also higher-tier safety
  (ASIL-D capable vs ASIL-B on S32K1).'
- 'Use case: high-compute automotive body domain, BMS, motor control
  (with electrification sub-series).'
extracted_at: '2026-06-30T18:42:00+08:00'
extraction_method: firecrawl-extract (keyed) of nxp.com product page
extraction_source: references/semiconductor-vendor/NXP/firecrawl-snapshots/S32K3-series_clean.md
extraction_source_raw: references/semiconductor-vendor/NXP/firecrawl-snapshots/S32K3-series_raw.md
extraction_credits_used: 1
