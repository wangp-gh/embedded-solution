# TI CC2642R — SimpleLink 32-bit Cortex-M4F BLE 5.2 Wireless MCU

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/TI/firecrawl-snapshots/CC2642R-family_raw.md`
(295,261 bytes). Captured from `https://www.ti.com/product/CC2642R`.

## Family Identity

- **Family:** SimpleLink™ CC26x2/CC13x2 multiprotocol wireless
- **Marketing tagline:** "SimpleLink™ 32-bit Arm Cortex-M4F Bluetooth® Low
  Energy wireless MCU with 352 kB Flash"
- **Position:** BLE 5.2 (5.x) flagship in TI's CC264x lineage. Sister to
  CC2640R2F (older, 128 KB flash) and CC2652R (multi-protocol + Zigbee).

## Core

- **Arm Cortex-M4F @ 48 MHz** (with FPU)
- EEMBC CoreMark: 148

## Memory

- **Flash:** 352 KB (in-system programmable)
- **ROM:** 256 KB (BLE 5.2 LE controller + drivers + bootloader in ROM)
- **Cache SRAM:** 8 KB (or general-purpose)
- **SRAM:** 80 KB ultra-low leakage (parity protected)
- **Sensor Controller SRAM:** 4 KB (independent of main CPU)

## Wireless (BLE 5.2 only)

### Radio

- **2.4 GHz RF transceiver**, Bluetooth 5.2 LE compatible
- 3-wire / 2-wire / 1-wire PTA coexistence mechanisms
- **Receiver sensitivity:**
  - -105 dBm for BLE 125 kbps (LE Coded PHY)
  - -97 dBm for 1 Mbps PHY
- **Output power:** up to **+5 dBm** (with temperature compensation)

### Regulatory Compliance

- EN 300 328 (Europe)
- EN 300 440 Category 2
- FCC CFR47 Part 15
- ARIB STD-T66 (Japan)

### Wireless Protocol

- Bluetooth Low Energy 5.2 + earlier LE specifications

## Peripherals

- 31 GPIOs
- 4× 32-bit / 8× 16-bit GP timers
- 12-bit ADC, 200 kSamples/s, 8 channels
- 2× comparators (1× continuous, 1× ultra-low power, internal ref DAC)
- Programmable current source
- 2× UART, 2× SSI (SPI, MICROWIRE, TI), I²C, I²S
- RTC, 8-bit DAC
- Capacitive sensing (up to 8 channels)
- Integrated temp + battery monitor

## Security

- Cryptographic acceleration
- Device attestation + anti-counterfeit
- **Secure Debug**
- Software IP protection
- AES 128/256, ECC, RSA, SHA-2 (up to SHA-512), TRNG

## Power

- **Active mode RX:** 6.9 mA
- **Active mode TX 0 dBm:** 7.0 mA
- **Active mode TX 5 dBm:** 9.2 mA
- **Active MCU 48 MHz (CoreMark):** 3.4 mA (71 µA/MHz)
- Sensor controller, 2 MHz, infinite loop: 30.1 µA
- Sensor controller, 24 MHz, infinite loop: 808 µA
- **Standby:** 0.94 µA (RTC on, 80 KB RAM + CPU retention)
- **Shutdown:** 150 nA (wakeup on external events)

## External System

- On-chip buck DC/DC converter

## OS

- TI-RTOS (drivers + bootloader + BLE 5.2 controller in ROM)
- FreeRTOS

## Package

- **VQFN (RGZ)** — 48 pins, 7×7 mm (49 mm²), 31 GPIOs
- RoHS-compliant

## Debug

- 2-pin cJTAG + JTAG
- OTA firmware update support

## Dev Tools

- **CC26x2R LaunchPad™ Development Kit**
- SimpleLink™ LOWPOWER F2 SDK
- SmartRF™ Studio (radio config)
- Sensor Controller Studio (low-power sensing)

## Use-Case Tier Hint

- **Premium BLE peripheral** with long battery life (150 nA shutdown,
  0.94 µA standby): wearable fitness/health tracker, BLE audio, smart lock,
  asset tracker, smart sensor node.
- **Direction finding** (AoA/AoD) enabled — for indoor positioning with
  BLE 5.1+.

## Application Areas

- Fitness / wearable / health (CGM, ECG patches)
- Smart locks, smart home sensors
- BLE beacons + direction finding (indoor positioning)
- Wireless audio (BLE 5.2 LE Audio capable)
- Industrial wireless sensors
- Outdoor asset tracking (BLE with Channel Sounding)
