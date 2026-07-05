# TI MSPM0L1106 — Cost-Down of MSPM0L1306 (no zero-drift OPA, 1× I²C)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/TI/firecrawl-snapshots/MSPM0L1106-family_raw.md`
(240,125 bytes). Captured from `https://www.ti.com/product/MSPM0L1106`.

## Family Identity

- **Family:** MSPM0L (cost-down tier of MSPM0L130x)
- **Marketing tagline:** "32-MHz Arm® Cortex®-M0+ MCU with 64-KB flash,
  4-KB SRAM, 12-bit ADC"
- **Position:** Cost-optimized version of MSPM0L1306 (existing yaml).
  Drops second OPA + second I²C + extended temp range. Otherwise identical
  power profile.

## Core

- **Arm Cortex-M0+ @ up to 32 MHz** (32-bit)

## Memory

- **Flash:** Up to 64 KB
- **SRAM:** 4 KB

## Operating Conditions

- **Supply voltage:** 1.62V to 3.6V
- **Temperature:** -40 to +105 °C (vs -40 to +125 on L1306)

## Power Modes (5 modes, identical to L1306)

| Mode | Current |
|---|---|
| RUN (CoreMark) | 71 µA/MHz |
| STOP @ 4 MHz | 151 µA |
| STOP @ 32 kHz | 44 µA |
| STANDBY | 1.0 µA (32-kHz 16-bit timer + SRAM/retention + 32 MHz wake-up 3.2 µs) |
| SHUTDOWN | 61 nA (IO wake-up) |

## Analog Peripherals

- 1× **12-bit 1.68-Msps ADC**, up to 10 external channels
- Configurable 1.4V / 2.5V internal VREF
- **1× general-purpose amplifier (GPAMP)** (vs L1306's **2× zero-drift
  zero-crossover chopper OPAs**)
- Integrated temperature sensor

## Digital Peripherals

- 3-channel DMA controller
- 3-channel event fabric signaling system
- 4× 16-bit GP timers (8 PWM channels total, STANDBY-capable)
- Windowed watchdog

## Communication (vs L1306: 1 less I²C!)

| Interface | Count | Notes |
|---|---|---|
| **UART** | 2 | one LIN/IrDA/DALI/Smart Card/Manchester; STANDBY-compatible |
| **I²C** | **1** (vs L1306's 2) | FM+ 1 Mbit/s, SMBus, PMBus, STOP wake-up |
| **SPI** | 1 | up to 16 Mbit/s |

## Clock System

- Internal 4-32 MHz oscillator (SYSOSC), ±1.2% accuracy
- Internal 32 kHz LFOSC, ±3% accuracy

## Data Integrity

- Cyclic redundancy checker (CRC-16 or CRC-32)

## I/O

- **Up to 28 GPIOs**
- 2× 5V-tolerant open-drain IOs

## Debug

- 2-pin Serial Wire Debug (SWD)

## Package Options

| Pkg. Type | Pins |
|---|---|
| VQFN (RHB) | 32 |
| VSSOP (DGS) | 28 |
| VQFN (RGE) | 24 |
| VSSOP (DGS) | 20 |
| SOT (DYY), WQFN (RTR) | 16 |

## Family Members

| Part | Flash | RAM |
|---|---|---|
| **MSPM0L1105** | 32 KB | 4 KB |
| **MSPM0L1106** | 64 KB | 4 KB |

## Dev Tools

- **LP-MSPM0L1306** LaunchPad™ (compatible - L1106 fits)
- MSP Software Development Kit (SDK)

## Use-Case Tier Hint

- **Cost-sensitive 5 lp-mode MCU** for industrial sensor nodes, smoke
  detectors, water/gas meters, smart locks.
- **Replacement for MSPM0L1306** when zero-drift OPA + extended temp range
  not needed.

## Application Areas

- Battery-powered wireless sensor MCU (companion to TI wireless MCU like
  CC2340R5 for BLE-only sensor nodes)
- Smoke detectors
- Water/gas meters
- Smart locks / IoT devices
