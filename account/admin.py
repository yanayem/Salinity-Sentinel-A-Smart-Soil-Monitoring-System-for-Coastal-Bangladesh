from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# -------------------------
# Inline admin for UserProfile
# -------------------------
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('profile_pic', 'phone_number', 'location', 'role', 'last_email_change')
    readonly_fields = ('last_email_change',)

# -------------------------
# Extend UserAdmin to include UserProfile
# -------------------------
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    # Optional: add profile fields to list display
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_select_related = ('userprofile',)

    def get_role(self, instance):
        return instance.userprofile.role if hasattr(instance, 'userprofile') else ''
    get_role.short_description = 'Role'

# -------------------------
# Re-register UserAdmin
# -------------------------
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# -------------------------
# Optional: Register UserProfile separately
# -------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'location', 'role', 'last_email_change')
    readonly_fields = ('last_email_change',)
