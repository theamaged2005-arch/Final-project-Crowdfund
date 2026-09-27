from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'is_activated', 'is_staff')
    list_filter = ('is_activated', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Crowdfunding profile', {
            'fields': ('phone', 'profile_picture', 'birthdate', 'facebook_profile', 'country', 'is_activated'),
        }),
    )