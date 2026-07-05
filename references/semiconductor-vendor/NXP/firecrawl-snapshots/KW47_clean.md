# NXP KW47 — Cortex-M33 96 MHz + BLE 6.x Wireless MCU

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/NXP/firecrawl-snapshots/KW47_raw.md`
(66,706 bytes). Captured from `https://www.nxp.com/products/KW47`.

## Family Identity

- **Family:** Kinetis W / MCX W Wireless MCU
- **Marketing tagline:** "Cortex-M33 + dedicated CM33 radio core +
  BLE 6.x upgradeable radio with Channel Sounding"
- **Position:** NXP's flagship BLE 6.x wireless MCU. Replaces KW45 in
  applications needing Channel Sounding (BLE ranging) + 96 MHz app core
  + secure upgradeable software radio.

## Cores (Dual-Core)

### Application Core

- **Arm Cortex-M33** @ up to 96 MHz

### Radio Subsystem

- **Dedicated CM33 core** @ up to 64 MHz
- 512 KB secure Flash (supports upgradable software radio)
- 171 KB SRAM optimized for link layer support
- 2.4 GHz BLE 6.x upgradeable radio

## Memory (Application Core)

- **Program flash:** Up to 2 MB with ECC
- **SRAM:** 264 KB with ECC + parity

## Wireless (BLE 6.x)

### Receive Sensitivity

| Rate | Sensitivity (dBm) |
|---|---|
| 125 kbit/s Long Range | -106 |
| 500 kbit/s Long Range | -102 |
| 1 Mbps | -97.5 |
| 2 Mbps | -95 |

### Transmit

- **Programmable TX power up to +10 dBm**

### Capacity

- Up to **24 simultaneous hardware connections** in any central/peripheral
  combination

### Data Rates / Modulation

- Data rates: 125 kbit/s, 500 kbit/s, 1 Mbps, 2 Mbps
- Modulation: 2-Level FSK, GFSK, MSK, GMSK

### Channel Sounding

- Bluetooth Channel Sounding supported (BLE ranging/HDM)

### RF Front-end

- On-chip balun with single-ended bidirectional RF port

## Peripherals

### Analog

- **16-bit single-ended SAR ADC** up to 2 Msps
- 2× High-speed analog comparators (CMP) with 8-bit DAC
- Voltage Reference: 1.0V to 2.1V

### Timers

- 2× 6-channel 32-bit timers (TPM) with PWM + DMA
- 2× 32-bit low-power timers (LPTMR) / pulse counters with compare
- 4-channel 32-bit low-power periodic interrupt timer (LPIT) with DMA
- 56-bit timestamp timer
- 32-bit seconds RTC with 32-bit alarm + independent power supply
- Signal frequency analyzer (SFA) for clock measurement

## Security

- (Details in raw / datasheet)
- EdgeLock / PSA Level (likely)

## Connectivity

- **FlexCAN** with CAN FD support (increased bandwidth, lower latency)

## Software

- NXP MCUXpresso SDK
- Zephyr, FreeRTOS support (likely)

## Dev Tools

- KW47-EVK (likely; details in raw)
