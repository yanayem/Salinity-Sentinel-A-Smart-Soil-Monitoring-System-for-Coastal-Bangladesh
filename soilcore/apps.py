# E:\SDP_200\soilcore\soilcore\apps.py

from django.apps import AppConfig  # ✅ import AppConfig

class SoilcoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'soilcore'
