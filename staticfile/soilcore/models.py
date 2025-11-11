from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# -----------------------------------------------
# Helper function for user file uploads
# -----------------------------------------------
def user_directory_path(instance, filename):
    return f'user_{instance.user.id}/{filename}'
# -----------------------------------------------
# UserProfile: Extend default User info
# -----------------------------------------------

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
# Newsletter: Subscriber emails
# -----------------------------------------------
class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
