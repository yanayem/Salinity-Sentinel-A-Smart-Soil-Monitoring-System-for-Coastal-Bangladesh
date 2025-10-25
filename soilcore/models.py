from django.db import models
from django.contrib.auth.models import User

# -----------------------------------------------
# UserProfile: Extend default User info
# -----------------------------------------------

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=50, default="Soil Analyst")  # Dynamic role

    def __str__(self):
        return f"{self.user.username} Profile"
# -----------------------------------------------
# SoilType: Soil type info
# -----------------------------------------------
class SoilType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default="No description")
    suitable_crops = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    ph_min = models.FloatField(blank=True, null=True)
    ph_max = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

    def ph_range(self):
        if self.ph_min is not None and self.ph_max is not None:
            return f"{self.ph_min} - {self.ph_max}"
        return "N/A"
    
    ph_range.short_description = "pH Range"


# -----------------------------------------------
# Device: IoT devices linked to users
# -----------------------------------------------
class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.name} ({self.location})"


# -----------------------------------------------
# SoilData: User soil readings (manual input)
# -----------------------------------------------
class SoilData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True)
    soil_type = models.ForeignKey(SoilType, on_delete=models.SET_NULL, null=True, blank=True)
    ph_level = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        soil_name = self.soil_type.name if self.soil_type else "N/A"
        return f"{self.user.username} - {soil_name}"


# -----------------------------------------------
# Newsletter: Subscriber emails
# -----------------------------------------------
class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email



# -----------------------------------------------
# PhReading: IoT device pH readings
# -----------------------------------------------
class PhReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()  # pH value

    def __str__(self):
        return f"{self.device.name} - {self.value:.2f} @ {self.timestamp:%Y-%m-%d %H:%M}"

# -----------------------------------------------
# Alert: Soil condition alerts for users    
# -----------------------------------------------
ALERT_TYPE_CHOICES = [
    ('high', 'High'),
    ('low', 'Low'),
]

class Alert(models.Model):
    device = models.ForeignKey('Device', on_delete=models.CASCADE)
    parameter = models.CharField(max_length=50)  # e.g., 'pH', 'Temperature'
    value = models.FloatField()
    threshold_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.name} {self.parameter} {self.threshold_type} @ {self.timestamp:%Y-%m-%d %H:%M}"

# -----------------------------------------------
# TemperatureReading: IoT device temperature readings
# -----------------------------------------------

class TemperatureReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()

    def __str__(self):
        return f"{self.device.name} - {self.value:.1f}°C @ {self.timestamp:%Y-%m-%d %H:%M}"


# -----------------------------------------------
# HumidityReading: IoT device humidity readings 
# -----------------------------------------------

class HumidityReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()

    def __str__(self):
        return f"{self.device.name} - {self.value:.1f}% @ {self.timestamp:%Y-%m-%d %H:%M}"


# -----------------------------------------------
# SensorData: Generic sensor data model
# -----------------------------------------------

class SensorData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)  # e.g., 'temperature', 'moisture', 'ph'
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.name} - {self.type}: {self.value}"


#alert


class Alert(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    parameter = models.CharField(max_length=50)
    value = models.FloatField()
    threshold_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    emailed = models.BooleanField(default=False)  # new field

    def __str__(self):
        return f"{self.device.name} {self.parameter} {self.threshold_type} @ {self.timestamp:%Y-%m-%d %H:%M}"
