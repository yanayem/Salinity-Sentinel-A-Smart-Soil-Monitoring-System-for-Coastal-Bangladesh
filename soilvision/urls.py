from django.urls import path
from . import views

app_name = 'soilvision'  # important for namespacing

urlpatterns = [
    path('upload/', views.soil_upload, name='soil_upload'),  # ← this name must match
    path('history/', views.soil_history, name='soil_history'),
]
