# ESP32-C5 — Dual-Band Wi-Fi 6 SoC with BLE 5 + 802.15.4

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/Espressif/firecrawl-snapshots/ESP32-C5-family_raw.md`
(10,353 bytes). Captured from `https://www.espressif.com/en/products/socs/esp32-c5`.

## Product Identity

- **Marketing tagline:** "2.4 and 5 GHz Dual-Band Wi-Fi 6 SoC, with
  Bluetooth® 5 (LE) + 802.15.4 for Secure & Reliable Connectivity"
- **Family:** ESP32-C5
- **Position:** First ESP32 SoC with Wi-Fi 6 + dual-band + 802.15.4 in one chip.

## Wireless Capabilities

### Wi-Fi

- **Dual-band:** 2.4 GHz + 5 GHz
- **Wi-Fi 6 (802.11ax):** TWT (Target Wake Time), MU-MIMO, OFDMA, BSS coloring
- Backward compatibility: 802.11a / b / g / n / ac

### Bluetooth LE 5

- Bluetooth 5 (LE) — supports long-range via advertising extensions + coded PHY
- 2 Mbps high throughput PHY
- BLE SIG Mesh
- ESP-Mesh-Lite

### IEEE 802.15.4

- Integrated PHY + MAC layers
- Software stacks supported:
  - Thread
  - Zigbee
  - Matter
  - HomeKit
  - MQTT

## Security (Espressif "affordable security")

- **Secure Boot**
- **Flash + PSRAM encryption** (hardware-accelerated)
- **Cryptographic accelerators**
- **Hardware-based Digital Signature Peripheral**
- **Dedicated Key Manager** for secure storage and deployment
- **Trusted Execution Environment (TEE)** with
  - Access Permission Management (APM) hardware block
  - Physical Memory Protection (PMP)

## Software Support

- **ESP-IDF** (open-source Espressif SDK)
- **ESP-AT** — communication co-processor mode (with external host)
- **ESP-Hosted** — communication co-processor mode (with external host)

## Memory (parametric, not in fetched spec block)

- Support for **PSRAM** (specific size not in firecrawl-fetched spec block;
  pending datasheet extraction)

## Modules and Kits

- **ESP32-C5-WROOM-1** (module)
- **ESP32-C5-DevKitC-1** (dev kit)

## Related SoC Series (Espressif portfolio)

- **ESP32-S31** (entry-level sister)
- **ESP32-H4** (low-power BLE)
- **ESP32-E22** (industrial-grade)

## Use-Case Tier Hint

- **Wi-Fi 6 + Matter + Thread bridge** with secure boot + PSRAM encryption:
  competitive to Nordic nRF54H20 + nRF7002 in Matter border router tier
- **Dual-band IoT device** for home/industrial with 802.15.4+Matter support.
