from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.urls import reverse_lazy

from .forms import UserProfileForm, CustomPasswordChangeForm


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """Vista de perfil del usuario (lectura)."""
    context = {
        "page_title": "Mi Perfil",
        "user": request.user,
    }
    
    if request.headers.get("HX-Request") == "true":
        return render(request, "accounts/profile.html", context)
    
    return render(request, "pages/shell.html", {"content_template": "accounts/profile.html", **context})


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    """Editar datos básicos del perfil."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente")
            return redirect("accounts:profile")
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        "page_title": "Editar Perfil",
        "form": form,
    }
    
    if request.headers.get("HX-Request") == "true":
        return render(request, "accounts/profile_edit.html", context)
    
    return render(request, "pages/shell.html", {"content_template": "accounts/profile_edit.html", **context})


class PasswordChangeView(DjangoPasswordChangeView):
    """Vista para cambio de contraseña."""
    form_class = CustomPasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Contraseña actualizada correctamente")
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Cambiar Contraseña"
        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request") == "true":
            return render(self.request, "accounts/password_change_form.html", context)
        
        context["content_template"] = "accounts/password_change_form.html"
        return render(self.request, "pages/shell.html", context, **response_kwargs)
