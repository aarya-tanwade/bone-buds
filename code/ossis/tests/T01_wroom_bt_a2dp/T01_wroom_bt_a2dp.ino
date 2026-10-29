// ═══════════════════════════════════════════════════════════════════
//  BoneBuds — ESP32 38-pin + MAX98357A + Bone Conduction Transducer
//  Fixes: hiss/noise, underwater sound, random pops, muddy audio
//
//  Pipeline: A2DP BT → HighPass(200Hz) → Peak(2.8kHz +4dB)
//                     → HighShelf(5kHz +2dB) → Volume → I2S
// ═══════════════════════════════════════════════════════════════════

#include "AudioTools.h"
#include "AudioTools/CoreAudio/AudioFilter/Filter.h"
#include "BluetoothA2DPSink.h"

// ── GPIO pins (DO NOT CHANGE) ──────────────────────────────────────
#define PIN_BCLK   26    // MAX98357A BCLK
#define PIN_WS     25    // MAX98357A LRC / WS
#define PIN_DOUT   22    // MAX98357A DIN

// ── Audio quality settings ─────────────────────────────────────────
#define SAMPLE_RATE      44100
#define BITS_PER_SAMPLE  16
#define CHANNELS         2      // Stereo in; MAX98357A mixes to mono

// ── EQ tuning ──────────────────────────────────────────────────────
#define HP_FREQ          200.0f   // High-pass cutoff Hz — cuts DC rumble
#define PEAK_FREQ       2800.0f   // Presence boost center — bone conduction clarity
#define PEAK_GAIN          4.0f   // Presence boost dB — lowered from +8dB to prevent noise floor amplification
#define PEAK_BW            0.8f   // Peaking bandwidth (octaves)
#define SHELF_FREQ      5000.0f   // High-shelf cutoff Hz — high frequencies
#define SHELF_GAIN         2.0f   // High-shelf gain dB — lowered from +4dB to control hiss
#define VOLUME             1.0f   // Master volume (1.0 = full output)


// ── Peaking EQ helper (Audio EQ Cookbook formula) ─────────────────
// Library has no PeakingEqFilter, so we compute coefficients manually
// and pass them to BiQuadDF2 directly.
// gain_db: positive = boost, negative = cut
// bw_oct:  bandwidth in octaves (0.5–2.0 is typical)
void makePeakEQ(float freq, float sampleRate, float gain_db, float bw_oct,
                float (&b)[3], float (&a)[3]) {
  float A  = pow(10.0f, gain_db / 40.0f);
  float w0 = 2.0f * PI * freq / sampleRate;
  float bw_rad = bw_oct * w0 / (2.0f * log(2.0f));  // convert octaves to rad
  float sinw0 = sin(w0);
  float cosw0 = cos(w0);
  float alpha = sinw0 * sinh(bw_rad);                // BW version of alpha

  b[0] =  1.0f + alpha * A;
  b[1] = -2.0f * cosw0;
  b[2] =  1.0f - alpha * A;
  a[0] =  1.0f + alpha / A;
  a[1] = -2.0f * cosw0;
  a[2] =  1.0f - alpha / A;
}


// ═══════════════════════════════════════════════════════════════════
//  Audio pipeline (declared back-to-front: each wraps the next)
//
//  a2dp_sink → f1_hp → f2_peak → f3_shelf → vol → i2s_out
// ═══════════════════════════════════════════════════════════════════
I2SStream                              i2s_out;
VolumeStream                           vol(i2s_out);
FilteredStream<int16_t, float>         f3_shelf(vol, CHANNELS);     // Stage 3
FilteredStream<int16_t, float>         f2_peak(f3_shelf, CHANNELS); // Stage 2
FilteredStream<int16_t, float>         f1_hp(f2_peak, CHANNELS);    // Stage 1
BluetoothA2DPSink                      a2dp_sink(f1_hp);


// ═══════════════════════════════════════════════════════════════════
void setup() {
  Serial.begin(115200);
  AudioLogger::instance().begin(Serial, AudioLogger::Warning);
  Serial.println("[BoneBuds] Starting...");

  // ── I2S output ────────────────────────────────────────────────────
  auto i2s_cfg             = i2s_out.defaultConfig(TX_MODE);
  i2s_cfg.pin_bck          = PIN_BCLK;
  i2s_cfg.pin_ws           = PIN_WS;
  i2s_cfg.pin_data         = PIN_DOUT;
  i2s_cfg.sample_rate      = SAMPLE_RATE;
  i2s_cfg.bits_per_sample  = BITS_PER_SAMPLE;
  i2s_cfg.channels         = CHANNELS;
  i2s_cfg.buffer_size      = 512;   // larger = fewer underrun pops
  i2s_cfg.buffer_count     = 8;
  i2s_out.begin(i2s_cfg);
  Serial.println("[BoneBuds] I2S ready");

  // ── Volume ────────────────────────────────────────────────────────
  auto v_cfg            = vol.defaultConfig();
  v_cfg.sample_rate     = SAMPLE_RATE;
  v_cfg.channels        = CHANNELS;
  v_cfg.bits_per_sample = BITS_PER_SAMPLE;
  vol.begin(v_cfg);
  vol.setVolume(VOLUME);

  // ── Shared AudioInfo for filter stages ───────────────────────────
  AudioInfo info(SAMPLE_RATE, CHANNELS, BITS_PER_SAMPLE);

  // ── EQ Stage 3: HighShelfFilter +2dB above 5kHz ──────────────────
  //   Reduced to +2dB to control hiss
  f3_shelf.setFilter(0, new HighShelfFilter<float>(SHELF_FREQ, SAMPLE_RATE, SHELF_GAIN));
  f3_shelf.setFilter(1, new HighShelfFilter<float>(SHELF_FREQ, SAMPLE_RATE, SHELF_GAIN));
  f3_shelf.begin(info);

  // ── EQ Stage 2: Peaking +4dB at 2.8kHz (bone conduction clarity) ─
  //   Reduced to +4dB to avoid amplifying noise floor
  float pb[3], pa[3];
  makePeakEQ(PEAK_FREQ, SAMPLE_RATE, PEAK_GAIN, PEAK_BW, pb, pa);
  f2_peak.setFilter(0, new BiQuadDF2<float>(pb, pa));
  f2_peak.setFilter(1, new BiQuadDF2<float>(pb, pa));
  f2_peak.begin(info);

  // ── EQ Stage 1: HighPassFilter 200Hz ─────────────────────────────
  //   Cuts DC offset, hum, sub-bass that makes bone transducer buzz
  f1_hp.setFilter(0, new HighPassFilter<float>(HP_FREQ, SAMPLE_RATE));
  f1_hp.setFilter(1, new HighPassFilter<float>(HP_FREQ, SAMPLE_RATE));
  f1_hp.begin(info);

  Serial.println("[BoneBuds] EQ pipeline ready");

  // ── Bluetooth A2DP Sink ──────────────────────────────────────────
  // ESP32-A2DP sink set_volume accepts 0..127 (127 = 100% full volume)
  a2dp_sink.set_volume(127);
  a2dp_sink.start("ESP32 Bone Speaker");
  Serial.println("[BoneBuds] Ready! Connect to \"ESP32 Bone Speaker\"");
}


void loop() {
  // A2DP runs on its own FreeRTOS task — nothing needed here.
}
