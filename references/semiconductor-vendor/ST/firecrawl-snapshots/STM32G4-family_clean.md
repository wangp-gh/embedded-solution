# STM32G4 Series — Cortex-M4 + FPU + DSP @ 170 MHz (Motor Control MCU)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/ST/firecrawl-snapshots/STM32G4-family_raw.md`
(40,726 bytes). Captured from `https://www.st.com/en/microcontrollers-microprocessors/stm32g4-series.html`.

## Family Identity

- **Family:** STM32G4
- **Position:** Cortex-M4 with rich analog peripherals for motor control,
  digital power, and high-end consumer applications.
- **Compatibility:** High degree of compatibility with **STM32F3 series**.
- **Temperature:** -40 to +125 °C

## Performance

- **Core:** Arm Cortex-M4 @ 170 MHz with FPU + DSP instructions
- Three hardware accelerators:
  - **ART Accelerator**
  - **CCM-SRAM routine booster**
  - **Mathematical accelerators**

## Memory

- 32 to 512 KB flash (dual-bank with ECC)
- In-field firmware upgrades (dual-bank)
- Securable memory area

## Sub-Series (Product Lines)

### STM32G4x1 — Access Line (entry-level)

- 170 MHz Arm Cortex-M4
- Up to 3× ultra-fast 12-bit ADCs
- 4× 12-bit DACs
- 4× ultra-fast comparators
- 32 to 512 KB flash
- 32 to 100 pins
- Ideal for generic functionality

### STM32G4x3 — Performance Line

- 170 MHz Arm Cortex-M4
- 5× ultra-fast 12-bit ADCs
- 7× 12-bit DACs
- 7× ultra-fast comparators
- Dual-bank flash
- Up to 3× FDCAN interfaces
- 48 to 128 pins
- Ideal for extensive analog and communication

### STM32G4x4 — Hi-Resolution Line

- **184 ps high-resolution timer**
- 170 MHz Arm Cortex-M4
- 5× ultra-fast 12-bit ADCs
- 7× 12-bit DACs
- 7× ultra-fast comparators
- Ideal for **digital power conversion**: D-SMPS, lighting, wireless chargers

## Analog Peripherals

- **5× 12-bit ADCs** (4 Msps with 16-bit hardware oversampling)
- **DACs, op amp, comparators**
- **FDCAN** (flexible data rate, 8 Msps)

## Security

- AES hardware encryption

## Connectivity

- USB Type-C® interface with power delivery including physical layer (PHY)

## Architecture

- Flexible interconnect matrix — peripherals can communicate autonomously
  with DMA, saving CPU and power

## Applications

- **Motor Control** (washing machines, pumps, drones, robotics)
- **High-end consumer**
- **Industrial devices**
- **Digital Power** (D-SMPS, lighting, wireless chargers)

## Dev Tools

- **STM32 Nucleo boards** (NUCLEO-G4 family) — flexible prototyping
- **STM32 Evaluation boards** — full feature
- **Motor control packs** (P-NUCLEO-IHM03) — feature for motor control + analog
- **STM32 Discovery kits** (B-G4* family) — key feature prototyping

## Related Series

- **STM32F3** — older generation; pin-compatible to ease migration
- **STM32G0** — Cortex-M0+ cost-down
- **STM32CubeG4** — STM32Cube MCU package for this series

## Why STM32G4

- Three hardware accelerators (ART, CCM-SRAM, math) → high sustained DSP throughput
- High-resolution timer (184 ps) for digital power / wireless charging
- Broadest analog peripheral set in STM32 family (12-bit ADC + DAC + op amp +
  comparator)
- Compatibility with F3 eases migration
