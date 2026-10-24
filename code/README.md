# Firmware

## Verified experiment

| Test | Platform | Record |
| --- | --- | --- |
| T01: Bluetooth A2DP audio playback | ESP32-WROOM-32 | [Source and instructions](alpha-0.1/tests/T01_wroom_bt_a2dp/README.md) |

The T01 sketch is an unchanged copy of `prototype1/prototype1.ino`, confirmed by the project owner as the successful test source on 2026-10-25. The original remains in place for review. Its folder name does not mean Prototype 1 is complete. It contains WROOM A2DP firmware, not S3 microphone loopback.

Source comments describe intended DSP benefits and automatic mono mixing. Those comments are preserved as historical source, not accepted as measured results. See [setup qualifications](../docs/test-setup.md).

Earlier S3 and alternative WROOM experiments outside this repository remain untouched. They are not verified entries in this collection.

## Adding a verified test

Assign the next sequential ID only after confirming the hardware result. Put the sketch in `alpha-0.1/tests/Txx_descriptive_name/`, with a matching `.ino` filename and a short README. Record the exact source, dependencies, wiring, procedure, limitations and evidence. Add the result to [test-results.md](../docs/test-results.md) and a dated entry to [development-log.md](../docs/development-log.md). Do not create empty future test folders.
