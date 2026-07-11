#!/usr/bin/env python3
"""update_specs.py — multi-vendor spec database updater.

This is a port/extension of the single-vendor
`renesas-search-publish/scripts/update_specs.py` to the multi-vendor
catalog under `specs/<Vendor>/<Part>.yaml`. See that file for the
detailed extraction heuristics; this module adds:

- Vendor dispatcher (different URL slugs per vendor)
- Family-specific extractors for Nordic / NXP / ST / TI in addition
  to the Renesas ones
- Single-part mode (`--vendor X --part Y`) for incremental updates

## Usage

    # Dry-run report for all parts (no network, no writes)
    python3 scripts/update_specs.py --dry-run

    # Update a single Renesas part (PDF already in embedded_dev/renesas/datasheet/)
    python3 scripts/update_specs.py --vendor Renesas --part DA14531

    # Update a single Nordic part (will download nRF52832 datasheet first)
    python3 scripts/update_specs.py --vendor Nordic --part nRF52832

    # Update all NXP parts
    python3 scripts/update_specs.py --vendor NXP

    # Only fill parts that are placeholder (don't touch already-populated YAMLs)
    python3 scripts/update_specs.py --only-placeholder

## Architecture

    PARTS catalog (vendor -> part -> URL config)
        |
        v
    download_pdf()   (or use existing file)
        |
        v
    extract_specs_from_pdf() with family-specific extractors
        |
        v
    merge_yaml()     (preserve unverified / notes / verified_by_human)
        |
        v
    save_yaml() + commit in local specs repo

## Status

- Renesas family extractors (DA BLE, RA, RX, RL78, ISL power, HS, NFC) are
  adapted from the renesas-search-publish reference. They will run on any
  Renesas YAML whose PDF is already in `embedded_dev/renesas/datasheet/`.
- Nordic family extractor (_extract_nrf) implemented 2026-06-23 against
  nRF52832 Product Specification v1.1 (Arduino mirror, see commit log).
  Verified to extract cores, CoreMark, flash/RAM, operating voltage, TX/RX
  current, RX sensitivity, TX power range, system OFF/ON currents.
- NXP family extractors (Kinetis / i.MX RT / KW / LPC) implemented 2026-06-23.
- TI family extractors (CC26xx / CC13xx / MSPM0) implemented 2026-06-23.
- Espressif family extractors (ESP32 / ESP32-S3 / ESP32-C3) implemented
  2026-06-25 — verified cores, clock, CoreMark, RAM, wireless.
- GigaDevice family extractor (GD32 unified extractor) implemented
  2026-06-25 — verified cores, clock, flash, RAM, supply voltage.
- ST family extractors are still TODO (st.com datasheet PDFs are
  Cloudflare-gated; download must happen on a network where st.com is
  reachable). Calling update_specs for ST will download the PDF and
  run only the **generic** pdfplumber pass.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import yaml

# === Paths ==============================================================
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR  = SCRIPT_DIR.parent
SPECS_DIR  = SKILL_DIR / "specs"               # multi-vendor: specs/<Vendor>/*.yaml
EMB_DIR    = SKILL_DIR / "embedded_dev"        # embedded_dev/<vendor>/datasheet/*.pdf

# === Parts catalog =======================================================
# Each entry maps (vendor, part) -> URL config + PDF filename.
# This is intentionally minimal — it lists only the parts that
# exist in specs/<Vendor>/<Part>.yaml. URLs follow the vendor's own
# datasheet-page pattern.

PARTS: dict[str, dict[str, dict]] = {

    # === Renesas (PDFs already in embedded_dev/renesas/datasheet/) ===
    "Renesas": {
        "DA14531": {
            "pdf_filename": "DA14531_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/da14531-datasheet",
            "family": "da_ble",
        },
        "DA14592": {
            "pdf_filename": "DA14592_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/da1459x-datasheet",
            "family": "da_ble",
        },
        "DA14594": {
            "pdf_filename": "DA14594_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/da1459x-datasheet",
            "family": "da_ble",
        },
        "DA14697": {
            "pdf_filename": "DA14697_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/da1469x-datasheet",
            "family": "da_ble",
        },
        "DA1470x": {
            "pdf_filename": "DA1470x_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/da1470x-datasheet",
            "family": "da_ble",
        },
        "RA6M5": {
            "pdf_filename": "RA6M5_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/ra6m5-group-datasheet",
            "family": "ra",
        },
        # === Expanded 2026-06-23: full Renesas catalog so all 35 yamls
        # under specs/Renesas/ are reachable by update_specs.py.
        # Family tags must match a key in FAMILY_EXTRACTORS; if a family
        # extractor is missing the generic pdfplumber pass still runs and
        # appends a note.
        #
        # URL field status:
        #   * verified-by-web-fetch — these return HTTP 200 + PDF (checked)
        #   * best-guess            — slug follows the <part>-datasheet
        #                             pattern but has NOT been verified.
        #                             If the PDF is ever re-downloaded and
        #                             the slug is wrong, update_specs.py
        #                             will fail the download (warning only;
        #                             the YAML placeholder note is appended)
        #   * shared-group          — multiple parts share one datasheet PDF

        # --- DA BLE (DA14531 standalone; DA14592 + DA14594 share da1459x;
        #     DA14697 / DA1470x standalone) ---
        "DA14531": {
            "pdf_filename": "DA14531_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/da14531-datasheet",
            "family": "da_ble",
        },
        "DA14592": {
            "pdf_filename": "DA14592_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/da1459x-datasheet",
            "family": "da_ble",
        },
        "DA14594": {
            "pdf_filename": "DA14594_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/da1459x-datasheet",
            "family": "da_ble",
        },
        "DA14697": {
            "pdf_filename": "DA14697_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/da1469x-datasheet",
            "family": "da_ble",
        },
        "DA1470x": {
            "pdf_filename": "DA1470x_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/da1470x-datasheet",
            "family": "da_ble",
        },

        # --- RA Cortex-M33 MCU (each is a group datasheet) ---
        "RA4M2": {
            "pdf_filename": "RA4M2_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/ra4m2-group-datasheet",
            "family": "ra",
        },
        "RA4M3": {
            "pdf_filename": "RA4M3_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/ra4m3-group-datasheet",
            "family": "ra",
        },
        "RA6M2": {
            "pdf_filename": "RA6M2_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/ra6m2-group-datasheet",
            "family": "ra",
        },
        "RA6M3": {
            "pdf_filename": "RA6M3_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/ra6m3-group-datasheet",
            "family": "ra",
        },
        "RA6M4": {
            "pdf_filename": "RA6M4_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/ra6m4-group-datasheet",
            "family": "ra",
        },
        "RA6M5": {  # already existed; kept here for catalog completeness
            "pdf_filename": "RA6M5_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/ra6m5-group-datasheet",
            "family": "ra",
        },

        # --- RL78 low-power MCU (best-guess URLs — not verified) ---
        "RL78G14": {
            "pdf_filename": "RL78G14_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/rl78g14-datasheet",
            "family": "rl78",
        },
        "RL78G23": {
            "pdf_filename": "RL78G23_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/rl78g23-datasheet",
            "family": "rl78",
        },
        "RL78H1D": {
            "pdf_filename": "RL78H1D_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/rl78h1d-datasheet",
            "family": "rl78",
        },
        "RL78I1D": {
            "pdf_filename": "RL78I1D_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/rl78i1d-datasheet",
            "family": "rl78",
        },

        # --- RX 32-bit MCU (best-guess URLs — not verified) ---
        "RX140": {
            "pdf_filename": "RX140_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/rx140-datasheet",
            "family": "rx",
        },
        "RX231": {
            "pdf_filename": "RX231_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/rx231-datasheet",
            "family": "rx",
        },
        "RX65N": {
            "pdf_filename": "RX65N_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/rx65n-datasheet",
            "family": "rx",
        },
        "RX66T": {
            "pdf_filename": "RX66T_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/rx66t-datasheet",
            "family": "rx",
        },
        "RX71M": {
            "pdf_filename": "RX71M_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/rx71m-datasheet",
            "family": "rx",
        },
        "RX72N": {
            "pdf_filename": "RX72N_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/rx72n-datasheet",
            "family": "rx",
        },

        # --- ISL power (Intersil legacy). ISL88705 + ISL88813 share
        #     one datasheet (verified 2026-06-23). ISL9205 / 9238 / 9305
        #     are standalone — URLs are best-guess. ---
        "ISL88705": {
            "pdf_filename": "ISL88705_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/isl88705-isl88706-isl88707-isl88708-isl88716-isl88813-datasheet",
            "family": "isl_power",
        },
        "ISL88813": {
            "pdf_filename": "ISL88813_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/isl88705-isl88706-isl88707-isl88708-isl88716-isl88813-datasheet",
            "family": "isl_power",
        },
        "ISL9205": {
            "pdf_filename": "ISL9205_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/isl9205-datasheet",
            "family": "isl_power",
        },
        "ISL9238": {
            "pdf_filename": "ISL9238_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/isl9238-datasheet",
            "family": "isl_power",
        },
        "ISL9305": {
            "pdf_filename": "ISL9305_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/isl9305-datasheet",
            "family": "isl_power",
        },

        # --- HS Sensor (HS3001 / HS3002 / HS3003 all share hs3xxx-datasheet,
        #     verified 2026-06-23) ---
        "HS3001": {
            "pdf_filename": "HS3001_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/hs3xxx-datasheet",
            "family": "sensor",
        },
        "HS3002": {
            "pdf_filename": "HS3002_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/hs3xxx-datasheet",
            "family": "sensor",
        },
        "HS3003": {
            "pdf_filename": "HS3003_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/hs3xxx-datasheet",
            "family": "sensor",
        },

        # --- NFC (Panthronics). PTX30W notes mention a DigiKey mirror as
        #     fallback because Renesas product page is anti-bot — URLs are
        #     best-guess. ---
        "PTX30W": {
            "pdf_filename": "PTX30W_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/ptx30w-datasheet",
            "family": "nfc",
        },
        "PTX130W": {
            "pdf_filename": "PTX130W_datasheet.pdf",
            "url": "https://www.renesas.com/en/document/dst/ptx130w-datasheet",
            "family": "nfc",
        },
    },

    # === Nordic (PDFs NOT yet downloaded) ===
    "Nordic": {
        "nRF52832": {
            "pdf_filename": "nRF52832_datasheet.pdf",
            "url": "https://www.nordicsemi.com/-/media/Product-and-Services/Product-pages/nRF52832/nRF52832-datasheet",
            "family": "nrf",  # TODO: extract from docs.nordicsemi.com/bundle/ps_nrf52832
        },
        "nRF52840": {
            "pdf_filename": "nRF52840_datasheet.pdf",
            "url": "https://www.nordicsemi.com/-/media/Product-and-Services/Product-pages/nRF52840/nRF52840-datasheet",
            "family": "nrf",
        },
        "nRF5340": {
            "pdf_filename": "nRF5340_datasheet.pdf",
            "url": "https://www.nordicsemi.com/-/media/Product-and-Services/Product-pages/nRF5340/nRF5340-datasheet",
            "family": "nrf",
        },
        "nRF54L15": {
            "pdf_filename": "nRF54L15_datasheet.pdf",
            "url": "https://www.nordicsemi.com/-/media/Product-and-Services/Product-pages/nRF54L15/nRF54L15-datasheet",
            "family": "nrf",
        },
        "nRF9160": {
            "pdf_filename": "nRF9160_datasheet.pdf",
            "url": "https://www.nordicsemi.com/-/media/Product-and-Services/Product-pages/nRF9160/nRF9160-datasheet",
            "family": "nrf",
        },
        "nRF7002": {
            "pdf_filename": "nRF7002_datasheet.pdf",
            # Farnell mirror of Nordic product spec PDF (Product Specification
            # v1.2, 2024-07-04, 69 pages, 2.1 MB). nordicsemi.com is gated by
            # Cloudflare; Farnell /datasheets/ serves the same PDF directly.
            "url": "https://www.farnell.com/datasheets/4393752.pdf",
            "url_status": "farnell_mirror_2026-06",
            "url_source": "farnell_datasheet",
            "family": "nrf_companion",
        },
    },

    # === NXP (PDFs NOT yet downloaded) ===
    "NXP": {
        "K66": {
            "pdf_filename": "K66_datasheet.pdf",
            "url": "https://www.nxp.com/docs/en/data-sheet/K66P144M180SF5V2.pdf",
            "family": "kinetis",
        },
        "KW45": {
            "pdf_filename": "KW45_datasheet.pdf",
            "url": "https://www.nxp.com/docs/en/data-sheet/KW45-datasheet.pdf",
            "url_status": "stale_2026-06_no_mirror",  # NXP /docs/ URL returns 'Not found';
                                                     # NXP Community only hosts the
                                                     # 'KW45 - K32W1 Hardware Design
                                                     # Recommendations' guide, not the
                                                     # chip-level datasheet. Mirror search
                                                     # exhausted 2026-06-23.
            "family": "kw",
        },
        "LPC55S69": {
            "pdf_filename": "LPC55S69_datasheet.pdf",
            "url": "https://www.nxp.com/docs/en/nxp/data-sheets/LPC55S6x_DS.pdf",
            "family": "lpc",
        },
        "i.MX_RT1064": {
            "pdf_filename": "iMX-RT1064_datasheet.pdf",
            "url": "https://www.nxp.com/docs/en/nxp/data-sheets/IMXRT1064CEC.pdf",
            "url_status": "stale_2026-06_no_mirror",  # NXP /docs/ URL returns 'Not found';
                                                     # NXP Community only hosts the
                                                     # MIMXRT1064 EVK User Guide (rev 0,
                                                     # 2018), not the chip datasheet.
                                                     # Mirror search exhausted 2026-06-23.
            "family": "imx_rt",
        },
        "i.MX_RT1170": {
            "pdf_filename": "iMX-RT1170_datasheet.pdf",
            # NXP's own /docs/ URL now returns 'Not found' for this part.
            # Community mirror hosts the same Rev. 2 datasheet.
            "url": "https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/imxrt/20232/1/IMXRT1170CEC.pdf",
            "url_source": "nxp_community_attachment",
            "family": "imx_rt",
        },
    },

    # === Espressif Systems (Shanghai-based Wi-Fi/BLE SoC vendor) ===
    # Source PDFs hosted on documentation.espressif.com (works in
    # 2026-06 environment); espressif.com main site is Cloudflare-gated
    # but the documentation subdomain serves PDFs directly.
    # Note: ESP32 family uses Xtensa LX6/LX7 cores; ESP32-C3 uses RISC-V.
    "Espressif": {
        "ESP32": {
            "pdf_filename": "ESP32_datasheet.pdf",
            "url": "https://documentation.espressif.com/esp32_datasheet_en.pdf",
            "family": "esp32_xtensa",
        },
        "ESP32-S3": {
            "pdf_filename": "ESP32-S3_datasheet.pdf",
            "url": "https://documentation.espressif.com/esp32-s3_datasheet_en.pdf",
            "family": "esp32s3_xtensa",
        },
        "ESP32-C3": {
            "pdf_filename": "ESP32-C3_datasheet.pdf",
            "url": "https://documentation.espressif.com/esp32-c3_datasheet_en.pdf",
            "family": "esp32c3_riscv",
        },
        "ESP32-C6": {
            "pdf_filename": "ESP32-C6_datasheet.pdf",
            # Mouser Latvia mirror of the official Espressif ESP32-C6
            # datasheet (Version 1.3, 83 pages, 1 MB). espressif.com's
            # own /sites/default/files/documentation/ is now anti-bot
            # gated (HTTP 403 to plain curl), so this regional Mouser
            # mirror is the working route. Mouser's regional CDNs
            # (lv.mouser.com) serve the same files without gating.
            "url": "https://lv.mouser.com/datasheet/3/5900/1/esp32c6_datasheet_soldered.pdf",
            "url_status": "mouser_lv_mirror_2026-06",
            "url_source": "mouser_datasheet",
            "family": "esp32c3_riscv",  # reuses the RISC-V family extractor
        },
    },

    # === Silicon Labs (Austin-based; EFR32 Series 2 wireless SoC family) ===
    # Source PDFs hosted on alcom.be mirror (Alcom is a Belgian/NL
    # distributor that caches ST/Silicon Labs datasheets). silabs.com
    # is Cloudflare-gated as of 2026-06 from this environment; the
    # alcom mirror is reachable and serves the same PDFs.
    "SiliconLabs": {
        "EFR32BG22": {
            "pdf_filename": "EFR32BG22_datasheet.pdf",
            "url": "https://alcom.be/uploads/efr32bg22-datasheet.pdf",
            "url_status": "alcom_mirror_2026-06",
            "url_source": "alcom_datasheet",
            "family": "efr32_ble",
        },
        "EFR32BG24": {
            "pdf_filename": "EFR32BG24_datasheet.pdf",
            "url": "https://alcom.be/uploads/efr32bg24-datasheet.pdf",
            "url_status": "alcom_mirror_2026-06",
            "url_source": "alcom_datasheet",
            "family": "efr32_ble",
        },
        "EFR32MG21": {
            "pdf_filename": "EFR32MG21_datasheet.pdf",
            "url": "https://alcom.be/uploads/Silicon-Labs-efr32mg21-datasheet.pdf",
            "url_status": "alcom_mirror_2026-06",
            "url_source": "alcom_datasheet",
            "family": "efr32_mp",  # multiprotocol
        },
        "EFR32MG24": {
            "pdf_filename": "EFR32MG24_datasheet.pdf",
            "url": "https://alcom.be/uploads/Silicon-Labs-efr32mg24-datasheet.pdf",
            "url_status": "alcom_mirror_2026-06",
            "url_source": "alcom_datasheet",
            "family": "efr32_mp",
        },
        "EFR32BG27": {
            "pdf_filename": "EFR32BG27_datasheet.pdf",
            # silabs.com official documents/public/data-sheets/ URL (NOT
            # Cloudflare-gated when called with a real User-Agent — the
            # 'Cloudflare-gated' note in the placeholder yaml was wrong).
            # 1.9 MB, 138 pages, full family datasheet.
            "url": "https://www.silabs.com/documents/public/data-sheets/efr32bg27-datasheet.pdf",
            "url_status": "silabs_official_2026-06",
            "url_source": "silabs_datasheet",
            "family": "efr32_ble",
        },
    },

    # === GigaDevice (Beijing-based; GD32 family of ARM Cortex-M/RISC-V MCUs) ===
    # PDFs hosted on gd32mcu.com (separate from gigadevice.com product portal);
    # direct /data/documents/datasheet/ URLs are reachable as of 2026-06-23.
    "GigaDevice": {
        "GD32F303xx": {
            "pdf_filename": "GD32F303xx_datasheet.pdf",
            "url": "https://www.gd32mcu.com/data/documents/datasheet/GD32F303xx_Datasheet_Rev1.9.pdf",
            "family": "gd32f3_cortex_m4",
        },
        "GD32F450xx": {
            "pdf_filename": "GD32F450xx_datasheet.pdf",
            "url": "https://www.gd32mcu.com/data/documents/datasheet/GD32F450xx_Datasheet_Rev2.1.pdf",
            "family": "gd32f4_cortex_m4",
        },
        "GD32E230xx": {
            "pdf_filename": "GD32E230xx_datasheet.pdf",
            "url": "https://www.gd32mcu.com/data/documents/datasheet/GD32E230xx_Datasheet_Rev1.4.pdf",
            "family": "gd32e2_cortex_m23",
        },
        "GD32VF103": {
            "pdf_filename": "GD32VF103_datasheet.pdf",
            # GigaDevice official datasheet URL (gd32mcu.com is NOT
            # Cloudflare-gated; serves the PDF to plain curl with a
            # realistic User-Agent). 2.4 MB, 87 pages, Rev 1.7.
            "url": "https://www.gd32mcu.com/data/documents/datasheet/GD32VF103_Datasheet_Rev1.7.pdf",
            "url_status": "gd32mcu_official_2026-06",
            "url_source": "gd32mcu_datasheet",
            "family": "gd32vf103_riscv",
        },
    },

    # === ST (PDFs NOT yet downloaded — see notes below) ===
    #
    # All five STM32 parts have valid-looking direct URLs in the
    # original catalog, but in the 2026-06 environment st.com is
    # entirely unreachable at the network layer:
    #   - Direct GET to www.st.com/resource/en/datasheet/*.pdf  -> HTTP 000
    #     (curl connects but the server resets within 0.14s)
    #   - web.archive.org wayback cache of the same URLs        -> HTTP 000
    #     (archive.org can fetch them on demand but not via this
    #     network)
    #   - m.st.com / estore.st.com / community.st.com           -> reachable
    #     but the /resource/en/datasheet/ paths return 000 here
    #   - alldatasheet.com / fcc.report / mouser.com mirrors    -> reachable
    #     but return HTML pages (anti-bot, not direct PDFs)
    #   - Tavily extract CAN read the ST PDF content             -> text only,
    #     but per SKILL.md 'no fabrication' rule we do NOT write
    #     that text into specs without first downloading the PDF
    #     to disk.
    #
    # Operator action: re-run from a network where st.com is
    # reachable, or pull the PDFs from a partner account
    # (DigiKey / Mouser / Future / Avnet download portals).
    "ST": {
        "STM32WB55": {
            "pdf_filename": "STM32WB55_datasheet.pdf",
            # Mouser mirror of st.com datasheet (st.com is Cloudflare-gated as
            # of 2026-06; mouser.com serves the same PDF without gating).
            "url": "https://www.mouser.com/datasheet/2/389/stm32wb55cc-1588841.pdf",
            "url_status": "mouser_mirror_2026-06",
            "url_source": "mouser_datasheet",
            "family": "stm32_wireless",
        },
        "STM32U575": {
            "pdf_filename": "STM32U5_datasheet.pdf",  # shared with family alias
            "url": "https://akizukidenshi.com/goodsaffix/stm32u575zi.pdf",
            "url_status": "akizukidenshi_mirror_2026-06",
            "url_source": "akizukidenshi_datasheet",
            "family": "stm32_ulp",
        },
        "STM32U585": {
            "pdf_filename": "STM32U585_datasheet.pdf",
            "url": "https://cdn-reichelt.de/documents/datenblatt/C700/STM32U585VIT6.pdf",
            "url_status": "reichelt_mirror_2026-06",
            "url_source": "reichelt_datasheet",
            "family": "stm32_ulp",
        },
        # Family alias: STM32U5 was historically a single representative YAML
        # for the whole U5 family. Kept as an alias to STM32U575 for backward
        # compat with any references; new code should use the per-variant keys
        # above. The `family_alias: STM32U575` marker tells update_specs.py
        # not to re-extract into this slot.
        "STM32U5": {
            "pdf_filename": "STM32U5_datasheet.pdf",
            "url": "https://akizukidenshi.com/goodsaffix/stm32u575zi.pdf",
            "url_status": "akizukidenshi_mirror_2026-06",
            "url_source": "akizukidenshi_datasheet",
            "family": "stm32_ulp",
            "family_alias": "STM32U575",
        },
        "STM32H7": {
            "pdf_filename": "STM32H7_datasheet.pdf",
            # SparkFun CDN mirror of st.com STM32H743 datasheet
            # (DS12110 Rev 5, 231 pages, 3.4 MB). The previous Octopart
            # URL was actually a 110-page data brief, not the full datasheet;
            # this SparkFun mirror is the full datasheet.
            "url": "https://cdn.sparkfun.com/assets/e/c/9/c/6/STM32H743VI.pdf",
            "url_status": "sparkfun_mirror_2026-06",
            "url_source": "sparkfun_datasheet",
            "family": "stm32_hp",
        },
        "STM32MP157": {
            "pdf_filename": "STM32MP157_datasheet.pdf",
            # Mouser mirror of st.com datasheet (st.com is Cloudflare-gated as
            # of 2026-06; mouser.com serves the same PDF without gating).
            "url": "https://www.mouser.com/datasheet/2/389/stm32mp157a-1568209.pdf",
            "url_status": "mouser_mirror_2026-06",
            "url_source": "mouser_datasheet",
            "family": "stm32_mpu",
        },
        "STM32WL55": {
            "pdf_filename": "STM32WL55_datasheet.pdf",
            # Mouser mirror of st.com datasheet (st.com is Cloudflare-gated as
            # of 2026-06; mouser.com serves the same PDF without gating).
            "url": "https://www.mouser.com/datasheet/2/389/stm32wl55cc-1947315.pdf",
            "url_status": "mouser_mirror_2026-06",
            "url_source": "mouser_datasheet",
            "family": "stm32_wireless",
        },
        "STM32G0": {
            "pdf_filename": "STM32G0_datasheet.pdf",
            # Mouser mirror of st.com STM32G070 datasheet
            # (st.com is Cloudflare-gated as of 2026-06; mouser.com serves
            # the same PDF without gating). DS13106 Rev as-shipped 2026-06.
            # G070CB/KB/RB is used here as the family-level representative;
            # 128 KB Flash / 36 KB RAM is the mainstream G0 spec, and
            # all G0 variants are Cortex-M0+ @ up to 64 MHz.
            "url": "https://www.mouser.com/datasheet/2/389/stm32g070cb-1851175.pdf",
            "url_status": "mouser_mirror_2026-06",
            "url_source": "mouser_datasheet",
            "family": "stm32_g0",
        },
        "STM32WBA": {
            # Datasheet NOT yet downloadable as of 2026-06-28:
            # - st.com Cloudflare-gated (HTTP 000)
            # - Mouser datasheet/2/389/ anti-bot blocks all WBA variant paths
            # - alldatasheet.com returns HTML subscription wall for PDF paths
            # - akizukidenshi.com in maintenance as of 2026-06-28
            # yaml/specs/ST/STM32WBA.yaml already exists as a placeholder from
            # the 2026-06-21 batch; this entry exists so the family extractor
            # `_extract_stm32_wba` (TBD) can be wired up cleanly once a PDF
            # mirror becomes available. url_status starts with st_blocked_ so
            # main() skips the download step.
            "pdf_filename": "STM32WBA_datasheet.pdf",
            "url": "https://www.st.com/resource/en/datasheet/stm32wba52ce.pdf",
            "url_status": "st_blocked_2026-06_no_mirror",
            "url_source": "st_official_blocked",
            "family": "stm32_wba",
        },
    },

    # === TI (PDFs NOT yet downloaded) ===
    "TI": {
        "CC2640R2F": {
            "pdf_filename": "CC2640R2F_datasheet.pdf",
            "url": "https://www.ti.com/lit/ds/symlink/cc2640r2f.pdf",
            "family": "cc26xx",
        },
        "CC2652R": {
            "pdf_filename": "CC2652R_datasheet.pdf",
            "url": "https://www.ti.com/lit/ds/symlink/cc2652r.pdf",
            "family": "cc26xx",
        },
        "CC1310": {
            "pdf_filename": "CC1310_datasheet.pdf",
            "url": "https://www.ti.com/lit/ds/symlink/cc1310.pdf",
            "family": "cc13xx",
        },
        "CC2340R5": {
            "pdf_filename": "CC2340R5_datasheet.pdf",
            "url": "https://www.ti.com/lit/ds/symlink/cc2340r5.pdf",
            "family": "cc26xx",
        },
        "MSPM0G3507": {
            "pdf_filename": "MSPM0G3507_datasheet.pdf",
            "url": "https://www.ti.com/lit/ds/symlink/mspm0g3507.pdf",
            "family": "mspm0",
        },
        "CC3300": {
            "pdf_filename": "CC3300_datasheet.pdf",
            # TI official lit/ds PDF (Rev. F as of 2026-06-28). Shared with
            # CC3301; CC3300 is the Wi-Fi 6 only variant, CC3301 adds BLE 5.4.
            "url": "https://www.ti.com/lit/ds/symlink/cc3300.pdf",
            "url_status": "ti_official_2026-06",
            "url_source": "ti_datasheet",
            "family": "cc33xx",
        },
    },

    # === WCH (Nanjing Qinheng / 沁恒) — RISC-V MCUs ===
    # wch-ic.com serves datasheets behind a JS SPA, so we use mirrors.
    "WCH": {
        "CH32V003": {
            "pdf_filename": "CH32V003_datasheet.pdf",
            # akizukidenshi mirror of the official English datasheet PDF.
            # 583 KB, 17 pages. wch-ic.com itself is a JS SPA that doesn't
            # serve PDFs to plain curl.
            "url": "https://akizukidenshi.com/goodsaffix/CH32V003.pdf",
            "url_status": "akizukidenshi_mirror_2026-06",
            "url_source": "akizukidenshi_datasheet",
            "family": "wch_riscv",
        },
        "CH32V103R8T6": {
            "pdf_filename": "CH32V103_datasheet.pdf",
            # platan.ru mirror (Russian electronics distributor) of the
            # official English datasheet PDF. 1.2 MB.
            "url": "https://doc.platan.ru/pdf/datasheets/wch/CH32V103.pdf",
            "url_status": "platan_mirror_2026-06",
            "url_source": "platan_datasheet",
            "family": "wch_riscv",
        },
        "CH32V307VCT6": {
            "pdf_filename": "CH32V307_datasheet.pdf",
            # jc-net.co.jp mirror (Japanese electronics shop) of the
            # CH32V303/305/307 family datasheet. 1.4 MB. WCH does not
            # publish a separate V307-only datasheet — the family PDF
            # covers V303/V305/V307 and V208.
            "url": "http://www.jc-net.co.jp/pdf/CH32V307DS0-EN.pdf",
            "url_status": "jcnet_mirror_2026-06",
            "url_source": "jcnet_datasheet",
            "family": "wch_riscv",
        },
    },

    # === Silergy (矽力杰) — DC/DC converters + battery chargers ===
    # silergy.com is a JS SPA and silergy.com/product/<x>/download is 404
    # to plain curl; we use distributor mirrors and Azure Blob.
    "Silergy": {
        "SY8089": {
            "pdf_filename": "SY8089_datasheet.pdf",
            # olimex.com carries SY8009A family resources; the SY8089AAAC
            # PDF is the closest match (datasheet header reads "SY8089").
            "url": "https://www.olimex.com/Products/Components/IC/SY8009A/resources/SY8089AAAC.pdf",
            "url_status": "olimex_mirror_2026-06",
            "url_source": "olimex_datasheet",
            "family": "silergy_dcdc",
        },
        "SY8120i": {
            "pdf_filename": "SY8120i_datasheet.pdf",
            # Azure Blob storage (xonstorage) — Application Note PDF for the
            # SY8120I family. Note: 11.4 MB includes full app note; the
            # actual datasheet is the first ~10 pages.
            "url": "https://xonstorage.z8.web.core.windows.net/pdf/silergy_sy8120iabc_xonjuly20_20_link.pdf",
            "url_status": "azure_blob_mirror_2026-06",
            "url_source": "xonstorage_datasheet",
            "family": "silergy_dcdc",
        },
        "SY6970": {
            "pdf_filename": "SY6970_datasheet.pdf",
            # us1.silergy.com download endpoint (Chinese datasheet, 11
            # pages, 1.2 MB). Note: id=3758 happens to be SY6970 in the
            # Silergy download backend.
            "url": "https://us1.silergy.com/download/downloadFile?id=3758&type=product&ftype=note",
            "url_status": "silergy_official_2026-06",
            "url_source": "silergy_datasheet",
            "family": "silergy_dcdc",
        },
    },

    # === SG Micro (圣邦微) — analog ICs (switches, amplifiers, LDOs) ===
    # sg-micro.com serves PDFs via /rect/assets/<uuid>/<file>.pdf with
    # an access_token. The token is short-lived but the URLs are public
    # enough that Tavily + browser can extract them. The file URLs in
    # the product page HTML are stable enough to be useful mirrors.
    "SGMicro": {
        "SGM3157": {
            "pdf_filename": "SGM3157_datasheet.pdf",
            # Sg-micro.com rect asset — 6Ω SPDT analog switch datasheet.
            "url": "https://www.sg-micro.com/rect/assets/a22623ad-a59a-4732-b010-4b667f6b9a7c/SGM3157.pdf",
            "url_status": "sgmicro_official_2026-06",
            "url_source": "sgmicro_datasheet",
            "family": "sgmicro_analog",
        },
        "SGM8903": {
            "pdf_filename": "SGM8903_datasheet.pdf",
            # Sg-micro.com rect asset — capless 3Vrms line driver datasheet.
            "url": "https://www.sg-micro.com/rect/assets/499e5773-5bd6-49f3-bd1d-021af3649000/SGM8903.pdf",
            "url_status": "sgmicro_official_2026-06",
            "url_source": "sgmicro_datasheet",
            "family": "sgmicro_analog",
        },
    },
}

# Vendor-keyed paths
def pdf_dir(vendor: str) -> Path:
    # Map vendor catalog name to the lowercase directory name used on
    # disk. Compound vendor names like "SiliconLabs" don't lowercase to
    # a sensible dir name, so spell out the mapping explicitly.
    dir_map = {"SiliconLabs": "silabs"}
    dirname = dir_map.get(vendor, vendor.lower())
    return EMB_DIR / dirname / "datasheet"

def yaml_path(vendor: str, part: str) -> Path:
    return SPECS_DIR / vendor / f"{part}.yaml"


# === Helpers =============================================================
def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def save_yaml(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        # width=10000 disables line wrapping, which would otherwise split
        # long scalars across two lines and round-trip as 'Arm Cortex\n
        # M33' instead of 'Arm Cortex M33' (PyYAML single-quote multi-line
        # folding bug). We accept potentially long output lines in
        # exchange for byte-stable round-trips.
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=10000)


def download_pdf(vendor: str, part: str, info: dict) -> Path:
    """Download the datasheet PDF for a part. Validates it's a real PDF."""
    # Honour url_status markers — don't even try a download if the URL
    # is known to be unreachable from this network.
    url_status = info.get("url_status", "")
    if url_status.startswith(("st_blocked_", "stale_2026-06_no_mirror")):
        raise FileNotFoundError(
            f"Skip: {vendor}/{part} marked url_status={url_status!r}; "
            f"PDF download is known to fail from this environment."
        )

    dest_dir = pdf_dir(vendor)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / info["pdf_filename"]
    url = info["url"]
    print(f"  [download] {url}")
    # Some distributor CDNs (alcom, mouser pdfDocs) check User-Agent;
    # without one they return HTML 403/404 instead of the PDF.
    subprocess.run([
        "curl", "-sSL",
        "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
        "-o", str(dest), url,
    ], check=True)
    with open(dest, "rb") as f:
        magic = f.read(8)
    if not magic.startswith(b"%PDF"):
        print(f"  [warn] downloaded file is not a PDF (magic={magic!r}); removing {dest.name}")
        dest.unlink()
        raise FileNotFoundError(
            f"Datasheet download for {vendor}/{part} returned a non-PDF page; URL may be wrong: {url}"
        )
    return dest


