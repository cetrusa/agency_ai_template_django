# Guía Rápida: Creación de un Módulo CRUD

Esta guía explica cómo crear un nuevo módulo CRUD utilizando el framework de la agencia, basado en el ejemplo de `apps/crud_example`.

El principio fundamental es la **configuración declarativa**: defines el comportamiento de tu CRUD en una clase `CrudConfig` y el framework se encarga del resto.

## Paso 1: Crear la App y el Modelo

Como en cualquier proyecto Django, empieza por crear una nueva app y definir tu modelo.

```bash
python PROJECT_BASE/manage.py startapp products PROJECT_BASE/apps/products
```

**`products/models.py`**:
```python
from django.db import models

class Product(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Disponible"
        DISCONTINUED = "discontinued", "Discontinuado"

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
```
No olvides añadir `"apps.products.apps.ProductsConfig"` a `INSTALLED_APPS` en `config/settings.py` y luego crear y ejecutar las migraciones.

## Paso 2: Crear el Formulario de Django

Crea un `forms.py` para tu modelo. Este formulario se usará para las acciones de creación y edición.

**`products/forms.py`**:
```python
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "status", "price"]
```

## Paso 3: Definir la Configuración del CRUD

Este es el paso más importante. Crea un archivo `crud_config.py` dentro de tu app `products`.

**`products/crud_config.py`**:
```python
from __future__ import annotations
from django.urls import reverse
from apps.core.crud import ColumnDef, CrudConfig, register_crud
from .models import Product
from .forms import ProductForm

# 1. Slug único para este CRUD
CRUD_SLUG_PRODUCT = "products.products"

# 2. Clase de configuración
class ProductCrudConfig(CrudConfig):
    crud_slug = CRUD_SLUG_PRODUCT
    model = Product

    # Títulos y etiquetas
    page_title = "Gestión de Productos"
    entity_label = "Producto"
    entity_label_plural = "Productos"

    # Búsqueda y paginación
    search_fields = ["name", "sku"]
    page_size = 20

    # Columnas de la tabla (explícitas)
    list_columns = [
        ColumnDef(key="name", label="Nombre", order_by=("name",)),
        ColumnDef(key="sku", label="SKU", sortable=True),
        ColumnDef(key="price", label="Precio", order_by=("price",)),
        ColumnDef(key="status", label="Estado", value=lambda o: o.get_status_display()),
    ]

    # Formularios para modales
    create_form_class = ProductForm
    edit_form_class = ProductForm

    # Permisos requeridos
    permission_list = "products.view_product"
    permission_create = "products.add_product"
    permission_edit = "products.change_product"
    permission_delete = "products.delete_product"

    # URLs para acciones de fila
    def row_urls(self, obj: Product, request, params) -> dict:
        return {
            "edit": reverse("products:edit", kwargs={"id": obj.pk}),
            "delete": reverse("products:delete", kwargs={"id": obj.pk}),
        }

# 3. Registro del CRUD
def register() -> None:
    register_crud(ProductCrudConfig())
```

## Paso 4: Definir las Vistas y URLs

El framework necesita vistas mínimas que actúen como puntos de entrada para el CRUD. **La lógica de filtrado/orden/permissions/export se delega a `CrudConfig`** para que no existan “dos fuentes de verdad”.

