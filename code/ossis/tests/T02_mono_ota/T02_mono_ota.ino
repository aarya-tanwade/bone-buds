
/*
  ====================================================
  BONEBUDS - TEST 02
  SINGLE BCT + MAX98357A + ESP32-WROOM-32

  Stable Bluetooth Audio + WiFi OTA

  MODE 1: Bluetooth audio only
  MODE 2: WiFi OTA only

  No simultaneous BT/WiFi radio usage.
  No OTA timeout.
  No physical button needed.

  GPIO:
    BCLK = 26
    WS   = 25
    DIN  = 22
  ====================================================
*/

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoOTA.h>
#include <Preferences.h>
#include <math.h>

#include "AudioTools.h"
#include "AudioTools/CoreAudio/AudioFilter/Filter.h"
#include "BluetoothA2DPSink.h"

// ================= GPIO =================

#define PIN_BCLK 26
#define PIN_WS   25
#define PIN_DOUT 22

// ================= AUDIO =================

#define SAMPLE_RATE      44100
#define BITS_PER_SAMPLE  16
#define CHANNELS         2

#define HP_FREQ          200.0f
#define PEAK_FREQ       2800.0f
#define PEAK_GAIN          4.0f
#define PEAK_BW            0.8f
#define SHELF_FREQ      5000.0f
#define SHELF_GAIN         2.0f
#define VOLUME             1.0f

// ================= OTA =================

// CHANGE BOTH PASSWORDS

const char* OTA_SSID = "BoneBuds-OTA";

const char* OTA_WIFI_PASS =
  "BoneBuds2026";

const char* OTA_UPLOAD_PASS =
  "BoneBudsUpdate2026";

const char* OTA_HOSTNAME = "bonebuds-test01";

const char* BT_NAME = "ESP32 Bone Speaker";

// ================= MODE SYSTEM =================

#define MODE_BLUETOOTH 0
#define MODE_OTA       1

// Initial Bluetooth pairing opportunity.
// After this, disconnected device enters OTA mode.
#define BT_PAIR_WINDOW_MS 20000UL

// After an established Bluetooth connection drops.
#define BT_DISCONNECT_DELAY_MS 3000UL

uint8_t currentMode = MODE_BLUETOOTH;

bool everConnected = false;
bool previousBT = false;
bool otaUpdating = false;

uint32_t btStartedAt = 0;
uint32_t disconnectedAt = 0;

WebServer server(80);

// ================= PEAK EQ =================

void makePeakEQ(
  float freq,
  float sampleRate,
  float gainDB,
  float bandwidth,
  float (&b)[3],
  float (&a)[3]
) {
  float A = powf(10.0f, gainDB / 40.0f);
  float w0 = 2.0f * PI * freq / sampleRate;

  float sw = sinf(w0);
  float cw = cosf(w0);

  float alpha = sw * sinhf(
    (logf(2.0f) / 2.0f) * bandwidth * w0 / sw
  );

  b[0] = 1.0f + alpha * A;
  b[1] = -2.0f * cw;
  b[2] = 1.0f - alpha * A;

  a[0] = 1.0f + alpha / A;
  a[1] = -2.0f * cw;
  a[2] = 1.0f - alpha / A;
}

// ================= AUDIO PIPELINE =================

I2SStream i2s_out;

VolumeStream vol(i2s_out);

FilteredStream<int16_t, float>
  shelf(vol, CHANNELS);

FilteredStream<int16_t, float>
  peak(shelf, CHANNELS);

FilteredStream<int16_t, float>
  hp(peak, CHANNELS);

BluetoothA2DPSink a2dp_sink(hp);

// ================= MODE STORAGE =================

uint8_t readMode() {
  Preferences prefs;

  if (!prefs.begin("bonebuds", true)) {
    return MODE_BLUETOOTH;
  }

  uint8_t mode = prefs.getUChar(
    "bootmode", MODE_BLUETOOTH
  );

  prefs.end();

  return mode == MODE_OTA
           ? MODE_OTA
           : MODE_BLUETOOTH;
}

void saveMode(uint8_t mode) {
  Preferences prefs;

  if (prefs.begin("bonebuds", false)) {
    prefs.putUChar("bootmode", mode);
    prefs.end();
  }
}

