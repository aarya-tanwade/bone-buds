# Test Results

**BoneBuds / OSSIS** | Hardware and firmware test index

Confirmed functionality is not equivalent to validated audio quality, battery life or electrical/thermal safety.

| ID | Test | Hardware | Result | Evidence |
| --- | --- | --- | --- | --- |
| **T01** | Bluetooth A2DP audio playback | ESP32-WROOM-32 + MAX98357A + one BCT | **Passed: playback confirmed** | [Video](https://youtube.com/shorts/Wacn75VJihI) |
| **T02** | Wireless firmware update over Wi-Fi OTA | ESP32-WROOM-32, same single-BCT setup | **Passed: owner-confirmed (29 Oct 2026)** | Test confirmed by owner; firmware not yet committed |
| **T03** | Independent left/right BCT stereo | Two MAX98357A amps + two BCTs | **Planned; awaiting replacement amplifier** | — |

## T01 | Bluetooth A2DP Audio Playback

**Date:** 24 October 2026  
**Firmware:** [T01_wroom_bt_a2dp.ino](../code/alpha-0.1/tests/T01_wroom_bt_a2dp/T01_wroom_bt_a2dp.ino)  
**Setup:** Laptop → Bluetooth A2DP → ESP32-WROOM-32 → I²S → MAX98357A → one BCT

### Objective

Check whether a laptop can stream music over Bluetooth to the ESP32 and play it through a bone-conduction transducer.

### Procedure

1. Connect the [T01 hardware setup](test-setup.md) with power disconnected.
2. Upload the verified WROOM sketch and pair the laptop with **ESP32 Bone Speaker**.
3. Play audio at a low source volume and check both the idle and playback behaviour.

See the [firmware README](../code/alpha-0.1/tests/T01_wroom_bt_a2dp/README.md) for dependencies and upload instructions.

### Observations

| Stage | What we observed |
| --- | --- |
| Initial attempts | No output or inconsistent playback with direct wiring. |
| First successful playback | Bluetooth pairing and music playback worked; noise, unwanted idle vibration and rapid heating were reported. |
| Corrected-connection retest | Audio playback was noticeably cleaner. |
| Latest check, 25 Oct | Playback working well; no unwanted vibration or noticeable heating reported during the check. A slight quality limitation remains. |

### Result

**Passed: basic Bluetooth audio playback through one BCT.** The cleaner result followed changes to the physical connections, not a measured DSP improvement. The exact cause of the earlier symptoms was not fully isolated.

**Not yet measured:** noise floor, audio output level, transducer temperature over time, power consumption, frequency response and long-duration stability.

**Evidence:** [T01 demonstration on YouTube](https://youtube.com/shorts/Wacn75VJihI). The recording demonstrates playback, not acoustic or thermal performance.

---

## T02 | Wireless OTA Firmware Update

**Reported verified:** 29 October 2026  
**Setup:** ESP32-WROOM-32, using separate Bluetooth-audio and Wi-Fi OTA modes.

**Result:** Owner confirmed successful testing of the OTA update capability. The tested T02 firmware and repeatability evidence have not yet been committed to this repository. This does not establish long-duration reliability, battery efficiency, or secure production-ready updating.

## T03 | Dual-BCT Stereo (Next)

Plan: use two MAX98357A amplifiers to drive separate left/right bone-conduction transducers. Awaiting a replacement amplifier after damage to the second module. No stereo playback result is recorded.

ESP32-S3 tone, local-player and microphone-loopback work remains exploratory.

[Development log](development-log.md) · [Wiring and setup](test-setup.md)
