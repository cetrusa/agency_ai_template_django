from django import forms
from apps.orgs.models import Organization

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name", "logo", "base_color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "logo": forms.FileInput(attrs={"class": "form-control"}),
            "base_color": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
        }
