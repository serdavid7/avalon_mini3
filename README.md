
# "Avalon Mini 3" Integration for Home Assistant!
---

**Avalon Mini 3** is a **Home Assistant integration** for the Canaan Avalon Mini 3 ASIC miner.

- 230 sensors (approx. 60 active)
- Workmode control (Low / Mid / High)
- Control LED color, brightness and effects
- Reboot button
- Change pool configuration data (password required!)

---

### Version 1.0.0.1 (edit readme.md)
Version: 1.0.0.0 first release

Tested so far:

- Avalon Mini 3 (Firmware 25061801_6cfb09a)

---

**Note:**

This integration may also be compatible with other firmware versions — unfortunately I cannot test this without additional hardware, so feedback is welcome!

With the “Avalon Mini 3”, only sensors work using this integration — workmode control does NOT.

---

## Overview

This integration allows full monitoring and control of the **Avalon Mini 3 Miner** directly from Home Assistant.

Features:

- Live miner statistics (temperature, fan, hashrate, power consumption)
- **LED control** (RGB colors, brightness, effects)
- Mining **workmode** selection (Low, Mid, High)
- Reboot button directly from Home Assistant
- Enter/change pool data via the **GUI Config Flow**

---

### Pool Configuration Notes

To change pool data from Home Assistant, the miner login password must be provided during installation or later in the integration options.

The password is ONLY required for pool configuration changes.

If you do not plan to modify pool data via Home Assistant, no password is required.

**Warning:** After changing any pool entry, the miner will automatically reboot!

---

## Installation

### Internal (via HACS)

Registered in HACS:

Simply search for **“Avalon Mini 3”** in HACS and download — restart Home Assistant — install!

--
