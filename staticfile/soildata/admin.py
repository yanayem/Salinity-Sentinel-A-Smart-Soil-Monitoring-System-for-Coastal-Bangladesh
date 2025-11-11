from django.contrib import admin
from .models import Device, DeviceReading

# -----------------------------
# Inline DeviceReading in Device
# -----------------------------
class DeviceReadingInline(admin.TabularInline):
    model = DeviceReading
    extra = 0
    readonly_fields = ('moisture', 'updated_at')
    can_delete = True

# -----------------------------
# Device admin
# -----------------------------
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active')
    list_filter = ('is_active', 'user')
    search_fields = ('name', 'user__username')
    inlines = [DeviceReadingInline]

# -----------------------------
# Optional: separate DeviceReading admin
# -----------------------------
@admin.register(DeviceReading)
class DeviceReadingAdmin(admin.ModelAdmin):
    list_display = ('device', 'moisture', 'updated_at')
    list_filter = ('device', 'updated_at')
    search_fields = ('device__name',)
    readonly_fields = ('device', 'moisture', 'updated_at')
