from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin
from .models import Salon, SalonAssignment

@admin.register(Salon)
class SalonAdmin(MPTTModelAdmin):
    list_display = ('name', 'owner', 'address', 'phone', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'owner__username')
    ordering = ('name',)

    fieldsets = (
        (None, {'fields': ('name', 'description', 'owner')}),
        (_('Contact Information'), {'fields': ('address', 'phone', 'email')}),
        (_('Hierarchy'), {'fields': ('parent',)}),
        (_('Status'), {'fields': ('is_active',)}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('owner',)
        return ()

@admin.register(SalonAssignment)
class SalonAssignmentAdmin(admin.ModelAdmin):
    list_display = ('barber', 'salon', 'start_date', 'end_date', 'is_active', 'is_current')
    list_filter = ('is_active', 'salon')
    search_fields = ('barber__username', 'salon__name')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)

    fieldsets = (
        (None, {'fields': ('barber', 'salon')}),
        (_('Assignment Period'), {'fields': ('start_date', 'end_date')}),
        (_('Status'), {'fields': ('is_active',)}),
        (_('Documents'), {'fields': ('contract',)}),
    )

    readonly_fields = ('is_current',)

    def is_current(self, obj):
        return obj.is_current
    is_current.boolean = True
    is_current.short_description = _("Is Current")

# Optionally, you can customize the admin site header and title
admin.site.site_header = _("Saloon Management Administration")
admin.site.site_title = _("Saloon Management Admin Portal")
admin.site.index_title = _("Welcome to Saloon Management Admin Portal")