# === Family-specific extractors ==========================================
# These are adapted from renesas-search-publish/scripts/update_specs.py.
# Each takes (extracted: dict, full_text: str) and may add to extracted["specs"].

def _extract_da_ble(extracted: dict, text: str) -> dict:
    """Renesas SmartBond DA series BLE SoC."""
    s = extracted.setdefault("specs", {})
    # Core. Capture 'Cortex-M33' (or M0+/M4) plus the description that
    # follows on the SAME pdfplumber line, up to the first ' MHz' or
    # 120 chars — DA1470x uses 'Arm Cortex\nM33 application processor,
    # 32 kHz to 160 MHz' across two pdfplumber lines. We don't try to
    # be clever about ranges like '32 kHz to 160 MHz'; we just keep the
    # description as-is and the user can see the underlying spec in the
    # PDF citation.
    if not s.get("cores"):
        core_m = re.search(
            r"Arm\s*®?\s*Cortex[\s-]*M(\d+\+?)"
            r"([^\n]{0,200}?(?:@?\s*\d+\s*MHz|MHz))?",
            text, re.IGNORECASE,
        )
        if core_m:
            label = f"Arm Cortex-M{core_m.group(1)}"
            if core_m.group(2):
                # trim trailing comma/whitespace, collapse runs of ws
                extra = re.sub(r"\s+", " ", core_m.group(2).strip().rstrip(",")).strip()
                if extra:
                    label += " " + extra
            s["cores"] = [label]
    # BLE version
    ble_m = re.search(r"Bluetooth\s*®?\s*(?:LE|low\s*energy)\s*(\d+\.\d+(?:\.[xX])?)", text, re.IGNORECASE)
    if ble_m and not s.get("ble_version"):
        s["ble_version"] = ble_m.group(1)
    # RAM
    ram_m = re.search(r"RAM\s+of\s+(\d+(?:\.\d+)?\s*kB)", text, re.IGNORECASE)
    if ram_m and not s.get("ram"):
        s["ram"] = ram_m.group(1)
    # Flash / OTP
    flash_m = re.search(r"(\d+\s*kB)\s+(?:embedded\s+)?(?:One-Time-Programmable\s*)?(?:Flash|OTP)", text, re.IGNORECASE)
    if flash_m and not s.get("flash"):
        s["flash"] = flash_m.group(1)
    # Packages
    # Dedupe on (type, pin_count) — the full PDF text often repeats the
    # package list across multiple sections.
    seen_pkgs = set()
    for pkg_m in re.finditer(
        r"(WLCSP[^\n,]+?balls?,\s*[\d.]+\s*[×x]\s*[\d.]+,?\s*[\d.]*\s*mm(?:\s*pitch)?)"
        r"|(FC?GQFN[^\n,]+?pins?,\s*[\d.]+\s*[×x]\s*[\d.]+,?\s*[\d.]*\s*mm)",
        text,
    ):
        pkg_text = pkg_m.group(0)
        pin_m = re.search(r"(\d+)\s*(?:balls?|pins?|Ld)", pkg_text)
        size_m = re.search(r"([\d.]+)\s*[×x]\s*([\d.]+)", pkg_text)
        type_m = re.search(r"(WLCSP|FC?GQFN|QFN|LQFP)", pkg_text)
        if pin_m and type_m:
            key = (type_m.group(1), int(pin_m.group(1)))
            if key in seen_pkgs:
                continue
            seen_pkgs.add(key)
            s.setdefault("packages", []).append({
                "type": type_m.group(1),
                "pin_count": int(pin_m.group(1)),
                "size_mm": f"{size_m.group(1)} × {size_m.group(2)}" if size_m else None,
            })
    return extracted


def _extract_ra(extracted: dict, text: str) -> dict:
    """Renesas RA Cortex-M MCU (covers M33 / M4 / M85 / M23 / M0+ etc.).

    Originally hardcoded to M33 (RA6M5 was the first RA part verified);
    widened to any Cortex-M variant after the 2026-07-07 phase2 re-extract
    of the 25 Renesas phase1-recovery yaml showed RA6M2 / RA6M3 (Cortex-M4)
    failed to extract cores and got stuck on 'needs-re-extraction-factory-
    error-2026-07-05'. RA6M5 behavior is unchanged because M33 still matches
    first in the union.
    """
    s = extracted.setdefault("specs", {})
    # Core + max freq — match any Arm Cortex-M variant
    freq_m = re.search(r"Maximum operating frequency\s*:?\s*(?:up to\s+)?(\d+)\s*MHz", text)
    core_m = re.search(r"Arm\s*®?\s*Cortex[\s-]*M(\d+\+?)", text)
    if core_m and freq_m and not s.get("cores"):
        s["cores"] = [f"Arm Cortex-M{core_m.group(1)} @ up to {freq_m.group(1)} MHz"]
    # Code flash
    cf_m = re.search(r"[Uu]p\s+to\s+(\d+(?:\.\d+)?)\s*-?\s*(KB|MB|Kbyte|Mbyte)\s*code\s*flash", text, re.IGNORECASE)
    if cf_m and not s.get("flash"):
        s["flash"] = f"up to {cf_m.group(1)} {cf_m.group(2)} code flash"
    # Data flash
    df_m = re.search(r"(\d+(?:\.\d+)?)\s*-?\s*(KB|MB)\s*[Dd]ata\s*flash(?:\s*memory)?", text)
    if df_m and not s.get("data_flash"):
        s["data_flash"] = f"{df_m.group(1)} {df_m.group(2)}"
    # SRAM
    ram_m = re.search(r"(\d+(?:\.\d+)?)\s*-?\s*(KB|MB)\s*SRAM", text)
    if ram_m and not s.get("ram"):
        s["ram"] = f"{ram_m.group(1)} {ram_m.group(2)} SRAM"
    # Packages
    # Dedupe on (type, pin_count) — the full PDF text often repeats the
    # package list across multiple sections (overview table, ordering
    # information, package code list). With MAX_FULL_TEXT_PAGES = 0 the
    # same package can show up 5-20 times.
    seen_pkgs = set()
    for pkg_m in re.finditer(r"(\d+)-pin\s+(LQFP|QFN|BGA|TFLGA|TQFN|WLCSP)", text):
        key = (pkg_m.group(2), int(pkg_m.group(1)))
        if key in seen_pkgs:
            continue
        seen_pkgs.add(key)
        s.setdefault("packages", []).append({"type": pkg_m.group(2), "pin_count": int(pkg_m.group(1))})
    return extracted


# TODO: implement the other Renesas family extractors (rx, rl78, isl_power,
# sensor, nfc) by porting from renesas-search-publish/scripts/update_specs.py
# Then add Nordic / NXP / ST / TI family extractors.
# (rl78/rx/isl_power/sensor/nfc ported 2026-06-23 — see below.
#  Nordic/NXP/ST/TI still TODO.)

def _extract_rl78(extracted: dict, text: str) -> dict:
    """Renesas RL78 low-power MCU — "NN to NN KB" range patterns.

    Ported from renesas-search-publish/scripts/update_specs.py.
    """
    s = extracted.setdefault("specs", {})

    # Cores
    if not s.get("cores"):
        s["cores"] = ["RL78 CPU core (CISC, 3-stage pipeline)"]

    # Code flash: "Code flash memory: 16 to 512 KB" / "16- to 512-Kbyte code flash"
    cf_m = re.search(
        r"Code\s*flash\s*(?:memory\s*)?:?\s*(\d+(?:\.\d+)?)\s*(?:to|-|~)\s*(\d+(?:\.\d+)?)\s*"
        r"(KB|MB|Kbyte|Mbyte|K-?byte|M-?byte)",
        text, re.IGNORECASE,
    )
    if cf_m and not s.get("flash"):
        s["flash"] = f"{cf_m.group(1)} to {cf_m.group(2)} {cf_m.group(3)} code flash"

    # Data flash: "Data flash memory: 4 KB and 8 KB"
    df_m = re.search(
        r"Data\s*flash\s*(?:memory\s*)?:?\s*((?:\d+\s*(?:KB|MB|Kbyte)\s*(?:and\s*)?){1,3})",
        text, re.IGNORECASE,
    )
    if df_m and not s.get("data_flash"):
        s["data_flash"] = df_m.group(1).strip().rstrip(",")

    # RAM: "On-chip RAM: 2.5 to 48 KB"
    ram_m = re.search(r"On-chip\s*RAM\s*:?\s*([\d.]+\s*to\s*[\d.]+\s*kB)", text, re.IGNORECASE)
    if ram_m and not s.get("ram"):
        s["ram"] = ram_m.group(1)

    # Operating frequency: "32 MHz operation"
    freq_m = re.search(r"(\d+)\s*MHz\s*operation", text)
    if freq_m and not s.get("max_core_frequency_mhz"):
        s["max_core_frequency_mhz"] = int(freq_m.group(1))

    # Active current: "66 μA/MHz"
    act_m = re.search(r"(\d+(?:\.\d+)?)\s*[μu]A\s*/\s*MHz", text)
    if act_m and not s.get("active_current_ua_per_mhz"):
        s["active_current_ua_per_mhz"] = float(act_m.group(1))

    return extracted


