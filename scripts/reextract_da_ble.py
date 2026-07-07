#!/usr/bin/env python3
"""reextract_da_ble.py — Re-extract specs for Renesas DA BLE series (DA14531, DA14592,
DA14594, DA14697) from local datasheet PDFs.

Tailored for the proven patterns in Renesas DA BLE datasheet page 1.

Usage:
    python3 scripts/reextract_da_ble.py              # all 4 parts
    python3 scripts/reextract_da_ble.py DA14592     # single part
    python3 scripts/reextract_da_ble.py --dry-run
"""

from __future__ import annotations
import re
import sys
import yaml
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Run: pip install pdfplumber")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent

# (vendor, part, pdf_filename, datasheet_doc_id, datasheet_revision, match_strategy)
# match_strategy: "da1459x_template" | "da1469x_template" | "da14531_template"
PARTS = [
    ("Renesas", "DA14531", "DA14531_datasheet.pdf", "R18DS0050EE0380", "3.8", "da14531_template"),
    ("Renesas", "DA14592", "DA14592_datasheet.pdf", "R18DS0045EE0320", "3.2", "da1459x_template"),
    ("Renesas", "DA14594", "DA14594_datasheet.pdf", "R18DS0051EE0xxx", "current", "da1459x_template"),
    ("Renesas", "DA14697", "DA14697_datasheet.pdf", "R18DS0049EE0340", "3.4", "da1469x_template"),
]


def _extract_da1459x(text: str) -> dict:
    """DA14592 / DA14594 page-1 — 'Multi-Core Bluetooth LE 5.x SoC with Embedded Flash' layout."""
    specs: dict = {}

    cores = []
    if re.search(r"Arm[\s\u00ae]*Cortex[\s\u00ae]*-?M33F?(?:\s*32-bit)?(?:\s*CPU)?(?:\s*processor)?", text, re.IGNORECASE):
        cores.append("Arm Cortex-M33F (with FPU)")
    if re.search(r"Arm[\s\u00ae]*Cortex[\s\u00ae]*-?M0\+", text, re.IGNORECASE):
        cores.append("Arm Cortex-M0+ (BLE MAC engine)")
    if cores:
        specs["cores"] = cores

    clock_m = re.search(r"32\s*kHz\s+(?:up\s*to\s+)?(\d+)\s*MHz", text, re.IGNORECASE)
    if clock_m:
        specs["max_clock_mhz"] = int(clock_m.group(1))

    dmips_m = re.search(r"(\d+)\s*dMIPS(?:\s+at\s+(\d+)\s*MHz)?", text)
    if dmips_m:
        specs["dmips"] = int(dmips_m.group(1))
        if dmips_m.group(2):
            specs["dmips_clock_mhz"] = int(dmips_m.group(2))

    flash_m = re.search(r"(\d+)\s*kB\s+embedded\s+Flash", text, re.IGNORECASE)
    if flash_m:
        specs["flash_kb"] = int(flash_m.group(1))

    ram_m = re.search(r"(\d+)\s*kB\s+Data\s*SRAM", text, re.IGNORECASE)
    if ram_m:
        specs["ram_kb"] = int(ram_m.group(1))

    cache_m = re.search(r"(\d+)\s*kB\s+Caches?\s+with\s+retention", text, re.IGNORECASE)
    if cache_m:
        specs["cache_kb"] = int(cache_m.group(1))

    rom_m = re.search(r"(\d+)\s*kB\s+ROM\b", text, re.IGNORECASE)
    if rom_m:
        specs["rom_kb"] = int(rom_m.group(1))

    ble_m = re.search(r"Bluetooth[\s\u00ae]*\s*Low\s+Energy\s*(\d+\.\d+(?:\.[xX])?)\s+standard", text, re.IGNORECASE)
    if ble_m:
        specs["ble_version"] = ble_m.group(1)

    # TX / RX — "TX output power -22 to +6 dBm, RX sensitivity -97 dBm" (High Performance)
    tx2_m = re.search(
        r"TX\s+output\s+power\s*[-]?\s*(\d+)\s+to\s+\+?(\d+)\s*dBm[,\s]+"
        r"RX\s+sensitivity\s*[-]?(\d+)\s*dBm",
        text, re.IGNORECASE,
    )
    if tx2_m:
        try:
            specs["tx_dbm_min_high_perf"] = -int(tx2_m.group(1))
            specs["tx_dbm_max_high_perf"] = int(tx2_m.group(2))
            specs["rx_sensitivity_dbm_high_perf"] = -int(tx2_m.group(3))
        except ValueError:
            pass

    gpio_m = re.search(r"[Uu]p\s*to\s+(\d+)\s+General\s+Purpose\s+I\s*/?\s*Os?", text)
    if gpio_m:
        specs["gpio_count_max"] = int(gpio_m.group(1))

    adc_m = re.search(r"(\d+)[-\s]+channel\s+(\d+)[-\s]+bit\s+SAR\s+ADC", text, re.IGNORECASE)
    if adc_m:
        specs["adc_channels"] = int(adc_m.group(1))
        specs["adc_resolution_bits"] = int(adc_m.group(2))

    sd_m = re.search(r"[\u03a3\u03c3]\s*[\u0394\u0394]?\s*ADC[,\s]+(\d+)\s*bits?\s+(?:at|@)\s+\d+\s*ksps", text, re.IGNORECASE)
    if sd_m:
        specs["sigma_delta_adc_bits"] = int(sd_m.group(1))

    crypto_m = re.search(r"AES-(\d+)\s+and\s+SHA-(\d+)", text)
    if crypto_m:
        specs["crypto"] = f"AES-{crypto_m.group(1)}, SHA-{crypto_m.group(2)}"

    hib_m = re.search(r"[Hh]ibernation[^\n.]*?<?\s*(\d+)\s*nA", text)
    if hib_m:
        try:
            specs["hibernation_current_na"] = int(hib_m.group(1))
        except ValueError:
            pass

    packages = []
    for pkg_m in re.finditer(
        r"(WLCSP\d+)[,\s]+([\d.]+)\s*[×x]\s*([\d.]+)(?:[,]?\s*([\d.]+)\s*mm\s*(?:diagonal\s*)?pitch)?",
        text,
    ):
        packages.append({
            "type": pkg_m.group(1),
            "size_mm": f"{pkg_m.group(2)} × {pkg_m.group(3)}",
            "pitch_mm": pkg_m.group(4) if pkg_m.group(4) else None,
        })
    for pkg_m in re.finditer(
        r"(FC?QFN\d+)[,\s]+([\d.]+)\s*[×x]\s*([\d.]+)(?:[,]?\s*([\d.]+)\s*mm\s*pitch)?",
        text,
    ):
        packages.append({
            "type": pkg_m.group(1),
            "size_mm": f"{pkg_m.group(2)} × {pkg_m.group(3)}",
            "pitch_mm": pkg_m.group(4) if pkg_m.group(4) else None,
        })
    if packages:
        seen = set()
        unique = []
        for p in packages:
            key = (p["type"], p["size_mm"])
            if key not in seen:
                seen.add(key)
                unique.append(p)
        specs["packages"] = unique

    return specs


