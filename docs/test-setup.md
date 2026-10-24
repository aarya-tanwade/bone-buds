# T01 | Hardware Test Setup

**BoneBuds Alpha 0.1** | ESP32-WROOM Bluetooth A2DP playback

This is the wiring used for the verified **single-BCT audio test**, not the final Prototype 1 hardware design.

## Hardware

| Part | Role |
| --- | --- |
| Laptop | Bluetooth audio source |
| ESP32-WROOM-32 DevKit, 38-pin | Bluetooth A2DP receiver and I²S output |
| MAX98357A breakout | I²S Class-D amplifier |
| Bone-conduction transducer (BCT) | Single audio output |
| USB cable | ESP32 power and firmware upload |

## Pin connections

| ESP32-WROOM / source | MAX98357A | Purpose |
| --- | --- | --- |
| **GPIO26** | BCLK / BCK | I²S bit clock |
| **GPIO25** | LRC / WS | I²S word select |
| **GPIO22** | DIN | I²S audio data |
| **Board 5V output** | VIN | Amplifier power |
| **GND** | GND | Common ground |
| **3V3** | SD / MODE | Amplifier enable and channel selection |
| Not connected | GAIN | Left open in T01 |
| BCT lead 1 | SPK+ | Amplifier output |
| BCT lead 2 | SPK− | Amplifier output |

**Power:** USB powers the ESP32. The board's 5V supply path feeds amplifier VIN; ESP32 3V3 feeds SD separately. Check your particular DevKit's 5V/VIN labels before wiring. **SPK− is not GND.**

The original test-setup graphic appears in the [main README](../README.md); use the table above if its power routing looks ambiguous.

## Firmware and playback

- **Board:** ESP32 Dev Module (original ESP32-WROOM, not S3)
- **Sketch:** [T01_wroom_bt_a2dp.ino](../code/alpha-0.1/tests/T01_wroom_bt_a2dp/T01_wroom_bt_a2dp.ino)
- **I²S settings in source:** 44.1 kHz, 16-bit, two channels
- **Bluetooth device name:** `ESP32 Bone Speaker`
- **Serial Monitor:** 115200 baud

1. Connect the amplifier and **one BCT** with USB disconnected.
2. Upload the sketch. Pair the laptop with `ESP32 Bone Speaker` and select it as the audio output.
3. Start with low laptop volume, check for vibration while idle, then play a short audio clip.
4. Stop and disconnect power if strong idle vibration or rapid heating returns.

The sketch sends two audio channels. The MAX98357A SD/MODE connection also affects channel selection, so **SD connected to 3V3 does not prove a stereo-to-mono mix**. Do not connect two BCTs in parallel without checking the amplifier's supported load and the transducer ratings.

## Safety and limits

- Power off before changing wiring; check the supply, ground and header contacts.
- Connect the BCT only between **SPK+** and **SPK−**. Do not ground either output.
- Keep tests off the head until output level and thermal behaviour have been evaluated.
- The latest short listening check had no reported heating or unwanted idle vibration, but sustained temperature and output-power tests are still pending.

[Test results](test-results.md) · [Development log](development-log.md) · [Firmware guide](../code/alpha-0.1/tests/T01_wroom_bt_a2dp/README.md)
