# Bone Buds - Rev B | Compact custom-IC design

**Status:** Preliminary engineering design / Stage 2. Not fabrication-validated.

This is **one wearable hardware revision** composed of three PCB projects:

- **controller** - central SoC, power, charging and system interconnects.
- **audio_left** - left-side audio electronics.
- **audio_right** - right-side audio electronics.

## Contents

- `pcb/controller/`, `pcb/audio_left/`, `pcb/audio_right/`: editable KiCad schematic + board + project files.
- `pcb/BoneBuds.pretty/`, `pcb/BoneBuds.kicad_sym`, `pcb/models/`: custom library/model resources.
- `mechanical/`: CAD build scripts and real STEP/STL exports for the assembled wearable.
- `exports/`: schematic PDFs and design visualization images.
- `documentation/`: DRC/ERC reports, design data, CAD checks and other engineering notes.
- `tools/`: scripts used to generate or inspect the design.
- `sources/`: part datasheets / reference material.

## Engineering cautions

1. ERC/DRC reports are design-rule checks, **not electrical, RF or clinical qualification**.
2. Purchased component dimensions, microphone acoustic routing, battery safety,
   antenna performance, enclosure comfort and transducer contact require physical validation.
3. Before ordering PCBs: reopen all three designs in KiCad, review the actual
   ERC/DRC reports, verify parts and footprints, and regenerate manufacturing outputs.
4. Manufacturing exports are intentionally kept local until reviewed.
5. An empty `mechanical/fusion/` folder does not establish that a native Fusion design was made.
   The available STEP/STL and CAD scripts are the currently identified artifacts.
