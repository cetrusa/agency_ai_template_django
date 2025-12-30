from django.contrib import admin
from django.utils.html import format_html

from .models import GlobalConfig


@admin.register(GlobalConfig)
class GlobalConfigAdmin(admin.ModelAdmin):
    list_display = ["site_name", "color_preview", "navbar_fixed"]
    fieldsets = (
        ("Identidad", {"fields": ("site_name", "logo")}),
        ("Tema Visual", {"fields": ("primary_color",)}),
        ("Layout", {"fields": ("navbar_fixed", "sidebar_collapsed")}),
    )

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 24px; height: 24px; background-color: {}; border-radius: 4px; border: 1px solid #ccc;"></div>',
            obj.primary_color,
        )

    color_preview.short_description = "Color"

    def has_add_permission(self, request):
        # Solo permitir 1 registro
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
