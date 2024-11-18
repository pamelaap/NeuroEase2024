void setup() {
  Serial.begin(115200);  // Tasa de baudios de 115200
}

void loop() {
  int signal1 = analogRead(A0);  // Leer señal del canal A0
  int signal2 = analogRead(A1);  // Leer señal del canal A1

  // Enviar las dos señales separadas por una coma
  Serial.print(signal1);
  Serial.print(",");
  Serial.println(signal2);

  delay(4);  // Asegura un muestreo a aproximadamente 250Hz
}
