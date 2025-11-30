from django.urls import path
from . import views

app_name = 'soilvision'  

urlpatterns = [
    path('upload/', views.soil_upload, name='soil_upload'),  
    path('history/', views.soil_history, name='soil_history'),
]
