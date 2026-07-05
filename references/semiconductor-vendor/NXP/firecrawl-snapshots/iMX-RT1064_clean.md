# i.MX-RT1064 — Crossover MCU (Arm Cortex-M7 @ up to 600 MHz)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/NXP/firecrawl-snapshots/iMX-RT1064_raw.md`
(173,833 bytes) since `clean_markdown.py` over-strips NXP single-H1 pages.
See `.planning/v0.4.0-resume.md` Gap #1 resolution.

## Product Identity

- **Family:** i.MX RT106x Crossover MCU
- **Marketing tagline:** "Highest performing Arm Cortex-M7"
- **Position:** Cost-down crossover MCU between LPC546xx and i.MX RT1170;
  edge of MCU + entry of MPU in performance/capability.

## Performance

- **Core:** Arm Cortex-M7 (single core)
- **Max frequency:** 600 MHz
- **CoreMark:** 3020 / DMIPS 1284 @ 600 MHz
- **Real-time response:** as low as 20 ns
- **Low-power run modes:** 24 MHz

## Memory

- **SRAM:** 1 MB on-chip (up to 512 KB configurable as TCM)
- **Flash:** 4 MB on-chip (per Buy/Parametrics table across all variants)

## Multimedia / HMI

- 2D graphics acceleration engine
- Parallel camera sensor interface
- LCD display controller (up to WXGA 1366×768)
- 3× I²S for high-performance multi-channel audio

## External Memory Interface

- NAND, eMMC, QuadSPI NOR Flash, Parallel NOR Flash

## Wireless (via companion ICs)

- Wi-Fi® (via companion IC, e.g. IW612)
- Bluetooth® / Bluetooth Low Energy
- ZigBee® and Thread™

## Software / Ecosystem

- **MCUXpresso suite:** IDE choices, pin/clock/peripheral/security/memory
  config tools, security programming/provisioning tools, SDK
- **Zephyr RTOS support** (Zephyr OS for edge-connected devices)

## Power

- Integrated DC-DC converter ("industry's lowest dynamic power")
- Low-power run modes down to 24 MHz

## Buy/Parametrics — Part Variants

All variants: Arm Cortex-M7 single core, 4000 kB flash, 1024 kB SRAM,
2× CAN, 4× I²C, 8× UART, 2× USB controllers, JTAG debug, LFBGA196 package.

| Part | Speed | Temperature | Pitch |
|---|---|---|---|
| MIMXRT1064CVJ5B | 528 MHz | -40 to +105 °C | 0.8 mm |
| MIMXRT1064CVL5B | 528 MHz | -40 to +105 °C | 0.65 mm |
| MIMXRT1064DVJ6B | 600 MHz | 0 to +95 °C | 0.8 mm |
| MIMXRT1064DVL6B | 600 MHz | 0 to +95 °C | 0.65 mm |

## Related Products (cross-reference)

- **IW612** — 2.4/5 GHz Dual-Band 1×1 Wi-Fi 6 + Bluetooth 5.4 +
  802.15.4 Tri-Radio (companion for wireless)
- **i.MX-RT1040** — entry-level sibling (lower frequency)
- **i.MX-RT1050** — previous generation
- **i.MX-RT1060** — slightly older variant

## Applications

### Automotive

- Heating Ventilation and Air Conditioning (HVAC)
- Motorcycle ECU / Small Engine Control

### Consumer

- Air Conditioning (AC)
- Hearables
- Major Home Appliances
- Robotic Appliance
- Small and Medium Appliances
- Smart Watch and Wristband

### Industrial

- Automatic Vehicle Identification
- Building Energy Management Controller
- Building Safety Detectors
- Building Security and Surveillance
- Circuit Breaker
- Electricity Metering
- Fleet Management
- General Avionics
- Home Control Panel
- In-Home Energy Display
- Industrial HMI
- Intermediate Flight Controller
- Inventory and Supply Chain Management
- Motion Control and Robotics
- Smart Lighting
- Smart Power Socket
- Solar Photovoltaic (PV) Energy Generation
- Transport Ticketing
