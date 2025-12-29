from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseBase, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from apps.core.crud.engine import build_list_context
from apps.core.crud.registry import get_crud
from apps.core.services.exporting import build_pdf_table, build_xlsx, stream_csv

from .crud_config import CRUD_SLUG_USERS
from .forms import UserCreateForm, UserEditForm


User = get_user_model()


def _crud_urls() -> dict:
    return {
        "list": reverse("users_admin:list"),
        "table": reverse("users_admin:table"),
        "create": reverse("users_admin:create"),
        "bulk": "#",
        "export_csv": reverse("users_admin:export_csv"),
        "export_xlsx": reverse("users_admin:export_xlsx"),
        "export_pdf": reverse("users_admin:export_pdf"),
    }


def _params_from_hx_current_url(request: HttpRequest):
    current = request.headers.get("HX-Current-URL") or ""
    if not current:
        return None

    parsed = urlparse(current)
    if not parsed.query:
        return None

    raw = parse_qs(parsed.query)
    flat = {k: (v[-1] if v else "") for k, v in raw.items()}
    from apps.core.crud.config import CrudParams  # local import to avoid cycle

    direction = (flat.get("dir") or "").strip().lower()
    if direction not in {"asc", "desc"}:
        direction = "asc"

    return CrudParams(
        q=(flat.get("q") or "").strip(),
        status=(flat.get("status") or "").strip(),
        sort=(flat.get("sort") or "").strip(),
        dir=direction,
        page=(flat.get("page") or "1").strip() or "1",
        date_from=(flat.get("from") or "").strip(),
        date_to=(flat.get("to") or "").strip(),
    )


def _build_context_with_params(request: HttpRequest, params) -> dict:
    config = get_crud(CRUD_SLUG_USERS)
    crud_urls = _crud_urls()
    qs = config.queryset_for_list(request, params)
    page_obj = config.paginate(qs, params)
    return {
        "crud_urls": crud_urls,
        "page_title": config.page_title or "Listado",
        "entity_label": config.entity_label or "",
        "entity_label_plural": config.entity_label_plural or "",
        "current_filters": params.as_dict(),
        "status_options": config.status_options,
        "columns": config.columns_for_template(),
        "items": config.build_items(page_obj, request, params),
        "page_obj": page_obj,
        "total_count": qs.count(),
        "qs": config.build_qs_without_page(params),
    }


def _hx_modal_success_refresh(request: HttpRequest) -> HttpResponse:
    config = get_crud(CRUD_SLUG_USERS)
    params = _params_from_hx_current_url(request) or config.parse_params(request)
    ctx = _build_context_with_params(request, params)
    resp = render(request, "crud_example/_oob_table_refresh.html", ctx)
    resp["HX-Trigger"] = "{\"modalClose\": true}"
    return resp


def list_view(request: HttpRequest) -> HttpResponse:
    config = get_crud(CRUD_SLUG_USERS)
    if not config.can_list(request):
        return HttpResponseForbidden("Forbidden")

    crud_urls = _crud_urls()
    ctx = build_list_context(config=config, request=request, crud_urls=crud_urls)
    return render(request, "crud/list.html", ctx)


def table_view(request: HttpRequest) -> HttpResponse:
    config = get_crud(CRUD_SLUG_USERS)
    if not config.can_list(request):
        return HttpResponseForbidden("Forbidden")

    crud_urls = _crud_urls()
    ctx = build_list_context(config=config, request=request, crud_urls=crud_urls)
    return render(request, "crud/_table.html", ctx)


def create_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_USERS)
    if not config.can_create(request):
        return HttpResponseForbidden("Forbidden")

    form_class = config.get_create_form_class() or UserCreateForm

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return _hx_modal_success_refresh(request)

        return render(
            request,
            "partials/modals/modal_form.html",
            {
                "modal_title": config.get_create_modal_title(),
                "modal_size": "md",
                "modal_backdrop_close": False,
                "form_action": reverse("users_admin:create"),
                "form": form,
                "submit_label": config.get_create_submit_label(),
            },
        )

    form = form_class()
    return render(
        request,
        "partials/modals/modal_form.html",
        {
            "modal_title": config.get_create_modal_title(),
            "modal_size": "md",
            "modal_backdrop_close": False,
            "form_action": reverse("users_admin:create"),
            "form": form,
            "submit_label": config.get_create_submit_label(),
        },
    )


