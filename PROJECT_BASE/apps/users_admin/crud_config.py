from __future__ import annotations

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.urls import reverse

from apps.core.crud import ColumnDef, CrudConfig, register_crud

from .forms import UserCreateForm, UserEditForm


User = get_user_model()

CRUD_SLUG_USERS = "users_admin.users"


class UserCrudConfig(CrudConfig):
    crud_slug = CRUD_SLUG_USERS
    model = User

    page_title = "Usuarios"
    entity_label = "Usuario"
    entity_label_plural = "Usuarios"

    page_size = 15

    search_fields = ["username", "email", "first_name", "last_name"]

    list_columns = [
        ColumnDef(
            key="username",
            label="Username",
            sortable=True,
            nowrap=True,
            order_by=("username",),
            value=lambda u: u.username,
        ),
        ColumnDef(
            key="email",
            label="Email",
            sortable=True,
            nowrap=True,
            order_by=("email",),
            value=lambda u: u.email or "-",
        ),
        ColumnDef(
            key="is_active",
            label="Estado",
            sortable=True,
            nowrap=True,
            order_by=("is_active",),
            value=lambda u: "Activo" if u.is_active else "Inactivo",
        ),
        ColumnDef(
            key="date_joined",
            label="Fecha de alta",
            sortable=True,
            nowrap=True,
            order_by=("date_joined",),
            value=lambda u: u.date_joined.strftime("%Y-%m-%d"),
        ),
    ]

    default_sort_key = "date_joined"
    default_dir = "desc"

    create_form_class = UserCreateForm
    edit_form_class = UserEditForm

    create_title = "Crear usuario"
    edit_title = "Editar usuario {pk}"
    delete_title = "Cambiar estado usuario {pk}"

    create_submit_label = "Crear"
    edit_submit_label = "Guardar"
    delete_confirm_label = "Confirmar"

    permission_list = "auth.view_user"
    permission_create = "auth.add_user"
    permission_edit = "auth.change_user"
    permission_delete = "auth.delete_user"

    export_enabled = True
    export_fields = ["username", "email", "is_active", "date_joined"]
    export_headers = {
        "username": "Username",
        "email": "Email",
        "is_active": "Activo",
        "date_joined": "Fecha de alta",
    }
    export_formats = {"csv", "xlsx", "pdf"}

    def row_urls(self, obj, request: HttpRequest, params):
        return {
            "detail": None,
            "edit": reverse("users_admin:edit", kwargs={"id": obj.pk}),
            "delete": reverse("users_admin:toggle", kwargs={"id": obj.pk}),
        }


def register() -> None:
    register_crud(UserCrudConfig())