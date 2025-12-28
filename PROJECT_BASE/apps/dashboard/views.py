"""Views UI-only para demostrar Server-Driven UI + HTMX.

Patrón clave:
- Si la request es HTMX (HX-Request: true), devolvemos SOLO el fragmento.
- Si no lo es, devolvemos página completa extendiendo base.html.

Esto permite:
- Navegación parcial (sin SPA)
- Deep-linking (URL real)
- Reutilización de templates
"""

from __future__ import annotations

from dataclasses import dataclass

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import DemoQuickActionForm, DemoTableFilterForm


def _is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


def dashboard(request: HttpRequest) -> HttpResponse:
    template = "dashboard/index.html" if _is_htmx(request) else "pages/dashboard.html"
    return render(request, template)


def kpis(request: HttpRequest) -> HttpResponse:
    return render(request, "dashboard/_kpis.html")


def charts(request: HttpRequest) -> HttpResponse:
    return render(request, "dashboard/_charts.html")


@dataclass(frozen=True)
class _Row:
    name: str
    status: str
    updated: str
    owner: str


def table(request: HttpRequest) -> HttpResponse:
    # Dataset demo (UI-only).
    rows = [
        _Row("API Billing", "ok", "hace 2m", "System"),
        _Row("Jobs Scheduler", "warn", "hace 12m", "Ops"),
        _Row("Payments", "ok", "hace 5m", "Finance"),
        _Row("Email Delivery", "down", "hace 1h", "Comms"),
        _Row("CRM Sync", "ok", "hace 9m", "Sales"),
        _Row("Data Warehouse", "warn", "hace 30m", "Data"),
        _Row("Search", "ok", "hace 3m", "Platform"),
        _Row("Webhooks", "ok", "hace 6m", "Platform"),
        _Row("SLA Monitor", "warn", "hace 17m", "Ops"),
        _Row("Exports", "ok", "hace 4m", "Finance"),
        _Row("Invoicing", "ok", "hace 11m", "Finance"),
        _Row("Audit Logs", "ok", "hace 8m", "Security"),
    ]

    form = DemoTableFilterForm(request.GET or None)
    if form.is_valid():
        q = (form.cleaned_data.get("q") or "").strip().lower()
        status = (form.cleaned_data.get("status") or "").strip()
        if q:
            rows = [r for r in rows if q in r.name.lower()]
        if status:
            rows = [r for r in rows if r.status == status]

    paginator = Paginator(rows, 5)
    page = paginator.get_page(request.GET.get("page") or 1)

    return render(
        request,
        "dashboard/_tables.html",
        {
            "filter_form": form,
            "page": page,
        },
    )


def quick_action(request: HttpRequest) -> HttpResponse:
    """Formulario HTMX: GET render + POST validation.

    No persiste nada; devuelve un mensaje de éxito para demostrar el flujo.
    """

    if request.method == "POST":
        form = DemoQuickActionForm(request.POST)
        if form.is_valid():
            return render(request, "ui/_quick_action_success.html", {"data": form.cleaned_data})
    else:
        form = DemoQuickActionForm()

    return render(request, "ui/_quick_action_form.html", {"form": form})


def modal_content(request: HttpRequest) -> HttpResponse:
    return render(request, "ui/_modal_content.html")
