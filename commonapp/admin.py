from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Currency, Attachment

# Register your models here.

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('code', 'name')
    ordering = ('code',)

    fieldsets = (
        (None, {'fields': ('code', 'name')}),
        (_('Settings'), {'fields': ('is_default',)}),
    )

    def save_model(self, request, obj, form, change):
        if obj.is_default:
            Currency.objects.filter(is_default=True).update(is_default=False)
        super().save_model(request, obj, form, change)

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file', 'description', 'created_at', 'modified_at')
    search_fields = ('file', 'description')
    readonly_fields = ('created_at', 'modified_at')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('file', 'description')}),
        (_('Timestamps'), {'fields': ('created_at', 'modified_at')}),
    )

# Optionally, you can customize the admin site header and title
admin.site.site_header = _("Common App Administration")
admin.site.site_title = _("Common App Admin Portal")
admin.site.index_title = _("Welcome to Common App Admin Portal")
