"""Admin configuration for problems and test cases."""

from django.contrib import admin

from problems.models import Problem, TestCase


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1
    fields = ("order", "input_data", "expected_output", "is_hidden")


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("title", "difficulty", "points", "time_limit", "is_active", "updated_at")
    list_filter = ("difficulty", "is_active")
    search_fields = ("title", "statement", "constraints")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TestCaseInline]


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ("problem", "order", "is_hidden", "created_at")
    list_filter = ("is_hidden", "problem__difficulty")
    search_fields = ("problem__title", "input_data", "expected_output")
