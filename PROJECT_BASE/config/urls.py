"""URL routing for the base dashboard template.

Este archivo se mantiene intencionalmente simple.
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth: login, logout, password_change, password_reset, etc.
    path("accounts/", include("django.contrib.auth.urls")),
    # Apps
    path("crud-example/", include("apps.crud_example.urls")),
    path("dashboard/", include(("apps.dashboard.urls", "dashboard"), namespace="dashboard")),
    path("organization/", include("apps.organization_admin.urls")),
    path("users/", include("apps.users_admin.urls")),
    path("", include(("apps.dashboard.urls", "dashboard"), namespace="home")),  # Default redirect (namespace distinto para evitar colisión)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
