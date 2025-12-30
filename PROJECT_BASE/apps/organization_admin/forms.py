from django import forms
from apps.core.models import GlobalConfig

class GlobalConfigForm(forms.ModelForm):
    class Meta:
        model = GlobalConfig
        fields = [
            "site_name", "logo", 
            "primary_color", "secondary_color",
            "company_address", "company_phone", "company_email",
            "social_facebook", "social_twitter", "social_instagram", "social_linkedin"
        ]
        widgets = {
            "site_name": forms.TextInput(attrs={"class": "form-control"}),
            "logo": forms.FileInput(attrs={"class": "form-control"}),
            "primary_color": forms.TextInput(attrs={"class": "form-control", "type": "color", "style": "height: 38px; width: 100px;"}),
            "secondary_color": forms.TextInput(attrs={"class": "form-control", "type": "color", "style": "height: 38px; width: 100px;"}),
            "company_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "company_phone": forms.TextInput(attrs={"class": "form-control"}),
            "company_email": forms.EmailInput(attrs={"class": "form-control"}),
            "social_facebook": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://facebook.com/..."}),
            "social_twitter": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://twitter.com/..."}),
            "social_instagram": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://instagram.com/..."}),
            "social_linkedin": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://linkedin.com/..."}),
        }
