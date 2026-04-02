import serial
import time
import csv
import requests
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ------------------------------
# CONFIGURATION
# ------------------------------
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
CSV_FILE = 'flight_data.csv'
DELAY_BETWEEN_READS = 1000  # ms
UPLOAD_INTERVAL = 15  # secondes entre envoi ThingSpeak

# ------------------------------
# THINGSPEAK
# ------------------------------
THINGSPEAK_WRITE_API_KEY = 'MLB0KGVVF9Y65Q0O'
THINGSPEAK_CHANNEL_URL = 'https://api.thingspeak.com/update'

# ------------------------------
# VARIABLES POUR GRAPHIQUES
# ------------------------------
timestamps, altitude, gps_speed = [], [], []
accZ_list = []
roll_list, pitch_list, yaw_list = [], [], []

# ------------------------------
# CONNEXION SÉRIE
# ------------------------------
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    time.sleep(2)  # stabilisation
except:
    print(f"Erreur : impossible de se connecter au port {SERIAL_PORT}")
    exit()

# ------------------------------
# INITIALISATION CSV
# ------------------------------
csv_file = open(CSV_FILE, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow([
    'time_elapsed', 'altitude', 'pressure', 'temp',
    'accX', 'accY', 'accZ',
    'gyroX', 'gyroY', 'gyroZ',
    'gps_speed', 'roll', 'pitch', 'yaw'
])

# Temps de début du vol
start_time = None
last_upload = 0  # suivi intervalle ThingSpeak

# ------------------------------
# FONCTION MISE À JOUR
# ------------------------------
def update(frame):
    global start_time, last_upload
    try:
        line = ser.readline().decode(errors='ignore').strip()
        if not line:
            return

        values = line.split(',')
        if len(values) != 13:
            print(f"Ligne invalide : {line}")
            return

        data = [float(v) for v in values]

        # Initialisation start_time
        if start_time is None:
            start_time = time.time()
        time_elapsed = time.time() - start_time

        # Enregistrement CSV
        csv_writer.writerow([time_elapsed] + data)
        csv_file.flush()  # assure que les données sont écrites immédiatement

        # Mise à jour listes graphiques
        timestamps.append(time_elapsed)
        altitude.append(data[0])   # altitude
        gps_speed.append(data[10]) # gps_speed
        accZ_list.append(data[6])  # accZ
        roll_list.append(data[11])
        pitch_list.append(data[12])
        yaw_list.append(data[12])  # correction index

        # Limiter mémoire graphique
        max_points = 200
        for lst in [timestamps, altitude, gps_speed, accZ_list, roll_list, pitch_list, yaw_list]:
            if len(lst) > max_points:
                lst.pop(0)

        # ------------------------------
        # ENVOI THINGSPEAK (limité)
        # ------------------------------
        current_time = time.time()
        if current_time - last_upload >= UPLOAD_INTERVAL:
            payload = {
                'api_key': THINGSPEAK_WRITE_API_KEY,
                'field1': data[0],   # altitude
                'field2': data[10],  # gps_speed
                'field3': data[6],   # accZ
                'field4': data[11],  # roll
                'field5': data[12],  # pitch
                'field6': data[12],  # yaw
            }
            try:
                requests.get(THINGSPEAK_CHANNEL_URL, params=payload, timeout=5)
                last_upload = current_time
            except requests.RequestException as e:
                print(f"Erreur Cloud : {e}")

        # ------------------------------
        # GRAPHIQUES TEMPS RÉEL
        # ------------------------------
        plt.clf()

        # Profil de montée (Altitude)
        plt.subplot(2,2,1)
        plt.plot(timestamps, altitude, color='blue')
        plt.title('Altitude vs Temps'); plt.xlabel('Temps (s)'); plt.ylabel('Altitude (m)'); plt.grid(True)

        # Vitesse (GPS)
        plt.subplot(2,2,2)
        plt.plot(timestamps, gps_speed, color='green')
        plt.title('Vitesse GPS vs Temps'); plt.xlabel('Temps (s)'); plt.ylabel('Vitesse (km/h)'); plt.grid(True)

        # Accélération verticale
        plt.subplot(2,2,3)
        plt.plot(timestamps, accZ_list, color='red')
        plt.title('Accélération verticale (Az)'); plt.xlabel('Temps (s)'); plt.ylabel('g'); plt.grid(True)

        # Orientation (Roll/Pitch/Yaw)
        plt.subplot(2,2,4)
        plt.plot(timestamps, roll_list, label='Roll')
        plt.plot(timestamps, pitch_list, label='Pitch')
        plt.plot(timestamps, yaw_list, label='Yaw')
        plt.title('Orientation'); plt.xlabel('Temps (s)'); plt.ylabel('Degrés'); plt.legend(); plt.grid(True)

        plt.tight_layout()

    except Exception as e:
        print(f"Erreur lecture/analyse : {e}")

# ------------------------------
# ANIMATION
# ------------------------------
plt.figure(figsize=(12,8))
ani = FuncAnimation(plt.gcf(), update, interval=DELAY_BETWEEN_READS)
plt.show()

# ------------------------------
# FERMETURE CSV à la fin
# ------------------------------
csv_file.close()