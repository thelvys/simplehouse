from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Hairstyle, Shave, HairstyleTariffHistory

@admin.register(Hairstyle)
class HairstyleAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_tariff', 'currency', 'salon')
    list_filter = ('salon', 'currency')
    search_fields = ('name',)
    ordering = ('name',)

    fieldsets = (
        (None, {'fields': ('name', 'current_tariff', 'currency', 'salon')}),
    )

@admin.register(Shave)
class ShaveAdmin(admin.ModelAdmin):
    list_display = ('barber', 'hairstyle', 'amount', 'currency', 'client', 'date_shave', 'salon', 'status')
    list_filter = ('barber', 'hairstyle', 'salon', 'status', 'date_shave')
    search_fields = ('barber__user__username', 'client__user__username', 'hairstyle__name')
    date_hierarchy = 'date_shave'
    ordering = ('-date_shave',)

    fieldsets = (
        (_('Service Details'), {'fields': ('barber', 'hairstyle', 'client', 'date_shave', 'salon', 'status')}),
        (_('Financial Details'), {'fields': ('amount', 'currency', 'exchange_rate', 'amount_in_default_currency', 'cashregister')}),
    )

    readonly_fields = ('amount_in_default_currency',)

@admin.register(HairstyleTariffHistory)
class HairstyleTariffHistoryAdmin(admin.ModelAdmin):
    list_display = ('hairstyle', 'tariff', 'effective_date')
    list_filter = ('hairstyle', 'effective_date')
    search_fields = ('hairstyle__name',)
    date_hierarchy = 'effective_date'
    ordering = ('-effective_date',)

    fieldsets = (
        (None, {'fields': ('hairstyle', 'tariff', 'effective_date')}),
    )

# Optionally, you can customize the admin site header and title
admin.site.site_header = _("Saloon Services Administration")
admin.site.site_title = _("Saloon Services Admin Portal")
admin.site.index_title = _("Welcome to Saloon Services Admin Portal")