def edit_view(request: HttpRequest, id: int) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_USERS)
    if not config.can_edit(request):
        return HttpResponseForbidden("Forbidden")

    form_class = config.get_edit_form_class() or UserEditForm
    obj = get_object_or_404(User, pk=id)

    if request.method == "POST":
        form = form_class(request.POST, instance=obj, request_user=request.user)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return _hx_modal_success_refresh(request)

        return render(
            request,
            "partials/modals/modal_form.html",
            {
                "modal_title": config.get_edit_modal_title(obj),
                "modal_size": "md",
                "modal_backdrop_close": False,
                "form_action": reverse("users_admin:edit", kwargs={"id": obj.pk}),
                "form": form,
                "submit_label": config.get_edit_submit_label(),
            },
        )

    form = form_class(instance=obj, request_user=request.user)
    return render(
        request,
        "partials/modals/modal_form.html",
        {
            "modal_title": config.get_edit_modal_title(obj),
            "modal_size": "md",
            "modal_backdrop_close": False,
            "form_action": reverse("users_admin:edit", kwargs={"id": obj.pk}),
            "form": form,
            "submit_label": config.get_edit_submit_label(),
        },
    )


def toggle_view(request: HttpRequest, id: int) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_USERS)
    if not config.can_edit(request):
        return HttpResponseForbidden("Forbidden")

    obj = get_object_or_404(User, pk=id)
    is_deactivating = obj.is_active

    if request.method == "POST":
        if obj.pk == getattr(request.user, "pk", None) and is_deactivating:
            return render(
                request,
                "partials/modals/modal_confirm.html",
                {
                    "modal_title": "Acción no permitida",
                    "modal_size": "sm",
                    "modal_backdrop_close": True,
                    "confirm_action": None,
                    "confirm_label": "Cerrar",
                    "confirm_variant": "secondary",
                    "confirm_message": "No puedes desactivar tu propio usuario.",
                    "confirm_detail": obj.username,
                },
            )

        obj.is_active = not obj.is_active
        obj.save(update_fields=["is_active"])
        return _hx_modal_success_refresh(request)

    confirm_label = "Desactivar" if is_deactivating else "Activar"
    confirm_variant = "danger" if is_deactivating else "primary"
    confirm_message = "¿Deseas desactivar este usuario?" if is_deactivating else "¿Deseas activar este usuario?"

    return render(
        request,
        "partials/modals/modal_confirm.html",
        {
            "modal_title": config.get_delete_modal_title(obj),
            "modal_size": "sm",
            "modal_backdrop_close": True,
            "confirm_action": reverse("users_admin:toggle", kwargs={"id": obj.pk}),
            "confirm_label": confirm_label,
            "confirm_variant": confirm_variant,
            "confirm_message": confirm_message,
            "confirm_detail": f"{obj.username} ({obj.email or 'sin email'})",
        },
    )


def export_csv_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_USERS)
    if not config.can_export(request):
        return HttpResponseForbidden("Forbidden")
    if not config.is_export_enabled():
        return HttpResponseForbidden("Export disabled")
    if not config.allows_format("csv"):
        return HttpResponseForbidden("Format not allowed")

    params = config.parse_params(request)
    qs = config.queryset_for_list(request=request, params=params)

    fields = config.get_export_fields() or ["username", "email", "is_active", "date_joined"]
    headers = config.get_export_headers() or ["Username", "Email", "Activo", "Fecha de alta"]
    return stream_csv(
        queryset=qs,
        fields=fields,
        headers=headers,
        filename_base="users",
    )


def export_xlsx_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_USERS)
    if not config.can_export(request):
        return HttpResponseForbidden("Forbidden")
    if not config.is_export_enabled():
        return HttpResponseForbidden("Export disabled")
    if not config.allows_format("xlsx"):
        return HttpResponseForbidden("Format not allowed")

    params = config.parse_params(request)
    qs = config.queryset_for_list(request=request, params=params)

    fields = config.get_export_fields() or ["username", "email", "is_active", "date_joined"]
    headers = config.get_export_headers() or ["Username", "Email", "Activo", "Fecha de alta"]
    return build_xlsx(
        queryset=qs,
        fields=fields,
        headers=headers,
        filename_base="users",
        sheet_name="Usuarios",
    )


def export_pdf_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_USERS)
    if not config.can_export(request):
        return HttpResponseForbidden("Forbidden")
    if not config.is_export_enabled():
        return HttpResponseForbidden("Export disabled")
    if not config.allows_format("pdf"):
        return HttpResponseForbidden("Format not allowed")

    params = config.parse_params(request)
    qs = config.queryset_for_list(request=request, params=params)

    fields = config.get_export_fields() or ["username", "email", "is_active", "date_joined"]
    headers = config.get_export_headers() or ["Username", "Email", "Activo", "Fecha de alta"]
    return build_pdf_table(
        queryset=qs,
        fields=fields,
        headers=headers,
        title="Usuarios",
        filename_base="users",
    )
