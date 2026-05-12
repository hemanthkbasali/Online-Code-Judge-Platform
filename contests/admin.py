"""Admin registration for Contest model."""

from django.contrib import admin

from contests.models import Contest


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "difficulty",
        "start_time",
        "duration_minutes",
        "participant_count",
        "is_registration_open",
        "is_active",
        "status",
    )
    list_filter = ("difficulty", "is_registration_open", "is_active")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("start_time",)
    list_editable = ("is_registration_open", "is_active", "participant_count")
    date_hierarchy = "start_time"

    fieldsets = (
        (None, {
            "fields": ("title", "slug", "description", "difficulty"),
        }),
        ("Schedule", {
            "fields": ("start_time", "duration_minutes"),
        }),
        ("Meta", {
            "fields": ("participant_count", "is_registration_open", "is_active"),
        }),
    )

    @admin.display(description="Status")
    def status(self, obj):
        return obj.status_display
