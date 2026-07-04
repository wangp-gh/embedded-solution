# GD32VF103 RISC-V MCU Reference

> **Source:** GigaDevice-published reference design using the GD32VF103 GigaDevice RISC-V MCU.
> BOM is **GigaDevice-only** (single-vendor). For multi-vendor gigadevice risc-v mcu solutions, see
> `references/application-solution/` (when applicable).

## Overview

A GigaDevice RISC-V reference design using the GD32VF103 as a cost-optimised STM32F103 pin-compatible alternative.

Common application: typical GigaDevice reference design example using the GD32VF103.

- **Vendor:** GigaDevice
- **Published as:** GigaDevice reference design in datasheet / SDK example
- **Document type:** Reference design (typical application schematic)
- **Date reviewed:** 2026-06-27
- **Document revision:** "GigaDevice-published, no formal revision number" — refer to vendor product page for the latest reference.

## Reference Design

- **Product page:** See `references/semiconductor-vendor/GigaDevice/product_families.md#gd32vf103`
- **Datasheet:** `embedded_dev/gigadevice/datasheet/GD32VF103_datasheet.pdf`
- **YAML:** `specs/GigaDevice/GD32VF103.yaml` *(maintainer-only — not shipped in the public release; for verification use `references/semiconductor-vendor/GigaDevice/product_families.md` and the datasheet)*

## BOM Candidates (GigaDevice only)

| Function | Part | Datasheet | Notes |
|----------|------|-----------|-------|
| Hero part (MCU / SoC) | **GD32VF103** | [link](../product_families.md#gd32vf103) | GigaDevice RISC-V MCU (GD32 family) |
| Decoupling / passives | (external) | — | 100 nF per VDD + bulk caps |
| Crystal (if external) | (external) | — | Verify frequency with datasheet |

External to GigaDevice (out of BOM scope for this single-vendor solution):
- Decoupling capacitors
- Crystal or resonator (if not internal)
- Antenna matching network (for wireless parts)
- Sensors / actuators (application-dependent)

## Reference Design Verification Status

- [x] Hero part (GD32VF103) has a vendor product page URL in
      `references/semiconductor-vendor/GigaDevice/product_families.md`
- [ ] Specific reference design / schematic from GigaDevice documentation
      was not downloaded in this entry. **This file documents the *type* of
      reference design, not the exact GigaDevice-published schematic.**

## Numerical Specs

> Per the skill's no-fabrication policy, **no numerical parameters are
> written into this system-solution file**. The GD32VF103 spec values
> live in the maintainer's private spec database (`specs/GigaDevice/GD32VF103.yaml`, if installed)
> and are cross-checked against the official vendor datasheet PDF
> under `embedded_dev/gigadevice/datasheet/`. Public-release users should
> verify against the GigaDevice product page and datasheet directly; see
> `references/semiconductor-vendor/GigaDevice/product_families.md#gd32vf103`.
