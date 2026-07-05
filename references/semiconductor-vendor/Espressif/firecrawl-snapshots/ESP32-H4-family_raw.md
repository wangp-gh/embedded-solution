[Skip to main content](https://www.espressif.com/en/products/socs/esp32-h4#main-content)

[![Home](https://www.espressif.com/sites/all/themes/espressif/logo-black.svg)](https://www.espressif.com/en "Home")

## Main menu

Search

- [English](https://www.espressif.com/en/products/socs/esp32-h4)
- [简体中文](https://www.espressif.com/zh-hans/products/socs/esp32-h4)
- [日本語](https://www.espressif.com/ja-jp/products/socs/esp32-h4)

[Subscribe](https://documentation.espressif.com/en/subscriptions)

## Search form

Search

Quick Connect

- [ESP32-S31](https://www.espressif.com/en/products/socs/esp32-s31)
- [ESP32-H4](https://www.espressif.com/en/products/socs/esp32-h4)
- [ESP32-E22](https://www.espressif.com/en/products/socs/esp32-e22)
- [Product Selector](https://products.espressif.com/)
- [ESP-IDF v6.0](https://docs.espressif.com/projects/esp-idf/en/v6.0/esp32/index.html)

## Hardware

## ESP32-H

## ESP32-H4

- ![](https://www.espressif.com/sites/default/files/banner/esp32-h4-banner.jpg)
![](https://www.espressif.com/sites/default/files/banner/esp32-h4-banner.jpg)

![](https://www.espressif.com/sites/default/files/banner/esp32-h4-2026-banner-mobile-bg.png)



# ESP32-H4



## Next-Gen Dual-Core Ultra-Low-Power   SoC, with Bluetooth® 5.4 (LE) +    802.15.4 for Long Battery Life & HMI


## You are here

[Home](https://www.espressif.com/en) » Hardware » ESP32-Wrap » ESP32-H » ESP32-H4

- [Overview](https://www.espressif.com/en/products/socs/esp32-h4#overview)
- [Features](https://www.espressif.com/en/products/socs/esp32-h4#features)
- [Products & Resources](https://www.espressif.com/en/products/socs/esp32-h4#products)
- [Product Selector](https://www.espressif.com/en/products/socs/esp32-h4#esp-product-selector-add-wrap)

![](https://www.espressif.com/sites/all/themes/espressif/images/esp32-h4/esp32-h4-video-cover-en.jpg)

ESP32-H4 is an advanced low-power dual-core 32-bit RISC-V SoC that integrates Bluetooth 5.4 (LE) and IEEE 802.15.4 connectivity in a single device. Designed for next-generation battery-powered products, it combines robust security, flexible memory support, and energy-efficient operation to address more demanding low-power applications. ESP32-H4 is ideal for wearables, wireless audio products, healthcare devices, and large-scale low-power sensor networks.


## Features

![Wireless Connectivity](https://www.espressif.com/sites/all/themes/espressif/images/esp32-h4/wireless-connectivity.png?v=3)

### Wireless Connectivity and Bluetooth 5.4 (LE)

Multi-protocol wireless connectivity for low-power mesh networks

ESP32-H4 integrates **Bluetooth 5.4 (LE)** and **IEEE 802.15.4** in a single SoC, fully supporting all features of the Bluetooth 5.4 (LE) core specification and certified with Bluetooth 6.0. The Bluetooth subsystem supports advanced capabilities, including LE Audio, LE Isochronous Channels (BIS/CIS), Connection Subrating, Periodic Advertising with Responses (PAwR) and Direction Finding (AoA/AoD). These features enable low-power audio products, indoor positioning and large-scale beacon and sensor deployments. The 802.15.4 subsystem supports Thread 1.4 and Zigbee 3.0, enabling Matter-over-Thread and other mesh-based applications.

![System and Memory](https://www.espressif.com/sites/all/themes/espressif/images/esp32-h4/system-memory.png?v=2)

### System and Memory

Dual-core RISC-V performance with flexible memory expansion

ESP32-H4 is built around **dual-core 32-bit RISC-V microcontroller** running up to **96 MHz** with integrated DSP extensions. It includes 384 KB SRAM and 128 KB ROM, with support for external memory. The SoC also supports **external PSRAM**, allowing developers to run **memory-intensive applications**, such as LE Audio buffering, complex protocol stacks, data logging or sensor fusion. This flexibility simplifies application development and improves future-proofing for feature upgrades.

![Low-Power Operation](https://www.espressif.com/sites/all/themes/espressif/images/esp32-h4/low-power.png)

### Low-Power Operation with Integrated DC-DC

Optimized power efficiency for long-lasting battery-powered devices

ESP32-H4 is optimized for **ultra-low power** operation. An **integrated DC-DC converter** improves overall efficiency through lower supply voltage and efficient power regulation. Combined with multiple low-power modes and **selective peripheral activation**, the ESP32-H4 enables devices to operate for extended periods on small batteries, such as coin cells or rechargeable packs. A **reduced maximum transmit power** further lowers RF current consumption, while Bluetooth LE optimizations—such as advertising without CPU involvement—make ESP32-H4 well suited for battery-powered sensors, wearables, LE Audio accessories, and Matter-over-Thread devices.

![Affordable Security](https://www.espressif.com/sites/all/themes/espressif/images/esp32-h4/security.png)

### Affordable Security

Essential hardware security for cost-sensitive IoT designs

Aligning with Espressif's philosophy of **affordable security**, ESP32-H4 integrates **secure boot, memory encryption, digital signature (ECDSA), cryptographic accelerators**, and a true random number generator. These hardware security features protect private keys and sensitive data, enabling secure communication and firmware integrity, even in cost-sensitive designs and helping developers meet modern IoT security requirements.

![Peripherals](https://www.espressif.com/sites/all/themes/espressif/images/esp32-h4/peripherals.png)

### Optimized Peripherals and Human-Machine Interaction

Rich peripherals and touch support for intuitive user interaction

ESP32-H4 offers **up to 40 GPIOs**, encompassing standard microcontroller peripherals such as I2C, I2S, SPI, UART, LED-PWM, ADC, Timers, DMA, TWAI, USB-OTG and MCPWM. Specialized peripherals include the **Event Task Matrix (ETM)** for automation-triggered tasks. With **15 touch-sensing GPIOs**, ESP32-H4 is ideal for **human-machine interaction devices**, such as touch panels, smart switches, control knobs, etc.

![Software Availability](https://www.espressif.com/sites/all/themes/espressif/images/esp32-h4/software.png?v=3)

### Software Availability

A mature software ecosystem to accelerate product development

ESP32-H4 is fully supported by Espressif's open-source **ESP-IDF** platform, giving developers access to a mature SDK, tools and extensive documentation. For Bluetooth Low Energy development, it integrates seamlessly with Espressif's Bluetooth LE software ecosystem, including **ESP-BLE-MESH** and **ESP-BLE-AUDIO**, helping developers accelerate productization across a broad range of BLE applications. Additionally, **ESP-Matter** will provide support for ESP32-H4, enabling the development of **battery-operated Matter-enabled devices** with Thread connectivity. For customers using ESP32-H4 as a connectivity co-processor, firmware solutions such as **ESP-AT** and **ESP-Hosted** can also be used.

- Wireless Connectivity and Bluetooth 5.4 (LE)Multi-protocol wireless connectivity for low-power mesh networks
- System and MemoryDual-core RISC-V performance with flexible memory expansion
- Low-Power Operation with Integrated DC-DCOptimized power efficiency for long-lasting battery-powered devices
- Affordable SecurityEssential hardware security for cost-sensitive IoT designs
- Optimized Peripherals and Human-Machine InteractionRich peripherals and touch support for intuitive user interaction
- Software AvailabilityA mature software ecosystem to accelerate product development

## Products & Resources

![](https://www.espressif.com/sites/all/themes/espressif/images/esp32-c61/icon-series.png)

- ESP32-H4

[See More SoCs >](https://www.espressif.com/en/products/socs?id=ESP32-H4)

![](https://www.espressif.com/sites/all/themes/espressif/images/esp32-c61/icon-modules.png)

- ESP32-H4-WROOM-1

[See More Modules >](https://www.espressif.com/en/products/modules?id=ESP32-H4)

![](https://www.espressif.com/sites/all/themes/espressif/images/esp32-c61/icon-devkits.png)

- Coming Soon...

[See More DevKits >](https://www.espressif.com/en/products/devkits?id=ESP32-H4)

- ![](https://www.espressif.com/sites/all/themes/espressif/images/esp32-c61/icon-1.png)[Documents >](https://www.espressif.com/en/support/documents/technical-documents)
- ![](https://www.espressif.com/sites/all/themes/espressif/images/esp32-c61/icon-2.png)[Product Change Notifications >](https://www.espressif.com/en/support/documents/pcns)
- ![](https://www.espressif.com/sites/all/themes/espressif/images/esp32-c61/icon-3.png)[Certificates >](https://www.espressif.com/en/support/documents/certificates)
- ![](https://www.espressif.com/sites/all/themes/espressif/images/esp32-c61/icon-4.png)[Advisories >](https://www.espressif.com/en/support/documents/advisories)

## ![](https://www.espressif.com/sites/all/themes/espressif/images/esp32-c3/esp-product-selector-logo.png)ESP Product Selector

Choosing the ESP products you need has never been easier!

[Start Now](https://products.espressif.com/#/product-selector?language=en)

[![](https://www.espressif.com/sites/all/themes/espressif/images/new-home/down.png?v=2)](https://www.espressif.com/en/contact-us/sales-questions)

/

![Project Logo](https://www.espressif.com/sites/all/themes/espressif/images/logo-ai-new.png)

Ask AI