def _extract_rx(extracted: dict, text: str) -> dict:
    """Renesas RX 32-bit MCU — "up to 4 MB" / "1 MB SRAM" patterns.

    Ported from renesas-search-publish/scripts/update_specs.py.
    """
    s = extracted.setdefault("specs", {})

    # Core + max freq (RX-specific phrasing)
    if not s.get("cores"):
        freq_m = re.search(r"Maximum operating frequency\s*:?\s*(?:up to\s+)?(\d+)\s*MHz", text)
        core_m = re.search(r"(32-bit\s+RXv\d\s+CPU)", text)
        if core_m:
            desc = core_m.group(1)
            if freq_m:
                desc += f" @ up to {freq_m.group(1)} MHz"
            s["cores"] = [desc]

    # Flash: "up to 4 MB" / "up to 4 Mbytes" / "up to 1-MB flash memory"
    flash_m = re.search(
        r"[Uu]p to\s+(\d+(?:\.\d+)?)\s*-?\s*(KB|MB|Kbytes|Mbytes|M-?byte|K-?byte)"
        r"(?:\s+(?:of\s+)?(?:code\s+|on-chip\s+)?flash(?:\s+memory)?)?",
        text,
    )
    if flash_m and not s.get("flash"):
        s["flash"] = f"up to {flash_m.group(1)} {flash_m.group(2)}"

    # SRAM: "1 MB SRAM" / "1 MBSRAM" / "128-KB SRAM"
    ram_m = re.search(r"(\d+(?:\.\d+)?)\s*-?\s*(KB|MB)\s*SRAM", text)
    if ram_m and not s.get("ram"):
        s["ram"] = f"{ram_m.group(1)} {ram_m.group(2)} SRAM"

    # Operating voltage: "2.7- to 3.6-V supply"
    vcc_m = re.search(
        r"(\d+(?:\.\d+)?)\s*-\s*to\s*-\s*(\d+(?:\.\d+)?)\s*-\s*V\s*supply", text,
    )
    if vcc_m and not s.get("operating_voltage_v"):
        s["operating_voltage_v"] = f"{vcc_m.group(1)} to {vcc_m.group(2)}"

    # Packages: Renesas package codes (PLQP0176KB-C etc.) — RX datasheets
    # use these codes more than pin-count-style. Cap at 6 entries.
    if not s.get("packages"):
        packages = []
        for pkg_m in re.finditer(
            r"(PLQP|PLBG|PTLG)\d+[A-Z\-]+(?:\s+[\dxX×\.\s\-]+mm(?:,\s*[\d.]+-mm\s*pitch)?)?",
            text,
        ):
            line = pkg_m.group(0)
            type_m = re.search(r"(PLQP|PLBG|PTLG)", line)
            size_m = re.search(r"(\d+)\s*[×x]\s*(\d+)\s*mm", line)
            pitch_m = re.search(r"([\d.]+)-mm\s*pitch", line)
            pkg = {"type": type_m.group(1) if type_m else "LQFP"}
            if size_m:
                pkg["size_mm"] = f"{size_m.group(1)} × {size_m.group(2)}"
            if pitch_m:
                pkg["pitch_mm"] = float(pitch_m.group(1))
            packages.append(pkg)
        if packages:
            s["packages"] = packages[:6]

    return extracted


def _extract_isl_power(extracted: dict, text: str) -> dict:
    """Renesas Intersil power management — DC/DC, LDO, charger, supervisor.

    Ported from renesas-search-publish/scripts/update_specs.py.
    """
    s = extracted.setdefault("specs", {})

    # Function/category detection
    if re.search(r"mini[\s-]*PMIC|Dual\s+Step[\s-]*Down", text):
        s["category"] = "DC/DC PMIC"
    elif re.search(r"Battery\s+Charger", text):
        s["category"] = "Battery Charger"
    elif re.search(r"Voltage\s+Supervisor|Watchdog\s+Timer", text):
        s["category"] = "Voltage Supervisor"
    elif re.search(r"Buck[\s-]*Boost\s+NVDC", text):
        s["category"] = "NVDC Battery Charger"

    # Voltage range
    vin_m = re.search(
        r"(?:Input|Input\s+Voltage\s+Range|VIN)[^.]*?(\d+(?:\.\d+)?)\s*V?\s*to\s*(\d+(?:\.\d+)?)\s*V",
        text, re.IGNORECASE,
    )
    if vin_m and not s.get("input_voltage_v"):
        s["input_voltage_v"] = f"{vin_m.group(1)} to {vin_m.group(2)}"

    # Current specs: "Dual 800mA" or "Up to 1A"
    cur_m = re.search(r"(?:Dual\s+)?(\d+)\s*mA", text)
    if cur_m and not s.get("max_output_current_ma"):
        s["max_output_current_ma"] = int(cur_m.group(1))

    # Quiescent current: "50μA IQ"
    iq_m = re.search(r"(\d+(?:\.\d+)?)\s*[μu]A\s*IQ", text, re.IGNORECASE)
    if iq_m and not s.get("quiescent_current_ua"):
        s["quiescent_current_ua"] = float(iq_m.group(1))

    return extracted


def _extract_sensor(extracted: dict, text: str) -> dict:
    """Renesas HS3xxx humidity/temperature sensor.

    Ported from renesas-search-publish/scripts/update_specs.py.
    """
    s = extracted.setdefault("specs", {})

    s["function"] = "Relative humidity and temperature sensor"
    s["interface"] = "I2C"

    rh_m = re.search(r"(\d+)\s*-\s*(\d+)\s*%\s*RH", text)
    if rh_m and not s.get("rh_range_percent"):
        s["rh_range_percent"] = f"{rh_m.group(1)} to {rh_m.group(2)}"

    return extracted


def _extract_nfc(extracted: dict, text: str) -> dict:
    """Panthronics/Renesas NFC wireless charging.

    Ported from renesas-search-publish/scripts/update_specs.py.
    """
    s = extracted.setdefault("specs", {})

    s["function"] = "NFC wireless charging IC"

    power_m = re.search(r"(?:up to|maximum)\s+(\d+(?:\.\d+)?)\s*W", text)
    if power_m and not s.get("max_output_power_w"):
        s["max_output_power_w"] = float(power_m.group(1))

    return extracted


def _extract_nrf(extracted: dict, text: str) -> dict:
    """Nordic Semiconductor nRF52 / nRF53 / nRF54 / nRF91 BLE/WiFi/cellular SoC.

    Nordic Product Specifications follow a very consistent "Key features" bullet
    list on page 1. Patterns verified against nRF52832 PS v1.1 (Arduino mirror).
    Other parts (nRF5340, nRF54L15, nRF9160) use the same wording style; the
    regex below targets that style and will silently skip fields that aren't
    present for a given part.

    Most matches are guarded with `not s.get(...)` so a re-run never overwrites
    a manually-edited value already in the YAML. The exception is `flash` /
    `ram`: we always overwrite the generic-pass values because the generic
    "kB RAM" regex picks the smaller SKU on Nordic page-1 text and we want
    the max-config variant.
    """
    s = extracted.setdefault("specs", {})

    # --- Core / clock ---
    # Nordic uses "ARM® Cortex®-M4 32-bit processor with FPU, 64 MHz"
    # (nRF52 series) or "Arm® Cortex®-M33 processor" (nRF53/nRF54 series,
    # without "32-bit" qualifier). The clock can appear either before
    # ("128 MHz Arm Cortex-M33 processor") or after ("Cortex-M4 ... 64 MHz")
    # the core mention, so we capture both positions. The ® characters
    # need to be in the character class.
    # The post-core MHz capture is bounded to 60 chars after 'processor'
    # to avoid wandering into unrelated MHz mentions on the same page —
    # nRF9160 (cellular SiP) cover page has "700 to 2200 MHz" LTE band
    # ranges 100+ chars after the first 'Cortex-M33' mention, and a greedy
    # `.*?` would have grabbed 2200 as the app CPU clock.
    if not s.get("cores"):
        # The post-core MHz window is 60 chars (NEWLINE-AGNOSTIC, using
        # \\s to span pdfplumber's line breaks), allowing capture of
        # 'Cortex-M33 with TrustZone technology \\n 128 MHz' style
        # (nRF5340) where pdfplumber puts 128 MHz on a new line.
        # The 60-char cap safely blocks nRF9160 cellular SiP's
        # 'Cortex-M33 ... 2200 MHz' LTE band ranges — the latter
        # appears 33,000+ chars after the first Cortex-M33 mention.
        core_m = re.search(
            r"(?:(\d+)\s*MHz\s+)?"
            r"ARM[\s®]*Cortex[\s®]*-?M(\d+)(?:\s*32-bit)?(?:\s*processor)?"
            r"(?:\s{0,30}?(?:with\s+)?(?:FPU|TrustZone)(?:\s+\w+)?)?"
            r"(?:.{0,80}?(\d+)\s*MHz)?",
            text, re.DOTALL | re.IGNORECASE,
        )
        if core_m:
            desc = f"Arm Cortex-M{core_m.group(2)}"
            mhz = core_m.group(1) or core_m.group(3)
            if mhz:
                desc += f" @ {mhz} MHz"
            # Detect FPU via a separate check (nRF52 wording)
            if re.search(r"Cortex[\s\u00ae]*-?M\d+(?:\s*32-bit)?\s*processor\s+with\s+FPU", text):
                desc += " with FPU"
            # TrustZone (nRF54L15)
            if re.search(r"Cortex[\s\u00ae]*-?M\d+(?:\s*32-bit)?(?:[^.\n]{0,30}processor)?(?:[^.\n]{0,40}?TrustZone)", text):
                desc += " with TrustZone"
            s["cores"] = [desc]

    # --- CoreMark ---
    cm_m = re.search(r"(\d+)\s*EEMBC\s*CoreMark", text, re.IGNORECASE)
    if cm_m and not s.get("coremark"):
        s["coremark"] = int(cm_m.group(1))

    # --- Flash / RAM. Nordic PS text varies across PS versions:
    #   * nRF52832 v1.1 page 1: "512 kB flash/64 kB RAM"  (paired, single SKU)
    #   * nRF52840 v1.1 page 1: "1 MB flash and 256 kB RAM" (separate lines)
    #   * nRF5340 v1.0 page 1: similar paired style
    #   * nRF54L15 PS: uses "NVM" instead of "flash" — "1.5 MB NVM and 256 KB RAM"
    # The FIRST occurrence is the max-config variant. The generic pdfplumber
    # pass may have already set `ram` to a smaller value via its looser
    # "kB RAM" regex — we always overwrite here. ---
    mem_matches = list(re.finditer(r"(\d+)\s*kB\s*flash\s*/\s*(\d+)\s*kB\s*RAM", text))
    if mem_matches:
        first = mem_matches[0]
        s["flash"] = f"{first.group(1)} kB"
        s["ram"] = f"{first.group(2)} kB"
    else:
        # Fallback: "1 MB flash and 256 kB RAM" or "1.5 MB NVM and 256 KB RAM"
        # (nRF54L15). Match either 'flash' or 'NVM' as the non-volatile memory
        # token.
        flash_only = re.search(
            r"(\d+(?:\.\d+)?)\s*(MB|kB)\s*(?:flash|NVM|non-volatile\s+memory)",
            text, re.IGNORECASE,
        )
        if flash_only and not s.get("flash"):
            s["flash"] = f"{flash_only.group(1)} {flash_only.group(2)} (NVM)"
        # RAM only if we got flash from the same fallback path (so we don't
        # accidentally pick up "256 kB RAM" without flash context).
        if "flash" in s and not s.get("ram"):
            ram_only = re.search(r"(\d+)\s*kB\s*RAM", text, re.IGNORECASE)
            if ram_only:
                s["ram"] = f"{ram_only.group(1)} kB"

    # --- Operating voltage.
    # Nordic PS text varies: some write "1.7 V–3.6 V" (en-dash), others
    # "1.7 V to 5.5 V". Accept both. ---
    vcc_m = re.search(
        r"Supply\s*voltage\s*range\s*(\d+(?:\.\d+)?)\s*V\s*"
        r"(?:[\u2013\u2014\-]+|to)\s*"
        r"(\d+(?:\.\d+)?)\s*V",
        text, re.IGNORECASE,
    )
    if vcc_m and not s.get("operating_voltage_v"):
        s["operating_voltage_v"] = f"{vcc_m.group(1)} to {vcc_m.group(2)}"
    # Fallback for PS that omit the word "range" but still mention both
    # voltages — nRF54L15 uses "1.7 V to 3.6 V supply and I/O voltage".
    if not s.get("operating_voltage_v"):
        vcc_fb = re.search(
            r"(\d+(?:\.\d+)?)\s*V\s*(?:[\u2013\u2014\-]+|to)\s*"
            r"(\d+(?:\.\d+)?)\s*V\s*(?:supply|and\s+I/O|supply\s*and\s*I/O)",
            text, re.IGNORECASE,
        )
        if vcc_fb:
            s["operating_voltage_v"] = f"{vcc_fb.group(1)} to {vcc_fb.group(2)}"

    # --- Radio: TX current, RX current, sensitivity, TX power range ---
    tx_cur_m = re.search(r"(\d+(?:\.\d+)?)\s*mA\s*peak\s*current\s*in\s*TX", text)
    if tx_cur_m and not s.get("tx_peak_current_ma"):
        s["tx_peak_current_ma"] = float(tx_cur_m.group(1))

    rx_cur_m = re.search(r"(\d+(?:\.\d+)?)\s*mA\s*peak\s*current\s*in\s*RX", text)
    if rx_cur_m and not s.get("rx_peak_current_ma"):
        s["rx_peak_current_ma"] = float(rx_cur_m.group(1))

    rx_sens_m = re.search(r"(-?\d+)\s*dBm\s*sensitivity", text, re.IGNORECASE)
    if rx_sens_m and not s.get("rx_sensitivity_dbm"):
        s["rx_sensitivity_dbm"] = int(rx_sens_m.group(1))

    # Nordic PS wording varies: nRF52832 v1.1 says "TX power -20 to +4 dBm",
    # nRF52840 v1.1 says "-20 to +8 dBm TX power". Accept either order.
    # The second number often has an explicit '+' sign — we capture it as a
    # separate group to preserve the sign in the output.
    tx_pwr_m = re.search(
        r"(?:TX\s*power\s*(-?\d+)\s*to\s*(\+?\d+)\s*dBm)"
        r"|(?:(-?\d+)\s*to\s*(\+?\d+)\s*dBm\s*TX\s*power)",
        text, re.IGNORECASE,
    )
    if tx_pwr_m and not s.get("tx_power_range_dbm"):
        a, b = tx_pwr_m.group(1), tx_pwr_m.group(2)
        if a is None:
            a, b = tx_pwr_m.group(3), tx_pwr_m.group(4)
        s["tx_power_range_dbm"] = f"{a} to {b}"

    # --- Low-power modes (Nordic calls them OFF and ON) ---
    off_m = re.search(
        r"(\d+(?:\.\d+)?)\s*[μu]A\s*at\s*3\s*V\s*in\s*OFF\s*mode(?:\s*with\s*(\d+)\s*kB\s*RAM\s*retention)?",
        text,
    )
    if off_m and not s.get("system_off_current_ua"):
        s["system_off_current_ua"] = float(off_m.group(1))
        if off_m.group(2):
            s.setdefault("off_mode_notes", []).append(
                f"{off_m.group(2)} kB RAM retention"
            )

    on_m = re.search(
        r"(\d+(?:\.\d+)?)\s*[μu]A\s*at\s*3\s*V\s*in\s*ON\s*mode(?:,\s*no\s*RAM\s*retention,\s*wake\s*on\s*RTC)?",
        text,
    )
    if on_m and not s.get("system_on_current_ua"):
        s["system_on_current_ua"] = float(on_m.group(1))

    return extracted


def _extract_nrf_companion(extracted: dict, text: str) -> dict:
    """Nordic Semiconductor WiFi 6 companion ICs (nRF7002, nRF7001, ...).

    Companion ICs are NOT standalone MCUs — they pair with a host MCU
    (nRF52840 / nRF5340 / nRF54L15) over SPI/QSPI. So traditional fields
    (cores / flash / ram) do not apply; the datasheet focuses on RF
    performance, supply voltage, package, and interface details.

    Verified against nRF7002 Product Specification v1.2 (Farnell mirror
    2026-06). Page 2 'Key features' bullet style:
      - 'Wi-Fi 6 companion IC with integrated RF'
      - 'Supports IEEE 802.11 ax and earlier standards'
      - 'Maximum output power 20 dBm'
      - 'Dual-band 2.4 GHz and 5 GHz'
      - 'Supply voltage range 2.9 – 4.5 V'
      - 'Operating temperature range -40°C to 85°C'
      - Package: 'QFN48 package, 6 x 6 mm' / 'WLCSP81 package, 3.8 x 3.4 mm'
    """
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        # Companion ICs have no host CPU of their own.
        s["cores"] = "Companion IC (no host CPU; pairs with nRF52/nRF53/nRF54)"

    if not s.get("wireless"):
        wireless_modes = []
        if re.search(r"Wi-?Fi[\s®]*\s*6\b|IEEE\s*802\.11\s*ax", text, re.IGNORECASE):
            wireless_modes.append("Wi-Fi 6 (802.11ax)")
        # Nordic datasheets list legacy standards as a list inside parens,
        # e.g. 'IEEE 802.11 a/b/g/n/ac'. Match a single 'ac' or 'n' in that
        # parenthesized form (avoid matching unrelated 'ac' abbreviations).
        if re.search(r"802\.11[^\n]*?\b(?:a/)?b/g/n/ac|802\.11[^\n]*?\b(?:a/)?b/g/n/a", text, re.IGNORECASE) \
                or re.search(r"802\.11\s*ac", text, re.IGNORECASE) \
                or re.search(r"Wi-?Fi[\s®]*\s*5\b", text, re.IGNORECASE):
            wireless_modes.append("Wi-Fi 5 (802.11ac)")
        if re.search(r"802\.11[^\n]*?\b(?:a/)?b/g/n/ac|802\.11[^\n]*?\b(?:a/)?b/g/n/a|802\.11\s*n", text, re.IGNORECASE) \
                or re.search(r"Wi-?Fi[\s®]*\s*4\b", text, re.IGNORECASE):
            wireless_modes.append("Wi-Fi 4 (802.11n)")
        if re.search(r"Dual-?band", text, re.IGNORECASE) and re.search(r"2\.4\s*GHz", text) and re.search(r"5\s*GHz", text):
            wireless_modes.append("Dual-band 2.4 + 5 GHz")
        if wireless_modes:
            s["wireless"] = wireless_modes

    if not s.get("tx_power_dbm_max"):
        m = re.search(r"[Mm]aximum\s+output\s+power\s+(\d+)\s*dBm", text, re.IGNORECASE)
        if m:
            s["tx_power_dbm_max"] = int(m.group(1))

    if not s.get("supply_voltage_v_min") or not s.get("supply_voltage_v_max"):
        m = re.search(r"Supply\s+voltage\s+range\s+([\d.]+)\s*[–\-]\s*([\d.]+)\s*V", text, re.IGNORECASE)
        if m:
            s["supply_voltage_v_min"] = float(m.group(1))
            s["supply_voltage_v_max"] = float(m.group(2))

    if not s.get("operating_temp_c_min") or not s.get("operating_temp_c_max"):
        m = re.search(
            r"Operating\s+temperature\s+range\s+(-?\d+)[°\s]*C?\s+to\s+(\+?\d+)[°\s]*C?",
            text, re.IGNORECASE,
        )
        if m:
            s["operating_temp_c_min"] = int(m.group(1))
            s["operating_temp_c_max"] = int(m.group(2))

    if not s.get("package"):
        packages = []
        if re.search(r"QFN\s*48", text, re.IGNORECASE):
            packages.append("QFN48 (6x6 mm)")
        if re.search(r"WLCSP\s*81", text, re.IGNORECASE):
            packages.append("WLCSP81 (3.8x3.4 mm)")
        if re.search(r"QFN\s*56", text, re.IGNORECASE):
            packages.append("QFN56")
        if packages:
            s["package"] = packages

    if not s.get("host_interface"):
        if re.search(r"SPI\s+or\s+QSPI", text, re.IGNORECASE):
            s["host_interface"] = "SPI / QSPI"
        elif re.search(r"\bSPI\b", text, re.IGNORECASE) and re.search(r"\bQSPI\b", text, re.IGNORECASE):
            s["host_interface"] = "SPI / QSPI"
        elif re.search(r"\bSPI\b", text, re.IGNORECASE):
            s["host_interface"] = "SPI"

    return extracted


