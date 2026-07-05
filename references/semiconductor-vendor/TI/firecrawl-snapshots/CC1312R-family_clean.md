# TI CC1312R — SimpleLink Sub-1 GHz Wireless MCU (Ultra-Low Power)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/TI/firecrawl-snapshots/CC1312R-family_raw.md`
(284,613 bytes). Captured from `https://www.ti.com/product/CC1312R`.

## Family Identity

- **Family:** SimpleLink™ Sub-1 GHz Wireless
- **Marketing tagline:** "SimpleLink™ 32-bit Arm Cortex-M4F Sub-1 GHz
  wireless MCU with 352 kB Flash"
- **Position:** TI flagship Sub-1 GHz-only wireless MCU with deep-sleep
  150 nA. Companion to CC1352P (multi-band Sub-1 + 2.4 GHz + PA) and
  CC1310 (older, smaller flash).

## Core

- **Arm Cortex-M4F @ 48 MHz** (with FPU)
- EEMBC CoreMark: 148

## Memory

- **Flash:** 352 KB (in-system programmable)
- **ROM:** 256 KB (protocols + library)
- **Cache SRAM:** 8 KB (or general-purpose)
- **SRAM:** 80 KB ultra-low leakage (parity protected)
- **Sensor Controller SRAM:** 4 KB (independent of main CPU)

## Wireless (Sub-1 GHz Only)

### Frequency Bands

- **1076-1315 MHz** (Europe Sub-1 GHz)
- **143-176, 287-351, 359-439, 431-527 MHz** (Lower band — global)
- **861-1054 MHz** (Japan/Australia)

### Modulation

- (G)MSK, 2(G)FSK, 4(G)FSK, ASK, OOK

### Sensitivity

- **-121 dBm** (SimpleLink long-range mode)
- -110 dBm at 50 kbps
- "Best in class" — for km-range Sub-1 GHz

### Output Power

- **+14 dBm** (with temperature compensation)

### Protocols (in ROM)

- IEEE 802.15.4g
- 6LoWPAN
- MIOTY
- Wireless M-Bus
- **Wi-SUN**
- KNX RF
- Amazon Sidewalk
- Proprietary systems
- SimpleLink™ TI 15.4 stack (Sub-1 GHz)
- Dynamic multiprotocol manager (DMM) driver

### Regulatory Compliance

- ETSI EN 300 220 Receiver Category 1.5 and 2
- EN 303 131, EN 303 204 (Europe)
- FCC CFR47 Part 15
- ARIB STD-T108

## Peripherals

- **30 GPIOs**
- 4× 32-bit / 8× 16-bit GP timers
- **12-bit ADC, 200 kSamples/s, 8 channels**
- 2× comparators with internal ref DAC (1× continuous time, 1× ultra-low
  power)
- Programmable current source
- 2× UART, 2× SSI (SPI, MICROWIRE, TI), I²C, I²S
- RTC, 8-bit DAC
- Capacitive sensing up to 8 channels
- Integrated temp + battery monitor

## Security

- Secure Boot, Secure Debug, Secure Firmware/Software Update (OTA)
- Device attestation + anti-counterfeit
- AES 128/256, ECC, RSA, SHA-2 (up to SHA-512), TRNG

## Power (Ultra-Low-Power Class-Leading)

- **Supply voltage:** 1.8V to 3.8V (wide range)
- **Active RX:** 5.8 mA (3.6V, 868 MHz)
- **Active TX +14 dBm:** 24.9 mA (868 MHz)
- **Active MCU @ 48 MHz (CoreMark):** 2.9 mA (60 µA/MHz)
- **Sensor controller, 2 MHz, infinite loop:** 30.1 µA
- **Sensor controller, 24 MHz, infinite loop:** 808 µA
- **Standby:** 0.85 µA (RTC on, 80 KB RAM + CPU retention)
- **Shutdown:** **150 nA** (wakeup on external events)

## External System

- On-chip buck DC/DC converter
- TCXO support

## Package

- **VQFN (RGZ)** — 48 pins, 7×7 mm, 49 mm² (30 GPIOs)
- RoHS-compliant

## Dev Tools

- CC1312R LaunchPad™ Development Kit
- SimpleLink™ CC13x2 and CC26x2 SDK
- SmartRF™ Studio (radio config)
- Sensor Controller Studio (low-power sensing apps)

## Use-Case Tier Hint

- **Long-range Sub-1 GHz sensor networks** (km range via +14 dBm + -121 dBm
  sensitivity). 150 nA SHUTDOWN = multi-year battery life on coin cell.
- **Smart metering (Wi-SUN)** for utility-grade mesh networks.
- **KNX RF** wireless building automation.
- **Amazon Sidewalk** low-bandwidth IoT bridge.
- **Sub-1 GHz proprietary** industrial wireless protocols (Wireless M-Bus,
  MIOTY).

## Application Areas

- AMI / smart meter / utility monitoring
- Building automation (KNX RF, wireless HVAC sensors)
- Long-range IoT sensor nodes (precision agriculture, oil/gas)
- Wireless alarm systems (PIR door sensors, smoke)
- Asset tracking with Wi-SUN mesh
