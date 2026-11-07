// ═══════════════════════════════════════════════════════════════════════════
//  BoneBuds Stereo HQ — ESP32 (38-pin) + Dual MAX98357A + Bone Transducers
//
//  Upgrades for Crystal-Clear High-Quality Stereo:
//   1. Single-Pass 32-bit Float DSP per channel (Left & Right isolated)
//      — Eliminates 3x int16<->float re-quantization hiss & buffer lag
//   2. Pre-Gain Headroom (-4.5 dB) + Soft-Knee Limiter
//      — Prevents +4 dB / +2.5 dB EQ boosts from overflowing int16_t
//   3. Fixed RBJ Audio EQ Cookbook math for Peaking & High-Shelf filters
//   4. ESP32 Hardware APLL enabled (use_apll = true) for low-jitter I2S clock
//
//  Pipeline: Bluetooth A2DP (Stereo) → StereoDSP (L/R Float Chain) → I2S DMA
// ═══════════════════════════════════════════════════════════════════════════

#include <Arduino.h>
#include <math.h>
#include "AudioTools.h"
#include "AudioTools/CoreAudio/AudioFilter/Filter.h"
#include "BluetoothA2DPSink.h"

// ── GPIO Pins (Unchanged — Wire both Left & Right MAX98357A to these) ──────
#define PIN_BCLK         26      // MAX98357A BCLK
#define PIN_WS           25      // MAX98357A LRC / WS
#define PIN_DOUT         22      // MAX98357A DIN

// ── Audio Format Settings ──────────────────────────────────────────────────
#define SAMPLE_RATE      44100
#define BITS_PER_SAMPLE  16
#define CHANNELS         2       // True 2-channel Stereo (Ch 0 = Left, Ch 1 = Right)

// ── Stereo Bone Conduction EQ Tuning ───────────────────────────────────────
#define PRE_GAIN_DB     -4.5f    // Headroom before EQ boosts (prevents digital clipping)
#define HP_FREQ          180.0f  // High-pass (Hz): stops transducer rattle, keeps warm upper-bass
#define HP_Q             0.7071f // Butterworth Q (flat passband, zero resonance bump)

#define PEAK_FREQ        2800.0f // Vocal/instrument presence center (Hz)
#define PEAK_GAIN_DB     4.0f    // Presence boost (dB)
#define PEAK_BW_OCT      0.8f    // Bandwidth in octaves

#define SHELF_FREQ       5500.0f // High-shelf corner (Hz) for stereo air & crispness
#define SHELF_GAIN_DB    2.5f    // High-shelf boost (dB)

#define MASTER_VOLUME    1.0f    // Post-EQ output scale (0.0 to 1.0)


// ═══════════════════════════════════════════════════════════════════════════
//  Direct Form II Transposed Biquad Section (32-bit Float)
// ═══════════════════════════════════════════════════════════════════════════
struct BiquadSection {
  float b0 = 1.0f, b1 = 0.0f, b2 = 0.0f;
  float a1 = 0.0f, a2 = 0.0f;
  float z1 = 0.0f, z2 = 0.0f;

  void setNormalized(float _b0, float _b1, float _b2, float _a0, float _a1, float _a2) {
    b0 = _b0 / _a0;
    b1 = _b1 / _a0;
    b2 = _b2 / _a0;
    a1 = _a1 / _a0;
    a2 = _a2 / _a0;
    z1 = 0.0f;
    z2 = 0.0f;
  }

  inline float process(float x) {
    float y = b0 * x + z1;
    z1 = b1 * x - a1 * y + z2;
    z2 = b2 * x - a2 * y;
    return y;
  }
};


// ═══════════════════════════════════════════════════════════════════════════
//  Single-Pass Per-Channel DSP (Pre-Gain → HPF → Peak → HighShelf → Limiter)
//  Each stereo channel (Left = 0, Right = 1) gets its own independent instance.
// ═══════════════════════════════════════════════════════════════════════════
class BoneChannelDSP : public Filter<float> {
public:
  BoneChannelDSP(float sampleRate) {
    configure(sampleRate);
  }

