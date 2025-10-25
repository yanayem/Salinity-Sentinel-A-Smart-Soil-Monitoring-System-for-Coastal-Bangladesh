from django.contrib import admin
from django.urls import path,include  
from soilcore import views  # import all from views.py

urlpatterns = [
    path('admin/', admin.site.urls),

    # ---------- Home / About ----------
    path('', views.homepage, name='homepage'),
    path('about/', views.aboutpage, name='aboutpage'),
    path('terms-privacy/', views.terms_privacy, name='terms_privacy'),
    path('subscribe-newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
   # path("weather/", views.weatherpage, name="weatherpage"),
   path('weather/', include('weather.urls')),

    # ---------- Authentication ----------
    path('login/', views.loginsignuppage, name='login_signup'),
    path('logout/', views.user_logout, name='logout'),

    # ---------- Dashboard & Profile ----------
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profilepage, name='profilepage'),
    path('settings/', views.settingpage, name='settingpage'),

    # ---------- Soil Types ----------
    path('soil-types/', views.soil_type_page, name='soil_types'),
    path('soil-types/add/', views.add_soil_type, name='add_soil_type'),
    path('soil-types/edit/<int:id>/', views.edit_soil_type, name='edit_soil_type'),
    path('soil-types/delete/<int:id>/', views.delete_soil_type, name='delete_soil_type'),

    # ---------- Sensors / Data ----------
    path('ph-levels/', views.ph_levels, name='ph_levels'),
    path('api/ph/latest/', views.api_ph_latest, name='api_ph_latest'),
    path('api/iot/push/', views.api_iot_push, name='api_iot_push'),

    path('live-data/', views.live_data, name='live_data'),
    path('api/live-data/', views.api_live_data, name='api_live_data'),
    path('soil-moisture/', views.soil_moisture, name='soil_moisture'),
    path('temperature/', views.temperaturepage, name='temperaturepage'),
   # path('data-temp/', views.data_temp, name='data_temp'),
    path('humidity/', views.humidity_page, name='humidity_page'),

    # ---------- Alerts / Advisor ----------
    path('alerts/', views.alerts_page, name='alerts_page'),
    path('crop-advisor/', views.crop_advisor, name='crop_advisor'),
    
]
