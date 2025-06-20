#include <SoftwareSerial.h>

#define SENSOR_PIN 2
#define RELAY_PIN 3
#define RED_LED_PIN 4
#define GREEN_LED_PIN 5
#define GSM_RX 7
#define GSM_TX 8

SoftwareSerial gsm(GSM_RX, GSM_TX);

const String token = "844f1f2f9cc69c91cbabc12bfbea3a2874133286c57313acdd30cb3ff8a54ea8";
const String sensor_id = "bins1234";
const String mahalla = "Yunusobod";
const String address = "Osiyo ko'chasi, 30-uy";
const String phoneNumber = "+998917240778";
const String serverUrl = "http://156.67.80.26/api/update-bin/";

bool binFilled = false;
bool lastSensorState = HIGH;
unsigned long lastUpdateTime = 0;
const unsigned long minUpdateInterval = 60000; // 1 daqiqa
const int debounceDelay = 500; // 500ms debouncing

void setup() {
  pinMode(SENSOR_PIN, INPUT_PULLUP);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);

  Serial.begin(9600);
  gsm.begin(9600);
  delay(1000);

  if (initGSM()) {
    Serial.println("GSM moduli tayyor");
    digitalWrite(GREEN_LED_PIN, HIGH);
  } else {
    Serial.println("GSM moduli ulanishida xato");
    digitalWrite(RED_LED_PIN, HIGH);
  }
}

bool initGSM() {
  gsm.println("AT"); delay(100);
  if (!waitForResponse("OK", 1000)) return false;

  gsm.println("AT+CMGF=1"); delay(100);
  if (!waitForResponse("OK", 1000)) return false;

  gsm.println("AT+SAPBR=3,1,\"Contype\",\"GPRS\""); delay(200);
  if (!waitForResponse("OK", 1000)) return false;

  gsm.println("AT+SAPBR=3,1,\"APN\",\"internet\""); delay(200);
  if (!waitForResponse("OK", 1000)) return false;

  gsm.println("AT+SAPBR=1,1"); delay(2000);
  if (!waitForResponse("OK", 3000)) return false;

  gsm.println("AT+SAPBR=2,1"); delay(1000);
  if (!waitForResponse("OK", 1000)) return false;

  return true;
}

bool waitForResponse(String expected, unsigned long timeout) {
  unsigned long start = millis();
  String response = "";
  while (millis() - start < timeout) {
    while (gsm.available()) {
      char c = gsm.read();
      response += c;
      if (response.indexOf(expected) != -1) return true;
    }
  }
  Serial.println("Javob olinmadi: " + response);
  return false;
}

void loop() {
  bool currentSensorState = digitalRead(SENSOR_PIN);
  static unsigned long lastChangeTime = 0;

  if (currentSensorState != lastSensorState) {
    lastChangeTime = millis();
  }

  if ((millis() - lastChangeTime > debounceDelay) && (millis() - lastUpdateTime > minUpdateInterval)) {
    if (currentSensorState == LOW && !binFilled) {
      binFilled = true;
      updateStatus("FILLED");
    } else if (currentSensorState == HIGH && binFilled) {
      binFilled = false;
      updateStatus("EMPTY");
    }
    lastUpdateTime = millis();
  }

  lastSensorState = currentSensorState;
  delay(100);
}

void updateStatus(String status) {
  Serial.println("Yuborilmoqda: " + status);

  digitalWrite(RED_LED_PIN, status == "FILLED" ? HIGH : LOW);
  digitalWrite(GREEN_LED_PIN, status == "FILLED" ? LOW : HIGH);
  digitalWrite(RELAY_PIN, status == "FILLED" ? HIGH : LOW);

  sendSMS(status);

  if (sendToServer(status)) {
    Serial.println("Serverga muvaffaqiyatli yuborildi");
  } else {
    Serial.println("Serverga yuborish xatosi");
  }
}

void sendSMS(String status) {
  gsm.print("AT+CMGS=\"");
  gsm.print(phoneNumber);
  gsm.println("\"");
  delay(200);

  gsm.print("Chiqindi holati: ");
  gsm.print(status);
  gsm.print("\nManzil: ");
  gsm.print(address);
  gsm.print("\nMahalla: ");
  gsm.print(mahalla);
  gsm.write(26); // CTRL+Z
  delay(3000);
}

bool sendToServer(String status) {
  int retries = 3;
  while (retries--) {
    gsm.println("AT+HTTPTERM"); delay(200);
    gsm.println("AT+HTTPINIT"); delay(200);
    if (!waitForResponse("OK", 1000)) continue;

    gsm.println("AT+HTTPPARA=\"CID\",1"); delay(200);
    if (!waitForResponse("OK", 1000)) continue;

    gsm.println("AT+HTTPPARA=\"URL\",\"" + serverUrl + "\""); delay(200);
    if (!waitForResponse("OK", 1000)) continue;

    gsm.println("AT+HTTPPARA=\"CONTENT\",\"application/x-www-form-urlencoded\""); delay(200);
    if (!waitForResponse("OK", 1000)) continue;

    String postData = "token=" + token + "&sensor_id=" + sensor_id + "&status=" + status + "&mahalla=" + mahalla + "&address=" + address;
    gsm.print("AT+HTTPDATA=");
    gsm.print(postData.length());
    gsm.println(",10000");
    delay(500);
    gsm.print(postData);
    delay(1000);
    if (!waitForResponse("DOWNLOAD", 2000)) continue;

    gsm.println("AT+HTTPACTION=1"); delay(5000);
    if (!waitForResponse("+HTTPACTION: 1,200", 10000)) continue;

    gsm.println("AT+HTTPREAD"); delay(1000);
    String response = "";
    unsigned long start = millis();
    while (millis() - start < 3000) {
      while (gsm.available()) {
        response += (char)gsm.read();
      }
    }
    Serial.println("Server javobi: " + response);

    gsm.println("AT+HTTPTERM"); delay(200);
    return response.indexOf("\"status\": \"success\"") != -1;
  }
  return false;
}