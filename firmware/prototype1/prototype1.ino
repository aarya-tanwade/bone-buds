#include <Arduino.h>
#include <ESP_I2S.h>

// =====================================================
// INMP441 MICROPHONE
// =====================================================
#define MIC_BCLK 7
#define MIC_WS   8
#define MIC_SD   9

// =====================================================
// MAX98357A AMPLIFIER
// =====================================================
#define AMP_BCLK 4
#define AMP_WS   5
#define AMP_DOUT 6

// =====================================================
// AUDIO SETTINGS
// =====================================================
#define SAMPLE_RATE 16000

// =====================================================
// GAIN CONTROL
// Useful range found by testing: ~0.90 to 1.10
// Step and limits set tight around that range for fine control.
// =====================================================

float gain = 1.0f;

const float GAIN_STEP = 0.02f;
const float GAIN_MAX  = 1.3f;   // headroom above the useful range
const float GAIN_MIN  = 0.7f;   // headroom below the useful range

void printGain()
{
    Serial.print("Gain: ");
    Serial.println(gain, 2);
}

void handleSerialInput()
{
    if (Serial.available() > 0)
    {
        char c = Serial.read();

        if (c == '+')
        {
            gain += GAIN_STEP;

            if (gain > GAIN_MAX)
                gain = GAIN_MAX;

            printGain();
        }
        else if (c == '-')
        {
            gain -= GAIN_STEP;

            if (gain < GAIN_MIN)
                gain = GAIN_MIN;

            printGain();
        }
        else if (c == '0')
        {
            gain = 1.0f;
            printGain();
        }
    }
}

I2SClass MicI2S;
I2SClass AmpI2S;

int32_t micBuffer[256];
int16_t audioBuffer[128];

void setup()
{
    Serial.begin(115200);
    delay(2000);

    Serial.println();
    Serial.println("==============================================");
    Serial.println(" ESP32-S3 LIVE MICROPHONE LOOPBACK + GAIN");
    Serial.println(" INMP441 -> ESP32-S3 -> MAX98357A");
    Serial.println("==============================================");
    Serial.println();
    Serial.println("Controls: '+' increase gain, '-' decrease, '0' reset to 1.0");
    Serial.println();

    // =================================================
    // MICROPHONE I2S
    // =================================================

    Serial.println("Initializing INMP441...");

    MicI2S.setPins(
        MIC_BCLK,
        MIC_WS,
        -1,
        MIC_SD
    );

    bool micOK = MicI2S.begin(
        I2S_MODE_STD,
        SAMPLE_RATE,
        I2S_DATA_BIT_WIDTH_32BIT,
        I2S_SLOT_MODE_STEREO
    );

    if (!micOK)
    {
        Serial.println("ERROR: INMP441 initialization FAILED!");

        while (true)
        {
            delay(1000);
        }
    }

    Serial.println("INMP441 initialization SUCCESSFUL.");
    Serial.println();

    // =================================================
    // MAX98357A I2S
    // =================================================

    Serial.println("Initializing MAX98357A...");

    AmpI2S.setPins(
        AMP_BCLK,
        AMP_WS,
        AMP_DOUT,
        -1
    );

    bool ampOK = AmpI2S.begin(
        I2S_MODE_STD,
        SAMPLE_RATE,
        I2S_DATA_BIT_WIDTH_16BIT,
        I2S_SLOT_MODE_MONO
    );

    if (!ampOK)
    {
        Serial.println("ERROR: MAX98357A initialization FAILED!");

        while (true)
        {
            delay(1000);
        }
    }

    Serial.println("MAX98357A initialization SUCCESSFUL.");
    Serial.println();

    Serial.println("----------------------------------------------");
    Serial.println("LIVE AUDIO LOOPBACK READY");
    Serial.println("----------------------------------------------");
    Serial.println();
    Serial.println("Speak near the INMP441.");
    Serial.println("Your voice should come through the");
    Serial.println("bone-conduction transducer.");
    Serial.println();

    printGain();
}

void loop()
{
    // =================================================
    // CHECK FOR GAIN COMMANDS
    // =================================================

    handleSerialInput();

    // =================================================
    // READ INMP441
    // =================================================

    size_t bytesRead = MicI2S.readBytes(
        (char*)micBuffer,
        sizeof(micBuffer)
    );

    if (bytesRead == 0)
    {
        Serial.println("WARNING: No microphone data!");
        delay(100);
        return;
    }

    int samplesRead =
        bytesRead / sizeof(int32_t);

    int outputSamples = 0;

    // =================================================
    // CONVERT LEFT CHANNEL
    // INMP441 L/R = GND
    // Therefore LEFT channel is used.
    // =================================================

    for (
        int i = 0;
        i < samplesRead;
        i += 2
    )
    {
        int32_t raw = micBuffer[i];

        // Convert 32-bit I2S sample
        // to 16-bit PCM
        int32_t sample = raw >> 16;

        // Apply adjustable gain
        int32_t scaled = (int32_t)(sample * gain);

        // Prevent clipping / wraparound
        if (scaled > 32767)
            scaled = 32767;

        if (scaled < -32768)
            scaled = -32768;

        audioBuffer[outputSamples] =
            (int16_t)scaled;

        outputSamples++;

        if (outputSamples >= 128)
        {
            break;
        }
    }

    // =================================================
    // SEND TO MAX98357A
    // =================================================

    if (outputSamples > 0)
    {
        AmpI2S.write(
            (uint8_t*)audioBuffer,
            outputSamples * sizeof(int16_t)
        );
    }
}