# Development Roadmap

Status labels describe project work, not validated product performance.

## Stage 1 — Hardware and audio baseline

- [x] ESP32-S3 + INMP441 microphone input
- [x] MAX98357A + bone-conduction output
- [x] Live audio loopback with serial-controlled gain (`prototype1`)
- [ ] Repeatable noise, level, and latency tests
- [ ] Improve microphone and transducer placement
- [ ] Compare available transducers and document results
- [ ] Test multi-microphone input and independent left/right outputs

## Stage 2 — Selective listening

- [ ] Evaluate direction-based target selection and beamforming
- [ ] Explore speech enhancement with competing speakers/noise
- [ ] Assess speech clarity in realistic listening scenarios

## Stage 3 — Safety sound awareness and personalization

- [ ] Detect horns, sirens, and alarms
- [ ] Estimate left/right direction and provide an appropriate audio cue
- [ ] Explore a user-guided pure-tone hearing profile (initial frequencies: 500 Hz, 1 kHz, 2 kHz, 4 kHz)
- [ ] Apply frequency-dependent gain/EQ; separate left/right profiles when hardware supports them

## Stage 4 — Integration and testing

- [ ] Combine audio processing, directional alerts, and profiles
- [ ] Evaluate speech clarity, detection accuracy, direction cues, latency, power use, and user feedback

## Exploratory

- [ ] Study whether transducer placement/contact changes can be detected and compensated

**Scope note:** The guided tone test is intended for prototype personalization only, not clinical diagnosis. These planned capabilities are not claimed as implemented.