def _extract_ti_cc26xx(extracted: dict, text: str) -> dict:
    """Texas Instruments SimpleLink CC26xx / CC2640 / CC265x / CC2642 / CC2340
    BLE wireless MCU family.

    Page-1 'Features' bullets verified against CC2640R2F (SWRS204C) and
    CC2340R5. Style: "Cortex-M3 48-MHz clock", "275KB of nonvolatile memory",
    "Wide supply voltage range 1.8 to 3.8 V", "Active-Mode RX: 5.9 mA".

    Picks the first numeric value for max-config variants (CC2640R2F reports
    "275KB of nonvolatile memory including 128KB" — we take 275KB as the max).
    """
    s = extracted.setdefault("specs", {})

    # --- Core / clock ---
    if not s.get("cores"):
        # CC2640R2F: "ARM Cortex-M3 48-MHz clock"
        # CC2340R5: "48MHz Arm Cortex-M0+ processor" (M0+ variant; '+' was
        # previously dropped, yielding M0 instead of M0+).
        m = re.search(
            r"(?:ARM[\s®]*)?Cortex[\s®]*-?M(\d+)(\+?)(?:F)?(?:\s+32-bit)?"
            r"(?:[^,.]*?(?:up to|@)\s+(\d+)\s*-?MHz)?",
            text,
        )
        if m:
            mnum = m.group(1)
            mplus = m.group(2) or ""
            s["cores"] = f"ARM Cortex-M{mnum}{mplus}"
            # Prefer an explicit clock figure if present; otherwise fall back
            # to a leading "48MHz" / "48-MHz" before the core name.
            if m.group(3):
                s["clock_mhz_max"] = int(m.group(3))
            else:
                m2 = re.search(r"(\d+)\s*-?MHz[^,.]*?Cortex[\s®]*-?M\d+\+?", text)
                if m2:
                    s["clock_mhz_max"] = int(m2.group(1))

    # --- Flash (nonvolatile memory) ---
    if not s.get("flash"):
        m = re.search(
            r"(\d+)\s*KB\s+of\s+nonvolatile\s+memory",
            text, re.IGNORECASE,
        )
        if m:
            s["flash"] = f"{m.group(1)} KB"

    # --- SRAM ---
    if not s.get("ram"):
        # CC2640R2F: "Up to 28KB of system SRAM" / "8KB of SRAM for cache"
        # CC2340R5: "32KB SRAM"
        m = re.search(
            r"(?:Up to\s+)?(\d+)\s*KB\s+of\s+(?:system\s+)?SRAM",
            text, re.IGNORECASE,
        )
        if m:
            s["ram"] = f"{m.group(1)} KB"

    # --- Supply voltage range ---
    if not s.get("supply_voltage_v"):
        # "Normal operation: 1.8 to 3.8 V" or "Wide supply voltage range 1.8 to 3.8 V"
        m = re.search(
            r"(?:Normal operation|Wide supply voltage range):?\s*([\d.]+)\s*to\s*([\d.]+)\s*V",
            text, re.IGNORECASE,
        )
        if m:
            s["supply_voltage_v"] = f"{m.group(1)}-{m.group(2)} V"

    # --- Active-mode RX current (mA) ---
    if not s.get("active_rx_ma"):
        m = re.search(
            r"Active-Mode\s+RX:\s*([\d.]+)\s*mA",
            text, re.IGNORECASE,
        )
        if m:
            s["active_rx_ma"] = float(m.group(1))

    # --- Active-mode TX current at 0 dBm (mA) ---
    if not s.get("active_tx_0dbm_ma"):
        m = re.search(
            r"Active-Mode\s+TX\s+at\s+0\s*dBm:\s*([\d.]+)\s*mA",
            text, re.IGNORECASE,
        )
        if m:
            s["active_tx_0dbm_ma"] = float(m.group(1))

    # --- Standby current ---
    if not s.get("standby_current_ua"):
        m = re.search(
            r"Standby:\s*([\d.]+)\s*[µu]A",
            text, re.IGNORECASE,
        )
        if m:
            s["standby_current_ua"] = float(m.group(1))

    # --- Shutdown current ---
    if not s.get("shutdown_current_na"):
        m = re.search(
            r"Shutdown:\s*(\d+)\s*nA",
            text, re.IGNORECASE,
        )
        if m:
            s["shutdown_current_na"] = int(m.group(1))

    # --- RF: BLE version + RX sensitivity ---
    ble_version = None
    for pattern in [
        r"Bluetooth[\s®]*Low\s+Energy\s+(\d+\.\d+)",
        r"Qualified\s+against\s+Bluetooth\s+Core\s+(\d+\.\d+)",
        r"Bluetooth\s+(?:Low\s+Energy\s+)?Core\s+(\d+\.\d+)",
    ]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            ble_version = m.group(1)
            break
    if ble_version and not s.get("wireless"):
        s["wireless"] = f"BLE {ble_version}"
    if ble_version and not s.get("ble_version"):
        s["ble_version"] = ble_version

    if not s.get("rx_sensitivity_dbm"):
        m = re.search(
            r"receiver\s+sensitivity\s*\(?(-?\d+)\s*dBm\)?\s*for\s+BLE",
            text, re.IGNORECASE,
        )
        if m:
            s["rx_sensitivity_dbm"] = int(m.group(1))

    return extracted


def _extract_ti_cc33xx(extracted: dict, text: str) -> dict:
    """Texas Instruments SimpleLink CC33xx WiFi 6 + BLE 5.4 companion ICs
    (CC3300 = WiFi only, CC3301 = WiFi 6 + BLE 5.4).

    Companion ICs pair with a host MCU/processor (MSPM0 / Sitara / Linux SoC)
    over SDIO or SPI. Like the nRF7002, traditional fields (cores / flash /
    ram) do not apply.

    Verified against CC3300/CC3301 datasheet SWRS294F (Rev. F, Oct 2025,
    TI official lit/ds mirror, 33 pages). Page 1 'Key Features' style:
      - 'Wi-Fi 6 (802.11ax)'
      - 'Bluetooth® Low Energy 5.4 in CC3301 devices'
      - 'Companion IC to any processor or MCU host'
      - 'Integrated 2.4GHz PA for a complete wireless solution with up to +20.5dBm output power'
      - 'Application throughput up to 50Mbps'
      - '40-pin, 5mm × 5mm quad flat no-leaded (QFN) package'
    """
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        s["cores"] = "Companion IC (no host CPU; pairs with MSPM0 / Sitara / Linux SoC)"

    if not s.get("wireless"):
        wireless_modes = []
        if re.search(r"Wi-?Fi[\s®]*\s*6\b|IEEE\s*802\.11\s*ax", text, re.IGNORECASE):
            wireless_modes.append("Wi-Fi 6 (802.11ax)")
        if re.search(r"Bluetooth[\s®]*\s*Low\s+Energy\s+5\.4|LE\s+5\.4", text, re.IGNORECASE):
            wireless_modes.append("BLE 5.4 (CC3301 only)")
        if wireless_modes:
            s["wireless"] = wireless_modes

    if not s.get("tx_power_dbm_max"):
        m = re.search(r"(?:up to|maximum)\s*\+?(\d+(?:\.\d+)?)\s*dBm", text, re.IGNORECASE)
        if m:
            s["tx_power_dbm_max"] = float(m.group(1))

    if not s.get("throughput_mbps_max"):
        m = re.search(r"[Aa]pplication\s+throughput\s+up\s+to\s+(\d+)\s*Mbps", text, re.IGNORECASE)
        if m:
            s["throughput_mbps_max"] = int(m.group(1))

    if not s.get("package"):
        if re.search(r"40-?pin.*QFN|40\s*pin.*quad\s*flat\s*no-?led", text, re.IGNORECASE):
            s["package"] = ["QFN40 (5x5 mm)"]

    if not s.get("host_interface"):
        if re.search(r"4-?bit\s+SDIO\s+or\s+SPI|SDIO\s+or\s+SPI", text, re.IGNORECASE):
            s["host_interface"] = "SDIO / SPI"

    if not s.get("security"):
        sec = []
        if re.search(r"WPA3", text):
            sec.append("WPA3")
        if re.search(r"WPA2", text):
            sec.append("WPA2")
        if re.search(r"[Ff]irmware\s+authentication", text):
            sec.append("Firmware authentication")
        if re.search(r"[Aa]nti-?rollback", text):
            sec.append("Anti-rollback")
        if sec:
            s["security"] = sec

    return extracted


def _extract_ti_cc13xx(extracted: dict, text: str) -> dict:
    """Texas Instruments SimpleLink CC13xx sub-GHz / multi-standard wireless
    MCU family (CC1310, CC1312, CC1350, CC1352). Page-1 Features style similar
    to CC26xx; key differences: sub-GHz band reference and TX power values
    rather than BLE sensitivity.

    Verified against CC1310 (SWRS181)."""
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        m = re.search(
            r"(?:ARM[\s®]*)?Cortex[\s®]*-?M(\d+)(?:F)?",
            text,
        )
        if m:
            s["cores"] = f"ARM Cortex-M{m.group(1)}"

    if not s.get("flash"):
        # CC1310: "Up to 128KB of flash" / "128KB In-System Programmable Flash"
        # CC1310 lists multiple flash sizes joined by commas with no spaces
        # (pdfplumber quirk on bullet lists); accept the max size.
        # Skip the fallback if the bare "(KB) Flash" form matches a small size
        # (e.g., "4 KB Flash" from cache descriptions).
        m = re.search(
            r"(?:Up to\s+)?(\d+)\s*KB\s+(?:of\s+)?(?:In-System\s+Programmable\s+)?[Ff]lash",
            text,
        )
        if m and int(m.group(1)) >= 32:
            s["flash"] = f"{m.group(1)} KB"
        else:
            # Fallback: CC1310 lists "32KB,64KB,and128KBofIn-SystemProgrammableFlash"
            # — grab all KB numbers preceding the first "Flash" mention and take the max.
            m = re.search(r"([\s\S]{0,200})[Ff]lash", text)
            if m:
                sizes = [int(x) for x in re.findall(r"(\d+)KB", m.group(1))]
                if sizes:
                    s["flash"] = f"{max(sizes)} KB"

    if not s.get("ram"):
        # CC1310: "Up to 20KB of ultra-low-leakage SRAM"
        m = re.search(
            r"(?:Up to\s+)?(\d+)\s*KB\s+of\s+(?:ultra-low-leakage\s+)?SRAM",
            text, re.IGNORECASE,
        )
        if m:
            s["ram"] = f"{m.group(1)} KB"

    if not s.get("supply_voltage_v"):
        m = re.search(
            r"(?:Wide\s+)?[Ss]upply\s+[Vv]oltage\s+[Rr]ange:?\s*([\d.]+)\s*to\s*([\d.]+)\s*V",
            text, re.IGNORECASE,
        )
        if m:
            s["supply_voltage_v"] = f"{m.group(1)}-{m.group(2)} V"

    # CC1310 references TX power "+14 dBm" or "+20 dBm" depending on band
    if not s.get("tx_power_dbm_max"):
        m = re.search(
            r"(?:\+|plus\s+)?(\d+)\s*dBm",
            text, re.IGNORECASE,
        )
        if m:
            s["tx_power_dbm_max"] = int(m.group(1))

    if not s.get("rx_sensitivity_dbm"):
        m = re.search(r"(-?\d+)\s*dBm.*?(?:Receiver\s+)?[Ss]ensitivity", text, re.IGNORECASE)
        if m:
            s["rx_sensitivity_dbm"] = int(m.group(1))

    return extracted


def _extract_ti_mspm0(extracted: dict, text: str) -> dict:
    """Texas Instruments MSPM0 Arm Cortex-M0+ MCU family.

    Verified against MSPM0G3507 datasheet (front-page features)."""
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        m = re.search(
            r"(?:ARM[\s®]*)?Cortex[\s®]*-?M0\+",
            text,
        )
        if m:
            s["cores"] = "ARM Cortex-M0+"

    if not s.get("clock_mhz_max"):
        m = re.search(
            r"(?:up to|@|operating\s+at)\s+(\d+)\s*-?MHz",
            text, re.IGNORECASE,
        )
        if m:
            s["clock_mhz_max"] = int(m.group(1))

    if not s.get("flash"):
        m = re.search(
            r"(\d+)\s*KB\s+(?:of\s+)?(?:flash|program\s+memory)",
            text, re.IGNORECASE,
        )
        if m:
            s["flash"] = f"{m.group(1)} KB"

    if not s.get("ram"):
        m = re.search(
            r"(\d+)\s*KB\s+(?:of\s+)?SRAM",
            text, re.IGNORECASE,
        )
        if m:
            s["ram"] = f"{m.group(1)} KB"

    return extracted


def _extract_nxp_kinetis(extracted: dict, text: str) -> dict:
    """NXP Kinetis K-series Cortex-M MCU (K66 etc).

    Verified against K66P144M180SF5V2 (Rev. 4, 04/2017) front-page bullets."""
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        m = re.search(
            r"ARM[\s®]*Cortex[\s®]*-?M(\d+)(?:F)?",
            text,
        )
        if m:
            s["cores"] = f"ARM Cortex-M{m.group(1)}"

    if not s.get("clock_mhz_max"):
        # K66: "Up to 180 MHz ARM Cortex-M4 based core"
        m = re.search(
            r"[Uu]p\s+to\s+(\d+)\s*MHz",
            text,
        )
        if m:
            s["clock_mhz_max"] = int(m.group(1))

    # K66: "memory options up to 2 MB total flash and 256 KB of SRAM"
    # Prefer the max-config value.
    if not s.get("flash"):
        m = re.search(
            r"(?:up to\s+)?(\d+(?:\.\d+)?)\s*MB\s+(?:total\s+|program\s+)?[Ff]lash",
            text,
        )
        if m:
            val = float(m.group(1))
            s["flash"] = f"{int(val*1024)} KB" if val < 10 else f"{val} MB"
        else:
            m = re.search(
                r"(?:Up to\s+)?(\d+)\s*KB\s+(?:of\s+)?(?:program\s+)?flash",
                text, re.IGNORECASE,
            )
            if m:
                s["flash"] = f"{m.group(1)} KB"

    if not s.get("ram"):
        m = re.search(
            r"(?:up to\s+)?(\d+)\s*KB\s+(?:of\s+)?(?:System\s+)?SRAM",
            text, re.IGNORECASE,
        )
        if m:
            s["ram"] = f"{m.group(1)} KB"

    return extracted


def _extract_nxp_imx_rt(extracted: dict, text: str) -> dict:
    """NXP i.MX RT crossover MCU series (Cortex-M7 / M7+M4).

    Style: "i.MX RT1060 series", "Up to 600 MHz", "1 MB SRAM" (typical).
    """
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        m = re.search(
            r"(?:ARM[\s®]*)?Cortex[\s®]*-?M(\d+)(?:F)?(?:\s*\+\s*Cortex[\s®]*-?M(\d+))?",
            text,
        )
        if m:
            cores = [f"Cortex-M{m.group(1)}"]
            if m.group(2):
                cores.append(f"Cortex-M{m.group(2)}")
            s["cores"] = "ARM " + " + ".join(cores)

    if not s.get("clock_mhz_max"):
        m = re.search(
            r"[Uu]p\s+to\s+(\d+(?:\.\d+)?)\s*(?:MHz|GHz)",
            text,
        )
        if m:
            val = float(m.group(1))
            s["clock_mhz_max"] = int(val) if val >= 100 else int(val * 1000)

    if not s.get("ram"):
        m = re.search(
            r"(?:Up to\s+)?(\d+(?:\.\d+)?)\s*(MB|KB)\s+(?:of\s+)?(?:on-?chip\s+)?SRAM",
            text, re.IGNORECASE,
        )
        if m:
            val = float(m.group(1))
            unit = m.group(2).upper()
            if unit == "MB":
                s["ram"] = f"{int(val*1024)} KB"
            else:
                s["ram"] = f"{int(val)} KB"

    return extracted


def _extract_nxp_kw(extracted: dict, text: str) -> dict:
    """NXP KW family automotive BLE MCU (KW45 / KW36 / KW47)."""
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        m = re.search(
            r"(?:ARM[\s®]*)?Cortex[\s®]*-?M(\d+)",
            text,
        )
        if m:
            s["cores"] = f"ARM Cortex-M{m.group(1)}"

    if not s.get("wireless"):
        m = re.search(
            r"Bluetooth[\s®]*LE?\s+(\d+\.\d+)",
            text, re.IGNORECASE,
        )
        if m:
            s["wireless"] = f"BLE {m.group(1)}"

    return extracted


def _extract_nxp_lpc(extracted: dict, text: str) -> dict:
    """NXP LPC55xx Cortex-M33 MCU family (LPC55S69 etc).

    Verified against LPC55S6x datasheet (Rev. 2.4, Dec 2022). Page-1 bullet
    style: "32-bit Arm Cortex-M33 ... 320 KB SRAM; 640 KB flash"."""
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        m = re.search(
            r"(?:32-bit\s+)?(?:Arm[\s®]*|ARM[\s®]*)?Cortex[\s®]*-?M(\d+)(?:F)?",
            text, re.IGNORECASE,
        )
        if m:
            s["cores"] = f"ARM Cortex-M{m.group(1)}"

    if not s.get("clock_mhz_max"):
        m = re.search(
            r"(?:up to|at a frequency of up to|Running at a frequency of up to)\s+(\d+)\s*MHz",
            text, re.IGNORECASE,
        )
        if m:
            s["clock_mhz_max"] = int(m.group(1))

    if not s.get("flash"):
        # LPC55S69 title: "640 KB flash" / "up to 640 KB on-chip flash"
        m = re.search(
            r"(?:up to\s+|Up to\s+)?(\d+)\s*KB\s+(?:on-chip\s+)?flash",
            text, re.IGNORECASE,
        )
        if m:
            s["flash"] = f"{m.group(1)} KB"

    if not s.get("ram"):
        # LPC55S69 title: "320 KB SRAM" / "up to 320 KB total SRAM"
        m = re.search(
            r"(?:up to\s+|Up to\s+|total\s+)?(\d+)\s*KB\s+(?:of\s+)?(?:on-chip\s+|total\s+)?SRAM",
            text, re.IGNORECASE,
        )
        if m:
            s["ram"] = f"{m.group(1)} KB"

    return extracted


def _extract_espressif_esp32_xtensa(extracted: dict, text: str) -> dict:
    """Espressif Systems ESP32 (original) Xtensa LX6 dual-core SoC.

    Verified against ESP32 Series Datasheet v5.2.
    Page-1 'Features' style:
      - 'Xtensa® single-/dual-core 32-bit LX6 microprocessor(s)'
      - 'CoreMark® score: 1 core at 240 MHz: 539.98 CoreMark'
      - '+9 dBm transmitting power'
      - '-94 dBm Bluetooth LE sensitivity'"""
    s = extracted.setdefault("specs", {})

    # --- Core ---
    if not s.get("cores"):
        m = re.search(
            r"Xtensa[\s®]*(?:single-)?/?(?:dual-)?core\s+32-bit\s+LX6\s+microprocessors?",
            text, re.IGNORECASE,
        )
        if m:
            # Default to dual-core if no explicit info
            if "single" in m.group(0).lower() and "dual" not in m.group(0).lower():
                s["cores"] = "Xtensa LX6 (single-core)"
            else:
                s["cores"] = "Xtensa LX6 (dual-core)"

    # --- BLE version (override generic pass which mis-matches 2.4 GHz Wi-Fi
    # band on page-2 block diagram to a Bluetooth version digit) ---
    # Two paths:
    #   1. Generic pass already wrote a (potentially wrong) value -> we
    #      REPLACE it only if our specific search yields a better match.
    #   2. Generic pass wrote nothing -> we try to find one.
    # We never hardcode. If we can't find a confident match, we leave the
    # value alone (or absent) so the human can verify against the datasheet.
    s_ble = s.get("ble_version")
    specific_ble = None
    # ESP32 datasheet uses 'Bluetooth v4.2 BR/EDR and Bluetooth LE' (with
    # the 'v' prefix). Match either 'Bluetooth X.Y' or 'Bluetooth vX.Y'.
    m = re.search(
        r"Bluetooth\s*(?:®)?\s*v?(\d+\.\d+)\s*BR/EDR(?:\s*(?:and|&)\s*BLE|\s*,)?",
        text, re.IGNORECASE,
    )
    if m:
        specific_ble = m.group(1)
    if specific_ble is None:
        # Fall back: 'Bluetooth ... X.Y ... LE-only' style
        m = re.search(
            r"Bluetooth\s*(?:®)?\s*v?(\d+\.\d+)(?:\s+(?:LE|LE-only))",
            text, re.IGNORECASE,
        )
        if m:
            specific_ble = m.group(1)
    if specific_ble is not None:
        s["ble_version"] = specific_ble
    # If specific_ble is None: do NOT set a hardcoded value. Leave whatever
    # the generic pass wrote (might be wrong) — the yaml `unverified` list
    # already flags everything, so a wrong ble_version will show up as
    # unverified when verified_by_human is false.

    # --- Clock / CoreMark ---
    if not s.get("clock_mhz_max"):
        # ESP32 datasheet: 'CoreMark score: 1 core at 240 MHz: 539.98'
        # or 'Xtensa LX6 ... up to 240 MHz' on features pages. Generic
        # r'(\d+)\s*MHz' is too greedy (hits Wi-Fi 20/40 MHz bandwidth).
        m = re.search(
            r"(?:CoreMark[\s®]*score[:\s]+.*?at|up\s+to|maximum\s+(?:CPU\s+)?clock\s+(?:of\s+)?|clock\s+speed[:\s]+up\s+to)\s*(\d+)\s*MHz",
            text, re.IGNORECASE,
        )
        if m:
            s["clock_mhz_max"] = int(m.group(1))

    if not s.get("coremark_score"):
        m = re.search(
            r"CoreMark[\s®]*\s*score[:\s]+([\d.]+)\s*CoreMark",
            text, re.IGNORECASE,
        )
        if m:
            s["coremark_score"] = float(m.group(1))

    # --- SRAM / Flash (typically stated in 'Features' as KB ranges) ---
    # ESP32 page 1 typically does not state max SRAM/Flash in cover bullets;
    # leave unverified unless a clear phrase is present.
    # (Page 4 "Memory" section has the details; this generic extractor
    # intentionally does not scan deep tables.)

    # --- Wireless ---
    if not s.get("wireless"):
        if "Wi-Fi" in text and "Bluetooth" in text:
            s["wireless"] = "Wi-Fi b/g/n + Bluetooth 4.2 BR/EDR + BLE"

    return extracted


