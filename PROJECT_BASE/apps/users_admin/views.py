from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserCreateForm, UserEditForm

User = get_user_model()

@login_required
@permission_required("auth.view_user", raise_exception=True)
def user_list(request: HttpRequest) -> HttpResponse:
    users = User.objects.all().order_by("-date_joined")
    
    context = {
        "users": users,
        "page_title": "Gestión de Usuarios"
    }
    
    if request.headers.get("HX-Request") == "true":
        return render(request, "users_admin/list.html", context)
        
    return render(request, "pages/shell.html", {"content_template": "users_admin/list.html", **context})

@login_required
@permission_required("auth.add_user", raise_exception=True)
def user_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente")
            return redirect("users_admin:list")
    else:
        form = UserCreateForm()
    
    context = {
        "form": form,
        "page_title": "Crear Usuario"
    }
    
    if request.headers.get("HX-Request") == "true":
        return render(request, "users_admin/form.html", context)
        
    return render(request, "pages/shell.html", {"content_template": "users_admin/form.html", **context})

@login_required
@permission_required("auth.change_user", raise_exception=True)
def user_edit(request: HttpRequest, pk: int) -> HttpResponse:
    user = get_object_or_404(User, pk=pk)
    
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente")
            return redirect("users_admin:list")
    else:
        form = UserEditForm(instance=user)
    
    context = {
        "form": form,
        "user_obj": user,
        "page_title": "Editar Usuario"
    }
    
    if request.headers.get("HX-Request") == "true":
        return render(request, "users_admin/form.html", context)
        
    return render(request, "pages/shell.html", {"content_template": "users_admin/form.html", **context})

@login_required
@permission_required("auth.change_user", raise_exception=True)
def user_toggle_status(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == "POST":
        user = get_object_or_404(User, pk=pk)
        if user != request.user:  # Prevent self-lockout
            user.is_active = not user.is_active
            user.save()
            status = "activado" if user.is_active else "desactivado"
            messages.success(request, f"Usuario {status} correctamente")
        else:
            messages.error(request, "No puedes desactivar tu propio usuario")
            
    return redirect("users_admin:list")