void switchMode(uint8_t mode) {
  if (otaUpdating) {
    Serial.println("[SYSTEM] Update in progress");
    return;
  }

  if (mode == currentMode) return;

  Serial.printf(
    "[SYSTEM] Switching to mode %u\n",
    (unsigned int)mode
  );

  saveMode(mode);

  Serial.println("[SYSTEM] Restarting for clean radio switch");

  Serial.flush();
  delay(300);

  ESP.restart();
}

// ================= BLUETOOTH AUDIO =================

void startBluetooth() {

  Serial.println("[BT] Starting Bluetooth mode");

  // Completely disable WiFi.
  WiFi.mode(WIFI_OFF);

  auto cfg = i2s_out.defaultConfig(TX_MODE);

  cfg.pin_bck = PIN_BCLK;
  cfg.pin_ws = PIN_WS;
  cfg.pin_data = PIN_DOUT;

  cfg.sample_rate = SAMPLE_RATE;
  cfg.bits_per_sample = BITS_PER_SAMPLE;
  cfg.channels = CHANNELS;

  cfg.buffer_size = 512;
  cfg.buffer_count = 8;

  if (!i2s_out.begin(cfg)) {
    Serial.println("[ERROR] I2S failed");

    while (true) {
      delay(1000);
    }
  }

  auto vcfg = vol.defaultConfig();

  vcfg.sample_rate = SAMPLE_RATE;
  vcfg.channels = CHANNELS;
  vcfg.bits_per_sample = BITS_PER_SAMPLE;

  vol.begin(vcfg);
  vol.setVolume(VOLUME);

  AudioInfo info(
    SAMPLE_RATE,
    CHANNELS,
    BITS_PER_SAMPLE
  );

  // High shelf: 5 kHz, +2 dB
  shelf.setFilter(
    0,
    new HighShelfFilter<float>(
      SHELF_FREQ, SAMPLE_RATE, SHELF_GAIN
    )
  );

  shelf.setFilter(
    1,
    new HighShelfFilter<float>(
      SHELF_FREQ, SAMPLE_RATE, SHELF_GAIN
    )
  );

  shelf.begin(info);

  // Peak: 2.8 kHz, +4 dB
  float b[3], a[3];

  makePeakEQ(
    PEAK_FREQ,
    SAMPLE_RATE,
    PEAK_GAIN,
    PEAK_BW,
    b,
    a
  );

  peak.setFilter(
    0, new BiQuadDF2<float>(b, a)
  );

  peak.setFilter(
    1, new BiQuadDF2<float>(b, a)
  );

  peak.begin(info);

  // High pass: 200 Hz
  hp.setFilter(
    0,
    new HighPassFilter<float>(
      HP_FREQ, SAMPLE_RATE
    )
  );

  hp.setFilter(
    1,
    new HighPassFilter<float>(
      HP_FREQ, SAMPLE_RATE
    )
  );

  hp.begin(info);

  Serial.println("[AUDIO] EQ initialized");
  Serial.println("[AUDIO] Volume unchanged");

  a2dp_sink.set_volume(127);

  a2dp_sink.start(BT_NAME);

  btStartedAt = millis();

  Serial.println("[BT] READY");
  Serial.print("[BT] Device: ");
  Serial.println(BT_NAME);

  Serial.println("[WIFI] OFF");
  Serial.printf(
    "[MEMORY] Free heap: %u\n",
    (unsigned int)ESP.getFreeHeap()
  );
}

// ================= OTA WEB PAGE =================

void handleHome() {

  String page =
    "<!DOCTYPE html>"
    "<html>"
    "<head>"
    "<meta name='viewport' "
    "content='width=device-width,initial-scale=1'>"
    "<title>BoneBuds OTA</title>"
    "</head>"
    "<body style='font-family:Arial;"
    "max-width:500px;margin:40px auto;"
    "padding:20px'>"
    "<h2>BoneBuds</h2>"
    "<p>Test 01 - Wireless Firmware Mode</p>"
    "<p>OTA server is running.</p>"
    "<p>Upload firmware using Arduino IDE "
    "or espota.py on port 3232.</p>"
    "<hr>"
    "<p>To return to Bluetooth audio:</p>"
    "<form method='POST' action='/bluetooth'>"
    "<button style='padding:14px;font-size:16px'>"
    "Start Bluetooth</button>"
    "</form>"
    "</body></html>";

  server.send(200, "text/html", page);
}

// ================= WIFI OTA =================