def _extract_espressif_esp32s3_xtensa(extracted: dict, text: str) -> dict:
    """Espressif Systems ESP32-S3 Xtensa LX7 dual-core SoC.

    Verified against ESP32-S3 Series Datasheet v2.2.
    Page-1 bullet style:
      - '512 KB on-chip SRAM'
      - '384 KB ROM: for booting and core functions'
      - 'Xtensa® LX7' (dual-core)"""
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        if re.search(r"Xtensa[\s®]*LX7", text, re.IGNORECASE):
            s["cores"] = "Xtensa LX7 (dual-core)"

    # --- BLE version (override generic pass) ---
    # ESP32-S3 datasheet page 1: '2.4 GHz Wi-Fi ... and Bluetooth 5 (LE)'.
    # Generic r'Bluetooth[^.]*?\d+\.\d+' mis-matches 2.4 GHz Wi-Fi band.
    # Family-specific: 'Bluetooth 5 (LE)' is the canonical phrase.
    if not s.get("ble_version"):
        m = re.search(
            r"Bluetooth\s*(?:®)?\s*(\d+)(?:\s*\(LE\)|\s+LE(?:-only)?|\s*,\s*BLE|\s+and\s+later)",
            text, re.IGNORECASE,
        )
        if m:
            s["ble_version"] = m.group(1) + ".0"

    if not s.get("clock_mhz_max"):
        # ESP32-S3 datasheet: 'CPU clock speed: up to 240 MHz' or
        # 'CoreMark score: 1 core at 240 MHz: ...'. Avoid generic
        # r'(\d+)\s*MHz' which would also match '20 MHz' / '40 MHz'
        # Wi-Fi bandwidth mentions.
        m = re.search(
            r"(?:CoreMark[\s®]*score[:\s]+.*?at|clock\s+speed[:\s]+up\s+to|up\s+to)\s*(\d+)\s*MHz",
            text, re.IGNORECASE,
        )
        if m:
            s["clock_mhz_max"] = int(m.group(1))

    # ESP32-S3: '512 KB on-chip SRAM' / '384 KB ROM'
    if not s.get("ram"):
        m = re.search(r"(\d+)\s*KB\s+on-chip\s+SRAM", text, re.IGNORECASE)
        if m:
            s["ram"] = f"{m.group(1)} KB"

    if not s.get("rom"):
        m = re.search(r"(\d+)\s*KB\s+ROM", text, re.IGNORECASE)
        if m:
            s["rom"] = f"{m.group(1)} KB"

    if not s.get("wireless"):
        if "Wi-Fi" in text and "Bluetooth" in text:
            s["wireless"] = "Wi-Fi + BLE 5"

    return extracted


def _extract_espressif_esp32c3_riscv(extracted: dict, text: str) -> dict:
    """Espressif Systems ESP32-C3 single-core 32-bit RISC-V SoC.

    Verified against ESP32-C3 Datasheet.
    Page-1 'Features' style:
      - '32-bit RISC-V single-core processor'
      - '400 KB SRAM'
      - 'Wi-Fi + BLE 5'"""
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        if re.search(r"RISC[\s-]*V\s+single-core", text, re.IGNORECASE):
            s["cores"] = "RISC-V (single-core, 32-bit)"

    # --- BLE version (override generic pass) ---
    # ESP32-C3 datasheet page 1: '2.4 GHz Wi-Fi ... and Bluetooth 5 (LE)'.
    # Generic r'Bluetooth[^.]*?\d+\.\d+' mis-matches 2.4 GHz Wi-Fi band.
    # Family-specific: 'Bluetooth 5 (LE)' is the canonical phrase.
    if not s.get("ble_version"):
        m = re.search(
            r"Bluetooth\s*(?:®)?\s*(\d+)(?:\s*\(LE\)|\s+LE(?:-only)?|\s*,\s*BLE|\s+and\s+later)",
            text, re.IGNORECASE,
        )
        if m:
            s["ble_version"] = m.group(1) + ".0"

    if not s.get("clock_mhz_max"):
        # ESP32-C3 datasheet: 'Clock speed: up to 160 MHz' (page 3 CPU
        # and Memory section). Avoid generic r'(\d+)\s*MHz' which
        # would match '20 MHz' / '40 MHz' Wi-Fi bandwidth mentions.
        m = re.search(
            r"(?:CoreMark[\s®]*score[:\s]+.*?at|clock\s+speed[:\s]+up\s+to|up\s+to)\s*(\d+)\s*MHz",
            text, re.IGNORECASE,
        )
        if m:
            s["clock_mhz_max"] = int(m.group(1))

    if not s.get("ram"):
        m = re.search(r"(\d+)\s*KB\s+SRAM", text, re.IGNORECASE)
        if m:
            s["ram"] = f"{m.group(1)} KB"

    if not s.get("wireless"):
        wireless = []
        if re.search(r"Wi-?Fi\s*6|Wi-?Fi\s*\(?(?:802\.11)?ax|IEEE\s*802\.11\s*ax", text, re.IGNORECASE):
            wireless.append("Wi-Fi 6 (802.11ax)")
        elif re.search(r"\bWi-?Fi\b", text, re.IGNORECASE):
            wireless.append("Wi-Fi")
        if re.search(r"Bluetooth[\s®]*\s*5\s*\(LE\)|Bluetooth\s*5", text, re.IGNORECASE):
            wireless.append("Bluetooth 5 (LE)")
        elif re.search(r"Bluetooth[\s®]*\s*LE|Bluetooth[\s®]*\s*Low\s+Energy", text, re.IGNORECASE):
            wireless.append("Bluetooth LE")
        if re.search(r"IEEE\s*802\.15\.4|Zigbee|Thread", text, re.IGNORECASE):
            wireless.append("IEEE 802.15.4 (Zigbee / Thread)")
        if wireless:
            s["wireless"] = wireless

    return extracted


def _extract_wch_riscv(extracted: dict, text: str) -> dict:
    """WCH (Nanjing Qinheng / 沁恒) CH32V series RISC-V microcontrollers.

    Verified against CH32V003 (akizukidenshi mirror 2026-06),
    CH32V103 (platan.ru mirror 2026-06), CH32V303/305/307 (jc-net.co.jp
    mirror 2026-06). Page-1 'Features' bullet style:
      - 'QingKe 32-bit RISC-V2A core, RV32EC instruction set'
      - 'Support system main frequency 48MHz'
      - '2KB volatile data storage area SRAM' / '16KB program memory CodeFlash'
      - 'System power supply VDD: 3.3V or 5V'
      - 'Operating temperature range is -40°C~85°C industrial grade'
    """
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        # CH32V003: 'QingKe 32-bit RISC-V2A core, RV32EC'
        # CH32V103: '32-bit RISC processor RISC-V3A' (the 'QingKe' brand
        #   is omitted on this older datasheet; just 'RISC-V3A')
        # CH32V307: 'QingKe 32-bit RISC-V4F core with multiple instruction set combinations'
        m = re.search(
            r"(?:QingKe\s*)?(?:32-bit\s+)?(?:RISC\s+processor\s+)?RISC[\s-]*V\s*(\d+)([A-Z]*)",
            text, re.IGNORECASE,
        )
        if m:
            ver = m.group(1)
            suf = m.group(2) or ""
            brand = "QingKe " if re.search(r"QingKe", text, re.IGNORECASE) else ""
            extras = []
            if re.search(r"hardware\s+FPU|RISC[\s-]*V4F|\bFPU\b", text, re.IGNORECASE):
                if "F" not in suf:
                    extras.append("FPU")
            if re.search(r"branch\s+prediction", text, re.IGNORECASE):
                extras.append("branch prediction")
            if re.search(r"single[\s-]*cycle\s+multiplication", text, re.IGNORECASE) or \
               re.search(r"hardware\s+multiplication\s+and\s+division", text, re.IGNORECASE):
                extras.append("hardware mul/div")
            s["cores"] = f"{brand}RV{ver}{suf}" + (f" ({', '.join(extras)})" if extras else "")

    if not s.get("clock_mhz_max"):
        m = re.search(
            r"[Ss]ystem\s+main\s+frequency\s+(?:up\s+to\s+|of\s+)?(\d+)\s*MHz",
            text, re.IGNORECASE,
        )
        if m:
            s["clock_mhz_max"] = int(m.group(1))
        else:
            # Fallback: 'Up to 144MHz' / '144MHz zero wait'
            m = re.search(r"\bup\s+to\s+(\d+)\s*MHz|(\d+)\s*MHz\s+zero\s+wait|(\d+)\s*MHz\s+system", text, re.IGNORECASE)
            if m:
                s["clock_mhz_max"] = int(next(g for g in m.groups() if g))

    if not s.get("flash"):
        # CH32V003: '16KB program memory CodeFlash'
        # CH32V103: '20KB ... CodeFlash' (table) / 'CodeFlash' nearby
        # CH32V307: '480KB program memory CodeFlash'
        m = re.search(
            r"(\d+(?:\.\d+)?)\s*(KB|MB)\s+(?:program\s+memory\s+)?CodeFlash",
            text, re.IGNORECASE,
        )
        if m:
            val = m.group(1)
            unit = m.group(2)
            s["flash"] = f"{val} {unit}"

    if not s.get("ram"):
        # CH32V003: '2KB volatile data storage area SRAM'
        # CH32V103: '20KB volatile data storage area, SRAM' (no "area SRAM")
        # CH32V307: '128KB volatile data storage area SRAM'
        m = re.search(
            r"(\d+(?:\.\d+)?)\s*(KB|MB)\s+volatile\s+data\s+storage\s+area[,]?\s*SRAM",
            text, re.IGNORECASE,
        )
        if m:
            val = m.group(1)
            unit = m.group(2)
            s["ram"] = f"{val} {unit}"

    if not s.get("supply_voltage_v_min") or not s.get("supply_voltage_v_max"):
        # CH32V003: 'VDD: 3.3V or 5V' (single-supply)
        # CH32V103/CH32V307: 'VDD: 2.7V~5.5V' or 'VDD: 3.3V power supply' (single number)
        m = re.search(
            r"(?:System\s+power\s+supply\s+)?VDD[:\s]+([\d.]+)\s*V\s*[~–\u2013\u2014\-]+\s*([\d.]+)\s*V",
            text, re.IGNORECASE,
        )
        if m:
            s["supply_voltage_v_min"] = float(m.group(1))
            s["supply_voltage_v_max"] = float(m.group(2))
        else:
            m = re.search(
                r"(?:System\s+power\s+supply\s+)?VDD[:\s]+([\d.]+)\s*V(?:\s+or\s+([\d.]+)\s*V)?",
                text, re.IGNORECASE,
            )
            if m:
                s["supply_voltage_v_min"] = float(m.group(1))
                s["supply_voltage_v_max"] = float(m.group(2) or m.group(1))

    if not s.get("operating_temp_c_min") or not s.get("operating_temp_c_max"):
        # 'operating temperature range is -40°C~85°C' or '-40℃~85℃'
        m = re.search(
            r"[Oo]perating\s+temperature\s+range[^\d-]*(-?\d+)\s*[\u00b0\u2103~]+\s*(\d+)\s*[\u00b0\u2103]+C?",
            text, re.IGNORECASE,
        )
        if m:
            s["operating_temp_c_min"] = int(m.group(1))
            s["operating_temp_c_max"] = int(m.group(2))

    if not s.get("package"):
        packages = []
        if re.search(r"\bQFN[\s-]*\d+", text, re.IGNORECASE):
            for m in re.finditer(r"QFN[\s-]*(\d+)", text, re.IGNORECASE):
                packages.append(f"QFN{m.group(1)}")
        if re.search(r"\bLQFP[\s-]*\d+", text, re.IGNORECASE):
            for m in re.finditer(r"LQFP[\s-]*(\d+)", text, re.IGNORECASE):
                packages.append(f"LQFP{m.group(1)}")
        if re.search(r"\bTSSOP[\s-]*\d+", text, re.IGNORECASE):
            for m in re.finditer(r"TSSOP[\s-]*(\d+)", text, re.IGNORECASE):
                packages.append(f"TSSOP{m.group(1)}")
        if packages:
            # De-duplicate while preserving order
            seen = set()
            unique = []
            for p in packages:
                if p not in seen:
                    seen.add(p)
                    unique.append(p)
            s["package"] = unique

    if not s.get("wireless"):
        # CH32V series is MCU only (no integrated radio in current SKUs).
        # Set explicit "none" so future extractions don't leave the field
        # empty, mirroring the STM32G0 pattern.
        s["wireless"] = "none"

    if not s.get("peripherals"):
        # WCH CH32V307/CH32V303 has a rich peripherals list. Common ones:
        # '10/100 Ethernet MAC', 'USB 2.0 FS host/device', 'USB 2.0 HS PHY',
        # 'CAN 2.0B', 'SDIO', 'FSMC' (external memory bus), 'DVP' (camera),
        # 'I2S', 'OTG_FS'.
        peripherals = []
        if re.search(r"Ethernet\s+MAC|Gigabit\s+Ethernet\s+MAC|10/?100\s*Ethernet", text, re.IGNORECASE):
            peripherals.append("10/100 Ethernet MAC")
        if re.search(r"USB2\.0\s+full-?speed\s+host", text, re.IGNORECASE):
            peripherals.append("USB 2.0 FS host/device")
        elif re.search(r"USB2\.0\s+high-?speed\s+PHY|USB2\.0\s+HS", text, re.IGNORECASE):
            peripherals.append("USB 2.0 HS PHY")
        if re.search(r"\bCAN\s*2\.0B|1\s+CAN\s+interfaces", text, re.IGNORECASE):
            peripherals.append("CAN 2.0B")
        if re.search(r"\bSDIO\b", text, re.IGNORECASE):
            peripherals.append("SDIO")
        if re.search(r"\bFSMC\b|external\s+memory\s+interface", text, re.IGNORECASE):
            peripherals.append("FSMC")
        if re.search(r"\bDVP\b", text, re.IGNORECASE):
            peripherals.append("DVP (camera interface)")
        if re.search(r"\bI2S\b", text, re.IGNORECASE):
            peripherals.append("I2S")
        if peripherals:
            s["peripherals"] = peripherals

    return extracted


def _extract_gigadevice_riscv(extracted: dict, text: str) -> dict:
    """GigaDevice GD32VF103 RISC-V MCU.

    Verified against GD32VF103 Datasheet Rev 1.7 (gd32mcu.com official,
    87 pages, 2.4 MB). Page 7 'General description' style:
      - 'GD32VF103 device incorporates the RISC-V 32-bit processor
        core operating at 108 MHz'
      - Uses Nuclei N200 (Bumblebee core) — RV32IMAC instruction set
      - GD32VF103 family is pin-compatible with STM32F103 (Cortex-M3)
    """
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        # GigaDevice uses Nuclei N200 'Bumblebee' core. The GD32VF103
        # datasheet usually only writes 'RISC-V 32-bit processor core'
        # (it does NOT use the 'Bumblebee' brand name) — and sometimes
        # 'RV32IMAC' for the ISA. Match either form.
        isa = re.search(r"\bRV(\d+)([A-Z]+)\b", text, re.IGNORECASE)
        extras = []
        if re.search(r"hardware\s+multiplication|hardware\s+division", text, re.IGNORECASE):
            extras.append("hardware mul/div")
        if re.search(r"\bFPU\b|floating[\s-]*point\s+unit", text, re.IGNORECASE):
            extras.append("FPU")
        # Bumblebee brand only appears in the longer user manual, not
        # the datasheet. Leave the brand as plain 'RISC-V' unless
        # 'Nuclei' is mentioned.
        brand = "Nuclei " if re.search(r"Nuclei", text, re.IGNORECASE) else ""
        s["cores"] = f"{brand}RISC-V " + (f"RV{isa.group(1)}{isa.group(2)}" if isa else "32-bit") + (f" ({', '.join(extras)})" if extras else "")

    if not s.get("clock_mhz_max"):
        # 'operating at 108 MHz' / 'up to 108MHz'
        m = re.search(r"operating\s+at\s+(\d+)\s*MHz|up\s+to\s+(\d+)\s*MHz", text, re.IGNORECASE)
        if m:
            s["clock_mhz_max"] = int(next(g for g in m.groups() if g))

    if not s.get("flash"):
        # GD32VF103 family: flash varies by SKU (16-128 KB). Datasheet
        # has a Table 2-1 with the variants. The headline figure is
        # usually the max. Common phrasings:
        #   - 'up to 128 KB on-chip Flash memory'
        #   - 'Maximum 128 KB Flash'
        m = re.search(
            r"(?:up\s+to\s+|maximum\s+|Max\.?\s+)?(\d+(?:\.\d+)?)\s*(KB|MB)\s+(?:on[\s-]*chip\s+)?(?:of\s+)?[Ff]lash(?:\s+memory)?",
            text, re.IGNORECASE,
        )
        if m:
            val = m.group(1)
            unit = m.group(2)
            s["flash"] = f"up to {val} {unit}"

    if not s.get("ram"):
        # '32 KB SRAM' / 'up to 32 KB SRAM'
        m = re.search(
            r"(?:up\s+to\s+)?(\d+(?:\.\d+)?)\s*(KB|MB)\s+SRAM(?:\s+memory)?",
            text, re.IGNORECASE,
        )
        if m:
            val = m.group(1)
            unit = m.group(2)
            s["ram"] = f"{val} {unit}"

    if not s.get("supply_voltage_v_min") or not s.get("supply_voltage_v_max"):
        # GD32VF103: 2.6 V to 3.6 V (similar to STM32F103)
        m = re.search(
            r"(\d+(?:\.\d+)?)\s*V\s*(?:to|[-–\u2013\u2014])\s*(\d+(?:\.\d+)?)\s*V",
            text, re.IGNORECASE,
        )
        if m:
            vmin = float(m.group(1))
            vmax = float(m.group(2))
            if 1.5 <= vmin <= 3.5 and 2.5 <= vmax <= 4.0 and vmin < vmax:
                s["supply_voltage_v_min"] = vmin
                s["supply_voltage_v_max"] = vmax

    if not s.get("operating_temp_c_min") or not s.get("operating_temp_c_max"):
        # '–40 to +85 °C' — note the en-dash (U+2013) for the sign.
        # Previous pattern was too greedy and matched VDD voltage ranges.
        m = re.search(
            r"[\u2013\u2212-](\d+)\s*(?:\u00b0C|\u2103|degC|C)\s*(?:to|[-–\u2013])\s*\+?(\d+)\s*(?:\u00b0C|\u2103|degC|C)",
            text, re.IGNORECASE,
        )
        if m:
            s["operating_temp_c_min"] = -int(m.group(1))
            s["operating_temp_c_max"] = int(m.group(2))

    if not s.get("package"):
        packages = []
        if re.search(r"\bQFN\s*\d+|LQFP\s*\d+|TSSOP\s*\d+|LQFP48|LQFP64|LQFP100", text, re.IGNORECASE):
            for m in re.finditer(r"(QFN|LQFP|TSSOP)[\s-]*(\d+)", text, re.IGNORECASE):
                packages.append(f"{m.group(1)}{m.group(2)}")
        if packages:
            seen = set()
            unique = []
            for p in packages:
                if p not in seen:
                    seen.add(p)
                    unique.append(p)
            s["package"] = unique

    if not s.get("wireless"):
        # GD32VF103 is MCU only (no integrated radio; needs external
        # radio for wireless). Set explicit "none" to match the
        # CH32V pattern.
        s["wireless"] = "none"

    return extracted


