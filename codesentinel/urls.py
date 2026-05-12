"""Root URL configuration for CodeSentinel."""

from django.contrib import admin
from django.urls import include, path

from codesentinel.views import landing_page


admin.site.site_header = "CodeSentinel Admin"
admin.site.site_title = "CodeSentinel"
admin.site.index_title = "Platform Management"

urlpatterns = [
    path("", landing_page, name="landing"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("problems/", include("problems.urls")),
    path("submissions/", include("submissions.urls")),
    path("contests/", include("contests.urls")),
]
