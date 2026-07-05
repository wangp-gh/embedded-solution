# Renesas RA6T2 — Cortex-M33 240 MHz Motor Control ASSP

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/Renesas/firecrawl-snapshots/RA6T2-family_raw.md`
(26,691 bytes). Captured from `https://www.renesas.com/en/products/ra6t2`.

## Product Identity

- **Family:** RA6T2 (second RA ASSP, targeting motor and inverter control)
- **Marketing tagline:** "240 MHz Arm Cortex-M33 TrustZone, High Real-time
  Engine for Motor Control"
- **Total variants:** 20 different part names × 5 package types

## Core

- **Arm Cortex-M33 @ 240 MHz** with TrustZone
- Hardware accelerator for motor control
- High-speed flash for real-time performance

## Memory

- **Program memory:** 256 KB or 512 KB flash
- **RAM:** 64 KB

## Operating Conditions

- **Supply Voltage:** 2.7V - 3.6V
- **Temperature:** -40 to +105 °C
- **No wireless** (host MCU)

## Peripherals

| Interface | Count |
|---|---|
| UART / SCI | 6 |
| SPI | 2 |
| I²C | 2 |
| CAN | 1 |
| CAN-FD | 0 or 1 |
| SDHI | 0 |
| 32-bit Timer | 10 |
| Asynchronous GPT | 2 |
| PWM output (pins) | 16, 18, 20 |
| High-Resolution Output Timer | yes |
| 12-bit ADC | 10 / 18 / 29 channels (variant) |
| 16-bit ADC | 0 / 10 / 18 / 29 channels (variant) |
| 12-bit DAC | 2 / 4 channels |
| Capacitive Touch | 0 |

## I/O Ports

- 35 / 51 / 84 (variant)

## Security & Encryption

- Unique ID
- TRNG (True Random Number Generator)
- AES (128-bit / 256-bit)
- GHASH
- Arm TrustZone

## Package Options

| Pkg. Type | Dim. (mm) | Lead Count | Pitch (mm) |
|---|---|---|---|
| HWQFN | 7×7×0.8 | 48 | 0.5 |
| HWQFN | 8×8×0.8 | 64 | 0.4 |
| LQFP | 7×7×1.7 | 48 | 0.5 |
| LQFP | 10×10×1.7 | 64 | 0.5 |
| LQFP | 14×14×1.7 | 100 | 0.5 |

## Communication

- No Ethernet, EtherCAT, USB (host/device), SDHI on this series.
  **Host MCU only for motor control.**

## Software

- **Flexible Software Package (FSP)** with Arm Partner Ecosystem
- Designed for "highly efficient and accurate motor and inverter control"

## Use-Case Tier Hint

- **Motor control / inverter control:** Primary use. High-resolution timer +
  PWM (16/18/20 pins) + hardware accelerator for FOC + 240 MHz Cortex-M33.
- **Industrial drives:** Compatible with 3-phase BLDC/PMSM motor algorithms.
