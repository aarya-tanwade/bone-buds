# OSSIS test results

| ID | Test | Status | Evidence |
| --- | --- | --- | --- |
| T01 | Bluetooth A2DP playback | **PASSED** · 24 October 2026 | [Video](https://youtube.com/shorts/Wacn75VJihI) |
| T02 | Wireless OTA | **PASSED** · 29 October 2026 | [Video](https://youtu.be/clWIIejxp3k) · [OTA screenshot](../images/tests/T02/ota-upload-arduino-ide.png) |
| T03 | Independent left/right playback | **NEXT** · Waiting for the second amplifier | Planned |

## T01: Bluetooth A2DP playback

We verified end-to-end A2DP playback through the ESP32-WROOM-32, I²S, MAX98357A and one BCT on 24 October.

[Verified sketch](../code/ossis/tests/T01_wroom_bt_a2dp/T01_wroom_bt_a2dp.ino) · [Procedure and DSP settings](../code/ossis/tests/T01_wroom_bt_a2dp/README.md)

## 29 October: shared-amplifier playback

We tested two Adafruit 8 Ω, 1 W BCTs in parallel on one MAX98357A output, using a phone as the Bluetooth source.

| Check | Our observation |
| --- | --- |
| Playback | Clear and loud, with no audible noise from the phone stream |
| Contact position | Clear output at the contact points just in front of the ears; earlier we had used placement behind the ears |
| Surroundings | We could still hear surrounding sounds during playback |
| Leakage | No noticeable leakage at normal levels; very faint leakage at maximum volume when closely listening for it |
| Volume | Maximum volume was unnecessary |
| Laptop source | Slight noise and intermittent breakup; we have not isolated the cause |

We will use the phone for repeat tests. The parallel BCTs share one output; T03 will test independent left/right channels with two amplifiers.

## T02: Wireless OTA

We uploaded firmware over Wi-Fi and returned to Bluetooth playback on 29 October.

[Verified sketch](../code/ossis/tests/T02_mono_ota/T02_mono_ota.ino) · [Mode flow and upload procedure](../code/ossis/tests/T02_mono_ota/README.md)

Our [Arduino IDE screenshot](../images/tests/T02/ota-upload-arduino-ide.png) shows **OTA upload in progress**.

[Development log](development-log.md) · [Bench setup](test-setup.md)