void startOTA() {

  Serial.println("[OTA] Starting WiFi-only mode");

  // No Bluetooth stack is started in this boot.
  WiFi.mode(WIFI_AP);

  bool ok = WiFi.softAP(
    OTA_SSID,
    OTA_WIFI_PASS,
    1,
    0,
    1
  );

  if (!ok) {
    Serial.println("[ERROR] WiFi AP failed");
    return;
  }

  ArduinoOTA.setHostname(OTA_HOSTNAME);
  ArduinoOTA.setPort(3232);
  ArduinoOTA.setPassword(OTA_UPLOAD_PASS);

  ArduinoOTA.onStart([]() {
    otaUpdating = true;

    Serial.println("[OTA] Upload started");
  });

  ArduinoOTA.onProgress(
    [](unsigned int done, unsigned int total) {

      static uint32_t lastPrint = 0;

      if (total > 0 &&
          millis() - lastPrint >= 600) {

        Serial.printf(
          "[OTA] %u%%\n",
          (unsigned int)(
            100ULL * done / total
          )
        );

        lastPrint = millis();
      }
    }
  );

  ArduinoOTA.onEnd([]() {

    Serial.println("[OTA] Upload complete");

    // Run Bluetooth after successful update.
    saveMode(MODE_BLUETOOTH);  });

  ArduinoOTA.onError([](ota_error_t error) {

    Serial.printf(
      "[OTA] Error: %u\n",
      (unsigned int)error
    );

    otaUpdating = false;
  });

  ArduinoOTA.begin();

  server.on("/", HTTP_GET, handleHome);

  server.on("/bluetooth", HTTP_POST, []() {

    if (otaUpdating) {
      server.send(
        409, "text/plain",
        "Firmware update in progress"
      );
      return;
    }

    server.send(
      200, "text/plain",
      "Switching to Bluetooth. Reconnect your phone."
    );

    server.client().flush();

    delay(300);

    switchMode(MODE_BLUETOOTH);
  });

  server.begin();

  Serial.println();
  Serial.println("==============================");
  Serial.println("BONEBUDS OTA MODE ACTIVE");
  Serial.println("==============================");

  Serial.print("[OTA] SSID: ");
  Serial.println(OTA_SSID);

  Serial.print("[OTA] IP: ");
  Serial.println(WiFi.softAPIP());

  Serial.println("[OTA] Port: 3232");
  Serial.println("[OTA] No timeout");
  Serial.println("[BT] OFF");

  Serial.println("[WEB] http://192.168.4.1");

  Serial.printf(
    "[MEMORY] Free heap: %u\n",
    (unsigned int)ESP.getFreeHeap()
  );
}

// ================= SETUP =================

void setup() {

  Serial.begin(115200);
  delay(500);

  AudioLogger::instance().begin(
    Serial,
    AudioLogger::Warning
  );

  Serial.println();
  Serial.println("==============================");
  Serial.println("BONEBUDS TEST 01 - STABLE OTA");
  Serial.println("==============================");

  Serial.printf(
    "[SYSTEM] Reset reason: %d\n",
    (int)esp_reset_reason()
  );

  currentMode = readMode();

  if (currentMode == MODE_OTA) {
    startOTA();
  } else {
    startBluetooth();
  }
}

// ================= LOOP =================

void loop() {

  // ---------------- OTA MODE ----------------
  if (currentMode == MODE_OTA) {

    ArduinoOTA.handle();
    server.handleClient();

    delay(5);
    return;
  }

  // -------------- BLUETOOTH MODE ------------
  bool connected = a2dp_sink.is_connected();

  if (connected != previousBT) {

    previousBT = connected;

    if (connected) {

      everConnected = true;
      disconnectedAt = 0;

      Serial.println("[BT] CONNECTED");
      Serial.println("[WIFI] OFF");

    } else {

      disconnectedAt = millis();

      Serial.println("[BT] DISCONNECTED");
    }
  }

  if (connected) {
    delay(20);
    return;
  }

  // If phone was previously connected,
  // switch to continuous OTA after disconnection.
  if (everConnected) {

    if (disconnectedAt != 0 &&
        millis() - disconnectedAt >=
          BT_DISCONNECT_DELAY_MS) {

      switchMode(MODE_OTA);
    }

  } else {

    // At first boot, allow pairing before entering OTA.
    if (millis() - btStartedAt >=
        BT_PAIR_WINDOW_MS) {

      Serial.println("[BT] No phone connected");
      switchMode(MODE_OTA);
    }
  }

  delay(20);
}
