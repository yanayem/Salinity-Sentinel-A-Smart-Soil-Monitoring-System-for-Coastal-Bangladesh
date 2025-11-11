import os
import sys
import django
import serial
import time

# ------------------------
# Django setup
# ------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soilcore.settings")
django.setup()

from django.contrib.auth.models import User
from soildata.models import Device, DeviceReading

# ------------------------
# Arduino Serial Setup
# ------------------------
ARDUINO_PORT = "COM7"  # change if needed
BAUD_RATE = 9600

try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to Arduino on {ARDUINO_PORT}")
except Exception as e:
    print(f"❌ Could not connect to {ARDUINO_PORT}: {e}")
    exit()

# ------------------------
# Select device
# ------------------------
user = User.objects.first()  # use first user or customize
if not user:
    raise Exception("No users found! Create a superuser first.")

device, created = Device.objects.get_or_create(
    name="My Soil Sensor",
    defaults={"user": user, "is_active": True}
)

# ------------------------
# Read and save data
# ------------------------
print("Reading data from Arduino... (Ctrl+C to stop)")

try:
    while True:
        line = ser.readline().decode().strip()
        if not line:
            continue

        try:
            moisture = float(line)  # Arduino sends numeric soil moisture
        except ValueError:
            print(f"⚠️ Failed to parse line: {line}")
            continue

        # Save to database
        reading = DeviceReading.objects.create(
            device=device,
            moisture=moisture
        )
        print(f"💾 Saved: Moisture={moisture}%")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopped by user.")
    ser.close()
