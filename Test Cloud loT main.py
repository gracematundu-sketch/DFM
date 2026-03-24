import requests
import time
import random

# --- CONFIGURATION ---
WRITE_API_KEY = "MLB0KGVVF9Y65Q0O"  # Colle ta clé ici
CHANNEL_ID = "3311060"  # Optionnel, pour ton suivi

print("Début de la simulation de vol vers ThingSpeak...")

try:
    while True:
        # Simulation de données
        altitude = random.uniform(10.0, 50.0)  # Simule entre 10 et 50m
        vitesse = random.uniform(5.0, 15.0)  # Simule entre 5 et 15 m/s

        # Préparation de l'URL d'envoi (API REST)
        # Field1 = Altitude, Field2 = Vitesse
        url = f"https://api.thingspeak.com/update?api_key={WRITE_API_KEY}&field1={altitude}&field2={vitesse}"

        # Envoi au Cloud
        reponse = requests.get(url)

        if reponse.status_code == 200:
            print(f"[OK] Données envoyées : Alt={altitude:.2f}m, Vit={vitesse:.2f}m/s")
        else:
            print(f"[ERREUR] Code : {reponse.status_code}")

        # Pause obligatoire (ThingSpeak gratuit = 15s minimum entre deux envois)
        time.sleep(20)

except KeyboardInterrupt:
    print("\nSimulation arrêtée.")