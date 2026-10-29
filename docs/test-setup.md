# OSSIS bench setup

We use an ESP32-WROOM-32, one MAX98357A and two Adafruit 8 Ω, 1 W BCTs connected in parallel. A phone is our reference Bluetooth A2DP source. USB powers the board; a computer runs Arduino IDE for uploads.

## Connections

| ESP32-WROOM / source | MAX98357A |
| --- | --- |
| GPIO26 | BCLK / BCK |
| GPIO25 | LRC / WS |
| GPIO22 | DIN |
| Board 5V | VIN |
| GND | GND |
| 3V3 | SD / MODE |
| Unconnected | GAIN |
| Both BCT positive leads | SPK+ |
| Both BCT negative leads | SPK− |

The two 8 Ω BCTs share one amplifier output in parallel, giving a nominal 4 Ω load. This is shared mono output. T03 will test independent left/right channels with two amplifiers.

[Wiring diagram](../images/diagrams/ossis-wiring.svg) · [Original T01 single-BCT wiring](../images/diagrams/t01-wiring.svg)

## Firmware

> **Main firmware:** [main.ino](../code/ossis/main/main.ino) holds our latest tested build, currently **T02 (Bluetooth + OTA)**.

[Upload guide](../code/README.md) · [T01 playback](../code/ossis/tests/T01_wroom_bt_a2dp/README.md) · [T02 OTA](../code/ossis/tests/T02_mono_ota/README.md) · [Test results](test-results.md)
