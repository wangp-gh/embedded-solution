# GigaDevice GD32W515 Series — Cortex-M33 180 MHz + Wi-Fi 4 SoC

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/GigaDevice/firecrawl-snapshots/GD32W515-family_raw.md`
(64,242 bytes). Captured from `https://www.gigadevice.com/product/mcu/wireless-mcus/gd32w515-series`.

## Family Identity

- **Family:** GD32W515 (GigaDevice wireless MCU series)
- **Core:** Arm Cortex-M33 with TrustZone
- **Position:** Cost-effective Wi-Fi 4 (802.11 b/g/n) MCU. Domestic (China)
  alternative to TI CC3135 / NXP IW612 in cost-sensitive Wi-Fi IoT designs.

## Performance

- **Cortex-M33 @ up to 180 MHz**
- Wi-Fi 4 (802.11 b/g/n), single-stream 2.4 GHz
- **Maximum transmit power:** up to **+21 dBm**
- **Receiver sensitivity:** -97.6 dBm
- **Total link budget:** **118.6 dBm**
- Adjacent Channel Rejection (ACR) up to **48 dB**
- **Throughput:** up to 50 Mbps (iperf); up to 80 Mbps (lab conditions)
- Fully integrated RF (reduces external component count, lowers BOM)

## Memory

- **Flash options:** 0 KB / 1024 KB / 2048 KB
- **SRAM:** 384 KB or 448 KB
- **External Flash support:** up to **32 MB**

## Power

- Wide operating voltage: **1.6V to 3.6V**
- I/O pins 5V tolerant

## Peripherals (typical across series)

- 12-bit ADC: 1 unit × 5-9 channels (variant)
- USB 2.0 FS OTG
- SDIO × 1
- Ethernet: 0 (No)
- SPI × 2, QSPI × 1
- I²S × 2
- USART + UART: 3 + 0
- LPUART: 0
- I²C × 2
- GPTM 32-bit: 2
- GPTM 16-bit: 3-4 (variant)
- Advanced TM 16-bit: 1
- LPTM 32-bit: 1
- SysTick 24-bit: 1
- WDG × 2
- RTC × 1
- CAN 2.0B × 1
- COMP × 1
- LIN × 1
- SENT × 0
- IPA / SAI / TMU / EXMC / CEC: not in this series

## Operating Conditions

- **Temperature:** -40 to +85 °C (industrial)

## Security

- **TrustZone** for Cortex-M33 isolation
- Security module (details in raw)

## Package / Variant Table

| Part | Core | Package | Flash | SRAM | I/O |
|---|---|---|---|---|---|
| GD32W515PIQ6 | Cortex-M33 | QFN56 | 2048 KB | 448 KB | up to 43 |
| GD32W515P0Q6 | Cortex-M33 | QFN56 | 0 KB (external flash only) | 448 KB | up to 43 |
| GD32W515TIQ6 | Cortex-M33 | QFN36 | 2048 KB | 448 KB | up to 25 |
| GD32W515TGQ6 | Cortex-M33 | QFN36 | 1024 KB | 384 KB | up to 25 |

## Documentation

- Datasheet
- User Manual
- Application Note
- Firmware Library

## Use-Case Tier Hint

- **Cost-sensitive Wi-Fi 4 IoT:** smart home lighting/switches, basic Wi-Fi
  sensor nodes. 100% domestic-China supply (no NXP / TI stock risk).
- **Industrial Wi-Fi 4 sensor with 32 MB external flash:** asset tracker
  with large local buffer for offline cache.
- **Replacement for TI CC3135 + external MCU combo** in some applications.

## Cross-Reference

- **vs TI CC3135 (substitution?):** CC3135 is a network processor (companion
  to host MCU); GD32W515 integrates MCU + Wi-Fi on one chip.
- **vs TI CC2640R2F + external Wi-Fi:** not exactly; GD32W515 has Wi-Fi + BLE-grade
  -no BLE yet (need GD32W515 BLE addition in future variants).

## Application Areas

- Wi-Fi IoT (smart home, lighting, switches)
- Industrial Wi-Fi sensor nodes (PLC, factory)
- Asset tracking (large external flash support)
- Domestic-China replacement for NXP / TI Wi-Fi 4 designs
