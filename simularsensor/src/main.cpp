// --- Bibliotecas ---
#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>

// --- Credenciais da rede Wi-Fi ---
const char* ssid = "Wokwi-GUEST"; 
const char* password = "";    

// --- Definição de Pinos ---
// Sensores (Entradas analógicas - pinos de exemplo, ajuste com base na sua placa ESP32 e fiação)
#define SENSOR_CHLORINE_PIN     34  // ADC1_CH4
#define SENSOR_TURBIDITY_PIN    32  // ADC1_CH6
#define SENSOR_CONDUCTIVITY_PIN 33  // ADC1_CH5
#define SENSOR_PH_PIN           35  // ADC1_CH7

// LEDs (Digital Outputs)
#define LED_GREEN_PIN           4
#define LED_YELLOW_PIN          16
#define LED_RED_PIN             17

// Botão para enviar dados
#define BUTTON_SEND_DATA        5   // Botão digital para enviar dados ao servidor

// --- Configurações do display OLED ---
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// --- Variáveis Globais ---
float chlorineValue = 0.00;
float turbidityValue = 0.00;
float conductivityValue = 0.00;
float phValue = 0.00;
String waterPrediction = "STANDBY"; // Armazena a previsão do servidor

// --- Endereço do Servidor Flask ---
String serverName = "http://192.168.0.35:8000/data"; 

// --- Função de Inicialização ---
void setup() {
  Serial.begin(115200);
  Serial.println("Iniciando sistema de monitoramento de água...");

  // Configura os pinos dos sensores como entrada
  // Os pinos analógicos são inseridos por padrão, nenhum pinMode é necessário para analogRead

  // Configura os pinos dos LEDs como saída
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_YELLOW_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);

  // Configura o pino do botão como entrada com pull-up interno
  pinMode(BUTTON_SEND_DATA, INPUT_PULLUP);

  // Desliga todos os LEDs inicialmente
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_YELLOW_PIN, LOW);
  digitalWrite(LED_RED_PIN, LOW);

  // Conecta ao Wi-Fi
  Serial.print("Conectando ao Wi-Fi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi conectado!");
    Serial.print("Endereço IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFalha ao conectar ao Wi-Fi. Verifique as credenciais ou a rede.");
  }

  // Inicializa o display OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Endereço 0x3C para 128x64
    Serial.println(F("Falha ao iniciar display OLED"));
    while (true); // Trava se o display falhar
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0,0);
  display.println("Monitor de Agua");
  display.setCursor(0,15);
  display.println("Pressione o botao");
  display.setCursor(0,30);
  display.println("para analisar...");
  display.display();
  delay(2000);
}

// --- Função para ler sensores e mapear valores ---
void readSensors() {
  // Leitura dos sensores analógicos (0-4095)
  int rawChlorine = analogRead(SENSOR_CHLORINE_PIN);
  int rawTurbidity = analogRead(SENSOR_TURBIDITY_PIN);
  int rawConductivity = analogRead(SENSOR_CONDUCTIVITY_PIN);
  int rawPh = analogRead(SENSOR_PH_PIN);

  // Mapeamento dos valores (Exemplos - ajuste conforme seus sensores e calibração)
  // Cloro: Ex: 0-4095 -> 0-5 mg/L. (Para LDR, pode ser inversamente proporcional à concentração)
  chlorineValue = map(rawChlorine, 0, 4095, 0, 50) / 10.00; // Exemplo: 0.00 a 5.00 mg/L

  // Turbidez: Ex: 0-4095 -> 0-1000 NTU (Para LDR, pode ser inversamente proporcional à turbidez)
  // Um valor analógico mais alto do LDR pode significar menos luz = mais turbidez
  turbidityValue = map(rawTurbidity, 0, 4095, 10000, 0) / 10.00 - 10; // Exemplo: 0.00 a 1000.00 NTU (invertido para LDR)

  // Condutividade: Ex: 0-4095 -> 0-2000 µS/cm
  conductivityValue = map(rawConductivity, 0, 4095, 0, 20000) / 10.00; // Exemplo: 0.0 a 2000.00 µS/cm

  // pH: Ex: 0-4095 -> 0-14
  phValue = map(rawPh, 0, 4095, 0, 140) / 10.00; // Mapeia para 0.00 a 14.00

  Serial.println("Valores dos Sensores:");
  Serial.print("Cloro (mg/L): "); Serial.println(chlorineValue);
  Serial.print("Turbidez (NTU): "); Serial.println(turbidityValue);
  Serial.print("Condutividade (uS/cm): "); Serial.println(conductivityValue);
  Serial.print("pH: "); Serial.println(phValue);
}

