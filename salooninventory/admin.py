from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Item, ItemUsed, ItemPurchase

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'currency', 'current_stock', 'salon')
    list_filter = ('salon', 'currency')
    search_fields = ('name', 'salon__name')
    ordering = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'item_purpose', 'price', 'currency', 'salon', 'current_stock')
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('exchange_rate', 'amount_in_default_currency'),
        }),
    )

    readonly_fields = ('amount_in_default_currency',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('salon',)
        return self.readonly_fields

@admin.register(ItemUsed)
class ItemUsedAdmin(admin.ModelAdmin):
    list_display = ('item', 'shave', 'barber', 'quantity', 'salon', 'created_at')
    list_filter = ('salon', 'barber', 'item', 'created_at')
    search_fields = ('item__name', 'barber__user__username', 'shave__client__user__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('item', 'shave', 'barber', 'quantity', 'salon')
        }),
        (_('Additional Information'), {
            'fields': ('note',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('salon',)
        return ()

@admin.register(ItemPurchase)
class ItemPurchaseAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity', 'purchase_price', 'currency', 'purchase_date', 'supplier', 'salon')
    list_filter = ('salon', 'currency', 'purchase_date', 'supplier')
    search_fields = ('item__name', 'supplier', 'salon__name')
    date_hierarchy = 'purchase_date'
    ordering = ('-purchase_date',)

    fieldsets = (
        (None, {
            'fields': ('item', 'quantity', 'purchase_price', 'currency', 'purchase_date', 'supplier', 'salon', 'cashregister')
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('exchange_rate', 'purchase_price_in_default_currency'),
        }),
    )

    readonly_fields = ('purchase_price_in_default_currency',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('salon', 'cashregister')
        return self.readonly_fields

# Optionally, you can customize the admin site header and title
admin.site.site_header = _("Saloon Inventory Administration")
admin.site.site_title = _("Saloon Inventory Admin Portal")
admin.site.index_title = _("Welcome to Saloon Inventory Admin Portal")