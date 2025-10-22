from django.db import models
from django.contrib.auth.models import User

# -----------------------------------------------
# UserProfile: Extend default User info
# -----------------------------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    location = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.user.username


# -----------------------------------------------
# SoilType: Soil type info
# -----------------------------------------------
class SoilType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default="No description")  # ✅ fixed
    suitable_crops = models.CharField(max_length=200, blank=True, null=True)

    # Optional fields for better soil details
    location = models.CharField(max_length=100, blank=True, null=True)
    ph_min = models.FloatField(blank=True, null=True)
    ph_max = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

    # Helper method for admin display
    def ph_range(self):
        if self.ph_min is not None and self.ph_max is not None:
            return f"{self.ph_min} - {self.ph_max}"
        return "N/A"
    
    ph_range.short_description = "pH Range"


# -----------------------------------------------
# SoilData: User soil readings
# -----------------------------------------------
class SoilData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
