from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()


class UserProfileForm(forms.ModelForm):
    """Formulario para actualizar el perfil del usuario."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise forms.ValidationError("El email es obligatorio")
        
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise forms.ValidationError("Ya existe un usuario con este email")
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulario personalizado para cambio de contraseña."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
