from django.urls import path
from . import views

app_name = "users_admin"

urlpatterns = [
    path("", views.user_list, name="list"),
    path("create/", views.user_create, name="create"),
    path("<int:pk>/edit/", views.user_edit, name="edit"),
    path("<int:pk>/toggle-status/", views.user_toggle_status, name="toggle_status"),
]