// --- Função para atualizar o display OLED ---
void updateOLED() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);

  display.print("Cloro: "); display.print(chlorineValue, 1); display.println(" mg/L");
  display.setCursor(0, 10);
  display.print("Turbidez: "); display.print(turbidityValue, 0); display.println(" NTU");
  display.setCursor(0, 20);
  display.print("Condut.: "); display.print(conductivityValue, 0); display.println(" uS/cm");
  display.setCursor(0, 30);
  display.print("pH: "); display.println(phValue, 1);

  display.setCursor(0, 45);
  display.setTextSize(1); // Texto menor para status
  display.print("Status: ");
  display.setTextSize(2); // Texto maior para previsão
  display.setCursor(0, 50); // Ajusta a posição do texto de previsão
  
  if (waterPrediction.equalsIgnoreCase("POTAVEL")) {
    display.setTextColor(SSD1306_BLACK, SSD1306_WHITE); // Inverso para destaque
    display.print("POTAVEL");
    display.setTextColor(SSD1306_WHITE);
  } else if (waterPrediction.equalsIgnoreCase("SUSPEITA")) {
    display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
    display.print("SUSPEITA");
     display.setTextColor(SSD1306_WHITE);
  } else if (waterPrediction.equalsIgnoreCase("NAO_POTAVEL")) {
    display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
    display.print("NAO POT."); // Abreviado para "NAO POT."
     display.setTextColor(SSD1306_WHITE);
  } else {
    display.print("AGUARDANDO");
  }
  display.display();
}

// --- Função para controlar LEDs ---
void controlLEDs(String prediction) {
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_YELLOW_PIN, LOW);
  digitalWrite(LED_RED_PIN, LOW);

  if (prediction.equalsIgnoreCase("POTAVEL")) {
    digitalWrite(LED_GREEN_PIN, HIGH);
  } else if (prediction.equalsIgnoreCase("SUSPEITA")) {
    digitalWrite(LED_YELLOW_PIN, HIGH);
  } else if (prediction.equalsIgnoreCase("NAO_POTAVEL")) {
    digitalWrite(LED_RED_PIN, HIGH);
  }
  // Se STANDBY ou outro, todos os LEDs permanecem BAIXOS
}

// --- Loop Principal ---
void loop() {
  if (digitalRead(BUTTON_SEND_DATA) == LOW) {
    Serial.println("Botão pressionado! Lendo sensores e enviando dados...");
    readSensors(); // Lê os valores dos sensores

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      
      // Monta a URL com os dados dos sensores
      String getData = serverName + "?chlorine=" + String(chlorineValue) +
                       "&turbidity=" + String(turbidityValue) +
                       "&conductivity=" + String(conductivityValue) +
                       "&ph=" + String(phValue);
      
      Serial.print("Enviando para: ");
      Serial.println(getData);

      http.begin(getData); // Especifica a URL do GET
      http.setTimeout(10000); // Timeout de 10 segundos
      int httpCode = http.GET();

      if (httpCode > 0) {
        Serial.printf("[HTTP] GET... code: %d\n", httpCode);
        if (httpCode == HTTP_CODE_OK) {
          waterPrediction = http.getString(); // Servidor deve retornar "POTAVEL", "SUSPEITA", ou "NAO_POTAVEL"
          Serial.print("Resposta do servidor (Predição): ");
          Serial.println(waterPrediction);
        } else {
          Serial.printf("[HTTP] GET... falhou, erro: %s\n", http.errorToString(httpCode).c_str());
          waterPrediction = "ERRO HTTP";
        }
      } else {
        Serial.printf("[HTTP] GET... falhou, erro: %s\n", http.errorToString(httpCode).c_str());
        waterPrediction = "FALHA COM."; // Falha de comunicação
      }
      http.end();
    } else {
      Serial.println("Wi-Fi desconectado. Não é possível enviar dados.");
      waterPrediction = "SEM WIFI";
    }

    controlLEDs(waterPrediction); // Controla os LEDs com base na predição
    updateOLED();                 // Atualiza o display OLED

    delay(1000); // Debounce para o botão e para evitar spam de requisições
    while(digitalRead(BUTTON_SEND_DATA) == LOW); // Aguarda soltar o botão
  }
  
  delay(50); 
}