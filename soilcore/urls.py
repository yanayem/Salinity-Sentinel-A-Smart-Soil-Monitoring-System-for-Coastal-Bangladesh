from django.contrib import admin
from django.urls import path, include
from soilcore import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home / About
    path('', views.homepage, name='homepage'),
    path('about/', views.aboutpage, name='aboutpage'),

    # Soil Types
    path('soil-types/', views.soil_type_page, name='soil_types'),
    path('soil-types/add/', views.add_soil_type, name='add_soil_type'),
    path('soil-types/edit/<int:id>/', views.edit_soil_type, name='edit_soil_type'),
    path('soil-types/delete/<int:id>/', views.delete_soil_type, name='delete_soil_type'),

    # Terms / Newsletter
    path('terms-privacy/', views.terms_privacy, name='terms_privacy'),
    path('subscribe-newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),

    # Weather
    path('weather/', include('weather.urls')),

    # Account / Authentication
    path('account/', include('account.urls', namespace='account')),
    # Soil Data
    path('soildata/', include('soildata.urls', namespace='soildata')),
    
    #soil vision
    path('soilvision/', include('soilvision.urls', namespace='soilvision')),

    # Chat
    path('chat/', include('chatApp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