def _extract_silergy_dcdc(extracted: dict, text: str) -> dict:
    """Silergy Corp (矽力杰) DC/DC converters and battery chargers.

    Verified against:
    * SY8089A1AAC (olimex mirror 2026-06): 2A sync buck
    * SY8120IABC (Azure Blob mirror 2026-06): 2A 18V sync buck
    * SY6970 (us1.silergy.com mirror 2026-06): 1S Li-ion linear charger
    (the Chinese datasheet for SY6970 is at a different URL; we use the
    English one to keep regex simple.)

    Page-1 'Features' style for sync buck:
      - '2.7-5.5V input voltage range'
      - '2A continuous, 3A peak load current capability'
      - '1MHz switching frequency minimizes the external components'
      - 'Compact package: SOT23-5'
      - 'Low RDS(ON) for internal switches (top/bottom): 110mΩ/80mΩ'
    """
    s = extracted.setdefault("specs", {})

    if not s.get("topology"):
        if re.search(r"synchronous\s+step[\s-]*down|synchronous\s+step[\s-]*down\s+regulator", text, re.IGNORECASE):
            s["topology"] = "Synchronous buck (integrated high-side + low-side FET)"
        elif re.search(r"step[\s-]*down\s+regulator|step[\s-]*down\s+DC/?DC", text, re.IGNORECASE):
            s["topology"] = "Step-down DC/DC"
        elif re.search(r"linear\s+(?:Li[\s-]*ion|battery)\s+charger", text, re.IGNORECASE):
            s["topology"] = "Linear Li-ion charger"
        elif re.search(r"1S\s+Li[\s-]*ion|1[\s-]*cell\s+Li[\s-]*ion", text, re.IGNORECASE):
            s["topology"] = "1S Li-ion linear charger"

    if not s.get("vin_v_min") or not s.get("vin_v_max"):
        m = re.search(
            r"(\d+(?:\.\d+)?)\s*V?\s*[-–to]+\s*(\d+(?:\.\d+)?)\s*V\s+[Ii]nput\s+[Vv]oltage\s+[Rr]ange",
            text,
        )
        if m:
            s["vin_v_min"] = float(m.group(1))
            s["vin_v_max"] = float(m.group(2))

    if not s.get("iout_a_max"):
        # '2A Output Current Capability' / '2A continuous, 3A peak'
        m = re.search(
            r"(?:up\s+to\s+)?(\d+(?:\.\d+)?)\s*A\s+(?:continuous|peak|output\s+current)",
            text, re.IGNORECASE,
        )
        if m:
            s["iout_a_max"] = float(m.group(1))

    if not s.get("switching_freq_mhz"):
        # '1MHz switching frequency' / '500kHz switching frequency'
        m = re.search(
            r"(\d+(?:\.\d+)?)\s*(MHz|kHz)\s+[Ss]witching\s+[Ff]requency",
            text, re.IGNORECASE,
        )
        if m:
            val = float(m.group(1))
            if m.group(2).lower() == "khz":
                val = val / 1000
            s["switching_freq_mhz"] = val

    if not s.get("rds_on_mohm"):
        # 'Low RDS(ON) for internal switches (top/bottom): 110mΩ/80mΩ'
        m = re.search(
            r"R\s*DS\(?ON\)?[^\d]*?(\d+)\s*m\s*[Ω\u03a9]\s*/\s*(\d+)\s*m\s*[Ω\u03a9]",
            text, re.IGNORECASE,
        )
        if m:
            s["rds_on_mohm"] = {"high_side": int(m.group(1)), "low_side": int(m.group(2))}

    if not s.get("package"):
        for pkg in ["SOT-23-6", "SOT-23-5", "SOT23-6", "SOT23-5", "SOT-23", "QFN", "DFN", "WLCSP", "MSOP-8", "MSOP-10", "TDFN"]:
            if re.search(re.escape(pkg), text, re.IGNORECASE):
                s["package"] = pkg
                break

    return extracted


def _extract_sgmicro_analog(extracted: dict, text: str) -> dict:
    """SG Micro (圣邦微) analog ICs — analog switches, audio amplifiers,
    op-amps, LDOs.

    Verified against:
    * SGM3157 (sg-micro.com 2026-06): 6Ω SPDT analog switch
    * SGM8903 (sg-micro.com 2026-06): capless 3Vrms line driver

    Page-1 'Features' style for SPDT switch:
      - 'Single Supply Voltage Range: 1.8V to 5.5V'
      - 'Low On-Resistance: 6Ω (TYP) at V+ = 4.5V'
      - 'tON: 20ns (TYP) / tOFF: 15ns (TYP)'
      - '-3dB Bandwidth: 300MHz'
      - 'Available in a Green SC70-6 Package'

    For line driver / amplifier:
      - 'Supply Voltage Range: 3V to 5.5V'
      - '3Vrms at 5V Supply Voltage' (output voltage)
      - 'SNR = 114dB (TYP)' / 'THD+N = 0.001% (f = 1kHz)'
      - 'Available in a Green TSSOP-14 Package'
    """
    s = extracted.setdefault("specs", {})

    if not s.get("supply_voltage_v_min") or not s.get("supply_voltage_v_max"):
        # '1.8V to 5.5V' / '3V to 5.5V' (supply range)
        m = re.search(
            r"(?:Single\s+)?[Ss]upply\s+[Vv]oltage\s+[Rr]ange:?\s+(\d+(?:\.\d+)?)\s*V?\s*(?:to|[-–])\s*(\d+(?:\.\d+)?)\s*V",
            text,
        )
        if m:
            s["supply_voltage_v_min"] = float(m.group(1))
            s["supply_voltage_v_max"] = float(m.group(2))

    if not s.get("ron_ohm_typ"):
        # 'Low On-Resistance: 6Ω (TYP)' for switches
        m = re.search(
            r"[Ll]ow\s+[Oo]n[\s-]*[Rr]esistance:?\s+(\d+(?:\.\d+)?)\s*[Ω\u03a9]\s*\(?TYP",
            text,
        )
        if m:
            s["ron_ohm_typ"] = float(m.group(1))

    if not s.get("bandwidth_mhz"):
        # '-3dB Bandwidth: 300MHz'
        m = re.search(r"-3\s*dB\s+[Bb]andwidth:?\s+(\d+)\s*MHz", text, re.IGNORECASE)
        if m:
            s["bandwidth_mhz"] = int(m.group(1))

    if not s.get("ton_ns") or not s.get("toff_ns"):
        # 'tON: 20ns (TYP) / tOFF: 15ns (TYP)' — handle space variations.
        m_on = re.search(r"\btON\s*[:\s]\s*(\d+)\s*ns", text, re.IGNORECASE)
        m_off = re.search(r"\btOFF\s*[:\s]\s*(\d+)\s*ns", text, re.IGNORECASE)
        if m_on:
            s["ton_ns"] = int(m_on.group(1))
        if m_off:
            s["toff_ns"] = int(m_off.group(1))

    if not s.get("operating_temp_c_min") or not s.get("operating_temp_c_max"):
        # '-40°C to +85°C Operating Temperature Range' / '-40℃ to +85℃'
        m = re.search(
            r"(-?\d+)\s*[\u00b0\u2103]?C?\s*(?:to|[-–])\s*\+?(\d+)\s*[\u00b0\u2103]?C?\s+[Oo]perating\s+[Tt]emperature",
            text,
        )
        if m:
            s["operating_temp_c_min"] = int(m.group(1))
            s["operating_temp_c_max"] = int(m.group(2))

    if not s.get("package"):
        for pkg in ["SC70-6", "SOT-23-6", "SOT-23-5", "MSOP-8", "MSOP-10", "TSSOP-14", "TSSOP-8", "SOIC-8", "QFN", "WLCSP"]:
            if re.search(re.escape(pkg), text, re.IGNORECASE):
                s["package"] = pkg
                break

    # Function/taxonomy tag — used by the catalog index to know what kind of
    # part this is (switch vs amplifier vs LDO). Two parallel fields:
    #   - function: human-readable description of the part's role
    #   - topology: short topology tag (used as the cross-part discriminator
    #     in the catalog and consistent with silergy_dcdc naming)
    if not s.get("function"):
        if re.search(r"\bSPDT\b|single[\s-]*pole[\s/]double[\s-]*throw", text, re.IGNORECASE):
            s["function"] = "Single-pole double-throw (SPDT) analog switch"
        elif re.search(r"[Ll]ine\s+[Dd]river|3\s*Vrms", text, re.IGNORECASE):
            s["function"] = "Capless line driver (3Vrms)"
        elif re.search(r"Class[\s-]*D", text, re.IGNORECASE):
            s["function"] = "Class-D amplifier"

    if not s.get("topology"):
        if re.search(r"\bSPDT\b|single[\s-]*pole[\s/]double[\s-]*throw", text, re.IGNORECASE):
            s["topology"] = "SPDT analog switch"
        elif re.search(r"[Cc]apless\s+[Ll]ine\s+[Dd]river|3\s*Vrms", text, re.IGNORECASE):
            s["topology"] = "Capless line driver"
        elif re.search(r"Class[\s-]*D\s+audio\s+amplifier|Class[\s-]*D\s+amplifier", text, re.IGNORECASE):
            s["topology"] = "Class-D amplifier"

    return extracted


def _extract_gigadevice_gd32(extracted: dict, text: str) -> dict:
    """GigaDevice GD32 series ARM Cortex-M MCU.

    Used for GD32F3 (Cortex-M4), GD32F4 (Cortex-M4 high-perf),
    GD32E2 (Cortex-M23 low-power). 'General description' section
    (around page 7-8 of the datasheet) consistently uses:

      - 'Arm® Cortex®-M{4,23} ... RISC core'
      - 'operating at {72,120,200} MHz frequency'
      - 'up to {N} KB on-chip Flash memory and {M} KB SRAM memory'
      - '2.6 to 3.6 V' supply

    Verified against GD32F303xx Rev1.9, GD32F450xx Rev2.1,
    GD32E230xx Rev1.4.
    """
    s = extracted.setdefault("specs", {})

    # --- Core ---
    if not s.get("cores"):
        m = re.search(
            r"Arm[\s®]+Cortex[\s®]*-?M(\d+)(F?)\s+32-bit\s+(?:RISC\s+)?(?:processor\s+)?core",
            text, re.IGNORECASE,
        )
        if m:
            label = f"ARM Cortex-M{m.group(1)}"
            if m.group(2):
                label += "F"
            s["cores"] = label

    # --- Clock ---
    if not s.get("clock_mhz_max"):
        # Both 'operating at 120 MHz' (GD32F3) and 'operating at up to 72 MHz' (GD32E2)
        m = re.search(
            r"operating\s+at(?:\s+up\s+to)?\s+(\d+)\s*MHz",
            text, re.IGNORECASE,
        )
        if m:
            s["clock_mhz_max"] = int(m.group(1))

    # --- Flash ---
    if not s.get("flash"):
        # Either 'up to 3072 KB on-chip Flash' (GD32F3) or 'up to 64 KB embedded Flash' (GD32E2)
        m = re.search(
            r"up\s+to\s+([\d,]+)\s*KB\s+(?:on-chip|embedded)\s+Flash",
            text, re.IGNORECASE,
        )
        if m:
            val = int(m.group(1).replace(",", ""))
            s["flash"] = f"{val} KB"

    # --- SRAM ---
    if not s.get("ram"):
        # Either 'and 96 KB SRAM' (GD32F3) or 'up to 8 KB SRAM' (GD32E2)
        m = re.search(
            r"(?:and|to)\s+(\d+)\s*KB\s+SRAM",
            text, re.IGNORECASE,
        )
        if m:
            s["ram"] = f"{m.group(1)} KB"

    # --- Supply voltage ---
    if not s.get("supply_voltage_v"):
        m = re.search(
            r"(\d+\.\d+)\s+to\s+(\d+\.\d+)\s*V",
            text,
        )
        if m:
            s["supply_voltage_v"] = f"{m.group(1)}-{m.group(2)} V"

    return extracted


# === ST family extractors ================================================

def _extract_stm32_wireless(extracted: dict, text: str) -> dict:
    """STMicroelectronics STM32WB / STM32WL series — dual-core
    wireless MCUs (Cortex-M4 application + Cortex-M0+ radio).

    Verified against:
    * STM32WB55xx DS13136 Rev 5 (Mouser mirror 2026-06)
    * STM32WL55xx DS13283 Rev 4 (Mouser mirror 2026-06)

    Cover page layout (Features list, p.1-2):
      - 'Arm® 32-bit Cortex®-M4 CPU with FPU, frequency up to 64 MHz'
      - 'Cortex® M0+ for real-time Radio layer' (WB) or 'Cortex-M0+
        core for radio' (WL)
      - 'Up to 1 MB flash memory'
      - 'Up to 256 KB SRAM' (WL: '256KB flash, 64KB SRAM')
      - 'Bluetooth® 5.x' / 'LoRa®' / IEEE 802.15.4
      - 'RX sensitivity: -96 dBm' (WB) or '-123 dBm for 2-FSK' (WL)
      - 'output power up to +6 dBm' (WB) or '+22 dBm' (WL)
      - '219 CoreMark' / 'Active-mode MCU: < 72 µA/MHz'
    """
    s = extracted.setdefault("specs", {})

    # --- Cores (M4 app + M0+ radio) ---
    if not s.get("cores"):
        m4_m = re.search(
            r"Arm[\s®]*32-bit\s+Cortex[\s®]*-?M4\s+CPU"
            r"(?:\s+with\s+FPU)?"
            r"[^\n]{0,80}?(?:frequency\s+up\s+to|up\s+to)\s*(\d+)\s*MHz",
            text, re.IGNORECASE | re.DOTALL,
        )
        m0_m = re.search(
            r"(?:Dedicated\s+)?Arm[\s®]*32-bit\s+Cortex[\s®]*-?M0\+",
            text, re.IGNORECASE,
        )
        if m4_m:
            desc = f"Arm Cortex-M4 @ up to {m4_m.group(1)} MHz"
            if m0_m:
                desc += " + Arm Cortex-M0+ (radio)"
            s["cores"] = [desc]

    # --- Flash / RAM ---
    if not s.get("flash"):
        m = re.search(r"(?:Up\s+to\s+)?(\d+(?:\.\d+)?)\s*(MB|KB)\s+flash(?:\s+memory)?", text, re.IGNORECASE)
        if m:
            s["flash"] = f"{m.group(1)} {m.group(2)}"

    if not s.get("ram"):
        m = re.search(r"(?:Up\s+to\s+)?(\d+(?:\.\d+)?)\s*(MB|KB)\s+SRAM", text, re.IGNORECASE)
        if m:
            s["ram"] = f"{m.group(1)} {m.group(2)}"

    # --- CoreMark / DMIPS ---
    if not s.get("coremark"):
        m = re.search(r"(\d+(?:\.\d+)?)\s*CoreMark", text, re.IGNORECASE)
        if m:
            s["coremark"] = float(m.group(1))

    # --- Wireless type ---
    if not s.get("wireless"):
        if "LoRa" in text:
            s["wireless"] = "LoRa / (G)FSK / (G)MSK / BPSK, sub-GHz 150-960 MHz"
        elif "Bluetooth" in text and "802.15.4" in text:
            s["wireless"] = "BLE 5.3 + 802.15.4 (Thread / Zigbee 3.0)"
        elif "Bluetooth" in text:
            s["wireless"] = "BLE"

    # --- Radio: TX power, RX sensitivity ---
    if not s.get("rx_sensitivity_dbm"):
        m = re.search(r"RX\s+sensitivity[:\s]+(-?\d+)\s*dBm", text, re.IGNORECASE)
        if m:
            s["rx_sensitivity_dbm"] = int(m.group(1))

    if not s.get("tx_power_dbm_max"):
        m = re.search(r"(?:output\s+power\s+)?up\s+to\s+(\+?\d+)\s*dBm", text, re.IGNORECASE)
        if m:
            s["tx_power_dbm_max"] = int(m.group(1).lstrip("+"))

    return extracted


def _extract_stm32_mpu(extracted: dict, text: str) -> dict:
    """STMicroelectronics STM32MP1 — heterogeneous A7+M4 MPU with
    GPU and TFT/DSI display support.

    Verified against:
    * STM32MP157A/D DS13029 Rev 4 (Mouser mirror 2026-06)

    Cover page layout (Features list, p.1-2):
      - 'Arm® 32-bit dual-core Cortex®-A7' @ up to 800 MHz
      - 'Cortex®-M4' co-processor @ up to 209 MHz
      - '256-Kbyte unified level 2 cache'
      - '3D GPU' / 'TFT/DSI'
      - 37 comm. interfaces, 29 timers
    """
    s = extracted.setdefault("specs", {})

    # --- Cores (dual A7 + M4) ---
    # STM32MP1 cover page (p.1) says 'Arm dual Cortex-A7 800 MHz' (no
    # '32-bit', no 'core'). Page 2 says '32-bit dual-core Arm Cortex-A7'
    # but the 800 MHz is 80+ chars away (separated by 'LFBGA448 ...' pkg
    # list). We accept both layouts: anchor on 'Cortex-A7' then look
    # forward for a MHz value within 100 chars.
    if not s.get("cores"):
        a7_anchor = re.search(
            r"Cortex[\s®]*-?A7",
            text, re.IGNORECASE,
        )
        a7_mhz = None
        if a7_anchor:
            after = text[a7_anchor.end():a7_anchor.end()+150]
            mhz = re.search(r"(\d+)\s*MHz", after)
            if mhz:
                a7_mhz = int(mhz.group(1))
        m4_m = re.search(
            r"Cortex[\s®]*-?M4(?:\s+\(co-?processor\))?[^\n]{0,80}?(?:up\s+to\s+)?(\d+)\s*MHz",
            text, re.IGNORECASE | re.DOTALL,
        )
        cores_list = []
        if a7_mhz:
            cores_list.append(f"Arm Cortex-A7 dual-core @ {a7_mhz} MHz")
        if m4_m:
            cores_list.append(f"Arm Cortex-M4 co-processor @ {m4_m.group(1)} MHz")
        if cores_list:
            s["cores"] = cores_list

    # --- L2 cache ---
    if not s.get("l2_cache_kb"):
        m = re.search(r"(\d+)\s*-?Kbyte\s+unified\s+level\s+2\s+cache", text, re.IGNORECASE)
        if m:
            s["l2_cache_kb"] = int(m.group(1))

    # --- Peripherals ---
    if not s.get("peripherals_count"):
        m = re.search(r"(\d+)\s+comm\.\s*interfaces[,\s]+(\d+)\s+timers", text, re.IGNORECASE)
        if m:
            s["peripherals_count"] = {
                "comm_interfaces": int(m.group(1)),
                "timers": int(m.group(2)),
            }

    # --- GPU / display ---
    if not s.get("gpu"):
        if "3D GPU" in text:
            s["gpu"] = "3D GPU (Vivante GC7000LiteXL)"
    if not s.get("display_interface"):
        if "TFT/DSI" in text or "DSI" in text:
            s["display_interface"] = "TFT/DSI"

    return extracted


def _extract_efr32_ble(extracted: dict, text: str) -> dict:
    """Silicon Labs EFR32BG Series 2 Bluetooth Low Energy SoC family
    (BG22, BG24). Page-1 Key Features style similar to ST/Nordic
    datasheets.

    Verified against:
    * EFR32BG22 datasheet V.01/24 (alcom.be mirror 2026-06)
    * EFR32BG24 datasheet 04/2022 (alcom.be mirror 2026-06)

    Cover page layout (Key Features bullets, p.1):
      - '32-bit ARM Cortex-M33 core with X MHz maximum operating frequency'
        (76.8 MHz for BG22, 78.0 MHz for BG24)
      - 'Up to 512 kB of flash and 32 kB of RAM' (BG22)
        'Up to 1536 kB flash and 256 kB RAM' (BG24)
      - 'Bluetooth 5.2 Direction Finding' or 'Bluetooth 5.x'
      - 'Integrated PA with up to 6 dBm (BG22) or 19.9 dBm (BG24) TX power'
      - 'Secure Boot with Root of Trust and Secure Loader (RTSL)'
      - 'Energy-efficient radio core with low active and sleep currents'
    """
    s = extracted.setdefault("specs", {})

    # --- Core / Clock ---
    if not s.get("cores"):
        # Allow newlines between MHz digits and the "MHz" word (pdfplumber
        # quirk on datasheets where bullet lists wrap mid-number).
        # Also accept "32-bit ARM Cortex" / "32-bit ARM® Cortex" lead-ins.
        m = re.search(
            r"(?:Arm[\s®]*\d+-bit\s+)?(?:Arm[\s®]*)?Cortex[\s®]*-?M33"
            r"(?:\s+core)?[\s\S]{0,200}?(\d+(?:\.\d+)?)\s*MHz",
            text, re.IGNORECASE,
        )
        if m:
            s["cores"] = [f"Arm Cortex-M33 @ {m.group(1)} MHz (TrustZone, FPU, DSP)"]
        else:
            m = re.search(r"Cortex[\s®]*-?M33", text, re.IGNORECASE)
            if m:
                s["cores"] = ["Arm Cortex-M33 (TrustZone, FPU, DSP)"]

    # --- Flash / RAM ---
    if not s.get("flash"):
        m = re.search(r"(?:Up\s+to\s+)?(\d+(?:,\d+)?)\s*kB\s+of\s+flash", text, re.IGNORECASE)
        if m:
            s["flash"] = f"up to {m.group(1)} kB"

    if not s.get("ram"):
        m = re.search(r"(\d+)\s*kB\s+of\s+RAM", text, re.IGNORECASE)
        if m:
            s["ram"] = f"{m.group(1)} kB"

    # --- Wireless / BLE ---
    if not s.get("wireless"):
        if "Bluetooth 5.2" in text and "Direction Finding" in text:
            s["wireless"] = "BLE 5.2 + Bluetooth Mesh + Direction Finding (AoA/AoD)"
        elif "Bluetooth 5" in text:
            s["wireless"] = "BLE 5.x"

    # --- TX power ---
    # Avoid matching RX sensitivity values (e.g. "-96.2 dBm sensitivity")
    # by requiring "up to <n> dBm" or "TX power" within ~30 chars after the dBm number.
    if not s.get("tx_power_dbm_max"):
        m = re.search(
            r"(?:up\s+to\s+)?(\+?\d+(?:\.\d+)?)\s*dBm[\s\S]{0,30}?(?:TX\s+power|transmit\s+power|output\s+power)",
            text, re.IGNORECASE,
        )
        if m:
            s["tx_power_dbm_max"] = float(m.group(1).lstrip("+"))

    # --- Security ---
    if not s.get("security"):
        sec = []
        if re.search(r"Secure\s+Boot", text, re.IGNORECASE):
            sec.append("Secure Boot with RTSL")
        if "Secure Vault" in text:
            sec.append("Secure Vault")
        if "True Random" in text or re.search(r"\bTRNG\b", text):
            sec.append("TRNG")
        if "AES" in text:
            sec.append("AES")
        if sec:
            s["security"] = sec

    # --- Voltage range ---
    if not s.get("voltage_v_min") or not s.get("voltage_v_max"):
        m = re.search(r"(\d+(?:\.\d+)?)\s*to\s+(\d+(?:\.\d+)?)\s*V", text, re.IGNORECASE)
        if m:
            s["voltage_v_min"] = float(m.group(1))
            s["voltage_v_max"] = float(m.group(2))

    return extracted


