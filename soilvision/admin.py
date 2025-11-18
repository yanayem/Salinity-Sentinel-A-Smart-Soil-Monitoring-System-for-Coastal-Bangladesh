from django.contrib import admin
from .models import SoilPrediction

@admin.register(SoilPrediction)
class SoilPredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'predicted_soil_type', 'confidence', 'created_at')
    list_filter = ('predicted_soil_type', 'created_at', 'user')
    search_fields = ('user__username', 'predicted_soil_type')
    readonly_fields = ('created_at', 'confidence')
    ordering = ('-created_at',)
