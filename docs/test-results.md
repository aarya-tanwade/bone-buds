
# OSSIS test results

| ID | Test | Status | Evidence |
| --- | --- | --- | --- |
| T01 | Bluetooth A2DP playback | **PASSED** · 24 October 2026 | [Demonstration](https://youtube.com/shorts/Wacn75VJihI) |
| T02 | Wireless OTA | **PASSED** · 29 October 2026 | [Demonstration](https://youtu.be/clWIIejxp3k) · [OTA screenshot](../images/tests/T02/ota-upload-arduino-ide.png) |
| T03 | Independent left/right stereo playback | **PASSED** | [Test sketch](../code/ossis/tests/T03_independent_stereo/T03_independent_stereo.ino) · [Test procedure](../code/ossis/tests/T03_independent_stereo/README.md) |

## T01: Bluetooth A2DP playback

**PASSED · 24 October 2026**

We verified Bluetooth Classic A2DP playback through the ESP32-WROOM-32, I²S, MAX98357A and one bone-conduction transducer.

[Verified sketch](../code/ossis/tests/T01_wroom_bt_a2dp/T01_wroom_bt_a2dp.ino) · [Procedure and DSP settings](../code/ossis/tests/T01_wroom_bt_a2dp/README.md)

## 29 October: Shared-amplifier playback

We tested two Adafruit 8 Ω, 1 W bone-conduction transducers connected in parallel to one MAX98357A amplifier, using a phone as the Bluetooth audio source.

| Check | Observation |
| --- | --- |
| Playback | Clear and loud audio without audible noise |
| Contact position | Clear output at contact points just in front of each ear |
| Surroundings | Surrounding sounds remained audible during playback |
| Sound leakage | No noticeable leakage at normal volume; very faint leakage at maximum volume when listening closely |
| Volume | Maximum volume was unnecessary |
| Laptop source | Slight noise and intermittent breakup; the cause was not isolated |

The two transducers shared one amplifier output. This configuration provided the playback baseline before independent stereo development.

## T02: Wireless OTA

**PASSED · 29 October 2026**

We verified wireless firmware uploads over Wi-Fi using ArduinoOTA on the ESP32-WROOM-32.

Bluetooth playback and wireless OTA operate in separate firmware modes. The ESP32 can enter OTA mode after the initial Bluetooth pairing window or after an established Bluetooth connection is lost.

We successfully uploaded firmware wirelessly and returned to Bluetooth playback.

[Verified sketch](../code/ossis/tests/T02_mono_ota/T02_mono_ota.ino) · [Mode flow and upload procedure](../code/ossis/tests/T02_mono_ota/README.md)

[OTA upload screenshot](../images/tests/T02/ota-upload-arduino-ide.png)

## T03: Independent stereo playback

**PASSED.**

We successfully tested independent left and right audio playback using:

- 1 × ESP32-WROOM-32 development board
- 2 × MAX98357A I²S amplifier modules
- 2 × Adafruit 8 Ω, 1 W bone-conduction transducers

Both amplifiers receive the shared I²S clock and data connections from the ESP32. Their SD_MODE channel-selection configurations are different, assigning one amplifier to the left channel and the other to the right channel.

Each amplifier drives its own transducer, producing independent stereo output.

### Verification results

| Check | Result |
| --- | --- |
| Bluetooth A2DP connection | **PASSED** |
| Left-channel playback | **PASSED** |
| Right-channel playback | **PASSED** |
| Independent left/right output | **PASSED** |
| Both amplifiers operating together | **PASSED** |
| Separate BCT outputs | **PASSED** |

Independent channel playback was verified using stereo test audio.

### Firmware

The T03 stereo implementation is now the current main firmware.

[Current firmware](../code/ossis/main/main.ino) · [T03 test sketch](../code/ossis/tests/T03_independent_stereo/T03_independent_stereo.ino) · [T03 test procedure](../code/ossis/tests/T03_independent_stereo/README.md)

The T03 firmware currently focuses on Bluetooth stereo playback. The wireless OTA functionality from T02 has not yet been integrated into it.

## Next development stage

With independent stereo playback verified, development moves from breadboard testing towards a more compact hardware prototype.

| Stage | Work | Status |
| --- | --- | --- |
| T04 | Perfboard implementation and battery-powered testing | NEXT |
| T05 | Product concept and industrial design exploration | PLANNED |
| T06 | 3D enclosure and mechanical design | PLANNED |
| T07 | Final hardware testing, audio optimization and refinement | PLANNED |

[Development log](development-log.md) · [Bench setup](test-setup.md) · [Documentation index](README.md)
