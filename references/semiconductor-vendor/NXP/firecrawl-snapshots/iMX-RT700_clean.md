# i.MX-RT700 — Crossover MCU (Multi-Core M33 + HiFi DSP + NPU)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/NXP/firecrawl-snapshots/iMX-RT700_raw.md`
(105,972 bytes). Captured from `https://www.nxp.com/products/i.MX-RT700`.

## Product Identity

- **Family:** i.MX RT Crossover MCU
- **Marketing tagline:** "Arm Cortex-M33 + HiFi 4 DSP + eIQ Neutron NPU"
- **Position:** Performance-leading crossover MCU for AI/ML edge inference +
  audio + graphics in wearable, smart home, industrial.

## Core Platform

### Main Compute Subsystem (up to 325 MHz)
- **Arm Cortex-M33** @ up to 325 MHz (application)
- **HiFi 4 DSP** @ up to 325 MHz (audio + signal)
- **eIQ Neutron NPU** @ up to 325 MHz (edge AI)

### Sense Compute Subsystem (up to 250 MHz)
- **Arm Cortex-M33** @ up to 250 MHz
- **HiFi 1 DSP** @ up to 250 MHz

## Memory

- **7.5 MB on-chip SRAM**
- 3× xSPI interfaces for off-chip memory expansion
- Up to 16-bit wide external memories @ up to 250 MHz DDR

## Peripherals

- **eUSB** support with integrated PHY
- 2× SD/eMMC interfaces — one supports **eMMC 5.0 with HS400/DDR** operation
- USB high-speed host/device controller with on-chip PHY
- Digital microphone interface (up to 8 channels)
- Serial peripherals: UART, I²C, I3C, SPI, HSPI, SAI

## Graphics

- **2.5D GPU** with vector graphics acceleration + frame buffer compression
- **EZH-V** (RISC-V core) with SIMD/DSP instructions
- Full openVG 1.1 support
- Up to 720p @ 60 FPS from on-chip SRAM
- LCD Interface + **MIPI DSI**
- Integrated JPEG + PNG support
- CSI 8/10/16-bit parallel (via FlexIO)

## Security (EdgeLock® Secure Enclave — Core Profile)

- Secure boot + debug
- Cryptographic services: TRNG, DICE, UID, PUF, OTP
- Crypto accelerators: PKC, AES, SHA
- Security monitoring: tamper detection, intrusion detection
- Device Attestation via Device Identifier Composition Engine (DICE)
- Life cycle management

## Software / Ecosystem

- MCUXpresso ecosystem (IDE, config tools, security, SDK)

## Related Products

- **PCA9420 / PCA9421** — PMIC
- **PCA9422** — PMIC
- **i.MX-RT600** — Predecessor (dual-core M33 + HiFi 4 DSP)
- **i.MX-RT500** — Lower-tier edge-AI crossover
- **i.MX 8ULP** — MPU sibling for ultra-low-power

## Applications

- AI/ML edge inference (NPU-enabled)
- Audio (smart speakers, hearables, voice assistants)
- Wearable (smart watch, health band)
- Smart home HMI (with 2.5D GPU + MIPI DSI)
- Industrial HMI

## Buy/Parametrics

(Refer to raw file for live part variants.)
