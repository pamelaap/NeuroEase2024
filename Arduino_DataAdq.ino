#include <Adafruit_NeoPixel.h>

// Configuración del aro de NeoPixels
#define PIN 6  // Pin de salida conectado al aro
#define NUM_PIXELS 45  // Número de LEDs en el aro
Adafruit_NeoPixel pixels(NUM_PIXELS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(115200);  // Inicia comunicación serial
  pixels.begin();        // Inicializa el aro de NeoPixels
  pixels.clear();        // Apaga todos los LEDs
  pixels.show();
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();  // Lee el comando recibido por el puerto serial

    // Procesar el comando recibido
    if (command == 'G') {  // Comando para relajación (verde)
      setColor(0, 255, 0);  // Verde
    } else if (command == 'R') {  // Comando para dolor neuropático (rojo)
      setColor(255, 0, 0);  // Rojo
    }
  }
}

// Función para establecer el color del aro
void setColor(int red, int green, int blue) {
  for (int i = 0; i < NUM_PIXELS; i++) {
    pixels.setPixelColor(i, pixels.Color(red, green, blue));
  }
  pixels.show();  // Actualiza los LEDs
}
