import serial
import requests
import time

ser = serial.Serial('COM3', 9600)  # Replace with your port
url = "http://127.0.0.1:8000/soildata/api/iot/push/"

device_id = 1  # ID of your device in Django

while True:
    if ser.in_waiting:
        line = ser.readline().decode().strip()
        try:
            moisture = float(line)
            payload = {
                "device_id": device_id,
                "moisture": moisture,
                "ph": 6.8,        # or get from sensor if available
                "temperature": 25 # dummy or real if sensor exists
            }
            r = requests.post(url, json=payload)
            print("Sent:", payload, "Response:", r.text)
        except Exception as e:
            print("Error:", e)
    time.sleep(5)
