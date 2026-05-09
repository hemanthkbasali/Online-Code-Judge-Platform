"""Admin setup for the custom user model."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class CodeSentinelUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("CodeSentinel Profile", {"fields": ("display_name", "institution", "bio")}),
    )
    list_display = ("username", "email", "display_name", "institution", "is_staff", "is_active")
    search_fields = ("username", "email", "display_name", "institution")
