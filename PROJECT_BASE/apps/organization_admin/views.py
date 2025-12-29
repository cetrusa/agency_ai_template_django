from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from apps.orgs.models import Organization
from .forms import OrganizationForm

@login_required
@permission_required("orgs.change_organization", raise_exception=True)
def detail(request: HttpRequest) -> HttpResponse:
    # Single tenant assumption for MVP
    org = Organization.objects.first()
    if not org:
        # Fallback if no org exists
        org = Organization.objects.create(name="Mi Empresa", slug="mi-empresa")
    
    context = {
        "org": org,
        "page_title": "Mi Empresa"
    }
    
    if request.headers.get("HX-Request") == "true":
        return render(request, "organization_admin/detail.html", context)
        
    return render(request, "pages/shell.html", {"content_template": "organization_admin/detail.html", **context})

@login_required
@permission_required("orgs.change_organization", raise_exception=True)
def edit(request: HttpRequest) -> HttpResponse:
    org = Organization.objects.first()
    
    if request.method == "POST":
        form = OrganizationForm(request.POST, request.FILES, instance=org)
        if form.is_valid():
            form.save()
            messages.success(request, "Empresa actualizada correctamente")
            return redirect("organization_admin:detail")
    else:
        form = OrganizationForm(instance=org)
    
    context = {
        "form": form,
        "org": org,
        "page_title": "Editar Empresa"
    }
    
    if request.headers.get("HX-Request") == "true":
        return render(request, "organization_admin/form.html", context)
        
    return render(request, "pages/shell.html", {"content_template": "organization_admin/form.html", **context})
