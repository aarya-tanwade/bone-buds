# Development Log

**BoneBuds Alpha 0.1** | Baseline audio testing

A dated record of our bench tests, issues and changes. Only **T01 Bluetooth A2DP playback** has been confirmed end to end so far. Dates are based on the test history, not file timestamps.

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

## Next checks

- Repeat T01 at controlled source volume; record idle behaviour, playback duration and temperature.
- Test dual-BCT output only after checking amplifier load and channel configuration.
- Continue ESP32-S3 local-audio and DSP experiments. Record each verified test separately.

[All test results](test-results.md) · [Current test wiring](test-setup.md)
