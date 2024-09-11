from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin
from .models import Salon, Barber, Client, BarberType, SalonPermission

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

@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ('user', 'salon', 'barber_type', 'phone', 'is_active')
    list_filter = ('salon', 'barber_type', 'is_active')
    search_fields = ('user__username', 'user__email', 'salon__name')
    ordering = ('user__username',)

    fieldsets = (
        (None, {'fields': ('user', 'salon', 'barber_type')}),
        (_('Contact Information'), {'fields': ('phone', 'address')}),
        (_('Employment'), {'fields': ('start_date', 'end_date')}),
        (_('Status'), {'fields': ('is_active',)}),
        (_('Documents'), {'fields': ('contract',)}),
        (_('Permissions'), {'fields': ('can_manage_finance', 'can_manage_inventory', 'can_manage_shave', 'can_manage_hairstyle', 'can_manage_barbers')}),
    )

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'salon', 'phone')
    list_filter = ('salon',)
    search_fields = ('user__username', 'user__email', 'salon__name')
    ordering = ('user__username',)

    fieldsets = (
        (None, {'fields': ('user', 'salon')}),
        (_('Contact Information'), {'fields': ('phone', 'address')}),
    )

@admin.register(BarberType)
class BarberTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(SalonPermission)
class SalonPermissionAdmin(admin.ModelAdmin):
    list_display = ('salon', 'user', 'permission_type')
    list_filter = ('permission_type', 'salon')
    search_fields = ('salon__name', 'user__username')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('salon', 'user')
        return ()

# Optionally, you can customize the admin site header and title
admin.site.site_header = _("Saloon Management Administration")
admin.site.site_title = _("Saloon Management Admin Portal")
admin.site.index_title = _("Welcome to Saloon Management Admin Portal")
