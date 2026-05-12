"""URL patterns for the contests app."""

from django.urls import path

from contests import views

app_name = "contests"

urlpatterns = [
    path("", views.contest_list, name="list"),
    path("<slug:slug>/", views.contest_detail, name="detail"),
]
