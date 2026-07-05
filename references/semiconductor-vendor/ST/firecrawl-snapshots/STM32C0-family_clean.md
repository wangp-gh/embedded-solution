# ST STM32C0 Series — Cheapest STM32 (Cortex-M0+ @ 48 MHz, from $0.21)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/ST/firecrawl-snapshots/STM32C0-family_raw.md`
(57,442 bytes). Captured from `https://www.st.com/en/microcontrollers-microprocessors/stm32c0-series.html`.

## Family Identity

- **Family:** STM32C0 (entry-tier STM32, replacement for 8/16-bit MCUs)
- **Marketing tagline:** "Your next 8-bit MCU is a 32-bit. It's called STM32C0.
  And the series is expanding."
- **Position:** Lowest-cost STM32 from ST. Replaces older 8-bit MCUs (e.g.
  STM8) with 32-bit Cortex-M0+ architecture.

## Performance

- **Arm Cortex-M0+ @ 48 MHz**

## Memory

- **Flash:** 16 to 256 KB
- **RAM:** Up to 36 KB
- 1% accuracy internal clock (no external crystal required)

## Key Differentiation

- **From $0.21** (Suggested Resale Price for STM32C011J4M6 per 10,000 units)
- "Setting the lowest STM32 price point ever"
- Compatible pinout with **STM32G0** for easier migration
- Same technology & IP platform (1% accuracy internal clock)

## Package Options

- **Down to 1.70 x 1.42 mm** (WLCSP12, UFQFPN, UFQFPN20)
- 8- to 64-pin packages including:
  - **WLCSP** (smallest)
  - **SON**
  - **TSSOP**
  - **LQFP**
  - **UFQFPN**
- Single power supply pair only

## Sub-Series

### STM32C011 (Entry, ≤32 KB)

| Part | Flash | Package | Price (10k units) |
|---|---|---|---|
| STM32C011J4M6 | 16 KB | SO8N | $0.21 |
| STM32C011F4P6 | 16 KB | TSSOP20 | $0.27 |
| STM32C011F6P6 | 32 KB | TSSOP20 | $0.32 |

### STM32C031 (32-pin LQFP, 16-32 KB)

| Part | Flash | Package | Price |
|---|---|---|---|
| STM32C031K4T6 | 16 KB | LQFP32 | $0.41 |
| STM32C031K6T6 | 32 KB | LQFP32 | $0.44 |
| STM32C031C6T6 | 32 KB | LQFP48 | $0.49 |

### STM32C051 (64 KB flash)

| Part | Flash | Package | Price |
|---|---|---|---|
| STM32C051F8P6 | 64 KB | TSSOP20 | $0.43 |
| STM32C051K8T6 | 64 KB | LQFP/UFQFPN32 | $0.49 |
| STM32C051C8T6 | 64 KB | LQFP/UFQFPN48 | $0.53 |

### STM32C071 (128 KB flash + USB crystal-less)

| Part | Flash | Package | Price |
|---|---|---|---|
| STM32C071KBT6 | 128 KB | LQFP/UFQFPN32 | $0.58 |
| STM32C071CBT6 | 128 KB | LQFP/UFQFPN48 | $0.61 |
| STM32C071RBT6 | 128 KB | LQFP/UFBGA64 | $0.70 |

### STM32C091 (256 KB flash, max flash)

| Part | Flash | Package | Price |
|---|---|---|---|
| STM32C091FCP6 | 256 KB | TSSOP20 | $0.68 |
| STM32C091CCT6 | 256 KB | LQFP/UFQFPN48 | $0.78 |
| STM32C091RCT6 | 256 KB | LQFP/UFBGA64 | $0.87 |

### STM32C092 (128-256 KB with FDCAN)

| Part | Flash | Package | Price |
|---|---|---|---|
| STM32C092FBP6 | 128 KB | TSSOP20 | $0.65 |
| STM32C092CBT6 | 128 KB | LQFP/UFQFPN48 | $0.75 |
| STM32C092RCT6 | 256 KB | LQFP/UFBGA64 | $0.92 |

## Highlighted Features

- 12-bit ADC with hardware resolution up to **16-bit** (oversampling)
- USB host/device **crystal-less** for **STM32C071**
- **FDCAN** function support for **STM32C092**
- Flexible DMA mapping
- Advanced timers
- 2× UART on every device (even smallest 8-pin)
- Temperature range up to +125°C

## Reliability

- Proven STM32 quality
- ST 10-year longevity program
- **IEC 61508** functional safety standard

## Dev Tools

- NUCLEO-C031C6
- NUCLEO-C051C8
- NUCLEO-C071RB (with X-NUCLEO-GFX01M2 display expansion)
- (STM32Cube ecosystem)

## Use-Case Tier Hint

- **8-bit MCU replacement** with 32-bit performance / 1.7 mm WLCSP:
  - **Coin-cell battery applications** (smoke detectors, IoT tags)
  - **Ultra-small form factor products** (wearable, hearable, biosensors)
  - **Cost-sensitive industrial control** (sensor nodes, simple actuators)
- **Low-cost USB peripherals** with STM32C071 crystal-less USB
- **Industrial CAN nodes** with STM32C092 FDCAN
- Migration path: STM32G0 → STM32C011 (pin-compatible family for upgrade)

## Application Areas

- LED lighting drivers / RGB controllers
- Smoke detectors
- Bike odometer
- Sensor nodes
- Touch sensor
- Small USB peripherals (mice, keyboards, HID)
- Industrial CAN nodes
- e-cigarettes / vape pens
- Vending machines
