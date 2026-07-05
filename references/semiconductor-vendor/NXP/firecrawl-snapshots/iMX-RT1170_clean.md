# i.MX-RT1170 — Crossover MCU (Dual-Core Cortex-M7 1 GHz + Cortex-M4 400 MHz)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/NXP/firecrawl-snapshots/iMX-RT1170_raw.md`
(307,447 bytes) since `clean_markdown.py` over-strips NXP single-H1 pages.
See `.planning/v0.4.0-resume.md` Gap #1 resolution.

## Product Identity

- **Family:** i.MX RT117x Crossover MCU
- **Marketing tagline:** "6468 CoreMark" dual-core crossover MCU
- **Position:** Top of MCU performance tier in NXP's RT lineup; below MPU.

## Compute (Dual-Core)

- **Cortex-M7 (application core):** 1 GHz, with 512 KB TCM
- **Cortex-M4 (real-time / peripheral offload):** 400 MHz, with 256 KB TCM
- **CoreMark:** 6468 (combined across cores)

## Memory

- **SRAM:** 2 MB total (512 KB TCM for M7 + 256 KB TCM for M4)
- **Flash:** varies by variant (per Buy/Parametrics)

## Connectivity

- 2× Gb Ethernet (ENET) with **AVB and TSN** — automotive audio/video
  networking + time-sensitive industrial
- USB (variants vary)
- Display / Camera: MIPI® CSI / DSI

## Multimedia / HMI

- 2D GPU
- Advanced graphics pipeline (vs RT1064's bare 2D accel engine)

## Security

- Secure boot
- Crypto engines (hardware-accelerated)
- **Part of NXP EdgeLock® Assurance program** — designed to meet
  industry standards + NXP's security-by-design approach. See
  https://www.nxp.com/products/nxp-product-information/nxp-product-programs/edgelock-assurance

## Software / Ecosystem

- **MCUXpresso ecosystem:** IDE choices, pin/clock/peripheral/security/memory
  config tools, security programming/provisioning tools, SDK
- **Zephyr RTOS support** (Zephyr OS for edge-connected devices)

## Related Products (cross-reference)

- **FS26** — Safety System Basis Chip with Low Power, for ASIL D Systems
  (complementary PMIC/system basis)
- **PF9453** — Low Power Multi-Rail PMIC for i.MX 91, i.MX 93 and Simple
  Linux Platforms
- **i.MX-RT1160** — step-down variant in same family (dual-core M7+M4 but
  lower speed / less memory)
- **IW612** — 2.4/5 GHz Dual-Band 1×1 Wi-Fi 6 + Bluetooth 5.4 + 802.15.4
  (companion for wireless)
- **PF5020** — Multi-Channel (5) PMIC for Automotive — 4 High Power + 1 Low
  Power, ASIL B Safety Level

## Applications

### Automotive

- Digital Cluster
- Driver Monitoring Systems (DMS) and Occupant Monitoring Systems
- Heating Ventilation and Air Conditioning (HVAC)

### Consumer

- Air Conditioning (AC)
- Home Appliances System Control
- Major Home Appliances
- Point-of-sales
- Robotic Appliance
- Small and Medium Appliances

### Industrial

- Automatic Vehicle Identification
- Brushless DC Motor (BLDC) Control
- Building Safety Detectors
- Building Security and Surveillance
- Circuit Breaker
- Fleet Management
- General Avionics
- Home Control Panel
- In-Home Energy Display
- Industrial HMI
- Intermediate Flight Controller
- Inventory and Supply Chain Management
- Motor Drives
- POS Terminal
- Power Grid Converter
- Smart Lock
- Smart Power Socket
- Solar Photovoltaic (PV) Energy Generation
- Transport Ticketing
- Vision and Advanced Sensing

## Use-Case Tier Hint

- **Industrial gateway / HMI:** RT1170 + GbE + TSN + MIPI-DSI display is the
  prototypical "gateway with local UI" combo — matches
  `references/application-solution/industrial-gateway/` template.
- **Automotive digital cluster:** RT1170's MIPI-DSI + AVB + EdgeLock
  Assurance maps directly to instrument cluster designs.