def _extract_da1469x(text: str) -> dict:
    """DA14697 page-1 — 'Multi-Core Bluetooth 5.2 SoC Family with System PMU' layout."""
    specs: dict = {}

    cores = []
    if re.search(r"Arm[\s\u00ae]*Cortex[\s\u00ae]*-?M33F?(?:\s*32-bit)?(?:\s*CPU)?(?:\s*processor)?", text, re.IGNORECASE):
        cores.append("Arm Cortex-M33F (with FPU)")
    if re.search(r"uCode(?:\s+based)?(?:\s+(?:sensor|motor))?\s+(?:controller|node)", text, re.IGNORECASE):
        cores.append("uCode sensor node controller (M0-class)")
    if cores:
        specs["cores"] = cores

    clock_m = re.search(r"32\s*kHz\s+(?:up\s*to\s+)?(\d+)\s*MHz", text, re.IGNORECASE)
    if clock_m:
        specs["max_clock_mhz"] = int(clock_m.group(1))

    dmips_m = re.search(r"(\d+)\s*dMIPS", text)
    if dmips_m:
        specs["dmips"] = int(dmips_m.group(1))

    flash_m = re.search(r"(\d+(?:\.\d+)?)\s*MB\s+(?:of\s+)?(?:embedded\s+)?Flash", text, re.IGNORECASE)
    if flash_m:
        specs["flash_mb"] = float(flash_m.group(1))

    ram_m = re.search(r"(\d+)\s*kB\s+Data\s*SRAM\s+with\s+retention", text, re.IGNORECASE)
    if ram_m:
        specs["ram_kb"] = int(ram_m.group(1))

    cache_m = re.search(r"(\d+)\s*kB[,\s]+4-way\s+associative\s+cache", text, re.IGNORECASE)
    if cache_m:
        specs["cache_kb"] = int(cache_m.group(1))

    otp_m = re.search(r"(\d+)\s*kB\s+One-Time-Programmable", text, re.IGNORECASE)
    if otp_m:
        specs["otp_kb"] = int(otp_m.group(1))

    rom_m = re.search(r"(\d+)\s*kB\s+ROM\b", text, re.IGNORECASE)
    if rom_m:
        specs["rom_kb"] = int(rom_m.group(1))

    ble_m = re.search(r"Bluetooth[\s\u00ae]*\s*(?:LE\s*)?(?:low\s+energy\s*)?(\d+\.\d+(?:\.[xX])?)\s+(?:Low\s+Energy\s+|standard|connectivity)", text, re.IGNORECASE)
    if ble_m:
        specs["ble_version"] = ble_m.group(1)

    tx_dbm_m = re.search(r"output\s+power\s*[-]?\s*(\d+)\s+to\s+\+?(\d+)\s*dBm", text, re.IGNORECASE)
    if tx_dbm_m:
        try:
            specs["tx_dbm_min"] = -int(tx_dbm_m.group(1))
            specs["tx_dbm_max"] = int(tx_dbm_m.group(2))
        except ValueError:
            pass

    rx_m = re.search(r"[-](\d+)\s*dBm\s+(?:receiver\s+)?sensitivity", text, re.IGNORECASE)
    if rx_m:
        specs["rx_sensitivity_dbm"] = -int(rx_m.group(1))

    crypto_m = re.search(r"AES-(\d+)", text)
    if crypto_m:
        specs["crypto"] = f"AES-{crypto_m.group(1)}"
    hash_m = re.search(r"SHA-(?:1[,\s]*)?(\d+)", text)
    if hash_m and "crypto" in specs:
        specs["crypto"] = f"{specs['crypto']}, SHA-{hash_m.group(1)}"

    gpio_m = re.search(r"[Uu]p\s*to\s+(\d+)\s+General\s+Purpose\s+I\s*/?\s*Os?", text)
    if gpio_m:
        specs["gpio_count_max"] = int(gpio_m.group(1))

    # ADC — "8-channel 10-bit SAR ADC" + "8-channel 14-bit ΣΔ ADC"
    sar_m = re.search(r"(\d+)-channel\s+(\d+)-bit\s+SAR\s+ADC", text)
    if sar_m:
        specs["adc_channels"] = int(sar_m.group(1))
        specs["adc_resolution_bits"] = int(sar_m.group(2))
    sd_m = re.search(r"(\d+)-channel\s+(\d+)-bit\s+[\u03a3\u03c3]\s*[\u0394\u0394]\s*ADC", text)
    if sd_m:
        specs["sigma_delta_adc_channels"] = int(sd_m.group(1))
        specs["sigma_delta_adc_bits"] = int(sd_m.group(2))

    packages = []
    for pkg_m in re.finditer(
        r"(VFBGA\d+|WLSCP\d+|WLCSP\d+|FC?QFN\d+)[,\s]+([\d.]+)\s*[×x]\s*([\d.]+)(?:[,]?\s*([\d.]+)\s*mm\s*pitch)?",
        text,
    ):
        packages.append({
            "type": pkg_m.group(1),
            "size_mm": f"{pkg_m.group(2)} × {pkg_m.group(3)}",
            "pitch_mm": pkg_m.group(4) if pkg_m.group(4) else None,
        })
    if packages:
        seen = set()
        unique = []
        for p in packages:
            key = (p["type"], p["size_mm"])
            if key not in seen:
                seen.add(key)
                unique.append(p)
        specs["packages"] = unique

    return specs


