# Bone Buds

**Intelligent Bone Conduction Hearing Assistance Device**

Bone Buds is an experimental ESP32-S3 project exploring clearer speech, awareness of important surrounding sounds, and personalized audio through bone conduction.

**Current status:** Prototype 1 — single-microphone live audio loopback with adjustable gain. Selective listening, sound detection, and hearing profiles are **planned**, not yet part of the firmware.

## Prototype 1

```text
INMP441 microphone → ESP32-S3 → MAX98357A amplifier → Bone-conduction transducer
```

| Component | Current hardware |
| --- | --- |
| Microcontroller | ESP32-S3 N16R8 |
| Microphone | INMP441 I2S MEMS |
| Amplifier | MAX98357A I2S |
| Output | 8 Ω, 1 W bone-conduction transducer |

The existing sketch runs at **16 kHz**, reads the microphone's left channel, converts samples to 16-bit audio, applies adjustable gain, and outputs mono audio.

## Run the firmware


1. Install Arduino IDE and the ESP32 board package that supports `ESP_I2S.h` (Arduino-ESP32 3.x).
2. Open [`firmware/prototype1/prototype1.ino`](firmware/prototype1/prototype1.ino).
3. Select your ESP32-S3 board and serial port, then upload.
4. Open Serial Monitor at **115200 baud**.

| Serial input | Action |
| --- | --- |
| `+` | Increase gain by 0.02 |
| `-` | Decrease gain by 0.02 |
| `0` | Reset gain to 1.00 |

Gain is limited to **0.70–1.30**. Start with a low, comfortable output level.

See [hardware pinout](hardware/pinout.md) before wiring.

## Repository structure

```text
bone-buds/
├── firmware/
│   └── prototype1/
│       └── prototype1.ino
├── hardware/
│   └── pinout.md
├── docs/
│   ├── progress.md
│   └── roadmap.md
├── images/
│   └── README.md
└── README.md
```

## Development

- **Current:** Improve the audio baseline, microphone/transducer placement, and noise performance.
- **Next:** Evaluate multiple microphones and independent left/right output paths.
- **Planned:** Selective speech enhancement, detection and direction cues for important sounds, and user-guided frequency-specific personalization.
- **Exploratory:** Study how transducer placement and contact affect output.

Follow the [development log](docs/progress.md) for changes and the [roadmap](docs/roadmap.md) for milestones.

## Disclaimer

This is an engineering research prototype, **not** a certified hearing aid or a clinical audiometry device.

## Hardware design

Current Rev B hardware and CAD: [hardware/README.md](hardware/README.md).

