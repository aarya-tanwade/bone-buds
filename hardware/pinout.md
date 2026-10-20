# Prototype 1 — Pinout

Firmware: [`firmware/prototype1/prototype1.ino`](../firmware/prototype1/prototype1.ino)

## INMP441 microphone → ESP32-S3

| INMP441 signal | ESP32-S3 |
| --- | --- |
| SCK / BCLK | GPIO 7 |
| WS / LRCLK | GPIO 8 |
| SD / DOUT | GPIO 9 |
| L/R | GND (left channel selected in firmware) |

## MAX98357A amplifier ← ESP32-S3

| MAX98357A signal | ESP32-S3 |
| --- | --- |
| BCLK | GPIO 4 |
| LRC / WS | GPIO 5 |
| DIN | GPIO 6 |

The amplifier drives the bone-conduction transducer; **do not** connect the transducer directly to an ESP32-S3 GPIO.

Connect compatible module power and a shared ground according to the boards' specifications. The pin tables above are the **signal pins defined in Prototype 1**, not a complete power-wiring diagram.

## Audio configuration

- Sample rate: **16,000 Hz**
- Microphone input: **32-bit stereo I2S**, using the left channel
- Amplifier output: **16-bit mono I2S**
- Gain control: **0.70–1.30**, step **0.02**

## Testing note

Transducer position and contact have a noticeable effect on perceived output. Early testing found better coupling behind the ear. Record observations and measurements in the [development log](../docs/progress.md).
