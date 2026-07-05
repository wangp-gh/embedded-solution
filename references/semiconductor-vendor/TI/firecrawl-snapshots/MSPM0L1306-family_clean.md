# TI MSPM0L1306 — Ultra-Low-Power 32-MHz Arm Cortex-M0+ MCU

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/TI/firecrawl-snapshots/MSPM0L1306-family_raw.md`
(286,796 bytes). Captured from `https://www.ti.com/product/MSPM0L1306`.

## Family Identity

- **Family:** MSPM0L (MSPM0 platform — low-power tier)
- **Marketing tagline:** "32-MHz Arm® Cortex®-M0+ MCU with 64-KB flash,
  4-KB SRAM, 12-bit ADC, comparator, OPA"
- **Position:** TI's most cost-effective Cortex-M0+, optimized for ultra-low
  power (5 lp modes). Companion to MSPM0G (high perf) and MSPM0C (cost).

## Core

- **Arm Cortex-M0+ @ up to 32 MHz**
- 32-bit

## Memory

- **Flash:** 64 KB (in-system programmable)
- **SRAM:** 4 KB
- **NVM:** 64 KB

## Operating Conditions

- **Supply voltage:** 1.62V to 3.6V (wide range)
- **Operating temperature:** -40 to +125 °C
- **Rating:** Catalog

## Power Modes (5 low-power modes)

| Mode | Current | Notes |
|---|---|---|
| RUN (CoreMark) | 71 µA/MHz | active processing |
| STOP @ 4 MHz | 151 µA | reduced clock |
| STOP @ 32 kHz | 44 µA | RTC-driven |
| STANDBY | 1.0 µA | 32-kHz 16-bit timer + SRAM/registers retained + 32 MHz wake-up in 3.2 µs |
| SHUTDOWN | 61 nA | IO wake-up capability |

## Analog Peripherals

- 1× 12-bit ADC, 1.68 Msps, up to 10 external channels
- Configurable 1.4V or 2.5V internal VREF
- 2× **Zero-drift Zero-crossover Chopper OPA**:
  - 0.5 µV/°C drift with chopping
  - 6-pA input bias current
  - Integrated programmable gain stage (1-32×)
- 1× General-purpose amplifier (GPAMP)
- 1× High-speed comparator (COMP) with 8-bit reference DAC
  - 32 ns propagation delay
  - Low-power mode down to <1 µA
- Programmable analog connections (ADC ↔ OPA ↔ COMP ↔ DAC)
- Integrated temperature sensor

## Digital Peripherals

- 3-channel DMA controller
- 3-channel event fabric signaling system
- 4× 16-bit general-purpose timers with 2 capture/compare each
  - Total 8 PWM channels
  - Operation in STANDBY mode
- Windowed watchdog timer
- **2× UART** (one LIN/IrDA/DALI/Smart Card/Manchester)
- **2× I²C** (one FM+ at 1 Mbit/s; both with SMBus, PMBus)
  - I²C wake-up from STOP
- **1× SPI** (up to 16 Mbit/s)
- **2× GPIO count options:** 13, 20, 24, 28 (across variants)

## Security

- Secure debug

## Package Options

| Pkg. Type | Pins | Size |
|---|---|---|
| SOT-23-THN (DYY) | 16 | 4.2×2 mm (8.4 mm²) |
| VQFN (RGE) | 24 | 4×4 mm (16 mm²) |
| VQFN (RHB) | 32 | 5×5 mm (25 mm²) |
| VSSOP (DGS) | 20 | 5.1×4.9 mm (24.99 mm²) |
| VSSOP (DGS) | 28 | 7.1×4.9 mm (34.79 mm²) |
| WQFN (RTR) | 16 | 2×3 mm (6 mm²) |

## Operating System

- BareMetal (No OS)

## Dev Tools

- **LP-MSPM0L1306** — LaunchPad™
- ALGO-3P-UISP1-TI — µISP1 Programmer (Algocraft)
- DEYAN-3P-MSPM0-KIT — Deyan M0 Eval Board
- GENCN-3P-GCM00L5 — humidity/temp sensor board reference
- TMDSEMU110-U / TMDSEMU200-U — XDS110/XDS200 JTAG Debug Probes
- SEGGR-3P-J-LINK — J-Link family

## Use-Case Tier Hint

- **Battery-powered sensor nodes:** 61 nA SHUTDOWN + 5 lp modes = years of
  battery life on coin cell.
- **Wearables / health patches:** STANDBY 1 µA + 32 kHz wake-up = always-on
  sensing.
- **Industrial sensor (4-20 mA loop):** -40 to +125 °C + 5V-tolerant IO +
  12-bit ADC + zero-drift OPA.

## Application Areas

- Smoke detectors
- Water/gas meters
- Battery management ICs
- Smart locks
- Wearable health patches (CGM, ECG patches)
