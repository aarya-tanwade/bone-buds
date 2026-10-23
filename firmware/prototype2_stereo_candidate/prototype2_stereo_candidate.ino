// Bone Buds Rev A stereo bring-up candidate. NOT compiled or hardware-tested.
// Requires Arduino-ESP32 ESP_I2S.h, as used by the preserved Prototype 1 sketch.
// First use dummy loads. Verify SD_MODE voltages before connecting transducers.
#include <Arduino.h>
#include <ESP_I2S.h>

constexpr int MIC_BCLK=7, MIC_WS=8, MIC_SD=9;
constexpr int AMP_BCLK=4, AMP_WS=5, AMP_DOUT=6, AUDIO_EN=10;
constexpr int SAMPLE_RATE=16000;
constexpr int32_t PCM_LIMIT=4096; // Conservative bring-up ceiling, not a calibrated SPL limit.
I2SClass MicI2S, AmpI2S;
int32_t micBuffer[256];
int16_t audioBuffer[256];
bool enabled=false;
float gain=0.05f;

void mute() { digitalWrite(AUDIO_EN,LOW); enabled=false; }
void setup() {
  digitalWrite(AUDIO_EN,LOW); pinMode(AUDIO_EN,OUTPUT);
  Serial.begin(115200);
  MicI2S.setPins(MIC_BCLK,MIC_WS,-1,MIC_SD);
  AmpI2S.setPins(AMP_BCLK,AMP_WS,AMP_DOUT,-1);
  bool rx=MicI2S.begin(I2S_MODE_STD,SAMPLE_RATE,I2S_DATA_BIT_WIDTH_32BIT,I2S_SLOT_MODE_STEREO);
  bool tx=AmpI2S.begin(I2S_MODE_STD,SAMPLE_RATE,I2S_DATA_BIT_WIDTH_16BIT,I2S_SLOT_MODE_STEREO);
  if (!rx || !tx) { mute(); Serial.println("I2S init failed; MUTED"); while(true) delay(1000); }
  memset(audioBuffer,0,sizeof(audioBuffer));
  AmpI2S.write((uint8_t*)audioBuffer,sizeof(audioBuffer));
  Serial.println("Stereo ready, muted. e=enable; m=mute; +/-=small gain step (0..0.1).");
}
void loop() {
  if (Serial.available()) {
    char c=Serial.read();
    if(c=='m') mute();
    if(c=='e') {enabled=true; digitalWrite(AUDIO_EN,HIGH);}
    if(c=='+') gain=min(0.10f,gain+0.005f);
    if(c=='-') gain=max(0.0f,gain-0.005f);
  }
  size_t bytes=MicI2S.readBytes((char*)micBuffer,sizeof(micBuffer));
  if(bytes==0 || bytes%8!=0) { mute(); return; }
  size_t samples=bytes/sizeof(int32_t);
  for(size_t i=0;i<samples;i++) { // Keep BOTH L,R samples; Prototype 1 discarded R.
    int32_t pcm=(int32_t)((micBuffer[i]>>16)*gain);
    pcm=max(-PCM_LIMIT,min(PCM_LIMIT,pcm));
    audioBuffer[i]=enabled ? (int16_t)pcm : 0;
  }
  size_t expected=samples*sizeof(int16_t);
  if(AmpI2S.write((uint8_t*)audioBuffer,expected)!=expected) mute();
}
