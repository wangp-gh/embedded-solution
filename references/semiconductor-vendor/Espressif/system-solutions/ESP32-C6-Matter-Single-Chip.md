# ESP32-C6 Matter Single-Chip

> **Source:** Espressif-published reference design using the ESP32-C6 Espressif RISC-V SoC with WiFi 6 + BLE 5 + Thread 1.3.
> BOM is **Espressif-only** (single-vendor). For multi-vendor espressif risc-v soc with wifi 6 + ble 5 + thread 1.3 solutions, see
> `references/application-solution/` (when applicable).

## Overview

An Espressif Matter-over-WiFi/Thread reference design using the ESP32-C6 single-chip solution (RISC-V + WiFi 6 + BLE 5.3 + Thread 1.3 in one SoC).

Common application: typical Espressif reference design example using the ESP32-C6.

- **Vendor:** Espressif
- **Published as:** Espressif reference design in datasheet / SDK example
- **Document type:** Reference design (typical application schematic)
- **Date reviewed:** 2026-06-27
- **Document revision:** "Espressif-published, no formal revision number" — refer to vendor product page for the latest reference.

## Reference Design

- **Product page:** See `references/semiconductor-vendor/Espressif/product_families.md#esp32-c6`
- **Datasheet:** `embedded_dev/espressif/datasheet/ESP32-C6_datasheet.pdf`
- **YAML:** `specs/Espressif/ESP32-C6.yaml` *(maintainer-only — not shipped in the public release; for verification use `references/semiconductor-vendor/Espressif/product_families.md` and the datasheet)*

## BOM Candidates (Espressif only)

| Function | Part | Datasheet | Notes |
|----------|------|-----------|-------|
| Hero part (MCU / SoC) | **ESP32-C6** | [link](../product_families.md#esp32-c6) | Espressif RISC-V SoC with WiFi 6 + BLE 5 + Thread 1.3 |
| Decoupling / passives | (external) | — | 100 nF per VDD + bulk caps |
| Crystal (if external) | (external) | — | Verify frequency with datasheet |

External to Espressif (out of BOM scope for this single-vendor solution):
- Decoupling capacitors
- Crystal or resonator (if not internal)
- Antenna matching network (for wireless parts)
- Sensors / actuators (application-dependent)

## Reference Design Verification Status

- [x] Hero part (ESP32-C6) has a vendor product page URL in
      `references/semiconductor-vendor/Espressif/product_families.md`
- [ ] Specific reference design / schematic from Espressif documentation
      was not downloaded in this entry. **This file documents the *type* of
      reference design, not the exact Espressif-published schematic.**

## Numerical Specs

> Per the skill's no-fabrication policy, **no numerical parameters are
> written into this system-solution file**. The ESP32-C6 spec values
> live in the maintainer's private spec database (`specs/Espressif/ESP32-C6.yaml`, if installed)
> and are cross-checked against the official vendor datasheet PDF
> under `embedded_dev/espressif/datasheet/`. Public-release users should
> verify against the Espressif product page and datasheet directly; see
> `references/semiconductor-vendor/Espressif/product_families.md#esp32-c6`.
