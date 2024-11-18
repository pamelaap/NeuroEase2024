import serial
import numpy as np
import time
import csv
import matplotlib.pyplot as plt
from collections import deque

# Configuración del puerto serial
ser = serial.Serial('COM12', 115200, timeout=0.001)  # Timeout ajustado

# Configuración de parámetros de la gráfica
window_size_seconds = 3  # Tamaño de la ventana en segundos
sample_rate_target = 250  # Frecuencia de muestreo esperada
window_size_samples = window_size_seconds * sample_rate_target

# Inicializar las listas para almacenar las señales
Alpha = deque(maxlen=window_size_samples)
Beta = deque(maxlen=window_size_samples)
fs_list = []

# Archivo de guardado
ruta_guardado = "C:\\Users\\pamel\\OneDrive\\Hip\\Imágenes\\Escuela\\EEGLAB bioinstru\\Frecuencias Sujetos\\sh!t.csv"
csv_file = open(ruta_guardado, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Ventana", "Potencia promedio Alpha", "Potencia promedio Beta", "Frecuencia de Muestreo Promedio (Hz)"])

# Variables para calcular la frecuencia de muestreo
prev_time = time.time()
window_counter = 1

# Configuración de la gráfica en tiempo real
plt.ion()
fig, ax = plt.subplots()
ax.set_ylim(-5, 5)
alpha_line, = ax.plot([], [], label='Alpha', color='b')
beta_line, = ax.plot([], [], label='Beta', color='r')
ax.legend(loc='upper right')
ax.set_title("Señales Alpha y Beta en tiempo real")
ax.set_xlabel("Muestras")
ax.set_ylabel("Voltaje (V)")

# Función para actualizar la gráfica
def update_plot():
    if len(Alpha) >= window_size_samples:
        alpha_line.set_data(range(len(Alpha)), Alpha)
        beta_line.set_data(range(len(Beta)), Beta)
        ax.set_xlim(0, len(Alpha))
        fig.canvas.draw()
        fig.canvas.flush_events()

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            data = line.split(',')
            if len(data) == 2:
                try:
                    s1 = int(data[0])
                    s2 = int(data[1])

                    # Convertir los datos a voltaje
                    v1 = s1 * (5.0 / 1023.0)
                    v2 = s2 * (5.0 / 1023.0)

                    # Agregar los datos leídos a las listas
                    Alpha.append(v1)
                    Beta.append(v2)

                    # Calcular la frecuencia de muestreo actual
                    current_time = time.time()
                    elapsed_time = current_time - prev_time
                    prev_time = current_time
                    fs = 1 / elapsed_time if elapsed_time > 0 else 0
                    fs_list.append(fs)

                    # Calcular la potencia de cada señal sin el offset
                    if len(Alpha) >= window_size_samples:
                        # Restar la media (offset) de las señales antes de calcular la potencia
                        alpha_centered = np.array(Alpha) - np.mean(Alpha)
                        beta_centered = np.array(Beta) - np.mean(Beta)

                        # Calcular la potencia como la media de los valores cuadrados centrados
                        power_avg_alpha = np.mean(alpha_centered ** 2)
                        power_avg_beta = np.mean(beta_centered ** 2)

                        # Calcular la frecuencia de muestreo promedio de la ventana
                        fs_avg = np.mean(fs_list[-window_size_samples:])

                        # Escribir en el archivo CSV la potencia promedio y la fs promedio de la ventana
                        csv_writer.writerow([window_counter, power_avg_alpha, power_avg_beta, fs_avg])
                        print(f"Ventana {window_counter}: Potencia promedio Alpha: {power_avg_alpha:.2f}, Potencia promedio Beta: {power_avg_beta:.2f}, Frecuencia de muestreo promedio: {fs_avg:.2f} Hz")

                        # Incrementar el contador de ventanas
                        window_counter += 1

                    update_plot()

                except ValueError:
                    pass

except KeyboardInterrupt:
    # Cerrar el puerto serial y el archivo CSV cuando el programa se interrumpe
    ser.close()
    csv_file.close()
    print("Programa terminado")
