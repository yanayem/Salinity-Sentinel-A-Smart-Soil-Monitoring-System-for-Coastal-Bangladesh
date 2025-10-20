# soilcore/urls.py

from django.contrib import admin
from django.urls import path
from . import views
from soilcore import views  # all views in soilcore/views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),

    # Auth system
    path('login/', views.loginsignuppage, name='login_signup'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Other pages
    path('soil-types/', views.soil_type_page, name='soil_types'),
    path('temperature/', views.temperature, name='temperature'),
    path('about/', views.aboutpage, name='aboutpage'),
]
