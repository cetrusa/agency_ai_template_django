"""URL routing for the base dashboard template.

Este archivo se mantiene intencionalmente simple.
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.dashboard.urls")),
]
