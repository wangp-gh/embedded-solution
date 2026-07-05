# ST STM32H7RS — Cortex-M7 600 MHz Bootflash MCU (H7R/7S)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/ST/firecrawl-snapshots/STM32H7-main-with-H7RS-family_raw.md`
(35,681 bytes). Note: page was fetched via
`https://www.st.com/en/microcontrollers-microprocessors/stm32h7-series.html`
(H7 main family page) which contains the STM32H7RS sub-series info.

## Family Identity

- **Family:** STM32H7RS (bootflash-based MCU, MPU-like)
- **Marketing tagline:** "STM32H7RS: a high performance, scalable and
  secure bootflash MCU"
- **Position:** Built on success of STM32H7 series. Cortex-M7 @ 600 MHz
  with **64 KB user flash + 620 KB SRAM** (small internal memory) for
  external memory scalability. Targets MPU-like GUI applications.

## Performance

- **Arm Cortex-M7 @ up to 600 MHz**

## Memory

- **User flash:** **64 KB** (bootflash-based; design for external memory)
- **SRAM:** **620 KB** (flexible)
- Designed for external memory scalability and flexibility

## Operating Sub-Series

- **STM32H7R3 / STM32H7S3** — general purpose line
- **STM32H7R7 / STM32H7S7** — graphics line (MPU-like GUI)

## Example Variants (H7RS sub-series)

- **STM32H7S3L8** — Cortex-M7 + 64 KB flash + 620 KB SRAM, TFBGA225
- **STM32H7S7L8** — Cortex-M7 + 64 KB flash + 620 KB SRAM, TFBGA225
- (S = security version; R/S suffixes denote line + security tier)

## Security

- **Secure Boot**
- **Secure Firmware Installation (SFI)**
- **Hardware encryption/decryption**
- Target certifications:
  - **SESIP3**
  - **PSA Certified Level 3**

## Use-Case Tier Hint

- **MPU-like GUI applications** with external memory (Octo-SPI flash
  + SDRAM). Tier with rich graphics + low cost.
- **IoT, medical, industrial** — high-end MCU with strong security.
- **Graphics line (H7R7/H7S7)** — high-resolution display driving
  (Chrom-GRC, JPEG codec, TFT-LCD, dual Octo-SPI).

## Use-Case Tier Hint vs H7 Family

- H7 main series (existing yaml STM32H7): traditional 1.4 MB SRAM,
  embedded flash — single-chip approach.
- **H7RS: bootflash-based with small internal flash + large SRAM** —
  external-memory-first architecture. Lower cost + scalable.

## Application Areas

- **MPU-like GUI** — driving large displays with external memory
- **IoT secure end nodes** (PSA L3 + SESIP3)
- **Medical** — secure devices with strong security posture
- **Industrial control panels** with TFT-LCD
- **Secure HMI** — high-perf UI with secure boot + secure firmware install

## Family Position (in H7)

- STM32H7 — embedded flash + 1.4 MB SRAM
- STM32H730 — Ethernet + dual Octo-SPI + SMPS, value line
- STM32H7B0 — value line, dual Octo-SPI + On-the-fly decryption
- **STM32H7RS** — bootflash-based with 64 KB flash + 620 KB SRAM,
  external memory scalability
- STM32H7S78-DK — dev kit for H7S78
- NUCLEO-H7S3L8 — Nucleo board for H7S3
