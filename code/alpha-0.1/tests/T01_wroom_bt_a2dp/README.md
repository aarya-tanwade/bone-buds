# T01 | ESP32-WROOM Bluetooth A2DP Audio Playback

**Hardware playback observed: 2026-10-24.** Purpose: verify wireless laptop music playback through one bone-conduction transducer.

## Source and environment

Use the original ESP32-WROOM-32, 38-pin development board. Select **ESP32 Dev Module**, not ESP32-S3. Exact original upload settings were not recorded.

| Dependency | Locally installed at documentation audit | Historical T01 version |
| --- | --- | --- |
| esp32 by Espressif Systems | 3.3.12 | Not independently recorded |
| audio-tools by Phil Schatzmann | 1.2.5 | Not independently recorded |
| ESP32-A2DP by Phil Schatzmann | 1.8.11 | Not independently recorded |

Includes: `AudioTools.h`, `AudioTools/CoreAudio/AudioFilter/Filter.h`, `BluetoothA2DPSink.h`. The pipeline uses I2SStream, VolumeStream and three FilteredStream stages. Source configuration: 44.1 kHz, 16-bit, two channels; 200 Hz high-pass, 2.8 kHz peaking stage (+4 dB), 5 kHz shelf (+2 dB), volume 1.0, A2DP volume 127. These are code settings, not measured response or proof that DSP improved playback.

## Build validation

On 2026-10-25, `arduino-cli compile --fqbn esp32:esp32:esp32` passed with the installed versions above and default board options. Program storage: 1,125,016 / 1,310,720 bytes (85%). Global RAM: 43,032 / 327,680 bytes (13%). This compilation does not establish the historical upload configuration or constitute a hardware retest.

## Reproduce

1. With power disconnected, connect the WROOM, MAX98357A and single BCT using the [wiring table](../../../../docs/test-setup.md#connections). GPIO26 → BCLK, GPIO25 → LRC, GPIO22 → DIN; 5 V → VIN, 3V3 → SD, common GND. BCT across SPK+ and SPK−; GAIN unconnected.
2. Install the dependencies above and open the matching sketch folder in Arduino IDE. Select ESP32 Dev Module and the actual serial port. Verify, then upload using a data-capable USB cable.
3. Open Serial Monitor at 115200 baud. Expect startup messages and the Bluetooth name **ESP32 Bone Speaker**.
4. Set laptop playback volume low before pairing. The preserved sketch initializes its software volume controls at full scale.
5. Pair the laptop with ESP32 Bone Speaker and select it as the audio output. Play a known audio file on the bench, off the body. Increase source level cautiously only as needed.
6. Record source track, volume, wiring, supply, duration, idle behavior and any heating. Stop and disconnect power if unexpected vibration or rapid heating recurs.

Expected: laptop audio reaches the BCT. Observed: pairing and playback worked; corrected direct wiring was followed by cleaner audio. The latest owner report (2026-10-25) confirms no unwanted vibration or heating in the current setup, with only a slight audio-quality limitation remaining. No claim is made for measured noise, output power, thermal safety or long-duration reliability.

[Full results](../../../../docs/test-results.md) · [Development log](../../../../docs/development-log.md) · [YouTube evidence](https://youtube.com/shorts/Wacn75VJihI)
