from django.db import models
from django.contrib.auth.models import User

# -------------------------
# Device Model
# -------------------------
class Device(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='devices'
    )
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    device_id = models.CharField(max_length=50, blank=True, unique=True)

    def __str__(self):
        return self.name


# -------------------------
# Device Reading Model
# -------------------------
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # <- Add this line

class DeviceReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    humidity = models.FloatField()
    ph_level = models.FloatField(blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(default=timezone.now)  # <- works now

    def __str__(self):
        return f"{self.device.name} reading at {self.updated_at}"

# -------------------------
# Optional SoilData Model
# -------------------------
class SoilData(models.Model):
    moisture = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.moisture}% at {self.timestamp}"


# -------------------------
# Soil Type Model (for crop advisor)
# -------------------------
class SoilType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    ph_min = models.FloatField()
    ph_max = models.FloatField()
    suitable_crops = models.TextField(blank=True, null=True)  # comma-separated list

    def __str__(self):
        return self.name


# -------------------------
# Alerts Model
# -------------------------
class Alert(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alerts')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert for {self.device.name} at {self.timestamp}"
