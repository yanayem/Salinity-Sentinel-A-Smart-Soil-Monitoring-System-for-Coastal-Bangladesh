import os
import sys
import django
import serial
import time
from collections import deque
from django.utils import timezone

# ------------------------
# Django setup
# ------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soilcore.settings")
django.setup()

from django.contrib.auth.models import User
from soildata.models import Device, DeviceReading

# ------------------------
# Arduino Serial Setup
# ------------------------
ARDUINO_PORT = "COM6"
BAUD_RATE = 9600

try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to Arduino on {ARDUINO_PORT}")
except serial.SerialException as e:
    print(f"❌ Could not connect to {ARDUINO_PORT}: {e}")
    raise SystemExit

# ------------------------
# Select device
# ------------------------
user = User.objects.first()
if not user:
    raise Exception("No users found! Create a superuser first.")

device, created = Device.objects.get_or_create(
    name="My Soil Sensor",
    defaults={"user": user, "is_active": True}
)
print(f"📡 Reading data from device: {device.name} (Ctrl+C to stop)")

# ------------------------
# Rolling average buffer for smoothing raw values
# ------------------------
BUFFER_SIZE = 5
raw_buffer = deque(maxlen=BUFFER_SIZE)

# ------------------------
# Read and save loop
# ------------------------
try:
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
        except Exception:
            continue

        if not line:
            continue

        try:
            clean = line.replace("%", "").strip()
            first_part = clean.split(",")[0].strip()
            if not first_part.replace('.', '', 1).isdigit():
                continue
            raw_value = float(first_part)
        except Exception:
            continue

        raw_buffer.append(raw_value)
        smooth_raw = round(sum(raw_buffer) / len(raw_buffer), 2)

        try:
            reading = DeviceReading.objects.create(
                device=device,
                moisture=smooth_raw, 
                updated_at=timezone.now()
            )
            print(f"💾 Saved: Raw={smooth_raw} (latest={raw_value})")
        except Exception as e:
            print(f"⚠️ Could not save reading: {e}")
            continue

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🛑 Stopped by user.")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("🔌 Serial connection closed.")
