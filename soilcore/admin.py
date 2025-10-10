from django.contrib import admin
from .models import SoilType, UserProfile, SoilData  # ✅ fixed imports 


@admin.register(SoilType)
class SoilTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'ph_range', 'suitable_crops')
    search_fields = ('name', 'description', 'suitable_crops')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'location')
    search_fields = ('user__username', 'user__email', 'phone_number', 'location')




@admin.register(SoilData)
class SoilDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'soil_type', 'ph_level', 'temperature', 'humidity', 'updated_at')
    list_filter = ('soil_type', 'user')

