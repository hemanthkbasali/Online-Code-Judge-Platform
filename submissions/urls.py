"""Submission URLs."""

from django.urls import path

from submissions import views


app_name = "submissions"

urlpatterns = [
    path("", views.submission_history, name="history"),
    path("run/", views.run_code, name="run"),
    path("submit/", views.submit_code, name="submit"),
]
