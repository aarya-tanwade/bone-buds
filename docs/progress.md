# Development Log

Add dated entries here as the hardware, firmware, and test results change. Keep observed results separate from ideas and planned work.

## 2026-10-20 — Repository organization

- Added hardware pinout, roadmap, and a running development log.
- Kept `firmware/prototype1/prototype1.ino` unchanged.
- Next: record repeatable noise/latency observations and hardware adjustments.

## 2026-10-18 — Prototype 1 firmware

- Added ESP32-S3 live microphone-to-transducer audio loopback.
- INMP441 input, MAX98357A output, and adjustable serial gain (`+`, `-`, `0`).
- Firmware settings: 16 kHz; left-channel microphone input; 16-bit mono output.

## Early hardware observations

- Transducer contact/placement noticeably affects audible output; placement behind the ear gave better results during initial testing.
- The INMP441 captures distant ambient sound as well as nearby speech, making noise suppression important.
- A separate Bluetooth A2DP experiment on a 38-pin ESP32 board produced audible audio but significant noise; it is **not** part of the current ESP32-S3 microphone firmware.

## Template for future updates

### YYYY-MM-DD — Change title

- **Changed:** Hardware, firmware, or documentation changes.
- **Tested:** Setup, conditions, and what was measured/observed.
- **Result:** Worked, failed, or still uncertain.
- **Next:** Single next action.
