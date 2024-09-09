from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CashRegister, Payment, Transalon

@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance', 'currency', 'salon')
    list_filter = ('salon', 'currency')
    search_fields = ('name',)
    ordering = ('name',)

    fieldsets = (
        (None, {'fields': ('name', 'balance', 'currency')}),
        (_('Location'), {'fields': ('salon',)}),
    )

    readonly_fields = ('balance',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('salon',)
        return self.readonly_fields

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('barber', 'amount', 'currency', 'payment_type', 'date_payment', 'salon')
    list_filter = ('payment_type', 'currency', 'salon', 'date_payment')
    search_fields = ('barber__user__username',)
    date_hierarchy = 'date_payment'
    ordering = ('-date_payment',)

    fieldsets = (
        (None, {'fields': ('barber', 'amount', 'currency', 'payment_type')}),
        (_('Payment Details'), {'fields': ('start_date', 'end_date', 'date_payment')}),
        (_('Financial Details'), {'fields': ('exchange_rate', 'amount_in_default_currency', 'cashregister')}),
        (_('Location'), {'fields': ('salon',)}),
    )

    readonly_fields = ('amount_in_default_currency',)

@admin.register(Transalon)
class TransalonAdmin(admin.ModelAdmin):
    list_display = ('trans_name', 'amount', 'currency', 'trans_type', 'date_trans', 'salon')
    list_filter = ('trans_type', 'currency', 'salon', 'date_trans')
    search_fields = ('trans_name',)
    date_hierarchy = 'date_trans'
    ordering = ('-date_trans',)

    fieldsets = (
        (None, {'fields': ('trans_name', 'amount', 'currency', 'trans_type')}),
        (_('Transaction Details'), {'fields': ('date_trans',)}),
        (_('Financial Details'), {'fields': ('exchange_rate', 'amount_in_default_currency', 'cashregister')}),
        (_('Location'), {'fields': ('salon',)}),
    )

    readonly_fields = ('amount_in_default_currency',)

# Optionally, you can customize the admin site header and title
admin.site.site_header = _("Saloon Finance Administration")
admin.site.site_title = _("Saloon Finance Admin Portal")
admin.site.index_title = _("Welcome to Saloon Finance Admin Portal")
