
from flask import Flask, request, render_template
import subprocess
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)
debug_log = []

# Konfigurationsdaten
NVR_IP = "10.20.5.150"
CAM_IP = "10.20.5.160"
USERNAME = "admin"
PASSWORD = "12345"
RTSP_PORT = 554
ONVIF_PORT = 80

def add_log(message):
    debug_log.append(message)
    if len(debug_log) > 100:
        debug_log.pop(0)

@app.route("/")
def index():
    return render_template("index.html", log=debug_log)

@app.route("/test")
def test():
    # PING Test
    for ip in [NVR_IP, CAM_IP]:
        response = os.system(f"ping -c 1 {ip}")
        add_log(f"Ping {ip}: {'✅ OK' if response == 0 else '❌ Fehlgeschlagen'}")

    # ONVIF Test
    try:
        onvif_response = requests.get(f"http://{CAM_IP}:{ONVIF_PORT}/onvif/device_service", timeout=5)
        if onvif_response.status_code == 200:
            add_log("ONVIF: ✅ Verbindung zur Kamera erfolgreich")
        else:
            add_log("ONVIF: ❌ Antwort erhalten, aber kein 200 OK")
    except Exception as e:
        add_log(f"ONVIF: ❌ Fehler beim Zugriff: {e}")

    # RTSP Test (nur URI, kein Stream)
    rtsp_url = f"rtsp://{USERNAME}:{PASSWORD}@{CAM_IP}:{RTSP_PORT}/Streaming/Channels/101"
    add_log(f"RTSP URI (manuell testen): {rtsp_url}")

    # Dummy Push Event Test
    try:
        push_test = requests.post("http://localhost:5000/push", json={"event": "TestAlarm"})
        add_log(f"Push Test: ✅ {push_test.status_code}")
    except Exception as e:
        add_log(f"Push Test: ❌ {e}")

    return render_template("index.html", log=debug_log)

@app.route("/push", methods=["POST"])
def push_event():
    data = request.json
    add_log(f"📡 Push-Event empfangen: {data}")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
