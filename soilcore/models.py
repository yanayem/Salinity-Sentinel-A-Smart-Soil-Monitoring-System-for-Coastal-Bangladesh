from django.db import models
from django.contrib.auth.models import User

# -----------------------------------------------
# Extended User Info
# -----------------------------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=150)

    def __str__(self):
        return self.user.username


# -----------------------------------------------
# Soil Type Info
# -----------------------------------------------
class SoilType(models.Model):
    # Matches your MySQL table exactly
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    ph_range = models.CharField(max_length=50, blank=True, null=True)
    suitable_crops = models.TextField(blank=True, null=True)

   

    def __str__(self):
        return self.name
    
    # -----------------------------------------------
# Soil Monitoring Data
# -----------------------------------------------
class SoilData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    soil_type = models.ForeignKey(SoilType, on_delete=models.SET_NULL, null=True, blank=True)
    ph_level = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.soil_type.name if self.soil_type else 'N/A'}"


class Newsletter(models.Model):
    email = models.EmailField(unique=True)  # Prevent duplicate emails
    subscribed_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp

    def __str__(self):
        return self.email