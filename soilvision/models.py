from django.db import models
from django.contrib.auth.models import User

class SoilPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='soil_images/')
    predicted_soil_type = models.CharField(max_length=50)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.predicted_soil_type} - {self.confidence}%"
