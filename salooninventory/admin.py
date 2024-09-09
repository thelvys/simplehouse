from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Item, ItemUsed, ItemPurchase

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'currency', 'current_stock', 'salon')
    list_filter = ('salon', 'currency')
    search_fields = ('name',)
    ordering = ('name',)

    fieldsets = (
        (None, {'fields': ('name', 'item_purpose')}),
        (_('Pricing'), {'fields': ('price', 'currency', 'exchange_rate', 'amount_in_default_currency')}),
        (_('Stock'), {'fields': ('current_stock',)}),
        (_('Location'), {'fields': ('salon',)}),
    )

    readonly_fields = ('amount_in_default_currency',)
    filter_horizontal = ('item_purpose',)

@admin.register(ItemUsed)
class ItemUsedAdmin(admin.ModelAdmin):
    list_display = ('item', 'shave', 'barber', 'quantity', 'salon')
    list_filter = ('item', 'barber', 'salon')
    search_fields = ('item__name', 'barber__user__username', 'shave__client__user__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('item', 'shave', 'barber', 'quantity')}),
        (_('Additional Information'), {'fields': ('note',)}),
        (_('Location'), {'fields': ('salon',)}),
    )

@admin.register(ItemPurchase)
class ItemPurchaseAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity', 'purchase_price', 'currency', 'purchase_date', 'supplier', 'salon')
    list_filter = ('item', 'currency', 'purchase_date', 'salon')
    search_fields = ('item__name', 'supplier')
    date_hierarchy = 'purchase_date'
    ordering = ('-purchase_date',)

    fieldsets = (
        (None, {'fields': ('item', 'quantity', 'purchase_price', 'currency')}),
        (_('Purchase Details'), {'fields': ('purchase_date', 'supplier')}),
        (_('Financial Details'), {'fields': ('exchange_rate', 'purchase_price_in_default_currency', 'cashregister')}),
        (_('Location'), {'fields': ('salon',)}),
    )

    readonly_fields = ('purchase_price_in_default_currency',)

# Optionally, you can customize the admin site header and title
admin.site.site_header = _("Saloon Inventory Administration")
admin.site.site_title = _("Saloon Inventory Admin Portal")
admin.site.index_title = _("Welcome to Saloon Inventory Admin Portal")
