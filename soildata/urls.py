from django.urls import path
from . import views

app_name = 'soildata'

urlpatterns = [
    # ------------------------------
    # Dashboard & Pages
    # ------------------------------
    path('soil-moisture/', views.soil_moisture, name='soil_moisture'),
    path('add-device/', views.add_device, name='add_device'),
   # path('live-data/', views.live_data, name='live_data'),
    path('temperature/', views.temperature_page, name='temperature_page'),
    path('humidity/', views.humidity_page, name='humidity_page'),
    path('ph-levels/', views.ph_levels, name='ph_levels'),
    path('crop-advisor/', views.crop_advisor, name='crop_advisor'),
    path('alerts/', views.alerts_page, name='alerts_page'),

    # ------------------------------
    # API Endpoints
    # ------------------------------
    path('api/live-data/', views.api_live_data, name='api_live_data'),
    path('api/ph-latest/', views.api_ph_latest, name='api_ph_latest'),
    path('api/soil-data/', views.soil_data_api, name='soil_data_api'),

     path('devices/', views.devices, name='devices'),
    path('add-device/', views.add_device, name='add_device'),
    path('activate-device/<int:device_id>/', views.activate_device, name='activate_device'),
    path('deactivate-device/<int:device_id>/', views.deactivate_device, name='deactivate_device'),  # <--- Add this
    path('remove-device/<int:device_id>/', views.remove_device, name='remove_device'),
    path('toggle-device/', views.toggle_device_status, name='toggle_device_status'),
    path('api/device-readings/', views.api_device_readings, name='api_device_readings'),



    path('live-data/', views.live_data_page, name='live_data'),  # <-- use live_data_page
    path('api/live-data/', views.api_live_data, name='api_live_data'),
]

