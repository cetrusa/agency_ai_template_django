from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from apps.core.models import GlobalConfig
from .forms import GlobalConfigForm

@login_required
def detail(request: HttpRequest) -> HttpResponse:
    config = GlobalConfig.load()
    
    context = {
        "config": config,
        "page_title": "Configuración de Empresa"
    }
    
    if request.headers.get("HX-Request") == "true":
        return render(request, "organization_admin/settings.html", context)
        
    return render(request, "pages/shell.html", {"content_template": "organization_admin/settings.html", **context})

@login_required
def edit(request: HttpRequest) -> HttpResponse:
    config = GlobalConfig.load()
    
    if request.method == "POST":
        form = GlobalConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración actualizada correctamente")
            return redirect("organization_admin:detail")
    else:
        form = GlobalConfigForm(instance=config)
    
    context = {
        "form": form,
        "config": config,
        "page_title": "Editar Configuración"
    }
    
    if request.headers.get("HX-Request") == "true":
        return render(request, "organization_admin/form.html", context)
        
    return render(request, "pages/shell.html", {"content_template": "organization_admin/form.html", **context})
