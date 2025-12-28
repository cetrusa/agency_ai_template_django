from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs
from urllib.parse import urlparse
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Item

from apps.core.services.exporting import build_pdf_table, build_xlsx, stream_csv
from .forms import ItemForm


@dataclass(frozen=True)
class _Col:
    key: str
    label: str
    sortable: bool = True
    nowrap: bool = False


def _get_params(request: HttpRequest) -> dict[str, str]:
    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()
    sort = (request.GET.get("sort") or "").strip()
    direction = (request.GET.get("dir") or "").strip().lower()
    page = (request.GET.get("page") or "1").strip()

    if direction not in {"asc", "desc"}:
        direction = "asc"

    return {
        "q": q,
        "status": status,
        "sort": sort,
        "dir": direction,
        "page": page,
        # presentes para compatibilidad con templates del kit
        "from": (request.GET.get("from") or "").strip(),
        "to": (request.GET.get("to") or "").strip(),
    }


def _build_qs_without_page(params: dict[str, str]) -> str:
    data = {k: v for k, v in params.items() if k != "page" and v not in {"", "all"}}
    return urlencode(data)


def _get_params_from_mapping(data: dict[str, str]) -> dict[str, str]:
    q = (data.get("q") or "").strip()
    status = (data.get("status") or "").strip()
    sort = (data.get("sort") or "").strip()
    direction = (data.get("dir") or "").strip().lower()
    page = (data.get("page") or "1").strip()

    if direction not in {"asc", "desc"}:
        direction = "asc"

    return {
        "q": q,
        "status": status,
        "sort": sort,
        "dir": direction,
        "page": page,
        "from": (data.get("from") or "").strip(),
        "to": (data.get("to") or "").strip(),
    }


def _get_params_from_hx_current_url(request: HttpRequest) -> dict[str, str] | None:
    current = request.headers.get("HX-Current-URL") or ""
    if not current:
        return None

    parsed = urlparse(current)
    if not parsed.query:
        return None

    raw = parse_qs(parsed.query)
    flat = {k: (v[-1] if v else "") for k, v in raw.items()}
    return _get_params_from_mapping(flat)


def _queryset(params: dict[str, str]):
    qs = Item.objects.all()

    if params["q"]:
        qs = qs.filter(Q(name__icontains=params["q"]))

    if params["status"] and params["status"] != "all":
        qs = qs.filter(status=params["status"])

    sort_map = {
        "name": "name",
        "status": "status",
        "created_at": "created_at",
    }
    sort_key = sort_map.get(params["sort"], "created_at")
    prefix = "-" if params["dir"] == "desc" else ""

    # Tie-breaker por PK para estabilidad.
    return qs.order_by(f"{prefix}{sort_key}", f"{prefix}id")


def _columns() -> list[dict]:
    return [
        _Col("name", "Nombre", sortable=True, nowrap=True).__dict__,
        _Col("status", "Estado", sortable=True, nowrap=True).__dict__,
        _Col("created_at", "Creado", sortable=True, nowrap=True).__dict__,
    ]


def _items(page_obj, *, params: dict[str, str]) -> list[dict]:
    rows = []
    qs_with_page = urlencode({k: v for k, v in params.items() if v not in {"", "all"}})
    for obj in page_obj.object_list:
        edit_url = reverse("crud_example:edit", kwargs={"id": obj.pk})
        delete_url = reverse("crud_example:delete", kwargs={"id": obj.pk})
        if qs_with_page:
            edit_url = f"{edit_url}?{qs_with_page}"
            delete_url = f"{delete_url}?{qs_with_page}"
        rows.append(
            {
                "id": obj.pk,
                "cells": [obj.name, obj.get_status_display(), obj.created_at.strftime("%Y-%m-%d")],
                # No implementamos modales en Step 2: dejamos placeholders.
                "urls": {"detail": None, "edit": edit_url, "delete": delete_url},
            }
        )
    return rows


def _context(request: HttpRequest) -> dict:
    params = _get_params(request)
    qs = _queryset(params)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(params["page"] or 1)

    crud_urls = {
        "list": reverse("crud_example:list"),
        "table": reverse("crud_example:table"),
        # No implementados en Step 2
        "create": reverse("crud_example:create"),
        "bulk": "#",
        "export_csv": reverse("crud_example:export_csv"),
        "export_xlsx": reverse("crud_example:export_xlsx"),
        "export_pdf": reverse("crud_example:export_pdf"),
    }

    return {
        "crud_urls": crud_urls,
        "page_title": "CRUD Example",
        "entity_label": "Item",
        "entity_label_plural": "Items",
        "current_filters": params,
        "status_options": [("all", "Todos"), ("active", "Activo"), ("inactive", "Inactivo")],
        "columns": _columns(),
        "items": _items(page_obj, params=params),
        "page_obj": page_obj,
        "total_count": qs.count(),
        "qs": _build_qs_without_page(params),
    }


