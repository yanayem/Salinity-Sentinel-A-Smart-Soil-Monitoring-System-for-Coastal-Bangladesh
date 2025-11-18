from django.db import models
from django.contrib.auth.models import User
from account.models import UserProfile


# -------------------------
# Device Model
# -------------------------
class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"


# -------------------------
# Device Reading Model
# -------------------------
class DeviceReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    moisture = models.FloatField(help_text="Soil moisture value (%)")
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.moisture}% at {self.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
