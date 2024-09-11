from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CashRegister, Payment, Transalon, PaymentType

@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance', 'currency', 'salon')
    list_filter = ('salon', 'currency')
    search_fields = ('name', 'salon__name')
    readonly_fields = ('balance',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('salon',)
        return self.readonly_fields

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('barber', 'amount', 'currency', 'payment_type', 'date_payment', 'salon')
    list_filter = ('payment_type', 'salon', 'date_payment')
    search_fields = ('barber__user__username', 'barber__user__first_name', 'barber__user__last_name')
    date_hierarchy = 'date_payment'

    fieldsets = (
        (None, {
            'fields': ('barber', 'amount', 'currency', 'exchange_rate', 'amount_in_default_currency')
        }),
        (_('Payment Details'), {
            'fields': ('start_date', 'end_date', 'payment_type', 'cashregister', 'date_payment')
        }),
        (_('Salon'), {
            'fields': ('salon',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('amount_in_default_currency',)
        return self.readonly_fields

@admin.register(Transalon)
class TransalonAdmin(admin.ModelAdmin):
    list_display = ('trans_name', 'amount', 'currency', 'trans_type', 'date_trans', 'salon')
    list_filter = ('trans_type', 'salon', 'date_trans')
    search_fields = ('trans_name',)
    date_hierarchy = 'date_trans'

    fieldsets = (
        (None, {
            'fields': ('trans_name', 'amount', 'currency', 'exchange_rate', 'amount_in_default_currency')
        }),
        (_('Transaction Details'), {
            'fields': ('date_trans', 'trans_type', 'cashregister')
        }),
        (_('Salon'), {
            'fields': ('salon',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('amount_in_default_currency',)
        return self.readonly_fields

@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

# Optionally, you can customize the admin site header and title
admin.site.site_header = _("Saloon Finance Administration")
admin.site.site_title = _("Saloon Finance Admin Portal")
admin.site.index_title = _("Welcome to Saloon Finance Admin Portal")
