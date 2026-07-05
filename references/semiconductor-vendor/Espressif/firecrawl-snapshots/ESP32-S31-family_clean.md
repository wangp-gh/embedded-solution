# Espressif ESP32-S31 — Dual-Core RISC-V 320 MHz Multi-Protocol SoC

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/Espressif/firecrawl-snapshots/ESP32-S31-family_raw.md`
(12,858 bytes). Captured from `https://www.espressif.com/en/products/socs/esp32-s31`.

## Product Identity

- **Marketing tagline:** "Dual-Core RISC-V SoC with High-Performance
  Multi-Protocol Connectivity & HMI"
- **Family:** ESP32-S (next-gen after S3)
- **Position:** Espressif's flagship multi-protocol host SoC with edge AI
  + 1 Gbps Ethernet. Sister to ESP32-S3 (Xtensa LX7).

## Core

- **Dual-core 32-bit RISC-V @ up to 320 MHz**
- Designed for **edge AI** (neural network inference, signal processing,
  computer vision, intelligent audio)

## Memory

- (Raw fetched data has detailed memory block; specifics in raw)

## Wireless (Comprehensive Connectivity)

### Wi-Fi 6

- **2.4 GHz Wi-Fi 6 (802.11ax)** with **enhanced transmission efficiency
  + reduced power consumption** — ideal for battery-powered and always-
  connected devices

### Bluetooth

- **Bluetooth 5.4 (LE)**
  - LE Audio (high-quality, low-power audio streaming)
  - Direction Finding
  - Bluetooth Mesh 1.1
- **Bluetooth Classic (BR/EDR)** — legacy audio device compatibility,
  low-latency HMI

### IEEE 802.15.4

- **Thread**
- **Zigbee**
- Matter-over-Thread supported

### Wired

- **1000 Mbps Ethernet MAC** — stable, high-bandwidth wired connectivity

## HMI (Rich)

- 60 GPIOs
- "Diverse display interfaces"
- Wide range of peripherals

## Peripherals

- DVP camera (8-16-bit)
- RGB LCD (8-24-bit)
- 14 touch channels
- USB OTG
- SPI
- I2S
- UART
- I2C
- LED PWM
- TWAI (CAN 2.0)

## Security

- Secure boot
- Flash / PSRAM encryption
- ECDSA digital signature
- RAM-based PUF
- Hardware crypto acceleration

## Software

- ESP-IDF (open-source Espressif SDK)
- Common cloud connectivity agents

## Use-Case Tier Hint

- **Edge AI IoT** — neural network inference, computer vision on-camera.
- **Industrial IoT gateway** — Wi-Fi 6 + BLE 5.4 + 802.15.4 + 1 Gbps
  Ethernet for wired backhaul.
- **Smart home hub** — multi-protocol bridge with Ethernet.
- **Audio product** — Bluetooth Classic + LE Audio + 14 touch channels.
- **Cross-protocol bridge** — Wi-Fi 6 → Thread/Zigbee (Matter).

## Application Areas

- Edge AI cameras (smart doorbell with face recognition)
- Smart home hub (Wi-Fi 6 + 1 Gbps Ethernet)
- Industrial IoT gateway
- Audio product (speaker, headset, smart speaker)
- Multi-protocol bridge
- HMI control panel

## Family Position

- ESP32-S3 — dual-core Xtensa LX7 @ 240 MHz, Wi-Fi + BLE, no 802.15.4
- **ESP32-S31** — dual-core RISC-V @ 320 MHz, Wi-Fi 6 + BLE 5.4 +
  802.15.4 + BT Classic + 1 Gbps Ethernet
- ESP32-P4 — MPU tier (no wireless)
