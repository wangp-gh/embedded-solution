# TI MSPM0G3519 — 80 MHz Cortex-M0+ MCU with 2× CAN-FD + PSA-L1

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/TI/firecrawl-snapshots/MSPM0G3519-family_raw.md`
(295,609 bytes). Captured from `https://www.ti.com/product/MSPM0G3519`.

## Family Identity

- **Family:** MSPM0G (high-performance Cortex-M0+ tier with advanced
  peripherals)
- **Marketing tagline:** "80 MHz ARM® Cortex®-M0+ MCU with dual-bank 512 kB
  flash, 128 kB SRAM, 2× CAN-FD, 2× ADC, DAC, COMP"
- **Position:** Top-tier MSPM0 platform. Companion to MSPM0G3507 (existing
  yaml) and MSPM0L1306/L1106 (low-power tier).
- **PSA-L1 Certification targeted**

## Core

- **Arm Cortex-M0+ @ 80 MHz** (with MPU)
- **Math accelerator** (DIV, SQRT, MAC, TRIG)

## Memory

- **Flash:** 512 KB with ECC, dual-bank with address swap (OTA updates)
- **Data flash:** 16 KB with ECC
- **SRAM total:** 128 KB
  - Bank 0: 64 KB with ECC or hardware parity, retention in STANDBY
  - Bank 1: 64 KB, retention in STOP

## Operating Conditions

- **Temperature:** -40 to +125 °C
- **Supply:** 1.62V to 3.6V

## Analog

- **2× simultaneous sampling 12-bit 4 Msps ADC** (up to 27 external channels)
  - 14-bit effective resolution at 250 ksps (hardware averaging)
- **3× high-speed comparators (COMP)** with 8-bit ref DAC
  - 32 ns propagation delay (high-speed mode)
  - <1 µA low-power mode
- **1× 12-bit 1 Msps DAC** with output buffer
- Programmable analog routing (ADC ↔ COMP ↔ DAC)
- Configurable 1.4V / 2.5V internal VREF
- Integrated temperature sensor

## Power (5 Low-Power Modes)

| Mode | Current |
|---|---|
| RUN (CoreMark) | 123 µA/MHz |
| SLEEP | 38 µA/MHz |
| STOP @ 4 MHz | 223 µA |
| STANDBY @ 32 kHz | 1.7 µA (RTC + Bank 0 SRAM + state retention) |
| SHUTDOWN | 92 nA (IO wake-up) |

## Digital

- **12-channel DMA controller**
- 9× timers (up to 28 PWM channels)
  - 2× 16-bit GP with QEI
  - 4× 16-bit GP with STANDBY-capable operation
  - 1× 32-bit GP
  - 2× 16-bit advanced with deadband + complementary outputs (12 PWM channels)
- 2× Windowed Watchdog + 1× Independent Watchdog
- RTC with alarm + calendar mode

## Communication

- **7× UART**
  - 2 supporting LIN/IrDA/DALI/Smart Card/Manchester
  - 3 supporting STANDBY operation
- **3× I²C** (FM+ 1 Mbit/s, SMBus, PMBus, wakeup from STOP)
- **3× SPI** (1× up to 32 Mbit/s)
- **2× CAN-FD** (CAN 2.0A/B + CAN-FD)

## Clock System

- Internal 4-32 MHz oscillator (SYSOSC), ±1.2% accuracy
- **PLL up to 80 MHz**
- Internal 32 kHz LFOSC, ±3% accuracy
- External 4-48 MHz crystal (HFXT)
- External 32 kHz crystal (LFXT)
- External clock input

## Security

- **AES-128/256 accelerator** with GCM/GMAC, CCM/CBC-MAC, CBC, CTR
- Secure key storage (up to 4 AES keys)
- Flexible firewalls (code + data protection)
- **True Random Number Generator (TRNG)**
- CRC-16 / CRC-32

## I/O

- **94 GPIOs**
- 2× 5V-tolerant open-drain IOs
- 3× high-drive IOs (20 mA)
- 4× high-speed IOs

## Debug

- 2-pin Serial Wire Debug (SWD)

## Package Options

- 100-pin nFBGA (ZAW) — 0.8 mm pitch
- 100-pin LQFP (PZ) — 0.5 mm pitch
- 80-pin LQFP (PN) — 0.5 mm pitch
- 64-pin LQFP (PM) — 0.5 mm pitch
- 48-pin LQFP (PT) — 0.5 mm pitch
- 48-pin VQFN (RGZ) — 0.5 mm pitch
- 32-pin VQFN (RHB) — 0.5 mm pitch

## Dev Tools

- **LP-MSPM0G3519** LaunchPad™ dev kit
- ALGO-3P-UISP1-TI Programmer
- TMDSEMU110-U / TMDSEMU200-U JTAG Debug Probes

## Use-Case Tier Hint

- **Industrial sensor hub** with CAN-FD + 80 MHz + 128 KB SRAM + 92 nA
  SHUTDOWN.
- **Battery-powered automotive sensor nodes** (PSA-L1 targeted, ASIL-B
  capable via firmware + companion PMIC).
- **Home/Building automation** with dual CAN-FD for HVAC + sensors.
- **Motor control** with advanced timers (deadband + complementary outputs)
  + math accelerator for FOC.

## Application Areas

- Industrial nodes / supervisory / edge PLCs
- Building automation (HVAC controllers)
- Battery-powered industrial IoT
- CAN-FD backbone nodes
- Motor control (with FOC firmware)
- Smart home gateways