def _extract_da14531(text: str) -> dict:
    """DA14531 page-1 — different layout (Memories/Radio are bullets, not bullets-with-keywords)."""
    specs: dict = {}

    # General description has 'Arm Cortex-M0+' + 'RAM of 48 kB'
    if re.search(r"Arm[\s\u00ae]*Cortex[\s\u00ae]*-?M0\+\s+microcontroller", text, re.IGNORECASE):
        specs["cores"] = ["Arm Cortex-M0+ (single core, application + BLE)"]

    # Clock — "16 MHz 32-bit Arm Cortex-M0+"
    clock_m = re.search(r"(\d+)\s*MHz\s+32-bit\s+Arm\s+Cortex-M0\+", text)
    if clock_m:
        specs["max_clock_mhz"] = int(clock_m.group(1))

    # IoTMark-Bluetooth LE score
    iot_m = re.search(r"(\d+)\s+EEMBC\s+IoTMark-Bluetooth", text)
    if iot_m:
        specs["eembc_iotmark_ble_score"] = int(iot_m.group(1))

    # Memories: '32 kB One-Time-Programmable (OTP)', '48 kB Retainable System RAM', '144 kB ROM'
    otp_m = re.search(r"(\d+)\s*kB\s+One-Time-Programmable\s+\(OTP\)", text)
    if otp_m:
        specs["otp_kb"] = int(otp_m.group(1))
    ram_m = re.search(r"(\d+)\s*kB\s+Retainable\s+System\s+RAM", text)
    if ram_m:
        specs["ram_kb"] = int(ram_m.group(1))
    rom_m = re.search(r"(\d+)\s*kB\s+ROM", text)
    if rom_m:
        specs["rom_kb"] = int(rom_m.group(1))

    # BLE 5.1 — main description
    ble_m = re.search(r"Bluetooth[\s\u00ae]*\s*(?:low\s+energy\s+)?5\.(\d+)\s+standard", text, re.IGNORECASE)
    if ble_m:
        specs["ble_version"] = f"5.{ble_m.group(1)}"

    # TX: '3.5 mA, RX: 2.2 mA (system currents with DCDC, V=3 V and 0 dBm)'
    tx_ma_m = re.search(r"TX:\s*([\d.]+)\s*mA,\s*RX:\s*([\d.]+)\s*mA.*?(\d+)\s*dBm", text)
    if tx_ma_m:
        try:
            specs["tx_current_ma_at_0dbm"] = float(tx_ma_m.group(1))
            specs["rx_current_ma"] = float(tx_ma_m.group(2))
        except ValueError:
            pass
    # TX range: -19.5 to +2.5 dBm
    tx_range_m = re.search(r"transmit\s+output\s+power\s+from\s*[-]?([\d.]+)\s+dBm\s+to\s+\+?([\d.]+)\s+dBm", text, re.IGNORECASE)
    if tx_range_m:
        try:
            specs["tx_dbm_min"] = -float(tx_range_m.group(1))
            specs["tx_dbm_max"] = float(tx_range_m.group(2))
        except ValueError:
            pass
    rx_m = re.search(r"[-](\d+)\s*dBm\s+receiver\s+sensitivity", text)
    if rx_m:
        specs["rx_sensitivity_dbm"] = -int(rx_m.group(1))

    # Hibernation
    hib_m = re.search(r"Clock-less\s+hibernation\s+mode:\s*Buck\s+(\d+)\s*nA,\s*Boost\s+(\d+)\s*nA", text, re.IGNORECASE)
    if hib_m:
        try:
            specs["hibernation_current_na_buck"] = int(hib_m.group(1))
            specs["hibernation_current_na_boost"] = int(hib_m.group(2))
        except ValueError:
            pass

    # GPIO — "GPIOs: 6 (WLCSP17), 12 (FCGQFN24)"
    gpio_m = re.search(r"GPIOs?:\s*(\d+)\s*\((\w+)\),\s*(\d+)\s*\((\w+)\)", text)
    if gpio_m:
        specs["gpio_per_package"] = {
            gpio_m.group(2): int(gpio_m.group(1)),
            gpio_m.group(4): int(gpio_m.group(3)),
        }

    # ADC — "4-channel 10-bit ADC"
    adc_m = re.search(r"(\d+)-channel\s+(\d+)-bit\s+ADC", text)
    if adc_m:
        specs["adc_channels"] = int(adc_m.group(1))
        specs["adc_resolution_bits"] = int(adc_m.group(2))

    # Crypto — AES-128
    crypto_m = re.search(r"AES-(\d+)\s+Encryption", text)
    if crypto_m:
        specs["crypto"] = f"AES-{crypto_m.group(1)}"

    # Packages
    packages = []
    for pkg_m in re.finditer(
        r"(WLCSP\d+)", text
    ):
        packages.append({"type": pkg_m.group(1), "size_mm": None, "pitch_mm": None})
    for pkg_m in re.finditer(
        r"(FC?GQFN\d+)", text
    ):
        packages.append({"type": pkg_m.group(1), "size_mm": None, "pitch_mm": None})
    if packages:
        seen = set()
        unique = []
        for p in packages:
            if p["type"] not in seen:
                seen.add(p["type"])
                unique.append(p)
        specs["packages"] = unique

    # Supply voltage
    buck_m = re.search(r"Buck:\s*([\d.]+)\s*V\s+[≤<]\s*V\s*[≤<]\s*([\d.]+)\s*V", text)
    if buck_m:
        try:
            specs["vbat_high_min_v"] = float(buck_m.group(1))
            specs["vbat_high_max_v"] = float(buck_m.group(2))
        except ValueError:
            pass
    boost_m = re.search(r"Boost:\s*([\d.]+)\s*V\s+[≤<]\s*V\s*[≤<]\s*([\d.]+)\s*V", text)
    if boost_m:
        try:
            specs["vbat_low_min_v"] = float(boost_m.group(1))
            specs["vbat_low_max_v"] = float(boost_m.group(2))
        except ValueError:
            pass

    return specs


