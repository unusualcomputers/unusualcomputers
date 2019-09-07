Rainbow tree is a tiny Arduino (digispark ATTiny85) driving a few led pixels, a button, a piece of wood and an old tree bark making a beautiful proud rainbow light.

The code driving it is also tiny, thanks to the excellent ![FastLED](https://fastled.io/) library, this is all there is to it:
 
```
#include <FastLED.h>

FASTLED_USING_NAMESPACE

#define DATA_PIN    0
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB
#define NUM_LEDS    12
#define BRIGHTNESS  230
#define DELAY       50
byte hue=0;
const byte saturation=255;
const byte value=255;

CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<LED_TYPE,DATA_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
}

void loop() {
  EVERY_N_MILLISECONDS( DELAY ) { FastLED.showColor(CHSV(hue++,saturation,value));}  
}
```
