# Test Results

**BoneBuds Alpha 0.1** | Hardware test index

Only tests with confirmed hardware output are listed here. **Playback verified** does not mean that audio quality, electrical power or thermal safety has been validated.

| ID | Test | Hardware | Result | Demo |
| --- | --- | --- | --- | --- |
| **T01** | Bluetooth A2DP audio playback | ESP32-WROOM-32 + MAX98357A + one BCT | **Playback confirmed** | [Watch](https://youtube.com/shorts/Wacn75VJihI) |

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

ESP32-S3 tone, local-player and microphone-loopback work is still exploratory. Dual-BCT and external Bluetooth-module tests are planned. **T02 will be added only after another hardware test is verified.**

[Development log](development-log.md) · [Wiring and setup](test-setup.md)
