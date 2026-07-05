# ST STM32C091 / STM32C092 — Cortex-M0+ 48 MHz, 256 KB Flash, PSA Level 3

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/ST/firecrawl-snapshots/STM32C091-family_raw.md`
(610,260 bytes). Captured from `https://www.st.com/en/microcontrollers-microprocessors/stm32c091cc.html`.

## Family Identity

- **Family:** STM32C091xB / STM32C092xB (mainstream MCU line)
- **Marketing tagline:** "STM32C091xB/xC STM32C092xB/xC mainstream MCUs,
  high-perf Cortex-M0+ 48 MHz, 256 KB flash, FDCAN (C092)"
- **Position:** ST's mainstream Cortex-M0+ family in the 256 KB flash
  tier — between STM32C011 (entry 32 KB) and STM32G0/G4 (higher tier).

## Core

- **Arm Cortex-M0+ @ up to 48 MHz** (32-bit RISC)
- **MPU** (memory protection unit)

## Memory

- **Flash:** Up to **256 KB** with read + write protection, proprietary
  code protection, securable area
- **SRAM:** Up to **36 KB** with hardware parity check

## Security

- **SESIP3 target**
- **PSA Level 3 target**
- 96-bit unique ID
- Securable memory area
- Proprietary code protection

## Operating Conditions

- **Temperature:** -40 to +85 / +105 / +125 °C
- **Supply voltage:** 2.0 V to 3.6 V

## Power

- Low-power modes: **Sleep, Stop, Standby, Shutdown** (4 modes)
- Power-on / Power-down reset (POR/PDR)
- Programmable brownout reset (BOR)

## Clock

- 4 to 48 MHz crystal oscillator
- 32 kHz crystal oscillator with calibration
- Internal 48 MHz RC oscillator (±1%)
- Internal 32 kHz RC oscillator (±5%)

## I/O

- **Up to 61 fast I/Os**
- All 5V-tolerant
- All mappable on external interrupt vectors

## DMA

- 7-channel DMA controller with flexible mapping

## Analog

- **12-bit ADC, 0.4 µs** (up to 19 external channels)
- Conversion range: 0 to 3.6 V

## Timers

- 10 timers total:
  - 1× 16-bit advanced timer (motor control)
  - 1× 32-bit general-purpose timer
  - 5× 16-bit general-purpose timers
  - 2× watchdog timers (WWDG + IWDG)
  - 1× SysTick timer
- Calendar RTC with alarm

## Communication Interfaces

- **2× I²C** (one supports Fast-mode Plus 1 Mbit/s + extra current sink;
  one supports SMBus/PMBus + wakeup from Stop)
- **4× USARTs** with master/slave synchronous SPI; one supports ISO7816,
  LIN, IrDA, auto baud rate detection, wakeup
- **2× SPIs** (24 Mbit/s, programmable bitframe 4-16 bit); one muxed
  with I²S; four extra SPIs via USARTs
- **1× FDCAN** controller (**STM32C092xx only** — not on C091)

## Debug

- Serial wire debug (SWD)

## Family Members

- **STM32C091** — without FDCAN
- **STM32C092** — with FDCAN

## Variants (per existing STM32C0 family page)

From the STM32C0 series page, variants include:
- STM32C091FCP6 — TSSOP20
- STM32C091CCT6 — LQFP/UFQFPN48
- STM32C091RCT6 — LQFP/UFBGA64

## Use-Case Tier Hint

- **Mainstream consumer / industrial / appliance MCU** with strong
  security posture (SESIP3 + PSA Level 3).
- **Smart home / IoT** secure end nodes needing PSA L3 certified device.
- **STM32C092 with FDCAN** for industrial control / CAN nodes; falls
  between STM32C0 (entry) and STM32G4 (mid) in capability.

## Family Position

- **STM32C091** — Cortex-M0+ 48 MHz, 256 KB flash, PSA Level 3
- **STM32C092** — same as C091 + FDCAN
- STM32C011/C031/C051/C071 — smaller flash (≤128 KB) without PSA L3 target
- STM32G0 (existing yaml) — Cortex-M0+ 64 MHz, more peripherals, no PSA L3

## Application Areas

- Smart home / IoT secure end nodes
- Industrial control nodes (with FDCAN for C092)
- Home appliances
- USB peripherals
- Secure sensor hubs
- Smart energy / metering (with PSA L3 certification)
