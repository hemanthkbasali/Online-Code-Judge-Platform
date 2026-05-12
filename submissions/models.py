"""Submission model."""

from django.conf import settings
from django.db import models


class Submission(models.Model):
    LANGUAGE_PYTHON = "python"
    LANGUAGE_C = "c"
    LANGUAGE_CPP = "cpp"
    LANGUAGE_JAVA = "java"

    LANGUAGE_CHOICES = [
        (LANGUAGE_PYTHON, "Python"),
        (LANGUAGE_C, "C"),
        (LANGUAGE_CPP, "C++"),
        (LANGUAGE_JAVA, "Java"),
    ]

    VERDICT_ACCEPTED = "Accepted"
    VERDICT_WRONG_ANSWER = "Wrong Answer"
    VERDICT_COMPILATION_ERROR = "Compilation Error"
    VERDICT_RUNTIME_ERROR = "Runtime Error"
    VERDICT_TIME_LIMIT_EXCEEDED = "Time Limit Exceeded"

    VERDICT_CHOICES = [
        (VERDICT_ACCEPTED, "Accepted"),
        (VERDICT_WRONG_ANSWER, "Wrong Answer"),
        (VERDICT_COMPILATION_ERROR, "Compilation Error"),
        (VERDICT_RUNTIME_ERROR, "Runtime Error"),
        (VERDICT_TIME_LIMIT_EXCEEDED, "Time Limit Exceeded"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    problem = models.ForeignKey("problems.Problem", on_delete=models.CASCADE, related_name="submissions")
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    code = models.TextField()
    verdict = models.CharField(max_length=40, choices=VERDICT_CHOICES)
    execution_time = models.FloatField(default=0)
    memory_usage = models.PositiveIntegerField(default=0, help_text="Peak memory usage in KB")
    failed_test_number = models.PositiveIntegerField(null=True, blank=True)
    output = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_accepted(self):
        return self.verdict == self.VERDICT_ACCEPTED

    @property
    def verdict_css_class(self):
        """Return a CSS-safe class name for the verdict."""
        _map = {
            self.VERDICT_ACCEPTED: "accepted",
            self.VERDICT_WRONG_ANSWER: "wrong-answer",
            self.VERDICT_COMPILATION_ERROR: "compilation-error",
            self.VERDICT_RUNTIME_ERROR: "runtime-error",
            self.VERDICT_TIME_LIMIT_EXCEEDED: "time-limit-exceeded",
        }
        return _map.get(self.verdict, "unknown")

    def __str__(self):
        return f"{self.user} - {self.problem} - {self.verdict}"
