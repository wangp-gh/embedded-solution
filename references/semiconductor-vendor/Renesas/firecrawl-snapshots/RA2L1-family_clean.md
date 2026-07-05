# Renesas RA2L1 — Cortex-M23 48 MHz Ultra-Low-Power MCU

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/Renesas/firecrawl-snapshots/RA2L1-family_raw.md`
(25,345 bytes). Captured from `https://www.renesas.com/en/products/ra2l1`.

## Family Identity

- **Family:** RA2L1 (RA2 series)
- **Marketing tagline:** "48 MHz Arm Cortex-M23 Ultra-Low-Power
  General-Purpose Microcontroller"
- **Position:** Renesas' most energy-efficient ultra-low-power MCU
  in the RA family. Companion to RA4M / RA6M general-purpose and RA6T
  motor-control.

## Core

- **Arm Cortex-M23 @ 48 MHz** (32-bit)
- Renesas' low-power process technology

## Memory

- **Flash:** 128 KB or 256 KB
- **SRAM:** 32 KB with ECC
- **Data Flash:** 8 KB (EEPROM-like)

## Operating Conditions

- **Supply voltage:** **1.6V to 5.5V** (very wide)
- **Temperature:** -40 to +85 °C or -40 to +105 °C (Ta)

## Peripherals

- **12-bit ADC**
- **12-bit DAC**
- **LPACMP** (Low-Power Analog Comparator)
- **32-bit general PWM timer**
- 16-bit general PWM timer
- Low-power asynchronous general-purpose timer
- **RTC**
- **Enhanced Capacitive Touch Sensing Unit (CTSU2)**

## Communication

- **5× SCI** (UART / Simple SPI / Simple I²C)
- **2× SPI** (multi-master interface)
- **2× I²C**
- **1× CAN**

## I/O Ports

- 37 / 53 / 69 / 85 (variant)

## Package

- 48-pin to 100-pin

## Internal Voltage Regulators

- Internal voltage regulators (low-power optimized)

## Safety

- Safety features (specifics in raw)
- (Renesas' standard safety IP across RA family)

## Security

- Security and encryption (Renesas' standard security IP)

## Use-Case Tier Hint

- **Ultra-low-power capacitive touch** — CTSU2 is Renesas' latest capacitive
  touch sensing unit. Suitable for touch-based UI (buttons, sliders, wheel
  sensors) with 1.6V-5.5V wide voltage for direct battery operation.
- **Battery-powered consumer / appliance** — wide voltage for 1.5V dry cell
  to 5V USB direct.
- **Industrial sensor nodes** — low-power mode + CAN for industrial
  networking.
- **Smart home / IoT** touch-controlled devices.

## Application Areas

- Touch-based UI (HMI buttons, sliders)
- Smart appliances (touch control)
- Battery-powered IoT sensors
- HVAC control (touch + CAN)
- Industrial sensor nodes with touch interface
- Wearable / fitness devices (touch-based)
