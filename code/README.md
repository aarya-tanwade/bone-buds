# OSSIS / Code

Firmware and verified test sketches for our first BoneBuds prototype.

> **Main firmware:** [main.ino](ossis/main/main.ino) holds our latest tested build, currently **T02 (Bluetooth + OTA)**.

| Source | Use |
| --- | --- |
| [main.ino](ossis/main/main.ino) | Current firmware |
| [T01 sketch](ossis/tests/T01_wroom_bt_a2dp/T01_wroom_bt_a2dp.ino) · [Guide](ossis/tests/T01_wroom_bt_a2dp/README.md) | Preserved Bluetooth playback baseline; **PASSED** |
| [T02 sketch](ossis/tests/T02_mono_ota/T02_mono_ota.ino) · [Guide](ossis/tests/T02_mono_ota/README.md) | Preserved wireless OTA experiment; **PASSED** |

## Upload the current firmware

1. Use the ESP32-WROOM-32 and [bench wiring](../docs/test-setup.md#connections). Select **ESP32 Dev Module**.
2. Install **esp32 by Espressif Systems**, **audio-tools** and **ESP32-A2DP** by Phil Schatzmann. WiFi, WebServer, ArduinoOTA and Preferences come with the ESP32 board package.
3. Open [main.ino](ossis/main/main.ino). Select the USB serial port and an **OTA-capable partition scheme** with space for the compiled application.
4. Verify and upload over USB for the first installation. Open Serial Monitor at **115200 baud**.
5. Pair with **ESP32 Bone Speaker** within 20 seconds of Bluetooth startup, or use the [OTA procedure](ossis/tests/T02_mono_ota/README.md#ota-procedure).

## Source notes

- We preserve test sketches as references and use `main.ino` for current work. Main and T02 share executable logic but retain legacy `Test 01`/`Test 02` labels.
- T01 and main/T02 share nominal DSP settings but use different peaking-filter coefficient helpers. See [T01 DSP settings](ossis/tests/T01_wroom_bt_a2dp/README.md).
