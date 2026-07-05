# Espressif ESP32-H4 — Dual-Core RISC-V SoC with BLE 5.4 + 802.15.4

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/Espressif/firecrawl-snapshots/ESP32-H4-family_raw.md`
(9,321 bytes). Captured from `https://www.espressif.com/en/products/socs/esp32-h4`.

## Product Identity

- **Marketing tagline:** "Next-Gen Dual-Core Ultra-Low-Power SoC, with
  Bluetooth® 5.4 (LE) + 802.15.4 for Long Battery Life & HMI"
- **Family:** ESP32-H (next-gen after ESP32-C family)
- **Position:** Espressif's flagship low-power wireless dual-core SoC.

## Core

- **Dual-core 32-bit RISC-V @ up to 96 MHz**
- Integrated DSP extensions

## Memory

- **SRAM:** 384 KB
- **ROM:** 128 KB
- Support for external memory
- Support for **external PSRAM** (for memory-intensive apps: LE Audio,
  complex protocol stacks, data logging, sensor fusion)

## Wireless

### Bluetooth 5.4 (LE) — certified to BLE 6.0

- LE Audio
- LE Isochronous Channels (BIS/CIS)
- Connection Subrating
- Periodic Advertising with Responses (PAwR)
- Direction Finding (AoA/AoD)
- Bluetooth Channel Sounding (per spec)

### IEEE 802.15.4

- **Thread 1.4**
- **Zigbee 3.0**
- Matter-over-Thread supported

## Power (Low-Power Optimized)

- **Integrated DC-DC converter** — better efficiency via lower VDD
- Multiple low-power modes
- **Selective peripheral activation**
- Reduced maximum transmit power (for lower RF current)
- **BLE advertising without CPU involvement**

## Security (Espressif "Affordable Security")

- (Details in raw: Secure Boot, flash encryption, crypto accelerators,
  Digital Signature, Key Manager, TEE, etc.)

## Software

- ESP-IDF (open-source Espressif SDK)
- ESP-AT, ESP-Hosted for co-processor mode

## Modules / Dev Kits

- (Family page shows the modules/devkits currently listed; details in raw)

## Use-Case Tier Hint

- **Wearables / LE Audio / health devices** (H4's low-power + LE Audio
  coding architecture; comparable to Nordic nRF54L15 in same tier).
- **Large-scale low-power mesh sensor networks** (BLE 5.4 + 802.15.4 + PAwR).
- **Battery-powered Matter-over-Thread devices** (12-18 month coin cell life).

## Application Areas

- Wearables
- Wireless audio (LE Audio)
- Healthcare devices (glucose monitor, ECG patch)
- Battery-powered Matter devices
- Low-power mesh sensor networks

## Family Position

- ESP32-C6 = dual-band Wi-Fi 6 + BLE 5 + 802.15.4
- ESP32-H4 = **BLE 5.4 + 802.15.4 only** (no Wi-Fi), dual-core RISC-V @ 96 MHz
- ESP32-S3 = dual-core Xtensa LX7 + Wi-Fi + BLE (no 802.15.4)
