# ESP32-E22 — Tri-Band Wi-Fi 6E + Bluetooth 5.4 Connectivity Co-Processor

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/Espressif/firecrawl-snapshots/ESP32-C5N-family_raw.md`
(84,101 bytes). Note: page returned via /products/socs/esp32-c5n URL but
content is for **ESP32-E22** (Espressif redirect/sibling — same SoC family
at different URL).

## Product Identity

- **Marketing tagline:** "Tri-band Wi-Fi 6E + Dual Mode Bluetooth 5.4
  Connectivity Co-Processor"
- **Family:** ESP32-E Series
- **Position:** Espressif's first **tri-band Wi-Fi 6E** co-processor.
  Pairs with application processors (ESP32-P4, other MCUs via PCIe 2.1 /
  SDIO 3.0).

## Wireless

### Tri-Band Wi-Fi 6E

- **2.4 GHz + 5 GHz + 6 GHz**
- **160 MHz channels**
- **2×2 MU-MIMO**
- **1024 QAM**
- Advanced link scheduling

### Bluetooth

- **Bluetooth Classic + BLE 5.4** ("Dual Mode")
- Versatile short-range wireless connectivity

## Performance / Process

- **Dual-core RISC-V @ up to 500 MHz**
- **1 MB internal RAM** (for drivers + data buffers)

## Host Interface (Co-Processor Mode)

- **PCIe 2.1**
- **SDIO 3.0**
- SPI (likely)
- UART (likely)

Pairs with:
- Espressif application processors (ESP32-P4)
- Third-party application processors

## Security

- (ESP32-E security features inherit from ESP32 platform; secure boot,
  flash encryption, hardware crypto accelerators expected)

## Variants / Modules / Dev Boards

- **ESP32-E22** — bare SoC (QFN 9×9, 41 GPIO, 192 KB RAM + 1 MB TCM)
- **ESP32-E22-M2** — module
- (Dev kit listed in Espressif's standard product page; details in raw)

## Use-Case Tier Hint

- **Wi-Fi 6E gateway co-processor** for application processors — pushes
  the most current Wi-Fi into products without rebuilding the host MCU.
- **6 GHz Wi-Fi 6E** is key: more spectrum, less congestion vs 5 GHz only.
  Future-proofing for 6 GHz-only infrastructure.
- **High-end routers / mesh nodes** with 2×2 MU-MIMO. (Co-processor form
  factor assumes host router SoC.)

## Application Areas

- Wi-Fi 6E routers, gateways, mesh nodes
- Smart home hubs with 6 GHz Wi-Fi backhaul
- Industrial wireless gateways with 6 GHz Wi-Fi + BLE
- Streaming media gateways (Wi-Fi 6E 160 MHz channels)

## Family Position

- ESP32-C5: dual-band Wi-Fi 6 + BLE 5 + 802.15.4 (host SoC)
- ESP32-C6: dual-band Wi-Fi 6 + BLE 5 + 802.15.4 (host SoC)
- **ESP32-E22 (this): tri-band Wi-Fi 6E + BT Classic + BLE 5.4
  (co-processor)**
- ESP32-H4: BLE 5.4 + 802.15.4 only (host SoC, ultra-low-power)
