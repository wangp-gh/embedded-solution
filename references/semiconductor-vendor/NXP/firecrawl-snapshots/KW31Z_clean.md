# NXP Kinetis KW31Z — Cortex-M0+ BLE 4.2 Wireless MCU

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/NXP/firecrawl-snapshots/KW31Z_raw.md`
(78,192 bytes). Captured from `https://www.nxp.com/products/KW31Z`.

## Family Identity

- **Family:** Kinetis® W Series
- **Marketing tagline:** "Cortex-M0+ Wireless MCU with Bluetooth Low Energy v4.2"
- **Position:** NXP cost-effective BLE 4.2-only MCU; sister to KW41Z (BLE + 802.15.4)
  and KW45 (BLE 5 + 802.15.4 LE).

## Wireless (BLE)

- **Bluetooth Low Energy 4.2** compliant
- Receiver Sensitivity (BLE) = -95 dBm typical
- TX power up to +3.5 dBm (programmable)
- Excellent coexistence performance

## Core

- **Arm Cortex-M0+ @ up to 48 MHz**
- Integrated balun (reduces BOM + PCB area)

## Memory

- **Up to 512 KB Flash**
- **Up to 128 KB SRAM**

## Power

- **Nine low-power modes**
- **Rx/Tx current (DC/DC):** 6.5 mA / 8.4 mA
- **Bypass voltage:** 1.71V to 3.6V
- **Buck DC/DC:** 2.1V to 4.2V
- **Boost DC/DC:** 0.9V to 1.795V

## Analog Modules

- **16-bit ADC**
- **12-bit DAC**
- **6-bit high-speed Analog Comparator (CMP)**

## Security

- **AES-128 Accelerator (AESA)**
- **True Random Number Generator (TRNG)**

## Software

- BLE Host Stack + Profiles
- Generic FSK Link Layer Software (for proprietary 2.4 GHz)
- Kinetis® SDK
- FreeRTOS kernel + bare-metal non-preemptive task scheduler
- IDE: MCUXpresso, IAR

## Part Variants

| Part | Wireless | Memory | Package |
|---|---|---|---|
| **MKW31Z512VHT4** | BLE | 512 KB Flash, 128 KB RAM | 7×7×1 mm, 48-pin Laminate QFN |
| **MKW31Z256VHT4** | BLE | 256 KB Flash, 64 KB SRAM | same QFN |
| **MKW31Z512CAT4R** | BLE | 512 KB Flash, 128 KB RAM | 3.9×3.8 mm, 75-pin WLCSP |

## Related Products (Kinetis W family)

- **KW41Z** — BLE + IEEE 802.15.4 (Thread + Zigbee)
- **KW45** — BLE 5 + 802.15.4 (already verified in yaml set)

## Use-Case Tier Hint

- Cost-effective BLE-only design (vs KW41Z for protocols needing 802.15.4)
- Asset tracking, BLE beacon, simple wearable, small home automation device
