from django.urls import path
from . import views

app_name = 'soildata' 

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('soil-moisture/', views.soil_moisture, name='soil_moisture'),
    path('api/moisture/', views.api_moisture, name='api_moisture'),
    path('alerts/', views.alerts, name='alerts'),
    path('crop-advisor/', views.crop_advisor, name='crop_advisor'),
]
