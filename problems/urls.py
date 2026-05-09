"""Problem URLs."""

from django.urls import path

from problems import views


app_name = "problems"

urlpatterns = [
    path("", views.problem_list, name="list"),
    path("<slug:slug>/", views.problem_detail, name="detail"),
    path("<slug:slug>/solve/", views.code_editor, name="solve"),
]