def _extract_efr32_mp(extracted: dict, text: str) -> dict:
    """Silicon Labs EFR32MG Series 2 Multiprotocol Wireless SoC family
    (MG21, MG24). Same Key Features style as BG family but supports
    Zigbee / Thread / Matter / Bluetooth Mesh in addition to BLE.

    Verified against:
    * EFR32MG21 datasheet Rev 1.1 (alcom.be mirror 2026-06)
    * EFR32MG24 datasheet V9/24 (alcom.be mirror 2026-06)
    """
    s = extracted.setdefault("specs", {})

    # --- Core / Clock ---
    if not s.get("cores"):
        m = re.search(
            r"(?:Arm[\s®]*\d+-bit\s+)?(?:Arm[\s®]*)?Cortex[\s®]*-?M33"
            r"(?:\s+core)?[\s\S]{0,200}?(\d+(?:\.\d+)?)\s*MHz",
            text, re.IGNORECASE,
        )
        if m:
            s["cores"] = [f"Arm Cortex-M33 @ {m.group(1)} MHz (TrustZone, FPU, DSP)"]
        else:
            m = re.search(r"Cortex[\s®]*-?M33", text, re.IGNORECASE)
            if m:
                s["cores"] = ["Arm Cortex-M33 (TrustZone, FPU, DSP)"]

    # --- Flash / RAM ---
    if not s.get("flash"):
        m = re.search(r"(?:up\s+to\s+)?(\d+(?:,\d+)?)\s*kB\s+(?:of\s+)?[Ff]lash(?:\s+memory)?", text, re.IGNORECASE)
        if m:
            s["flash"] = f"up to {m.group(1)} kB"

    if not s.get("ram"):
        m = re.search(r"(\d+)\s*kB\s+(?:of\s+)?RAM", text, re.IGNORECASE)
        if m:
            s["ram"] = f"{m.group(1)} kB"

    # --- Wireless: multiprotocol ---
    if not s.get("wireless"):
        protos = []
        if "Zigbee" in text: protos.append("Zigbee")
        if "Thread" in text: protos.append("Thread")
        if "Matter" in text: protos.append("Matter")
        if "Bluetooth Mesh" in text or re.search(r"\bMesh\b", text): protos.append("Bluetooth Mesh")
        if "Bluetooth" in text and "BLE" not in protos: protos.append("BLE")
        if "802.15.4" in text and "IEEE 802.15.4" not in protos: protos.append("IEEE 802.15.4")
        if protos:
            s["wireless"] = " / ".join(protos)

    # --- TX power ---
    # Avoid matching RX sensitivity values by requiring "TX power" / "transmit power" /
    # "output power" within ~30 chars after the dBm number.
    if not s.get("tx_power_dbm_max"):
        m = re.search(
            r"(?:up\s+to\s+)?\+?(\d+(?:\.\d+)?)\s*dBm[\s\S]{0,30}?(?:TX\s+power|transmit\s+power|output\s+power)",
            text, re.IGNORECASE,
        )
        if m:
            s["tx_power_dbm_max"] = float(m.group(1).lstrip("+"))

    # --- AI/ML MVP (MG24 differentiator) ---
    if not s.get("ai_ml_accelerator"):
        if re.search(r"\bMVP\b|Matrix\s+Vector\s+Processor|AI/ML", text, re.IGNORECASE):
            s["ai_ml_accelerator"] = "MVP (Matrix Vector Processor)"

    # --- Security ---
    if not s.get("security"):
        sec = []
        if re.search(r"Secure\s+Boot", text, re.IGNORECASE):
            sec.append("Secure Boot with RTSL")
        if "Secure Vault" in text:
            sec.append("Secure Vault")
        if "True Random" in text or re.search(r"\bTRNG\b", text):
            sec.append("TRNG")
        if sec:
            s["security"] = sec

    return extracted


def _extract_stm32_hp(extracted: dict, text: str) -> dict:
    """STMicroelectronics STM32H7 series — high-performance Cortex-M7 MCUs.

    Verified against:
    * STM32H743xI DS12110 Rev 5 (SparkFun CDN mirror 2026-06)
    * STM32H743VIT6 DS12110 Rev 2 (Octopart mirror 2026-06)

    Cover page layout (Features list, p.1-2):
      - '32-bit Arm Cortex-M7' @ up to 480 MHz (H743/H750) or 280 MHz (H742)
      - 'Up to 2 MB flash', 'Up to 1 MB SRAM'
      - 'L1 cache: 16 KB I-cache + 16 KB D-cache'
      - 'Chrom-ART Accelerator', 'JPEG Codec'
      - '1284 CoreMark' (H743 @ 480 MHz)
    """
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        m = re.search(
            r"(?:32-bit\s+)?Arm[\s®]*(?:32-bit\s+)?Cortex[\s®]*-?M7"
            r"(?:\s+core)?[^\n]{0,200}?(?:up\s+to|at)?\s*(\d+)\s*MHz",
            text, re.IGNORECASE | re.DOTALL,
        )
        if m:
            s["cores"] = [f"Arm Cortex-M7 @ up to {m.group(1)} MHz"]
        else:
            m = re.search(r"Arm[\s®]*(?:32-bit\s+)?Cortex[\s®]*-?M7", text, re.IGNORECASE)
            if m:
                s["cores"] = ["Arm Cortex-M7 (single-core)"]

    if not s.get("flash"):
        m = re.search(r"(?:Up\s+to\s+)?(\d+(?:\.\d+)?)\s*(MB|KB)\s+(?:of\s+)?flash(?:\s+memory)?", text, re.IGNORECASE)
        if m:
            s["flash"] = f"{m.group(1)} {m.group(2)}"

    if not s.get("ram"):
        # Accept both "SRAM" (typical) and "RAM" (H7 uses "1 Mbyte of RAM").
        m = re.search(r"(?:Up\s+to\s+)?(\d+(?:\.\d+)?)\s*(MB|KB)\s+(?:of\s+)?(?:S)?RAM", text, re.IGNORECASE)
        if m:
            s["ram"] = f"{m.group(1)} {m.group(2)}"

    if not s.get("coremark"):
        m = re.search(r"(\d+(?:\.\d+)?)\s*CoreMark", text, re.IGNORECASE)
        if m:
            s["coremark"] = float(m.group(1))

    if not s.get("voltage_v_min") or not s.get("voltage_v_max"):
        m = re.search(r"(\d+(?:\.\d+)?)\s*V\s+to\s+(\d+(?:\.\d+)?)\s*V\s+(?:power\s+supply|operating\s+supply|application\s+supply)", text, re.IGNORECASE)
        if m:
            s["voltage_v_min"] = float(m.group(1))
            s["voltage_v_max"] = float(m.group(2))

    if not s.get("accelerators"):
        accelerators = []
        if "Chrom-ART" in text:
            accelerators.append("Chrom-ART Accelerator (DMA2D)")
        if "JPEG" in text and ("codec" in text.lower() or "JPEG Codec" in text):
            accelerators.append("JPEG Codec")
        if "MIPI-DSI" in text or "MIPI DSI" in text:
            accelerators.append("MIPI-DSI host")
        if accelerators:
            s["accelerators"] = accelerators

    return extracted


def _extract_stm32_ulp(extracted: dict, text: str) -> dict:
    """STMicroelectronics STM32U5 series — ultra-low-power Cortex-M33 MCUs.

    Verified against:
    * STM32U575xx DS13737 Rev 9 (Akizukidenshi mirror 2026-06)
    * STM32U585xx DS13086 Rev 10 (Reichelt CDN mirror 2026-06)

    Cover page layout (Features list, p.1-2):
      - 'Ultra-low-power Arm Cortex-M33 ... 240 DMIPS' @ up to 160 MHz
      - 'Up to 2 MB flash', '786 KB SRAM'
      - 'TrustZone, FPU, MPU, DSP'
      - '651 CoreMark', '450 ULPMark-CP'
      - '1.71 V to 3.6 V power supply'
      - '19.5 µA/MHz Run mode', '160 nA Shutdown'
      - 'CORDIC' / 'FMAC' coprocessors
      - For U585: 'AES, PKA, OTFDEC' crypto accelerators
    """
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        # Allow arbitrary text between M33 mention and the MHz figure,
        # since STM32 datasheets put "up to 160 MHz" in a Features bullet
        # separate from the headline Cortex-M33 line.
        m = re.search(
            r"Arm[\s®]*32-bit\s+Cortex[\s®]*-?M33"
            r"(?:[\s\S]{0,400}?)(?:up\s+to|at)\s*(\d+)\s*MHz",
            text, re.IGNORECASE,
        )
        if m:
            desc = f"Arm Cortex-M33 @ up to {m.group(1)} MHz (TrustZone, FPU, MPU, DSP)"
            s["cores"] = [desc]
        else:
            m = re.search(r"Arm[\s®]*32-bit\s+Cortex[\s®]*-?M33", text, re.IGNORECASE)
            if m:
                s["cores"] = ["Arm Cortex-M33 (TrustZone, FPU, MPU, DSP)"]

    if not s.get("dmips"):
        m = re.search(r"(\d+)\s*DMIPS", text, re.IGNORECASE)
        if m:
            s["dmips"] = int(m.group(1))

    if not s.get("flash"):
        m = re.search(r"(?:up\s+to\s+)?(\d+(?:\.\d+)?)\s*(MB|KB)\s+flash(?:\s+memory)?", text, re.IGNORECASE)
        if m:
            s["flash"] = f"up to {m.group(1)} {m.group(2)}"

    if not s.get("ram"):
        # Prefer the headline figure (e.g., "786 KB SRAM") over
        # mode-specific figures (e.g., "16-Kbyte SRAM" in Stop modes).
        m = re.search(r"(?:up\s+to\s+)?(\d+(?:\.\d+)?)\s*KB\s+SRAM(?!\s+with)", text, re.IGNORECASE)
        if m:
            s["ram"] = f"{m.group(1)} KB"

    if not s.get("coremark"):
        m = re.search(r"(\d+(?:\.\d+)?)\s*CoreMark", text, re.IGNORECASE)
        if m:
            s["coremark"] = float(m.group(1))

    if not s.get("ulpmark_cp"):
        m = re.search(r"(\d+)\s*ULPMark[\u2122\s-]*CP", text, re.IGNORECASE)
        if m:
            s["ulpmark_cp"] = int(m.group(1))
    if not s.get("ulpmark_pp"):
        m = re.search(r"(\d+(?:\.\d+)?)\s*ULPMark[\u2122\s-]*PP", text, re.IGNORECASE)
        if m:
            s["ulpmark_pp"] = float(m.group(1))

    if not s.get("voltage_v_min") or not s.get("voltage_v_max"):
        m = re.search(r"(\d+(?:\.\d+)?)\s*V\s+to\s+(\d+(?:\.\d+)?)\s*V\s+(?:power\s+supply|operating\s+supply)", text, re.IGNORECASE)
        if m:
            s["voltage_v_min"] = float(m.group(1))
            s["voltage_v_max"] = float(m.group(2))

    if not s.get("shutdown_current_na"):
        m = re.search(r"(\d+)\s*nA\s+Shutdown", text, re.IGNORECASE)
        if m:
            s["shutdown_current_na"] = int(m.group(1))
    if not s.get("run_current_ua_per_mhz"):
        m = re.search(r"(\d+(?:\.\d+)?)\s*[u\u00b5A/MHz\s]*Run\s+mode", text, re.IGNORECASE)
        if m:
            s["run_current_ua_per_mhz"] = float(m.group(1))

    if not s.get("crypto_accelerators"):
        crypto = []
        if re.search(r"\bAES\b", text):
            crypto.append("AES")
        if re.search(r"\bPKA\b", text):
            crypto.append("PKA")
        if re.search(r"\bOTFDEC\b|\bSAES\b", text):
            crypto.append("OTFDEC/SAES")
        if re.search(r"\bHASH\b", text):
            crypto.append("HASH")
        if crypto:
            s["crypto_accelerators"] = crypto

    if not s.get("math_coprocessors"):
        coproc = []
        if "CORDIC" in text:
            coproc.append("CORDIC")
        if re.search(r"\bFMAC\b", text):
            coproc.append("FMAC")
        if coproc:
            s["math_coprocessors"] = coproc

    return extracted


def _extract_stm32_g0(extracted: dict, text: str) -> dict:
    """STMicroelectronics STM32G0 series — entry-level Cortex-M0+ MCUs.

    Verified against:
    * STM32G070CB/KB/RB DS13106 (Mouser mirror 2026-06)

    Cover page layout (Features list, p.1-2):
      - 'Arm Cortex-M0+ ... up to 64 MHz' (no DMIPS/CoreMark for M0+)
      - '128 Kbytes of Flash memory' / '36 Kbytes of SRAM'
      - '2.0 V to 3.6 V' (note: G0 is 2.0-3.6V, NOT 1.71-3.6V like U5)
      - No crypto / no FPU / no accelerators

    G0 family characteristics (informational, NOT extracted):
      - STM32G030/G031: 16-64 KB flash, value line
      - STM32G050/G051: with FDCAN
      - STM32G070/G071: 64-128 KB flash, mainstream
      - STM32G0B0/G0B1: 256-512 KB flash, premium
      - All variants are Cortex-M0+ @ up to 64 MHz
    """
    s = extracted.setdefault("specs", {})

    if not s.get("cores"):
        # G0 datasheets lead with "Arm Cortex-M0+ ... frequency up to 64 MHz".
        # Some also add a bullet "frequency up to 64 MHz" on the cover.
        m = re.search(
            r"Arm[\s®]*32-bit\s+Cortex[\s®]*-?M0\+"
            r"(?:[\s\S]{0,200}?)(?:frequency\s+up\s+to|up\s+to)\s*(\d+)\s*MHz",
            text, re.IGNORECASE,
        )
        if m:
            s["cores"] = [f"Arm Cortex-M0+ @ up to {m.group(1)} MHz"]
        else:
            m = re.search(r"Arm[\s®]*32-bit\s+Cortex[\s®]*-?M0\+", text, re.IGNORECASE)
            if m:
                s["cores"] = ["Arm Cortex-M0+"]

    if not s.get("flash"):
        # G0 datasheets use "Kbytes of Flash memory" (note plural Kbytes + 'Flash memory').
        m = re.search(
            r"(?:Up\s+to\s+)?(\d+(?:\.\d+)?)\s*(KB|Kbytes|Kbytes of|MB|Mbytes)\b"
            r"(?:\s+of)?\s*[Ff]lash(?:\s+memory)?",
            text, re.IGNORECASE,
        )
        if m:
            val = m.group(1)
            unit = m.group(2).lower()
            if unit.startswith("kbyte") or unit == "kb":
                unit = "KB"
            elif unit.startswith("mbyte") or unit == "mb":
                unit = "MB"
            s["flash"] = f"{val} {unit}"

    if not s.get("ram"):
        # G0 datasheets use "Kbytes of SRAM" or "Kbytes of RAM".
        m = re.search(
            r"(?:Up\s+to\s+)?(\d+(?:\.\d+)?)\s*(KB|Kbytes|Kbytes of|MB|Mbytes)\b"
            r"(?:\s+of)?\s*(?:S)?RAM",
            text, re.IGNORECASE,
        )
        if m:
            val = m.group(1)
            unit = m.group(2).lower()
            if unit.startswith("kbyte") or unit == "kb":
                unit = "KB"
            elif unit.startswith("mbyte") or unit == "mb":
                unit = "MB"
            s["ram"] = f"{val} {unit}"

    if not s.get("voltage_v_min") or not s.get("voltage_v_max"):
        # G0: 2.0 V to 3.6 V operating range (NOT 1.71 like U5).
        m = re.search(
            r"(\d+(?:\.\d+)?)\s*V\s+to\s+(\d+(?:\.\d+)?)\s*V",
            text, re.IGNORECASE,
        )
        if m:
            vmin = float(m.group(1))
            vmax = float(m.group(2))
            # Sanity: G0 voltage range is 1.7-3.6V or 2.0-3.6V depending on variant.
            # Reject clearly wrong ranges that come from unrelated V-bat / V-ref mentions.
            if 1.5 <= vmin <= 3.5 and 2.5 <= vmax <= 4.0 and vmin < vmax:
                s["voltage_v_min"] = vmin
                s["voltage_v_max"] = vmax

    if not s.get("wireless"):
        # G0 has NO wireless. Set explicit "none" so future extractions don't
        # accidentally leave the field empty.
        s["wireless"] = "none"

    return extracted


# === Family-extractor registry ===========================================
# Maps the `family` string used in PARTS to the per-family extractor function.
# Nordic / NXP / TI / Espressif / GigaDevice extractors are now implemented;
# ST is still TODO (see module docstring).
FAMILY_EXTRACTORS: dict[str, callable] = {
    # Renesas
    "da_ble":     _extract_da_ble,
    "ra":         _extract_ra,
    "rl78":       _extract_rl78,
    "rx":         _extract_rx,
    "isl_power":  _extract_isl_power,
    "sensor":     _extract_sensor,
    "nfc":        _extract_nfc,
    # Nordic
    "nrf":        _extract_nrf,
    # NXP
    "kinetis":    _extract_nxp_kinetis,
    "imx_rt":     _extract_nxp_imx_rt,
    "kw":         _extract_nxp_kw,
    "lpc":        _extract_nxp_lpc,
    # TI
    "cc26xx":     _extract_ti_cc26xx,
    "cc13xx":     _extract_ti_cc13xx,
    "mspm0":      _extract_ti_mspm0,
    # Espressif
    "esp32_xtensa":     _extract_espressif_esp32_xtensa,
    "esp32s3_xtensa":   _extract_espressif_esp32s3_xtensa,
    "esp32c3_riscv":    _extract_espressif_esp32c3_riscv,
    # GigaDevice
    "gd32f3_cortex_m4": _extract_gigadevice_gd32,
    "gd32f4_cortex_m4": _extract_gigadevice_gd32,
    "gd32e2_cortex_m23": _extract_gigadevice_gd32,
    "gd32vf103_riscv":  _extract_gigadevice_riscv,
    # Chinese domestic vendors
    "wch_riscv":       _extract_wch_riscv,
    "silergy_dcdc":    _extract_silergy_dcdc,
    "sgmicro_analog":  _extract_sgmicro_analog,
    # ST (Mouser mirrors; see .link_verification_report.md Round 3)
    "stm32_wireless": _extract_stm32_wireless,
    "stm32_mpu":      _extract_stm32_mpu,
    "stm32_hp":       _extract_stm32_hp,
    "stm32_ulp":      _extract_stm32_ulp,
    "stm32_g0":       _extract_stm32_g0,
    # Companion ICs (no host CPU; pair with external MCU over SPI/SDIO)
    "nrf_companion":  _extract_nrf_companion,
    "cc33xx":         _extract_ti_cc33xx,
    # Silicon Labs (alcom mirror; see product_families.md)
    "efr32_ble":      _extract_efr32_ble,
    "efr32_mp":       _extract_efr32_mp,
}

# === Generic extraction (no family-specific knowledge) ==================