EXTRACTORS = {
    "da1459x_template": _extract_da1459x,
    "da1469x_template": _extract_da1469x,
    "da14531_template": _extract_da14531,
}


def reextract_one(vendor: str, part: str, pdf_filename: str, doc_id: str, revision: str,
                  strategy: str, dry_run: bool):
    pdf_path = REPO_ROOT / "embedded_dev" / vendor.lower() / "datasheet" / pdf_filename
    yaml_path = REPO_ROOT / "specs" / vendor / f"{part}.yaml"

    if not pdf_path.exists():
        print(f"  ❌ {vendor}/{part}: PDF missing at {pdf_path}")
        return False

    if not yaml_path.exists():
        print(f"  ❌ {vendor}/{part}: yaml missing at {yaml_path}")
        return False

    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text() or ""
        # For DA1469x some fields are on p2
        if strategy == "da1469x_template" and len(pdf.pages) > 1:
            text += "\n" + (pdf.pages[1].extract_text() or "")

    extractor = EXTRACTORS[strategy]
    new_specs = extractor(text)

    if not new_specs:
        print(f"  ⚠️  {vendor}/{part}: extraction returned 0 fields")
        return False

    # Load existing yaml
    text_yaml = yaml_path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text_yaml)
    except yaml.YAMLError as e:
        print(f"  ❌ {vendor}/{part}: yaml parse error: {e}")
        return False

    if not isinstance(data, dict):
        print(f"  ❌ {vendor}/{part}: yaml top is not a dict")
        return False

    # Update fields
    data["part"] = part
    data["source_pdf"] = f"../../embedded_dev/{vendor.lower()}/datasheet/{pdf_filename}"
    data["datasheet_revision"] = revision
    data["datasheet_doc_id"] = doc_id
    data["extracted_at"] = "2026-07-05T23:50:00+08:00"
    data["extracted_from_pages"] = [1]
    data["extraction_method"] = (
        f"reextract_da_ble.py (strategy={strategy}; page-1 Key Features + General Description)"
    )
    data["verified_by_human"] = False
    data["link_status"] = (
        f"verified_{revision.replace('.', '-')} (datasheet-pdf-extracted, dedicated page-1 extractor)"
    )

    existing_unverified = data.get("unverified", [])
    data["specs"] = new_specs
    if existing_unverified:
        data["unverified"] = existing_unverified

    note_str = (
        f"Re-extracted 2026-07-05 via scripts/reextract_da_ble.py (strategy={strategy}). "
        f"Prior versions had RX72N content mislabeled with part={part}; previous tooling "
        f"(update_specs.py) wrote incomplete fields. This run produces {len(new_specs)} spec fields "
        f"sourced directly from the DA BLE datasheet page-1 Key Features block."
    )
    data["notes"] = [note_str]

    # PDF cross-check warning
    if strategy == "da1459x_template" and part != "DA14592":
        # Heuristic: if filename says 'DA14594' but PDF doesn't mention 'DA14594' or
        # mentions DA1459x generically, it might be DA14592's PDF
        if part not in text:
            note_str += (
                f" WARNING: PDF at {pdf_filename} appears to be a sibling-series document "
                f"(no '{part}' literal found on page 1). Specs were extracted from the shared "
                f"'DA1459x' template. Verify PDF identity before relying on these fields."
            )
            data["notes"] = [note_str]

    if dry_run:
        print(f"  [dry-run] {vendor}/{part} ({strategy}): would write {len(new_specs)} spec fields")
        return True

    yaml.safe_dump(data, yaml_path.open("w", encoding="utf-8"),
                   sort_keys=False, allow_unicode=True, default_flow_style=False)
    print(f"  ✅ {vendor}/{part} ({strategy}): wrote {len(new_specs)} spec fields")
    return True


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if not a.startswith("--")]

    if not args:
        target_parts = [p[1] for p in PARTS]
    else:
        target_parts = args

    print(f"Re-extracting {len(target_parts)} DA BLE part(s)...")
    print()
    ok = 0
    for vendor, part, pdf_filename, doc_id, revision, strategy in PARTS:
        if part not in target_parts:
            continue
        if reextract_one(vendor, part, pdf_filename, doc_id, revision, strategy, dry_run):
            ok += 1

    print(f"\nDone: {ok}/{len(target_parts)} succeeded")


if __name__ == "__main__":
    main()