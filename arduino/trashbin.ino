#include <SoftwareSerial.h>

#define SENSOR_PIN 2      // Optik sensor pini
#define RELAY_PIN 3       // Rele pini
#define GSM_RX 7          // GSM RX pini
#define GSM_TX 8          // GSM TX pini
#define DEBOUNCE_DELAY 50 // Debounce vaqti (ms)

SoftwareSerial gsm(GSM_RX, GSM_TX);

bool lastSensorState = HIGH;
bool currentSensorState;
unsigned long lastDebounceTime = 0;
bool messageSent = false;

const char* server = "your-ngrok-url.ngrok.io"; // Ngrok yoki server domeni
const char* apiEndpoint = "/api/update-bin/";   // API endpoint
const char* apn = "net.ums.uz";                 // Mobiuz APN
const char* sensorId = "sensor_001";            // Sensor ID
const char* address = "Yunusobod tumani, Osiyo ko'chasi, 30-uy yonida";
const char* mahalla = "Yunusobod";

void setup() {
  pinMode(SENSOR_PIN, INPUT_PULLUP);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  Serial.begin(9600);
  gsm.begin(9600);
  Serial.println(F("Initializing GSM..."));

  // GSM modulini sozlash
  if (!initializeGSM()) {
    Serial.println(F("GSM initialization failed!"));
    while (1); // Nosozlik bo‘lsa to‘xtash
  }
  Serial.println(F("GSM initialized."));
}

void loop() {
  bool reading = digitalRead(SENSOR_PIN);

  // Debouncing
  if (reading != lastSensorState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > DEBOUNCE_DELAY) {
    if (reading != currentSensorState) {
      currentSensorState = reading;

      if (currentSensorState == LOW && lastSensorState == HIGH) {
        digitalWrite(RELAY_PIN, HIGH);
        sendToServer(F("FILLED"));
        Serial.print(F("FILLED - "));
        Serial.println(address);
        messageSent = true;
      } else if (currentSensorState == HIGH && lastSensorState == LOW) {
        digitalWrite(RELAY_PIN, LOW);
        sendToServer(F("EMPTY"));
        Serial.print(F("EMPTY - "));
        Serial.println(address);
        messageSent = true;
      }
    }
  }

  lastSensorState = reading;
  processGSMResponses();
}

bool initializeGSM() {
  // AT buyruqlari ketma-ketligi
  const char* commands[] = {
    "AT",                   // Modulni tekshirish
    "AT+CPIN?",            // SIM karta holati
    "AT+CREG?",            // Tarmoqqa ulanish
    "AT+CGATT=1",          // GPRS yoqish
    "AT+CIPSHUT",          // Oldingi ulanishlarni yopish
    "AT+CSTT=\"net.ums.uz\",\"\",\"\"", // APN sozlamalari
    "AT+CIICR",            // GPRS ulanishini boshlash
    "AT+CIFSR"             // IP manzil olish
  };

  for (int i = 0; i < 8; i++) {
    if (!sendAT(commands[i], (i == 6) ? 5000 : 2000, "OK")) {
      return false;
    }
  }
  return true;
}

bool sendAT(const char* command, int timeout, const char* expected) {
  gsm.println(command);
  String response = "";
  unsigned long start = millis();
  while (millis() - start < timeout) {
    if (gsm.available()) {
      char c = gsm.read();
      response += c;
      Serial.write(c);
    }
  }
  return response.indexOf(expected) != -1;
}

void sendToServer(const __FlashStringHelper* status) {
  char data[200];
  snprintf_P(data, sizeof(data), PSTR("sensor_id=%s&status=%s&address=%s&mahalla=%s"),
             sensorId, status, address, mahalla);

  char postRequest[300];
  snprintf_P(postRequest, sizeof(postRequest),
             PSTR("POST %s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s"),
             apiEndpoint, server, strlen(data), data);

  if (sendAT("AT+CIPSTART=\"TCP\",\"" + String(server) + "\",80", 5000, "CONNECT OK")) {
    gsm.print(F("AT+CIPSEND="));
    gsm.println(strlen(postRequest));
    if (sendAT("", 1000, ">")) {
      gsm.print(postRequest);
      gsm.write(26); // CTRL+Z
      sendAT("", 5000, "SEND OK");
    }
    sendAT("AT+CIPCLOSE", 1000, "CLOSE OK");
  } else {
    Serial.println(F("Connection failed!"));
  }
}

void processGSMResponses() {
  if (gsm.available()) {
    String response = "";
    unsigned long start = millis();
    while (gsm.available() && millis() - start < 2000) {
      char c = gsm.read();
      response += c;
      Serial.write(c);
    }
    if (response.indexOf("OK") != -1) {
      Serial.println(F("Command successful!"));
    } else if (response.indexOf("ERROR") != -1) {
      Serial.println(F("Command failed!"));
    }
  }
}