def extract_specs_from_pdf(pdf_path: Path, family: Optional[str] = None) -> dict:
    """Generic pdfplumber pass: revision, RAM, Flash, BLE, voltage, package.
    Family-specific deep extraction is layered on top via `family` (looked up
    in FAMILY_EXTRACTORS, populated from the `family` key in PARTS).
    """
    try:
        import pdfplumber
    except ImportError:
        print("  [error] pdfplumber not installed; run: pip install pdfplumber")
        return {}

    extracted = {
        "extracted_from_pages": [],
        "extraction_method": "pdfplumber Key Features / General Description",
        "specs": {},
    }

    with pdfplumber.open(pdf_path) as pdf:
        for pn in [1, 2]:
            if pn > len(pdf.pages):
                break
            text = pdf.pages[pn-1].extract_text() or ""
            extracted["extracted_from_pages"].append(pn)

            # Revision
            rev_m = re.search(r"(R\w+).*?(?:[Rr]evision|[Rr]ev\.?)\s*(\d+(?:\.\d+)+)", text)
            if rev_m and not extracted.get("datasheet_doc_id"):
                extracted["datasheet_doc_id"] = rev_m.group(1)
                extracted["datasheet_revision_partial"] = f"{rev_m.group(2)} (page {pn} rev-line)"

            # BLE version
            # Anchor on 'Bluetooth 5.x' / 'Bluetooth 5 (LE)' / 'BLE 5.x' style.
            # Bare 'Bluetooth[^.]*?\d+\.\d+' is too greedy and matches
            # '...Bluetooth ... 2.4 GHz' (Wi-Fi band) or '...Bluetooth ... 1.8 V'
            # (supply voltage) on the same page. The version number must be
            # immediately adjacent to 'Bluetooth'/'BLE' (within 2 words), and
            # the word immediately after the number should be a version
            # separator (LE/LE-only/only/-/end-of-sentence) — not a unit
            # (GHz / MHz / V / mA).
            ble_m = re.search(
                r"(?:Bluetooth\s*(?:®)?\s*|BLE\s+)"
                r"(\d+\.\d+(?:\.[xX])?)"
                r"(?:\s*(?:LE|LE-only|only|and\s+later|®|\(LE\))|\b)",
                text,
            )
            if ble_m and not extracted["specs"].get("ble_version"):
                extracted["specs"]["ble_version"] = ble_m.group(1)

            # RAM
            ram_m = re.search(r"(\d+\s*kB)\s+(?:of\s+)?(?:Retainable\s+)?(?:System\s+)?RAM", text, re.IGNORECASE)
            if ram_m and not extracted["specs"].get("ram"):
                extracted["specs"]["ram"] = ram_m.group(1)

            # Flash / OTP
            flash_m = re.search(r"(\d+\s*kB)\s+(?:embedded\s+)?(?:One-Time-Programmable\s*)?(?:Flash|OTP)", text, re.IGNORECASE)
            if flash_m and not extracted["specs"].get("flash"):
                extracted["specs"]["flash"] = flash_m.group(1)

            # Operating voltage
            vcc_m = re.search(r"(?:VCC|VDD|VIN)[ :=]+(\d+(?:\.\d+)?)\s*(?:to|-)\s*(\d+(?:\.\d+)?)\s*V", text, re.IGNORECASE)
            if vcc_m and not extracted["specs"].get("operating_voltage_v"):
                extracted["specs"]["operating_voltage_v"] = f"{vcc_m.group(1)} to {vcc_m.group(2)}"

    # Family-specific layering
    # Read full PDF text so extractors can search any page that contains
    # the relevant bullet / table / parameter list. As of the 2026-07-05
    # factory-error fix-up we don't cap page coverage — different
    # vendors place 'Key features' / 'General description' /
    # 'Absolute maximum ratings' sections at wildly different page
    # offsets (GigaDevice: page 4, NXP: page 8-12, Nordic PS: page 30,
    # Renesas group datasheets: page 18-25). A 800-page Nordic PS
    # takes ~6 s to text-extract once; a 200-page TI datasheet takes
    # ~1.5 s. Capping at MAX_FULL_TEXT_PAGES = 0 means "no cap"
    # (read every page). Set to a finite integer to cap for speed on
    # genuinely huge docs (e.g. ST RM0444-style reference manuals at
    # 1500+ pages).
    MAX_FULL_TEXT_PAGES = 0  # 0 = unlimited
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        cap = page_count if MAX_FULL_TEXT_PAGES == 0 else min(page_count, MAX_FULL_TEXT_PAGES)
        for pn in range(cap):
            full_text += "\n" + (pdf.pages[pn].extract_text() or "")
        # Track which pages contributed, but keep the original
        # extracted_from_pages [1, 2] for the generic-pass provenance.
        # When MAX_FULL_TEXT_PAGES = 0 we cite every page so an external
        # verifier can reproduce the extraction by re-running pdfplumber.
        extracted["extracted_from_pages"] = list(range(1, min(page_count, 12) + 1))

    # Dispatch to the family-specific extractor declared in PARTS.
    # Unknown family values (or families whose extractor is still TODO)
    # fall through to the generic pass above — no-op is fine, the YAML
    # just stays minimal.
    if family:
        extractor = FAMILY_EXTRACTORS.get(family)
        if extractor is not None:
            extracted = extractor(extracted, full_text)
        else:
            extracted.setdefault("notes", []).append(
                f"No family-specific extractor registered for family={family!r}; "
                f"generic pdfplumber pass only."
            )

    # Vendor-agnostic supplementary pass.
    # Run AFTER the family extractor so the family regexes can win the
    # fill-first race. This pass is intentionally narrow: only captures
    # fields that are common across vendors AND that have a distinctive
    # page-1 bullet format that doesn't false-positive on later-page
    # figure captions / table noise.
    #
    # We pass page1_text (first 3 pages only) NOT full_text. Bullet
    # lists on page 1-3 are vendor-curated 'Key features' summaries
    # and yield clean signals; later pages contain parameter tables
    # whose numeric cells (e.g. 'cycle time × 50 ns', '0x4009_0000
    # SDHI0') match the same regexes as bullets and pollute the output.
    page1_text = ""
    for pn in range(min(3, page_count)):
        page1_text += "\n" + (pdf.pages[pn].extract_text() or "")
    extracted = _extract_page1_bullets(extracted, page1_text)

    return extracted


def _extract_page1_bullets(extracted: dict, text: str) -> dict:
    """Vendor-agnostic supplementary extractor for page-1 bullet formats.

    Only fills fields that the family extractor did NOT fill. Targets
    the most common page-1 'Operating Temperature / Packages / Peripherals'
    bullet styles across Renesas, NXP, ST, Nordic, TI, etc.

    Pass `text` should be page-1-only text (caller's responsibility).
    Do not pass the full PDF text here — figure captions / parameter
    tables on later pages match the same regexes with noise like
    'AGT (6ch)*4 50' (where 4 is cycles, 50 is ns).
    """
    s = extracted.setdefault("specs", {})

    # --- Operating temperature: 'Ta = -40℃ to +105℃' / 'Tstg = -55°C to +150°C'
    if not s.get("operating_temperature_c"):
        # Anchored on 'Ta' (operating) or 'Tj' (junction) — these are
        # the conventional symbols used by all major MCU vendors on
        # page 1 / package information. Avoid bare '-40°C to +85°C'
        # because that captures storage temp too.
        m = re.search(
            r"(?:Ta|Tj|TAMB)\s*=\s*[-]?(\d+)\s*°?C?\s*(?:to|~|…|\u2013|-)\s*\+?(\d+)\s*°?C",
            text,
        )
        if m:
            s["operating_temperature_c"] = f"{m.group(1)} to +{m.group(2)}"

    # --- Packages: '<N>-pin <TYPE> (WxH mm, P mm pitch)' dedup
    if not s.get("packages"):
        seen_pkgs = set()
        for pkg_m in re.finditer(
            r"(\d+)-pin\s+(LQFP|QFN|BGA|TFLGA|TQFN|WLCSP|HWQFN|LQFP-?EP)",
            text,
        ):
            key = (pkg_m.group(2), int(pkg_m.group(1)))
            if key in seen_pkgs:
                continue
            seen_pkgs.add(key)
            s.setdefault("packages", []).append({
                "type": pkg_m.group(2),
                "pin_count": int(pkg_m.group(1)),
            })

    # --- Connectivity / peripheral counts: '<PERIPHERAL NAME> × N'
    # Captures the 'SCI × 10' / 'GPT32 × 4' / 'ADC × 2' style used on
    # all Renesas / ST / NXP page-1 bullet lists.
    #
    # Tightness constraints (otherwise we pollute the count dict with
    # noise from '12-bit ADC' text, 'GPT32 bit-width=32', etc.):
    #   * Symbol MUST be followed by ' × ' or ' x ' (literal Unicode '×'
    #     or ASCII 'x' surrounded by spaces) — a numeric quantity of
    #     peripheral instances, not a bit width or address
    #   * Count must be 2..32 (n=1 is usually a footnote, n>32 is
    #     usually bits/bytes/cycles from a table)
    #   * Symbol list is sorted longest-first so 'USBHS' wins over 'USB'
    PERIPHERAL_SYMBOLS = [
        # Renesas (longest first)
        "ADC12", "DAC12", "GPT32", "GPT16", "USBFS", "USBHS", "CANFD",
        "ETHERC", "EDMAC", "SDHI", "SSIE", "OSPI", "QSPI", "DMAC", "CTSU",
        "TSN", "IWDT", "SCI", "IIC", "SPI", "USB", "CAN", "AGT", "WDT",
        "DTC", "LVD", "CAC", "ICU", "CEC",
        # ST
        "FDCAN", "USART", "SDMMC", "OTG_FS", "OTG_HS", "UART", "I2C",
        "ADC", "DAC", "TIM", "RTC", "ETH", "CRC", "RNG", "DMA", "GPIO",
        # NXP
        "FlexIO", "LPUART", "LPSPI", "LPI2C", "eMIOS", "DSPI", "FlexCAN",
        "ENET", "TSC", "PDB", "SAI", "I2S", "PWM", "eDMA",
    ]
    if not s.get("peripheral_counts"):
        peripheral_counts = {}
        symbol_alt = "|".join(re.escape(s) for s in sorted(PERIPHERAL_SYMBOLS, key=len, reverse=True))
        # Required literal '× ' (Unicode U+00D7) or ' x ' or '×N' (no space)
        # — the symbol must be IMMEDIATELY followed by the multiplication
        # mark. We allow one optional space on each side.
        for peri_m in re.finditer(
            r"(?<![\w])(" + symbol_alt + r")\s*[×x]\s*(\d{1,2})(?![\w])",
            text,
        ):
            symbol = peri_m.group(1)
            n = int(peri_m.group(2))
            if n < 2 or n > 32:
                continue
            if symbol in peripheral_counts:
                continue
            peripheral_counts[symbol] = n
        if peripheral_counts:
            s["peripheral_counts"] = peripheral_counts

    # --- Security / encryption: 'AES / RSA / ECC / SHA / TrustZone'
    if not s.get("security_features"):
        sec_bits = []
        for sec_m in re.finditer(
            r"\b(AES(?:-128|-256|-192)?|RSA|ECC(?:(?:\s+(?:P-?\d+|secp\d+r?\d*))?)|"
            r"SHA(?:-?\d{3,4})?(?:,?\s*SHA(?:-?\d{3,4}))*|TrustZone(?:[\s®]+(?:enabled|secure))?|"
            r"secure\s*boot|HASH|GHASH|HMAC|DSA|ECDSA|TRNG|PUF|secure\s*debug|"
            r"DICE|silent\s*CAN|life\s*cycle\s*management|tamper\s*detection)\b",
            text, re.IGNORECASE,
        ):
            token = sec_m.group(0).strip()
            if token and token not in sec_bits:
                sec_bits.append(token)
        if sec_bits:
            s["security_features"] = sec_bits[:20]  # cap to avoid noise

    return extracted


# === Merge into existing YAML ============================================

def merge_yaml(existing: dict, fresh: dict) -> dict:
    """Overwrite fields the script extracted; preserve unverified / notes / verified_by_human."""
    merged = dict(existing)
    merged["extracted_at"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    if fresh.get("datasheet_doc_id"):
        merged["datasheet_doc_id"] = fresh["datasheet_doc_id"]
    if fresh.get("datasheet_revision_partial"):
        merged["datasheet_revision"] = fresh["datasheet_revision_partial"] + " — refresh-needed"
    if fresh.get("extracted_from_pages"):
        merged["extracted_from_pages"] = fresh["extracted_from_pages"]
    if fresh.get("extraction_method"):
        merged["extraction_method"] = fresh["extraction_method"]
    merged.setdefault("specs", {})
    # If existing YAML was human-verified, only update keys that are
    # explicitly in the existing unverified list (i.e. the human marked
    # them as still-needs-work). Otherwise the regex extractor's
    # partial capture (e.g. 'Arm Cortex-M33' from a 200-char description)
    # would silently overwrite a richer human-written value.
    human_verified = bool(merged.get("verified_by_human"))
    unverified_set = set(merged.get("unverified") or [])
    extracted_keys = []
    for k, v in (fresh.get("specs") or {}).items():
        if human_verified and k not in unverified_set:
            continue
        merged["specs"][k] = v
        extracted_keys.append(k)
    if extracted_keys and merged.get("unverified"):
        merged["unverified"] = [k for k in merged["unverified"] if k not in extracted_keys]

    # Promote unverified: ['all'] -> cleared when the extractor covers
    # every spec field in the existing YAML and the extracted values
    # match the existing values byte-for-byte. This unsticks the
    # placeholder state left by the 2026-06-21 batch where the
    # extractor (added later in 01fe411) was never re-run.
    unverified_list = merged.get("unverified") or []
    if unverified_list == ["all"] and merged.get("specs"):
        existing_specs = (existing or {}).get("specs") or {}
        merged_specs = merged["specs"]
        # Every existing key must have been re-extracted with the same value.
        if existing_specs and set(existing_specs).issubset(set(extracted_keys)):
            all_match = all(
                merged_specs.get(k) == existing_specs.get(k)
                for k in existing_specs
            )
            if all_match:
                merged["unverified"] = []
                merged["link_status"] = (
                    f"verified_{dt.datetime.now().strftime('%Y-%m-%d')}"
                    f" (extractor-match)"
                )

    # Auto-remove the 2026-07-05 phase1-recovery factory-error note
    # when the new spec dict no longer matches the RX72N template that
    # produced the pollution. This is the data-loss fix-up:
    #   * Before the factory error: spec contents were the RX72N
    #     template (RX family flagship 32-bit MCU, 1396 CoreMark, etc.)
    #   * After re-extract with the correct datasheet PDF: spec contents
    #     are part-specific (e.g. 'RA Cortex-M33 @ 200 MHz', etc.)
    # The phase1-recovery note is no longer needed once the spec dict
    # stops resembling RX72N.
    #
    # Two clean-up actions:
    #   1. Drop any existing spec key whose value still contains an
    #      RX72N marker (the fresh extract didn't provide a new value
    #      for that key, so we should drop the stale RX72N data rather
    #      than keep it alongside the new part-specific data).
    #   2. If after step 1 the spec dict is fully part-specific, remove
    #      the phase1-recovery note and promote link_status.
    if extracted_keys:
        existing_specs = (existing or {}).get("specs") or {}
        rx72n_markers = ("RX family", "1396 CoreMark", "Trigonometric function", "Address space: 4 GB", "Register bank save function")

        def _specs_has_rx72n(specs_dict):
            """Check if any string value (scalar OR nested in list)
            contains an RX72N marker. The factory-error pollution
            spread via list values (cores: [...], security_features:
            [...]) so we have to walk lists too."""
            for k, v in specs_dict.items():
                if isinstance(v, str):
                    if any(m in v for m in rx72n_markers):
                        return True
                elif isinstance(v, list):
                    if any(
                        isinstance(item, str)
                        and any(m in item for m in rx72n_markers)
                        for item in v
                    ):
                        return True
            return False

        old_was_rx72n = _specs_has_rx72n(existing_specs)
        if old_was_rx72n:
            # Step 1: drop stale RX72N-templated keys
            new_specs = merged.get("specs") or {}
            keys_with_rx72n_marker = [
                k for k in list(new_specs.keys())
                if isinstance(new_specs.get(k), str)
                and any(m in new_specs.get(k, "") for m in rx72n_markers)
            ]
            for k in keys_with_rx72n_marker:
                del new_specs[k]
            merged["specs"] = new_specs

            # Step 2: also drop deeply-nested RX72N pollution (e.g.
            # peripherals.ethernet_mac text that came from the RX72N
            # datasheet and was preserved under peripherals.*).
            # We only do this for shallow scalars; complex nested dicts
            # are left alone to avoid accidental data loss.
            for k, v in list(new_specs.items()):
                if isinstance(v, str) and any(m in v for m in rx72n_markers):
                    del new_specs[k]

            # Step 3: decide whether to clear phase1-recovery note
            new_is_not_rx72n = all(
                not (
                    isinstance(new_specs.get(k), str)
                    and any(m in new_specs.get(k, "") for m in rx72n_markers)
                )
                for k in new_specs
            )
            # also check for list values (security_features can contain
            # RX72N tokens in some pathological cases)
            if new_is_not_rx72n:
                for v in new_specs.values():
                    if isinstance(v, list):
                        if any(
                            isinstance(item, str)
                            and any(m in item for m in rx72n_markers)
                            for item in v
                        ):
                            new_is_not_rx72n = False
                            break

            if new_is_not_rx72n:
                merged["notes"] = [
                    n for n in (merged.get("notes") or [])
                    if "phase1-recovery" not in str(n)
                    and "needs-re-extraction-factory-error" not in str(n)
                ]
                # Promote link_status — the re-extraction is verified
                # by the fact that the new spec dict contains part-
                # specific data with no RX72N markers left.
                if merged.get("link_status", "").startswith("needs-re-extraction"):
                    merged["link_status"] = (
                        f"verified_{dt.datetime.now().strftime('%Y-%m-%d')}"
                        f" (datasheet-pdf-extracted, phase1-recovery cleared)"
                    )

        # Note-only cleanup: if existing yaml still carries the
        # phase1-recovery note or needs-re-extraction link_status, but
        # the spec dict is already part-specific (no RX72N markers), we
        # should still drop the note. The old_was_rx72n branch above
        # is gated on the *previous* spec dict containing RX72N markers,
        # but a re-extract on a yaml that was already partially fixed
        # (e.g. cores already corrected, function still RX72N) needs the
        # same cleanup. Run this independently.
        existing_link = (existing or {}).get("link_status", "")
        existing_notes = (existing or {}).get("notes") or []
        has_factory_marker = (
            existing_link.startswith("needs-re-extraction-factory-error")
            or any("phase1-recovery" in str(n) for n in existing_notes)
        )
        if has_factory_marker:
            new_specs = merged.get("specs") or {}

            # If the new extractor only produced 2-3 part-specific
            # fields (typical for sensor/PMIC parts without cores/
            # flash/ram), the stale RX72N-templated cores/flash/ram
            # entries from the previous dump would otherwise keep the
            # phase1-recovery marker forever. Drop the stale top-level
            # keys that the new extract *did* provide (they overwrite
            # the stale values) and also drop the templated keys the
            # new extract didn't provide (no new value to keep).
            new_extracted_keys = set(extracted_keys or [])
            templated_keys_to_drop = (
                "cores", "flash", "ram", "function", "operating_voltage_v",
                "low_power_modes",
            )
            for k in templated_keys_to_drop:
                if k in new_specs and _specs_has_rx72n({k: new_specs[k]}):
                    if k in new_extracted_keys:
                        # New extract produced a non-RX72N value here —
                        # keep it (already overwritten).
                        continue
                    # Stale RX72N-templated value with no replacement.
                    del new_specs[k]
            merged["specs"] = new_specs

            if _specs_has_rx72n(new_specs):
                # Still polluted — leave the marker for next pass
                pass
            else:
                merged["notes"] = [
                    n for n in (merged.get("notes") or [])
                    if "phase1-recovery" not in str(n)
                    and "needs-re-extraction-factory-error" not in str(n)
                ]
                if merged.get("link_status", "").startswith("needs-re-extraction"):
                    merged["link_status"] = (
                        f"verified_{dt.datetime.now().strftime('%Y-%m-%d')}"
                        f" (datasheet-pdf-extracted, phase1-recovery cleared)"
                    )

    return merged


# === Main ================================================================

def main():
    parser = argparse.ArgumentParser(description="Update multi-vendor YAML spec database")
    parser.add_argument("--vendor", help="Only this vendor (default: all)")
    parser.add_argument("--part", help="Only this part (default: all for vendor)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be done; do not download / write / commit")
    parser.add_argument("--only-placeholder", action="store_true",
                        help="Skip parts that already have populated specs")
    args = parser.parse_args()

    vendors = {args.vendor: PARTS[args.vendor]} if args.vendor else PARTS

    for vendor, parts in vendors.items():
        for part, info in parts.items():
            if args.part and part != args.part:
                continue
            print(f"\n[{vendor}/{part}]")
            yp = yaml_path(vendor, part)
            existing = load_yaml(yp)
            existing_specs = existing.get("specs") or {}
            if args.only_placeholder and len(existing_specs) > 0:
                print(f"  [skip] --only-placeholder and specs already populated")
                continue
            if info.get("family_alias"):
                print(f"  [skip] family_alias → {info['family_alias']} (use that entry for extraction)")
                continue

            pdf_path = pdf_dir(vendor) / info["pdf_filename"]
            url_status = info.get("url_status", "")
            if url_status.startswith(("st_blocked_", "stale_2026-06_no_mirror")):
                print(f"  [skip-download] url_status={url_status!r} (known to fail from this network)")
                continue
            if not pdf_path.exists():
                if args.dry_run:
                    print(f"  [dry-run] would download {info['url']}")
                    continue
                try:
                    pdf_path = download_pdf(vendor, part, info)
                except FileNotFoundError as e:
                    print(f"  [skip-extract] {e}")
                    note = (f"- Auto-update: {vendor}/{part} datasheet download failed on "
                            f"{dt.datetime.now().strftime('%Y-%m-%d')}; YAML remains placeholder.")
                    merged = dict(existing)
                    merged.setdefault("notes", [])
                    if not any("datasheet download failed" in str(n) for n in merged["notes"]):
                        merged["notes"].append(note)
                    save_yaml(yp, merged)
                    print(f"  [write] placeholder updated with failure note")
                    continue
            else:
                print(f"  [exists] {pdf_path.name}")

            if args.dry_run:
                print(f"  [dry-run] would extract + write {yp.name}")
                continue

            fresh = extract_specs_from_pdf(pdf_path, family=info.get("family"))
            merged = merge_yaml(existing, fresh)
            save_yaml(yp, merged)
            print(f"  [write] {yp.name} (extracted {len(fresh.get('specs', {}))} spec fields)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
