# Development Log

**BoneBuds / OSSIS** | Baseline audio and OTA tests

A dated record of bench tests, issues and changes. **T01 Bluetooth playback** and **T02 OTA** have been confirmed by the project owner. Dates below reflect recorded test history or owner confirmation, not GitHub commit dates.

## Earlier work | Dates not recorded

**ESP32-S3 audio bring-up**

- Tried I²S output, tone generation, local audio playback and microphone-loopback code.
- Faced USB detection and upload issues. Changing a faulty USB cable restored board connectivity.
- Some audio tests produced no output. We checked GPIO mapping, amplifier wiring and transducer connections.
- **Outcome:** No complete ESP32-S3 playback test confirmed yet. These remain exploratory attempts, not verified test entries.

## 24 October 2026 | T01: Bluetooth playback

**Setup:** Laptop → Bluetooth A2DP → ESP32-WROOM-32 → I²S → MAX98357A → one BCT.

- Paired the laptop and played audio through the transducer successfully.
- The initial working setup had substantial background noise and strong vibration even before music started.
- The transducer also heated up quickly during an earlier playback attempt.
- **Outcome:** Bluetooth playback confirmed. Noise and heating needed further investigation.

[Watch T01](https://youtube.com/shorts/Wacn75VJihI) · [Test results](test-results.md)

## 24 October 2026 | Direct-connection retest

- Earlier direct wiring had produced inconsistent or no output.
- Rechecked and corrected the physical connections, then repeated the WROOM playback test.
- Audio sounded noticeably cleaner, with much less unwanted behaviour than the earlier setup.
- **Outcome:** The revised connection worked better. We did not isolate every faulty contact or measure the change in noise level.

## 25 October 2026 | Latest listening check

- The current single-BCT setup was reported to play well, with **no unwanted idle vibration or noticeable heating during the check**.
- A slight audio-quality limitation remains.
- **Outcome:** Current playback is encouraging, but long-duration temperature, output level and sound-quality measurements have not been completed.

## 29 October 2026 | T02: Wireless OTA

- Added separate Bluetooth playback and Wi-Fi OTA modes.
- Owner confirmed OTA testing was completed successfully.
- **Outcome:** T02 marked passed; tested sketch and repeatability evidence still need to be archived.

## Next / T03: Dual-BCT stereo

- Obtain a replacement MAX98357A after damage to the second amplifier.
- Test separate left/right outputs with two amplifiers and two transducers.
- Continue ESP32-S3 and DSP experimentation; record each confirmed test individually.

[All test results](test-results.md) · [Current test wiring](test-setup.md)
