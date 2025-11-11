from django.contrib import admin
from .models import SoilType, Newsletter

# -----------------------------
# SoilType admin
# -----------------------------
@admin.register(SoilType)
class SoilTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'ph_range', 'suitable_crops')
    search_fields = ('name', 'location', 'suitable_crops')
    list_filter = ('location',)
    readonly_fields = ('ph_range',)  # ph_range is a computed field

# -----------------------------
# Newsletter admin
# -----------------------------
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    list_filter = ('subscribed_at',)
    readonly_fields = ('subscribed_at',)
