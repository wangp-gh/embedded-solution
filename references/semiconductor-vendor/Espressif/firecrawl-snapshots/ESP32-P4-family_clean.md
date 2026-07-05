# Espressif ESP32-P4 — High-Performance SoC (no wireless, MPU tier)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/Espressif/firecrawl-snapshots/ESP32-P4-family_raw.md`
(15,259 bytes). Captured from `https://www.espressif.com/en/products/socs/esp32-p4`.

## Product Identity

- **Marketing tagline:** "High-Performing SoC Offering Extensive IO
  Connectivity, HMI, and Security Features"
- **Family:** ESP32-P (application processor tier — no wireless)
- **Position:** Espressif's MPU-grade application processor for advanced HMI,
  edge computing, and host-controller to Wi-Fi/BLE wireless companions.

## Core (Multi-Core)

- **Dual-core RISC-V HP-Core @ up to 400 MHz** (with single-precision FPU
  + AI extensions)
- **LP-Core @ up to 40 MHz** (for ultra-low-power always-on tasks)

## Memory

- **768 KB on-chip SRAM** (accessible as cache when external PSRAM available)
- **8 KB zero-wait TCM RAM**
- External PSRAM support

## HMI (Rich Multimedia)

- **MIPI-CSI** with integrated ISP — high-resolution camera interfaces
- **MIPI-DSI** — high-resolution display
- Handles **up to 1080p** for both display + camera
- Parallel display + parallel camera interfaces (broad compatibility)
- **Capacitive touch inputs**
- **Speech recognition** hardware
- H.264 **hardware encoding** (max 1080p @ 30 fps)
- Integrated hardware **Pixel Processing Accelerator (PPA)**
- **2D-DMA** for GUI development

## Peripherals

- **55 programmable GPIOs** (significant increase vs previous Espressif SoCs)
- SPI, I²S, I²C, LED PWM, MCPWM, RMT, ADC, UART, TWAI™
- **USB OTG 2.0 HS** (high-speed)
- **Ethernet**
- **SDIO Host 3.0** (high-speed connectivity)

## Security (Best-in-Class)

- **Secure Boot**
- **Flash Encryption**
- **Cryptographic accelerators**
- **TRNG**
- **Digital Signature Peripheral**
- **Dedicated Key Management Unit** (private keys generated within SoC, not
  exposed in plaintext to software)
- **Access Permission Management** (hardware)
- **Privilege Separation**

## Software

- ESP-IDF (open-source Espressif SDK)
- Target operating systems:
  - FreeRTOS
  - Zephyr
  - Linux (with external wireless companion)

## Companion Wireless (typical use)

Pair with an Espressif wireless SoC (ESP32-C6 / ESP-HOSTED firmware / etc.)
for applications that need Wi-Fi/BLE at the network layer plus high-performance
RISC-V MPU at the application layer.

## Use-Case Tier Hint

- **Smart home control panel** with 1080p display + capacitive touch + voice
  wake-word (LP-Core wakes HP-Core on voice).
- **Edge AI / vision** for face recognition on-camera inferencing
  (RISC-V AI extensions + PPA + ISP).
- **Industrial HMI / POS terminal** with dual-band Wi-Fi through companion
  ESP32-C6.
- **Camera-based IoT edge node** with low-power sleep (LP-Core) until motion
  detected.

## Application Areas

- Smart home hubs / control panels (knob panel, wall switch with display)
- Smart doorbell + facial recognition
- Industrial control panels (1080p HMI)
- POS terminals
- Edge AI camera gateway
- Voice assistant with local wake-word

## Family Position

- ESP32-S3 = wireless + small SoC
- **ESP32-P4 = NO wireless, application processor tier**
- Pairs with ESP32-C6 / ESP-HOSTED for network layer
