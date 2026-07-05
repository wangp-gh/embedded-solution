# TI CC3301 — SimpleLink Wi-Fi 6 + BLE 5.4 Companion IC

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/TI/firecrawl-snapshots/CC3301-family_raw.md`
(72,568 bytes). Captured from `https://www.ti.com/product/CC3301`.

## Family Identity

- **Family:** SimpleLink™ CC33xx
- **Marketing tagline:** "SimpleLink™ 2.4 GHz Wi-Fi® 6 and Bluetooth® Low
  Energy companion IC"
- **Position:** TI's Wi-Fi 6 + BLE 5.4 co-processor (companion IC).
  Pairs with any host MCU or MPU capable of running TCP/IP stack.

## Wireless Capabilities

### Wi-Fi 6 (802.11ax)

- **2.4 GHz**, 20 MHz, single spatial stream
- MAC + baseband + RF transceiver
- **IEEE 802.11 a/b/g/n/ax backward compatibility**
- **OFDMA, trigger frame, MU-MIMO (downlink), BSS coloring, TWT**
- **Hardware-based encryption/decryption for WPA2 and WPA3**
- Multirole support (concurrent STA + AP)
- Antenna diversity / selection optional
- **3-wire or 1-wire PTA** for coexistence with Thread/Zigbee

### Bluetooth Low Energy 5.4

- LE Coded PHYs (long range)
- LE 2M PHY (high speed)
- Advertising extension
- **HCI transport** with **UART or shared SDIO** option

## RF Performance

- **Integrated 2.4 GHz PA** with up to **+20.5 dBm output power**
- Application throughput up to **50 Mbps**

## Host Interface

- **4-bit SDIO or SPI**
- Companion to any processor / MCU host (no host CPU in CC3301)

## Power Management

- VMAIN, VIO, Vpp: 1.8V
- VPA: 3.3V (for PA)

## Clock Sources

- 40 MHz XTAL fast clock
- Internal slow clock or external 32.768 kHz slow clock

## Operating Conditions

- **Temperature:** -40 to +105 °C

## Security

- Secured host interface
- Firmware authentication
- Anti-rollback protection

## Package

- **40-pin WQFN (RSB)** — 5×5 mm, 0.4 mm pitch

## OS Support (host-side)

- Android
- FreeRTOS
- Linux
- Zephyr RTOS

## Certifications

- Wi-Fi CERTIFIED Chip

## Dev Tools

- CC3301 LaunchPad (or dev kit; details in raw)

## Use-Case Tier Hint

- **Wi-Fi 6 companion IC** for any host MCU that needs Wi-Fi 6 + BLE 5.4.
  Pair with NXP i.MX-RT1170 / STM32H7 / ESP32-P4 application processor.
- **Industrial gateway with Wi-Fi 6 + BLE 5.4** — 50 Mbps throughput, WPA3.
- **Smart home hub** — Wi-Fi 6 + BLE provisioning + 802.15.4 coexistence.
- **Replaces TI CC3100/CC3200** in legacy products upgrading to Wi-Fi 6.

## Application Areas

- Wi-Fi 6 gateways
- Smart home hubs
- Industrial IoT (Wi-Fi 6 + BLE 5.4)
- Consumer Wi-Fi + BLE combo products
- Audio streaming (Wi-Fi 6 50 Mbps)

## Family Position

- **CC3301** — Wi-Fi 6 + BLE 5.4 (this entry)
- CC3300 — Wi-Fi 6 only (existing yaml, no BLE)
- CC3351 — modular certification variant (likely)
