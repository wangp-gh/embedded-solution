# TI CC1352P — SimpleLink Multi-Protocol Sub-1 GHz & 2.4 GHz MCU + Integrated PA

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/TI/firecrawl-snapshots/CC1352P-family_raw.md`
(302,015 bytes). Captured from `https://www.ti.com/product/CC1352P`.

## Family Identity

- **Family:** SimpleLink™ Multi-Protocol Wireless
- **Marketing tagline:** "SimpleLink™ Arm Cortex-M4F multiprotocol Sub-1 GHz
  & 2.4 GHz wireless MCU integrated power amplifier"
- **Position:** TI's flagship multi-band wireless MCU. Companion to CC2642/CC1352
  without integrated PA, and CC2340R (2.4 GHz only).

## Core

- **Arm Cortex-M4F @ 48 MHz** (with FPU)
- EEMBC CoreMark score: 148
- 2-pin cJTAG + JTAG debug

## Memory

- **Flash:** 352 KB (in-system programmable)
- **ROM:** 256 KB (protocols + library)
- **Cache SRAM:** 8 KB (or general-purpose)
- **SRAM:** 80 KB ultra-low leakage (parity protected)
- **Sensor Controller SRAM:** 4 KB (independent of main CPU)

## Wireless Capabilities

### Sub-1 GHz

- **Frequency bands:** 1069-1329 MHz, 861-1054 MHz, 431-527 MHz
- Modulation: (G)MSK, 2(G)FSK, 4(G)FSK, ASK, OOK
- **Sensitivity:** **-121 dBm (best)**
- **TX power max:** **+20 dBm** (integrated PA)

### 2.4 GHz

- **Frequency band:** 2360-2500 MHz
- Bluetooth 5.2 Low Energy (LE)
- IEEE 802.15.4 (Thread/Zigbee)
- BLE + 802.15.4 simultaneous

### Protocols Supported (in ROM)

- 6LoWPAN
- Amazon Sidewalk
- Bluetooth Low Energy 5.2
- IEEE 802.15.4
- MIOTY
- Matter
- Proprietary
- Thread
- Wi-SUN
- Wireless M-Bus
- Zigbee

## Security

- Cryptographic acceleration
- Device attestation + anti-counterfeit
- **Secure Boot**, **Secure Debug**
- **Secure Firmware & Software Update** (over-the-air)
- Crypto accelerators: **AES (128/256), ECC, RSA, SHA-2 (up to SHA-512), TRNG**

## Peripherals

- **12-bit ADC** (200 kSamples/s, 8 channels)
- 2× comparators with internal reference DAC (1× continuous time, 1× ultra-low power)
- Programmable current source
- 4× 32-bit / 8× 16-bit general-purpose timers
- **2× UART**, **2× SSI** (SPI, MICROWIRE, TI)
- **I²C, I²S**
- Real-time clock (RTC)
- 8-bit DAC
- Capacitive sensing (up to 8 channels)
- Integrated temperature and battery monitor
- **26 GPIOs** (digital peripherals can be routed to any GPIO)

## Ultra-Low Power Sensor Controller

- Independent sample-store-process from main CPU
- 4 KB SRAM
- Fast wake-up for low-power operation

## OS / Software

- TI-RTOS, drivers, bootloader, BLE 5.2 controller, IEEE 802.15.4 MAC (in ROM)
- FreeRTOS, RTOS support

## Operating Conditions

- **Temperature:** -40 to +85 °C
- **Rating:** Catalog

## Package

- **VQFN (RGZ)** — 48 pins, **7×7 mm** (49 mm², 26 GPIOs)
- RoHS-compliant

## Dev Tools

- **LAUNCHXL-CC1352P** — LaunchPad™ development kit for multi-band wireless

## Use-Case Tier Hint

- **Long-range wireless sensor (Sub-1 GHz + 2.4 GHz combo):**
  -121 dBm sensitivity + 20 dBm TX = several km range with proper antenna.
- **Matter over Thread, Wi-SUN, Amazon Sidewalk gateways** for smart metering /
  asset tracking.
- **Multi-band proprietary** for industrial protocols (Wireless M-Bus, MIOTY).

## Application Areas

- Smart metering (Wi-SUN)
- Asset tracking (Amazon Sidewalk)
- Building automation (Matter + Thread/Zigbee)
- Industrial IoT (Wirelss M-Bus, MIOTY)
