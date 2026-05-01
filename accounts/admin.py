from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'student_id', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'student_id', 'first_name', 'last_name')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('role', 'student_id', 'phone_number', 'date_of_birth', 'profile_picture')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('role', 'student_id', 'phone_number', 'date_of_birth', 'profile_picture')
        }),
    )

