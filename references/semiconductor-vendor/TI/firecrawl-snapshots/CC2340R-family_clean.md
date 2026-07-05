# TI CC2340R5 Family — SimpleLink™ 2.4 GHz Wireless MCU

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/TI/firecrawl-snapshots/CC2340R-family_raw.md`
(251,842 bytes). Captured from `https://www.ti.com/product/CC2340R5`.

## Family Overview

- **Family:** CC2340R SimpleLink™ 2.4-GHz Wireless MCUs
- **Marketing tagline:** "SimpleLink™ 32-bit Arm® Cortex®-M0+ 2.4 GHz
  wireless MCU with 512 kB flash"
- **Position:** Low-power multi-standard wireless MCU family for BLE 5.3/5.4,
  Zigbee, Thread, and proprietary 2.4 GHz. Replaces CC2642/CC2640 in
  cost-sensitive apps.

## Core

- **CPU:** Arm® Cortex®-M0+ @ up to 48 MHz optimized
- 12 KB ROM for bootloader and drivers

## Memory

- **Flash:** 512 KB in-system programmable
- **SRAM:** 36 or 64 KB ultra-low leakage (full RAM retention in standby)

## Wireless Protocol Support

- **Bluetooth LE 5.4** (qualified)
  - LE 2M, LE Coded S2/S8, Periodic Advertising, Extended Advertising,
    LE Secure Connections
- **Zigbee®** (R23 plan from TI), **Zigbee 3.0**
- **Thread** (1.x)
- **Proprietary 2.4 GHz**

## Radio Performance

- Output power up to **+8 dBm** (temperature compensated)
- RX sensitivity:
  - -102 dBm for BLE Coded 125 kbps (PHY)
  - -96.5 dBm for BLE 1 Mbps
  - -98 dBm for IEEE 802.15.4 (2.4 GHz)
- Integrated balun
- Supports OTA firmware upgrade

## Power Consumption

- MCU active: 2.6 mA running CoreMark; 53 µA/MHz
- Standby: <710 nA
- Shutdown: 165 nA (wake-up on pin)
- Radio:
  - RX: 5.3 mA
  - TX at 0 dBm: 5.1 mA
  - TX at +8 dBm: <11.0 mA

## MCU Peripherals

- Up to 26 I/O pads (22 DIOs, SWD/LFXT muxed)
- Up to 3× 16-bit + 1× 24-bit general-purpose timers (quadrature decode + IR)
- 12-bit ADC, 1.2 Msps (ext ref), 267 ksps (int ref), up to 12 ext inputs
- 1× low-power comparator
- 1× UART, 1× SPI, 1× I²C
- Real-time clock (RTC)
- Integrated temperature + battery monitor
- Watchdog timer

## Security

- AES 128-bit cryptographic accelerator
- True Random Number Generator (TRNG)
- Cryptographic accelerators: AES, RNG
- OTA upgrade support

## Operating Conditions

- Temperature: -40 to +125 °C
- Voltage: not stated in fetched spec block (assumed 1.8-3.6 V typical)

## Package Options (CC2340R5)

| Package | Pins | Size |
|---|---|---|
| DSBGA (YBG) | 28 | 2.806×1.606 mm (4.5064 mm²) |
| VQFN (RGE) | 24 | 4×4 mm (16 mm²) |
| VQFN (RKP) | 40 | 5×5 mm (25 mm²) |

## Family Members

| Part | RAM | GPIOs | Notes |
|---|---|---|---|
| CC2340R5 | 36/64 KB | up to 26 | Flagship 512 KB flash |
| CC2340R52 | 36/64 KB | up to 26 | Lower-power standby variant |
| CC2340R53 | 36/64 KB | up to 26 | Higher TX power/variant |
| CC2340R53P | 36/64 KB | up to 26 | P suffix (different pinout/sw package) |
| LP-EM-CC2340R5 | — | — | LaunchPad™ dev kit |
| LP-EM-CC2340R53 | — | — | LaunchPad™ dev kit for multi-standard |

## Regulatory Compliance

Suitable for systems targeting:
- EN 300 328 (Europe)
- FCC CFR47 Part 15
- ARIB STD-T66 (Japan)

## OS Support

- FreeRTOS
- Zephyr RTOS

## Modules & Tools (mentioned)

- DREAM-3P-CC2340 (DreamLNK Bluetooth module)
- BDE-3P-LE2340 (BDE wireless module)
- TTC-3P-BLE-CGM-SIP (BLE CGM SiP)
- TTC-3P-BLE-SIP-MODULE (ultra-small SiP)
- TUYA-3P-WIRELESS-MODULES (Tuya BDU module for CC2340R5)
- RFSTAR-3P-CC2340R5-BLE-MOD (BT LE + Zigbee module)

## Use-Case Tier Hint

- **Fitness / wearable / sensor:** BTV-3P-FMC (M0 self-powered control) +
  CC2340R2 EnergyTrace → Application includes home fitness machines,
  continuous glucose monitors (CGM), BLE beacons, asset trackers.
