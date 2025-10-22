from django.contrib import admin
from .models import SoilType, UserProfile, SoilData, Newsletter

# -----------------------------------------------
# SoilType Admin
# -----------------------------------------------
@admin.register(SoilType)
class SoilTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'ph_range', 'location', 'suitable_crops')
    search_fields = ('name', 'description', 'suitable_crops', 'location')
    list_filter = ('location',)
    ordering = ('name',)

    # Optional: Add a method to display pH range
    def ph_range(self, obj):
        if obj.ph_min is not None and obj.ph_max is not None:
            return f"{obj.ph_min} - {obj.ph_max}"
        return "N/A"
    
    ph_range.short_description = "pH Range"


# -----------------------------------------------
# UserProfile Admin
# -----------------------------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'location')
    search_fields = ('user__username', 'user__email', 'phone_number', 'location')
    ordering = ('user__username',)


# -----------------------------------------------
# SoilData Admin
# -----------------------------------------------
@admin.register(SoilData)
class SoilDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'soil_type', 'ph_level', 'temperature', 'humidity', 'updated_at')
    list_filter = ('soil_type', 'user')
    search_fields = ('user__username', 'soil_type__name')
    ordering = ('-updated_at',)


# -----------------------------------------------
# Newsletter Admin
# -----------------------------------------------
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    ordering = ('-subscribed_at',)