  void configure(float fs) {
    // 1. Pre-gain headroom + master volume combined
    preGain = powf(10.0f, PRE_GAIN_DB / 20.0f) * MASTER_VOLUME;

    // 2. Stage 1: 2nd-Order Butterworth High-Pass Filter (180 Hz)
    {
      float w0    = 2.0f * PI * HP_FREQ / fs;
      float cosw0 = cosf(w0);
      float alpha = sinf(w0) / (2.0f * HP_Q);

      float b0 =  (1.0f + cosw0) * 0.5f;
      float b1 = -(1.0f + cosw0);
      float b2 =  (1.0f + cosw0) * 0.5f;
      float a0 =   1.0f + alpha;
      float a1 =  -2.0f * cosw0;
      float a2 =   1.0f - alpha;
      hpf.setNormalized(b0, b1, b2, a0, a1, a2);
    }

    // 3. Stage 2: Peaking EQ (2.8 kHz, +4 dB, 0.8 Oct) — Fixed RBJ Formula
    {
      float A     = powf(10.0f, PEAK_GAIN_DB / 40.0f);
      float w0    = 2.0f * PI * PEAK_FREQ / fs;
      float sinw0 = sinf(w0);
      float cosw0 = cosf(w0);
      float alpha = sinw0 * sinhf((logf(2.0f) * 0.5f) * PEAK_BW_OCT * (w0 / sinw0));

      float b0 =  1.0f + alpha * A;
      float b1 = -2.0f * cosw0;
      float b2 =  1.0f - alpha * A;
      float a0 =  1.0f + alpha / A;
      float a1 = -2.0f * cosw0;
      float a2 =  1.0f - alpha / A;
      peak.setNormalized(b0, b1, b2, a0, a1, a2);
    }

    // 4. Stage 3: High-Shelf EQ (5.5 kHz, +2.5 dB, Slope = 1.0)
    {
      float A     = powf(10.0f, SHELF_GAIN_DB / 40.0f);
      float w0    = 2.0f * PI * SHELF_FREQ / fs;
      float sinw0 = sinf(w0);
      float cosw0 = cosf(w0);
      float alpha = sinw0 * 0.5f * sqrtf(2.0f); // S = 1.0
      float twoSqrtAAlpha = 2.0f * sqrtf(A) * alpha;

      float b0 =      A * ((A + 1.0f) + (A - 1.0f) * cosw0 + twoSqrtAAlpha);
      float b1 = -2.0f * A * ((A - 1.0f) + (A + 1.0f) * cosw0);
      float b2 =      A * ((A + 1.0f) + (A - 1.0f) * cosw0 - twoSqrtAAlpha);
      float a0 =           (A + 1.0f) - (A - 1.0f) * cosw0 + twoSqrtAAlpha;
      float a1 =    2.0f * ((A - 1.0f) - (A + 1.0f) * cosw0);
      float a2 =           (A + 1.0f) - (A - 1.0f) * cosw0 - twoSqrtAAlpha;
      shelf.setNormalized(b0, b1, b2, a0, a1, a2);
    }
  }

  float process(float in) override {
    // Run entire chain in 32-bit float (no intermediate int16 quantization)
    float s = in * preGain;
    s = hpf.process(s);
    s = peak.process(s);
    s = shelf.process(s);

    // Soft-knee saturation above 90% full scale to prevent harsh clipping
    const float threshold = 29490.0f; // 90% of 32767
    if (s > threshold) {
      s = threshold + (32767.0f - threshold) * tanhf((s - threshold) / (32767.0f - threshold));
    } else if (s < -threshold) {
      s = -threshold - (32767.0f - threshold) * tanhf((-s - threshold) / (32767.0f - threshold));
    }

    // Hard safety clamp so int16_t never wraps around
    if (s > 32767.0f)  s = 32767.0f;
    if (s < -32768.0f) s = -32768.0f;
    return s;
  }

private:
  float preGain = 1.0f;
  BiquadSection hpf;
  BiquadSection peak;
  BiquadSection shelf;
};


// ═══════════════════════════════════════════════════════════════════════════
//  Stream Pipeline: a2dp_sink → stereo_dsp → i2s_out
// ═══════════════════════════════════════════════════════════════════════════
I2SStream                      i2s_out;
FilteredStream<int16_t, float> stereo_dsp(i2s_out, CHANNELS);
BluetoothA2DPSink              a2dp_sink(stereo_dsp);

BoneChannelDSP* leftDSP  = nullptr;
BoneChannelDSP* rightDSP = nullptr;


// ═══════════════════════════════════════════════════════════════════════════
void setup() {
  Serial.begin(115200);
  AudioLogger::instance().begin(Serial, AudioLogger::Warning);
  Serial.println("[BoneBuds Stereo] Starting HQ pipeline...");

  // ── 1. Configure I2S Output with Hardware APLL (Low Jitter Stereo) ──────
  auto i2s_cfg            = i2s_out.defaultConfig(TX_MODE);
  i2s_cfg.pin_bck         = PIN_BCLK;
  i2s_cfg.pin_ws          = PIN_WS;
  i2s_cfg.pin_data        = PIN_DOUT;
  i2s_cfg.sample_rate     = SAMPLE_RATE;
  i2s_cfg.bits_per_sample = BITS_PER_SAMPLE;
  i2s_cfg.channels        = CHANNELS;
  i2s_cfg.use_apll        = true;   // Dedicated ESP32 Audio PLL for clean clock
  i2s_cfg.buffer_size     = 512;    // Large DMA buffers prevent BT underrun pops
  i2s_cfg.buffer_count    = 10;
  i2s_out.begin(i2s_cfg);

  // ── 2. Configure Independent Left & Right Float DSP Chains ──────────────
  AudioInfo info(SAMPLE_RATE, CHANNELS, BITS_PER_SAMPLE);
  leftDSP  = new BoneChannelDSP(SAMPLE_RATE);
  rightDSP = new BoneChannelDSP(SAMPLE_RATE);

  stereo_dsp.setFilter(0, leftDSP);   // Channel 0: Left Ear
  stereo_dsp.setFilter(1, rightDSP);  // Channel 1: Right Ear
  stereo_dsp.begin(info);

  // ── 3. Start Bluetooth A2DP Sink ────────────────────────────────────────
  a2dp_sink.set_volume(127);          // Full digital resolution from phone/PC
  a2dp_sink.start("BoneBuds Stereo HQ");
  Serial.println("[BoneBuds Stereo] Ready! Connect to \"BoneBuds Stereo HQ\"");
}


void loop() {
  // Audio processing runs on the high-priority A2DP/I2S FreeRTOS tasks
  delay(1000);
}
