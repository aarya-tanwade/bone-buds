
# OSSIS / Code

Firmware and verified test sketches for the first BoneBuds prototype.

> **Current firmware:** [main.ino](ossis/main/main.ino) contains the latest working **T03 independent stereo build**. It receives Bluetooth Classic A2DP audio, processes the left and right channels independently and outputs stereo over I²S to two MAX98357A amplifiers.

| Source | Purpose | Status |
| --- | --- | --- |
| [main.ino](ossis/main/main.ino) | Current Bluetooth stereo firmware (T03) | **CURRENT** |
| [T01 sketch](ossis/tests/T01_wroom_bt_a2dp/T01_wroom_bt_a2dp.ino) · [Guide](ossis/tests/T01_wroom_bt_a2dp/README.md) | Original Bluetooth playback baseline | **PASSED** |
| [T02 sketch](ossis/tests/T02_mono_ota/T02_mono_ota.ino) · [Guide](ossis/tests/T02_mono_ota/README.md) | Wireless firmware update experiment | **PASSED** |
| [T03 sketch](ossis/tests/T03_independent_stereo/T03_independent_stereo.ino) · [Guide](ossis/tests/T03_independent_stereo/README.md) | Independent left/right stereo playback using two amplifiers | **PASSED** |

## Audio pipeline

The current firmware uses the following signal path:

```text
Bluetooth Classic A2DP
          |
     ESP32-WROOM-32
          |
     Stereo DSP
       /     \
   Left      Right
    DSP       DSP
       \     /
      Stereo I²S
          |
    Two MAX98357A
       /     \
   Left BCT  Right BCT
```

Each channel has its own independent filter state.

### Current DSP configuration

| Stage | Setting |
| --- | --- |
| Pre-gain | -4.5 dB |
| High-pass filter | 180 Hz, Q = 0.7071 |
| Peaking EQ | 2.8 kHz, +4 dB, 0.8-octave bandwidth |
| High-shelf EQ | 5.5 kHz, +2.5 dB |
| Output limiter | Soft-knee above 90% full scale |
| Master volume | 1.0 |

The processing chain uses 32-bit floating-point calculations before conversion to the 16-bit I²S output.

### Audio format

| Parameter | Configuration |
| --- | --- |
| Sample rate | 44,100 Hz |
| Bit depth | 16-bit |
| Channels | 2 (Left + Right) |
| I²S BCLK | GPIO 26 |
| I²S WS / LRC | GPIO 25 |
| I²S DIN | GPIO 22 |
| APLL | Enabled |
| DMA buffer size | 512 |
| DMA buffer count | 10 |

## Upload the current firmware

1. Connect the ESP32-WROOM-32 to your computer over USB.
2. Open [main.ino](ossis/main/main.ino) in Arduino IDE.
3. Select **ESP32 Dev Module** as the board.
4. Install the following libraries:
   - **ESP32 by Espressif Systems** (Arduino board package)
   - **AudioTools** by Phil Schatzmann
   - **ESP32-A2DP** by Phil Schatzmann
5. Select the correct USB serial port and verify the sketch.
6. Upload the firmware over USB.
7. Open Serial Monitor at **115200 baud**.
8. Connect your phone to the Bluetooth device named **BoneBuds Stereo HQ**.

For the amplifier connections and channel selection, follow the [bench setup guide](../docs/test-setup.md).

## Previous experiments

The earlier tests remain preserved as separate firmware references.

- **T01:** Established Bluetooth A2DP playback through the ESP32-WROOM-32 and MAX98357A.
- **T02:** Added wireless OTA updates using a separate Wi-Fi operating mode. Bluetooth and Wi-Fi OTA operate on separate boots.
- **T03:** Established independent left/right playback using two MAX98357A amplifiers and two bone-conduction transducers.

The current `main.ino` is the T03 stereo firmware. It does not currently include the T02 OTA functionality. The T02 sketch and its upload procedure remain available separately.

## Repository structure

```text
code/
├── README.md
└── ossis/
    ├── main/
    │   └── main.ino
    └── tests/
        ├── T01_wroom_bt_a2dp/
        │   ├── T01_wroom_bt_a2dp.ino
        │   └── README.md
        ├── T02_mono_ota/
        │   ├── T02_mono_ota.ino
        │   └── README.md
        └── T03_independent_stereo/
            ├── T03_independent_stereo.ino
            └── README.md
```

[Documentation index](../docs/README.md) · [Test results](../docs/test-results.md) · [Bench setup](../docs/test-setup.md) · [Development log](../docs/development-log.md)
