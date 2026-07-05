# STM32H5 Series — Arm Cortex-M33 with TrustZone @ 250 MHz

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/ST/firecrawl-snapshots/STM32H5-family_raw.md`
(33,744 bytes). Captured from `https://www.st.com/en/microcontrollers-microprocessors/stm32h5-series.html`.

## Family Identity

- **Family:** STM32H5
- **Marketing tagline:** "Industry-first 32-bit MCUs Arm® Cortex®-M33 with
  TrustZone® core running at 250 MHz"
- **Position:** Mainstream secure MCU bridging STM32F4 (legacy) and STM32H7
  (high performance). TrustZone in this tier is industry-first for ST.
- Process: ST-optimized **40 nm**

## Performance

- **Core:** Arm Cortex-M33 @ up to 250 MHz with TrustZone
- Embedded graphics: Chrom-ART2 (no info on Chrom-GRC family)
- MJPEG / PLAY accelerator on higher-end parts

## Memory (by sub-series)

| Sub-series | Flash | RAM | Notes |
|---|---|---|---|
| H503 | 128 KB | 32 KB | entry-level |
| H523 / H533 | 512 KB | 272 KB | crypto available |
| H562 | 2 MB | 640 KB | cost-optimized |
| H563 / H573 | 2 MB | 640 KB | Ethernet + SMPS option; H573 has hardware encryption accelerator |
| H5E4 / H5F4 | 4 MB | 1.5 MB | Ethernet, Chrom-ART2, TFT-LCD, MJPEG, PLAY, SMPS; F4 has hw crypto + TrustZone |
| H5E5 / H5F5 | 4 MB | 1.5 MB | same + USB-HS w/ PHY, USB FS/UCPD; F5 has hw crypto + TrustZone |

All flash is **dual-bank**.

## Peripherals (typical across family)

- 12-bit ADC × 3 on mid/high end
- FDCAN × 3 on E4/F4 and above
- Ethernet on F4/F5 and H563+
- USB: HS PHY/FS/UCPD variants
- 2× SDMMC, FMC, 2× OctoSPI on F4/F5
- SMPS option (except H503)

## Security (ST's "scalable security offer")

- **TrustZone** for Cortex-M33 isolation
- **STM32Trust TEE Secure Manager** (delivered as X-CUBE-SEC-M-H5) on
  H573, H5F4, H5F5
- Hardware encryption accelerator (AES / SAES / PKA / OTFDEC / HUK / ST-iROT)
  on selected lines
- **CCB** (Compromise / Configurable Black-box / Crypto Core Block) on
  selected lines
- Maintained by ST over the product lifecycle ("fully certified building
  blocks")

## Package Options

- 25 to 225 pins (large choice)
- Operating temperature up to 125 °C ambient — suitable for harsh environments
- Affordable cost

## Applications

### Smart Home
- Air conditioners
- Refrigerators and freezers
- Central alarm systems
- Washing machines

### Personal Electronics
- Keyboards
- Smartphones
- IoT tags and tracking devices

### Smart City
- Industrial communication
- Lighting controls
- Digital power

### Medical and Healthcare
- CPAP and respirators
- Dialysis machines
- Pills distributors
- Powered patient beds

## Why STM32H5

- **More performance + more memory** vs STM32F4
- **TrustZone at 250 MHz** is industry-first
- **Scalable security offer** — choose from essential services to fully
  certified secure elements
- Optimized 40 nm process keeps cost affordable

## Dev Tools

- Discovery kits (2)
- STM32 Nucleo boards (4)
- STM32Cube MCU & MPU Packages
- STM32Cube Expansion Packages (8 partner)
- STM32CubeMX configurator + IDE
