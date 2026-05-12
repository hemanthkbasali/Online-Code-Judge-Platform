"""Contest model for CodeSentinel."""

from django.db import models
from django.utils import timezone


class Contest(models.Model):
    DIFFICULTY_EASY = "easy"
    DIFFICULTY_MEDIUM = "medium"
    DIFFICULTY_HARD = "hard"
    DIFFICULTY_EXPERT = "expert"

    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY, "Easy"),
        (DIFFICULTY_MEDIUM, "Medium"),
        (DIFFICULTY_HARD, "Hard"),
        (DIFFICULTY_EXPERT, "Expert"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField(blank=True)
    difficulty = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_MEDIUM
    )
    start_time = models.DateTimeField()
    # duration in minutes
    duration_minutes = models.PositiveIntegerField(default=90)
    participant_count = models.PositiveIntegerField(default=0)
    is_registration_open = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_time"]

    # ── Computed helpers ────────────────────────────────────────────────

    @property
    def end_time(self):
        from datetime import timedelta
        return self.start_time + timedelta(minutes=self.duration_minutes)

    @property
    def status(self):
        """Return one of: 'upcoming' | 'live' | 'completed'."""
        now = timezone.now()
        if now < self.start_time:
            return "upcoming"
        if now <= self.end_time:
            return "live"
        return "completed"

    @property
    def status_display(self):
        mapping = {
            "upcoming": "Upcoming",
            "live": "Live Now",
            "completed": "Completed",
        }
        return mapping.get(self.status, "Upcoming")

    @property
    def registration_status(self):
        """Combined registration + life-cycle label."""
        s = self.status
        if s == "completed":
            return "completed"
        if s == "live":
            return "live"
        if not self.is_registration_open:
            return "closed"
        return "open"

    @property
    def duration_display(self):
        h, m = divmod(self.duration_minutes, 60)
        if h and m:
            return f"{h}h {m}m"
        if h:
            return f"{h}h"
        return f"{m}m"

    @property
    def difficulty_css(self):
        return self.difficulty  # maps directly to CSS class

    @property
    def start_time_iso(self):
        """ISO-8601 string for JS Date parsing."""
        return self.start_time.isoformat()

    @property
    def end_time_iso(self):
        return self.end_time.isoformat()

    def __str__(self):
        return self.title
