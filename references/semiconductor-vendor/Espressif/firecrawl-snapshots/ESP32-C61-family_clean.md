# Espressif ESP32-C61 — Affordable Wi-Fi 6 SoC (single-band, no 802.15.4)

Manual enrichment 2026-06-30 from
`references/semiconductor-vendor/Espressif/firecrawl-snapshots/ESP32-C61-family_raw.md`
(9,789 bytes). Captured from `https://www.espressif.com/en/products/socs/esp32-c61`.

## Product Identity

- **Marketing tagline:** "Delivering affordable Wi-Fi 6 connectivity"
- **Family:** ESP32-C (entry-level Wi-Fi 6 tier)
- **Position:** Cost-down of C6 — single-band Wi-Fi 6 + BLE 5 + Bluetooth
  Mesh 1.1, but **without 802.15.4** (no Thread/Zigbee/Matter).

## Wireless

### Wi-Fi 6 (single-band, 2.4 GHz)

- **20 MHz** bandwidth for 802.11ax mode
- **20/40 MHz** bandwidth for 802.11b/g/n mode
- 802.11ax features: **OFDMA**, **MU-MIMO**, **Target Wake Time (TWT)**
  (basis for ultra-low-power apps)

### Bluetooth 5 (LE)

- Long-range via advertisement extension + coded PHY
- 2 Mbps high-throughput PHY
- Bluetooth Mesh 1.1 protocol

## Memory

- "Expanded memory options" (likely more than C6 / C5; exact size in raw)

## Position

- **Cost-effective Wi-Fi 6 SoC** for mass-market IoT
- Drops 802.15.4 (no Thread/Zigbee/Matter) compared to C6 → cheaper BOM
  for cost-sensitive Wi-Fi-only designs (smart home lighting, smart switches,
  asset tracker with Wi-Fi backhaul)

## Use-Case Tier Hint

- **Cost-sensitive Wi-Fi 6 IoT:** smart plugs, light switches, simple sensor
  nodes with Wi-Fi 6 mesh backhaul, ESP-Mesh + BLE provisioning.
- **Single-band Wi-Fi 6 replacement for C3** (which is single-band Wi-Fi 4):
  use C61 if budget permits for TWT/MU-MIMO/OFDMA benefits.