**`apps/products/views.py`**:
```python
from __future__ import annotations

from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBase
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from apps.core.crud.engine import build_list_context
from apps.core.crud.registry import get_crud
from apps.core.services.exporting import build_pdf_table, build_xlsx, stream_csv

from .crud_config import CRUD_SLUG_PRODUCT
from .models import Product


def list_view(request: HttpRequest) -> HttpResponse:
    config = get_crud(CRUD_SLUG_PRODUCT)
    if not config.can_list(request):
        return HttpResponseForbidden("Forbidden")

    crud_urls = {
        "list": reverse("products:list"),
        "table": reverse("products:table"),
        "create": reverse("products:create"),
        "bulk": "#",
        "export_csv": reverse("products:export_csv"),
        "export_xlsx": reverse("products:export_xlsx"),
        "export_pdf": reverse("products:export_pdf"),
    }

    ctx = build_list_context(config=config, request=request, crud_urls=crud_urls)
    return render(request, "crud/list.html", ctx)


def table_view(request: HttpRequest) -> HttpResponse:
    config = get_crud(CRUD_SLUG_PRODUCT)
    if not config.can_list(request):
        return HttpResponseForbidden("Forbidden")

    crud_urls = {
        "list": reverse("products:list"),
        "table": reverse("products:table"),
        "create": reverse("products:create"),
        "bulk": "#",
        "export_csv": reverse("products:export_csv"),
        "export_xlsx": reverse("products:export_xlsx"),
        "export_pdf": reverse("products:export_pdf"),
    }

    ctx = build_list_context(config=config, request=request, crud_urls=crud_urls)
    return render(request, "crud/_table.html", ctx)


def _hx_modal_success_refresh(request: HttpRequest) -> HttpResponse:
    """Patrón del framework: cerrar modal y refrescar tabla preservando querystring."""
    # En la app de ejemplo esto se hace con un partial OOB.
    resp = render(request, "products/_oob_table_refresh.html", {})
    resp["HX-Trigger"] = '{"modalClose": true}'
    return resp


def create_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_PRODUCT)
    if not config.can_create(request):
        return HttpResponseForbidden("Forbidden")

    form_class = config.get_create_form_class()
    if form_class is None:
        from .forms import ProductForm as _FallbackForm

        form_class = _FallbackForm

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
                "form_action": reverse("products:create"),
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
            "form_action": reverse("products:create"),
            "form": form,
            "submit_label": config.get_create_submit_label(),
        },
    )


def edit_view(request: HttpRequest, id: int) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_PRODUCT)
    if not config.can_edit(request):
        return HttpResponseForbidden("Forbidden")

    form_class = config.get_edit_form_class()
    if form_class is None:
        from .forms import ProductForm as _FallbackForm

        form_class = _FallbackForm

    obj = get_object_or_404(Product, pk=id)

    if request.method == "POST":
        form = form_class(request.POST, instance=obj)
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
                "form_action": reverse("products:edit", kwargs={"id": obj.pk}),
                "form": form,
                "submit_label": config.get_edit_submit_label(),
            },
        )

    form = form_class(instance=obj)
    return render(
        request,
        "partials/modals/modal_form.html",
        {
            "modal_title": config.get_edit_modal_title(obj),
            "modal_size": "md",
            "modal_backdrop_close": False,
            "form_action": reverse("products:edit", kwargs={"id": obj.pk}),
            "form": form,
            "submit_label": config.get_edit_submit_label(),
        },
    )


def delete_view(request: HttpRequest, id: int) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_PRODUCT)
    if not config.can_delete(request):
        return HttpResponseForbidden("Forbidden")

    obj = get_object_or_404(Product, pk=id)
    if request.method == "POST":
        with transaction.atomic():
            obj.delete()
        return _hx_modal_success_refresh(request)

    return render(
        request,
        "partials/modals/modal_confirm.html",
        {
            "modal_title": config.get_delete_modal_title(obj),
            "modal_size": "sm",
            "modal_backdrop_close": True,
            "confirm_action": reverse("products:delete", kwargs={"id": obj.pk}),
            "confirm_label": config.get_delete_confirm_label(),
            "confirm_variant": "danger",
            "confirm_message": "¿Eliminar este registro?",
            "confirm_detail": str(obj),
        },
    )


def export_csv_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_PRODUCT)
    if not config.can_export(request):
        return HttpResponseForbidden("Forbidden")
    if not config.is_export_enabled() or not config.allows_format("csv"):
        return HttpResponseForbidden("Export disabled")

    params = config.parse_params(request)
    qs = config.queryset_for_list(request=request, params=params)

    fields = config.get_export_fields() or ["name", "sku", "status", "price", "created_at"]
    headers = config.get_export_headers() or ["Nombre", "SKU", "Estado", "Precio", "Creado"]
    return stream_csv(queryset=qs, fields=fields, headers=headers, filename_base="products")


def export_xlsx_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_PRODUCT)
    if not config.can_export(request):
        return HttpResponseForbidden("Forbidden")
    if not config.is_export_enabled() or not config.allows_format("xlsx"):
        return HttpResponseForbidden("Export disabled")

    params = config.parse_params(request)
    qs = config.queryset_for_list(request=request, params=params)

    fields = config.get_export_fields() or ["name", "sku", "status", "price", "created_at"]
    headers = config.get_export_headers() or ["Nombre", "SKU", "Estado", "Precio", "Creado"]
    return build_xlsx(queryset=qs, fields=fields, headers=headers, filename_base="products", sheet_name="Products")


def export_pdf_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_PRODUCT)
    if not config.can_export(request):
        return HttpResponseForbidden("Forbidden")
    if not config.is_export_enabled() or not config.allows_format("pdf"):
        return HttpResponseForbidden("Export disabled")

    params = config.parse_params(request)
    qs = config.queryset_for_list(request=request, params=params)

    fields = config.get_export_fields() or ["name", "sku", "status", "price", "created_at"]
    headers = config.get_export_headers() or ["Nombre", "SKU", "Estado", "Precio", "Creado"]
    return build_pdf_table(
        queryset=qs,
        fields=fields,
        headers=headers,
        title="Products",
        filename_base="products",
    )
```

**`apps/products/urls.py`**:
```python
from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.list_view, name="list"),
    path("table/", views.table_view, name="table"),
    path("create/", views.create_view, name="create"),
    path("<int:id>/edit/", views.edit_view, name="edit"),
    path("<int:id>/delete/", views.delete_view, name="delete"),
    path("export/csv/", views.export_csv_view, name="export_csv"),
    path("export/xlsx/", views.export_xlsx_view, name="export_xlsx"),
    path("export/pdf/", views.export_pdf_view, name="export_pdf"),
]
```

## Paso 5: Integrar en el Proyecto

Finalmente, incluye las URLs de tu app en el `urls.py` principal del proyecto y registra el CRUD **de forma autocontenida**.

**`config/urls.py`**:
```python
# ...
urlpatterns = [
    # ...
    path("products/", include("apps.products.urls")),
    # ...
]
```

### Registrar el CRUD usando AppConfig.ready() (patrón correcto)

**Qué NO se hace**

- No registrar CRUDs en un archivo central.
- No editar `apps/core/crud/registry.py` manualmente.
- No llamar funciones “bootstrap” globales.

**Qué SÍ se hace**

1) En `apps/products/apps.py`:

```python
from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.products"

    def ready(self):
        from .crud_config import register

        register()
```

2) En `config/settings.py` (INSTALLED_APPS):

```python
INSTALLED_APPS = [
    # ...
    "apps.products.apps.ProductsConfig",
]
```

⚠️ Nota importante: el registro de CRUDs **no es centralizado** por diseño. Cada app se registra a sí misma en `ready()` para mantener apps autocontenidas y seguir el ciclo de vida estándar de Django.

¡Listo! Con estos pasos, tienes un módulo CRUD funcional, con listado, búsqueda, paginación, creación, edición y eliminación, todo ello respetando los permisos de Django y siguiendo las mejores prácticas de la agencia.
