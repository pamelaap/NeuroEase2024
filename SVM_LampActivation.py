import serial
import numpy as np
import time
import matplotlib.pyplot as plt
from collections import deque
from scipy.io import loadmat
from sklearn.svm import SVC

# Cargar el modelo SVM exportado desde MATLAB
mat = loadmat('svm_model.mat')
svm_model = mat['trainedModel']['ClassificationSVM'][0][0]

# Configuración del modelo SVM con los parámetros exportados
svm = SVC(C=svm_model['Cost'][0][0], kernel='rbf', gamma=svm_model['KernelParameters']['Scale'][0][0])
svm.support_ = svm_model['SupportVectors']
svm.dual_coef_ = svm_model['Alpha']
svm.intercept_ = svm_model['Bias']

# Configuración del puerto serial con Arduino
arduino = serial.Serial("COM12", 115200, timeout=0.001)  # Cambia COM12 según tu configuración

# Parámetros de la gráfica
window_size_seconds = 3
sample_rate_target = 250
window_size_samples = window_size_seconds * sample_rate_target

# Inicializar listas de almacenamiento para la ventana
Alpha = deque(maxlen=window_size_samples)
Beta = deque(maxlen=window_size_samples)
fs_list = []

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

# Función para clasificar el estado en función de potencias de Alfa y Beta
def classify_state(alpha_power, beta_power):
    features = np.array([[alpha_power, beta_power]])
    return svm.predict(features)[0]

try:
    prev_time = time.time()
    while True:
        line = arduino.readline().decode('utf-8').strip()
        if line:
            data = line.split(',')
            if len(data) == 2:
                try:
                    s1 = int(data[0])
                    s2 = int(data[1])

                    # Convertir las señales a voltaje
                    v1 = s1 * (5.0 / 1023.0)
                    v2 = s2 * (5.0 / 1023.0)

                    # Almacenar las señales
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
                        # Restar el offset y calcular la potencia
                        alpha_centered = np.array(Alpha) - np.mean(Alpha)
                        beta_centered = np.array(Beta) - np.mean(Beta)
                        power_avg_alpha = np.mean(alpha_centered ** 2)
                        power_avg_beta = np.mean(beta_centered ** 2)

                        # Clasificar estado: 1 (relajación), 2 (dolor neuropático)
                        state = classify_state(power_avg_alpha, power_avg_beta)
                        if state == 1:
                            arduino.write(b'G')  # Verde para relajación
                        elif state == 2:
                            arduino.write(b'R')  # Rojo para dolor neuropático

                    update_plot()

                except ValueError:
                    pass

except KeyboardInterrupt:
    arduino.close()
    print("Programa terminado")
