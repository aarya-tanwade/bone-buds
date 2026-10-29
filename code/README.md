# OSSIS / Firmware

BoneBuds' first experimental bone-conduction audio system. Firmware tests are recorded separately from hardware concepts.

## Test index

| ID | Experiment | Result | Source |
| :-- | :-- | :-- | :-- |
| **T01** | Bluetooth A2DP audio through one BCT | **Passed** · 24 Oct 2026 | [Verified sketch and setup](alpha-0.1/tests/T01_wroom_bt_a2dp/README.md) |
| **T02** | Wireless firmware update (Wi-Fi OTA) | **Passed** · owner-confirmed, 29 Oct 2026 | Local tested sketch; not yet committed |
| **T03** | Dual-BCT stereo playback | **Next** · awaiting replacement amplifier | Not started |

T01 is an unchanged archive of [`prototype1.ino`](prototype1/prototype1.ino). The `alpha-0.1/` folder name is retained for existing links; the prototype is now named **OSSIS**.

## Audio pipeline

```mermaid
flowchart LR
    BT["Bluetooth A2DP"] --> HP["High-pass · 200 Hz"]
    HP --> EQ["Peak · 2.8 kHz, +4 dB"]
    EQ --> HS["High-shelf · 5 kHz, +2 dB"]
    HS --> V["Volume"] --> I["ESP32 I²S"]
    I --> AMP["MAX98357A"] --> BCT["One BCT"]
```

**Configuration:** ESP32-WROOM-32 · 44.1 kHz / 16-bit · GPIO **26** BCLK, **25** WS, **22** DIN · software volume **1.0** · Bluetooth volume **127**.

EQ settings are implemented in firmware; improved noise floor and frequency response have **not** been measured. The MAX98357A is mono, even when receiving two-channel I²S data.

## T02 / OTA

Added Wi-Fi access point, ArduinoOTA, local mode-control page and persistent boot-mode selection. Bluetooth playback and Wi-Fi OTA use **separate modes** with a restart when switching. OTA has **no inactivity timeout** while active.

**Wireless updating tested successfully**, as confirmed by the project owner. Long-term reliability, repeated updates and battery consumption remain unmeasured. OTA credentials must not be committed publicly.

## Next / T03

Test two independent MAX98357A amplifiers and BCTs for left/right stereo after replacing the damaged amplifier. No T03 results are claimed yet.

[Results](../docs/test-results.md) · [Setup](../docs/test-setup.md) · [Development log](../docs/development-log.md)