def _context_for_refresh(request: HttpRequest) -> dict:
    """Context para refrescar tabla tras modales.

    Prioriza HX-Current-URL (URL actual del navegador) para preservar filtros/sort/page.
    Fallback: usa request.GET.
    """

    params = _get_params_from_hx_current_url(request) or _get_params(request)
    qs = _queryset(params)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(params["page"] or 1)

    crud_urls = {
        "list": reverse("crud_example:list"),
        "table": reverse("crud_example:table"),
        "create": reverse("crud_example:create"),
        "bulk": "#",
        "export_csv": reverse("crud_example:export_csv"),
        "export_xlsx": reverse("crud_example:export_xlsx"),
        "export_pdf": reverse("crud_example:export_pdf"),
    }

    return {
        "crud_urls": crud_urls,
        "page_title": "CRUD Example",
        "entity_label": "Item",
        "entity_label_plural": "Items",
        "current_filters": params,
        "status_options": [("all", "Todos"), ("active", "Activo"), ("inactive", "Inactivo")],
        "columns": _columns(),
        "items": _items(page_obj, params=params),
        "page_obj": page_obj,
        "total_count": qs.count(),
        "qs": _build_qs_without_page(params),
    }


def list_view(request: HttpRequest) -> HttpResponse:
    return render(request, "crud/list.html", _context(request))


def table_view(request: HttpRequest) -> HttpResponse:
    # Endpoint HTMX: solo el partial de tabla
    return render(request, "crud/_table.html", _context(request))


def _export_queryset(request: HttpRequest):
    params = _get_params(request)
    return _queryset(params)


def export_csv_view(request: HttpRequest) -> HttpResponseBase:
    qs = _export_queryset(request)
    return stream_csv(
        queryset=qs,
        fields=["name", "status", "created_at"],
        headers=["Nombre", "Estado", "Creado"],
        filename_base="crud_example_items",
    )


def export_xlsx_view(request: HttpRequest) -> HttpResponseBase:
    qs = _export_queryset(request)
    return build_xlsx(
        queryset=qs,
        fields=["name", "status", "created_at"],
        headers=["Nombre", "Estado", "Creado"],
        filename_base="crud_example_items",
        sheet_name="Items",
    )


def export_pdf_view(request: HttpRequest) -> HttpResponseBase:
    qs = _export_queryset(request)
    return build_pdf_table(
        queryset=qs,
        fields=["name", "status", "created_at"],
        headers=["Nombre", "Estado", "Creado"],
        title="CRUD Example · Items",
        filename_base="crud_example_items",
    )


def _hx_modal_success_refresh(request: HttpRequest) -> HttpResponse:
    """Respuesta estándar de éxito para modales:

    - Cierra modal vía HX-Trigger
    - Refresca tabla preservando filtros/sort/page vía OOB swap
    """

    resp = render(request, "crud_example/_oob_table_refresh.html", _context_for_refresh(request))
    resp["HX-Trigger"] = '{"modalClose": true}'
    return resp


def create_view(request: HttpRequest) -> HttpResponseBase:
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return _hx_modal_success_refresh(request)

        return render(
            request,
            "partials/modals/modal_form.html",
            {
                "modal_title": "Nuevo Item",
                "modal_size": "md",
                "modal_backdrop_close": False,
                "form_action": reverse("crud_example:create"),
                "form": form,
                "submit_label": "Crear",
            },
        )

    form = ItemForm()
    return render(
        request,
        "partials/modals/modal_form.html",
        {
            "modal_title": "Nuevo Item",
            "modal_size": "md",
            "modal_backdrop_close": False,
            "form_action": reverse("crud_example:create"),
            "form": form,
            "submit_label": "Crear",
        },
    )


def edit_view(request: HttpRequest, id: int) -> HttpResponseBase:
    obj = get_object_or_404(Item, pk=id)

    if request.method == "POST":
        form = ItemForm(request.POST, instance=obj)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return _hx_modal_success_refresh(request)

        return render(
            request,
            "partials/modals/modal_form.html",
            {
                "modal_title": f"Editar Item #{obj.pk}",
                "modal_size": "md",
                "modal_backdrop_close": False,
                "form_action": reverse("crud_example:edit", kwargs={"id": obj.pk}),
                "form": form,
                "submit_label": "Guardar",
            },
        )

    form = ItemForm(instance=obj)
    return render(
        request,
        "partials/modals/modal_form.html",
        {
            "modal_title": f"Editar Item #{obj.pk}",
            "modal_size": "md",
            "modal_backdrop_close": False,
            "form_action": reverse("crud_example:edit", kwargs={"id": obj.pk}),
            "form": form,
            "submit_label": "Guardar",
        },
    )


def delete_view(request: HttpRequest, id: int) -> HttpResponseBase:
    obj = get_object_or_404(Item, pk=id)

    if request.method == "POST":
        with transaction.atomic():
            obj.delete()
        return _hx_modal_success_refresh(request)

    return render(
        request,
        "partials/modals/modal_confirm.html",
        {
            "modal_title": f"Eliminar Item #{obj.pk}",
            "modal_size": "sm",
            "modal_backdrop_close": True,
            "confirm_action": reverse("crud_example:delete", kwargs={"id": obj.pk}),
            "confirm_label": "Eliminar",
            "confirm_variant": "danger",
            "confirm_message": "¿Eliminar este registro?",
            "confirm_detail": obj.name,
        },
    )
