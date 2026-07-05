# i.MX-RT1160 — Crossover MCU (Dual-Core M7 600 MHz + M4 240 MHz)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/NXP/firecrawl-snapshots/iMX-RT1160_raw.md`
(202,606 bytes). Captured from `https://www.nxp.com/products/i.MX-RT1160`.

## Product Identity

- **Family:** i.MX RT Crossover MCU
- **Marketing tagline:** "i.MX RT1160 Crossover MCU Dual-Core Arm® Cortex®-M7
  and Cortex-M4"
- **Position:** Step-down of i.MX-RT1170 (same M7+M4 heterogeneous cores, lower
  clock + cost). Companion to RT1170 (top tier) and RT1064 (single-core M7).

## Cores (Heterogeneous Multi-Core)

- **Arm Cortex-M7** application core **@ up to 600 MHz**
- **Arm Cortex-M4** real-time / peripheral offload core **@ up to 240 MHz**

## Memory

- **Boot ROM:** 256 KB
- **On-chip RAM:** 1 MB total
  - 512 KB RAM shared with M7 TCM
  - 256 KB RAM shared with M4 TCM
  - Remaining: shared SRAM

## External Memory Interfaces

- **8/16/32-bit SDRAM** (up to SDRAM-133 / SDRAM-166 / SDRAM-200)
- **8/16-bit SLC NAND FLASH**

## Graphics and HMI

- Parallel RGB LCD interface (eLCDIF)
- **Parallel RGB LCD Interface Version 2 (LCDIFv2)**
- **MIPI Display Serial Interface (MIPI DSI)** with integrated PHY
- S/PDIF input and output
- PDM microphone interface (4 pairs of inputs)
- Asynchronous Sample Rate Converter (ASRC)
- **Generic 2D (PXP)**
- Vector Graphics Processing
- Parallel Camera Sensor Interface (CSI)
- **MIPI Camera Serial Interface (MIPI CSI)** with integrated PHY

## Connectivity

- 2× USB 2.0 OTG with integrated PHY
- 2× uSDHC with eMMC 5.0 + SD/SDIO 3.0 compliance
- 1× 10M/100M Ethernet (IEEE 1588 support)
- 1× Gigabit Ethernet (AVB support)
- **12× UART**
- 6× I²C
- 6× SPI
- 3× FlexCAN (with Flexible Data-rate / CAN FD)
- 2× EMV SIM (Europay-Mastercard-Visa SIM modules)

## Analog

- 2× ADC (differential + single-ended)
- 1× DAC
- 4× Analog Comparators (ACMP)

## Security

- (advanced embedded security including secure boot)
- MCUXpresso security provisioning tools

## Software / Ecosystem

- **MCUXpresso developer experience** (IDE, config tools, security
  programming, SDK)
- **Zephyr RTOS support**

## Package

- 289-pin MAPBGA, 14×14 mm, 0.8 mm pitch

## Operating Conditions

- (Industrial temperature range; details in raw)

## Use-Case Tier Hint

- **Cost-down crossover MCU** for industrial HMI applications that don't
  need RT1170's 1 GHz M7 + GbE + larger flash.
- **Edge AI gateway + industrial HMI** with M4 offloading real-time tasks
  while M7 runs application.
- **Replace i.MX RT1064 + RT1170 mid-tier** with cost-down for high-volume
  industrial designs.
