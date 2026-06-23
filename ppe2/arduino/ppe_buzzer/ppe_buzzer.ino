/*
 * PPE Alarm Buzzer — Arduino Uno/Nano
 *
 * TWO-PIN BUZZER WIRING (most student kits):
 *
 *   Passive piezo (marks say "Passive" or no label):
 *     Buzzer pin 1  ->  Digital pin 8
 *     Buzzer pin 2  ->  GND
 *     (If silent, swap the two pins.)
 *
 *   Active buzzer (has sticker on top, or says "Active"):
 *     Buzzer (+) red/long leg  ->  Digital pin 8
 *     Buzzer (-) black/short leg ->  GND
 *     (If silent, swap the two pins.)
 *
 *   Louder active buzzer (needs more current than pin 8 alone):
 *     5V -> buzzer (+)
 *     buzzer (-) -> collector of 2N2222 / S8050 NPN transistor
 *     emitter -> GND
 *     pin 8 -> 1k resistor -> transistor base
 *
 * On upload you should hear one short beep (startup test).
 *
 * Serial from laptop (9600 baud):
 *   ALARM  -> buzzer ON
 *   SILENT -> buzzer OFF
 */

const int BUZZER_PIN = 8;
const unsigned long BAUD = 9600;
const int TONE_HZ = 2500;

String inputBuffer = "";
bool alarmActive = false;

void setBuzzer(bool on) {
  alarmActive = on;
  if (on) {
    // tone() works for passive buzzers; many active buzzers also respond
    tone(BUZZER_PIN, TONE_HZ);
  } else {
    noTone(BUZZER_PIN);
    digitalWrite(BUZZER_PIN, LOW);
  }
}

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  Serial.begin(BAUD);

  // Startup test — you should hear this once after every upload
  tone(BUZZER_PIN, TONE_HZ);
  delay(300);
  noTone(BUZZER_PIN);
  digitalWrite(BUZZER_PIN, LOW);
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      inputBuffer.trim();
      if (inputBuffer.equalsIgnoreCase("ALARM")) {
        setBuzzer(true);
        Serial.println("OK:ALARM");
      } else if (inputBuffer.equalsIgnoreCase("SILENT")) {
        setBuzzer(false);
        Serial.println("OK:SILENT");
      }
      inputBuffer = "";
    } else {
      inputBuffer += c;
    }
  }
}
