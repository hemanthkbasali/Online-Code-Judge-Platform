"""Admin configuration for submissions."""

from django.contrib import admin

from submissions.models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "problem", "language", "verdict", "execution_time", "created_at")
    list_filter = ("verdict", "language", "created_at")
    search_fields = ("user__username", "problem__title", "code", "error_message")
    readonly_fields = ("created_at",)
