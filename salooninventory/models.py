''' Models for the salooninventory app '''

from django.db import models, transaction 
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Sum, F

from commonapp.models import TimestampMixin
from accounts.models import Barber, Client 
from saloon.models import Salon
from saloonfinance.models import Currency, CashRegister
from saloonservices.models import Shave, Hairstyle

class Item(TimestampMixin):
    name = models.CharField(_("Name"), max_length=255)
    item_purpose = models.ManyToManyField(Hairstyle, related_name='items', verbose_name=_("Item purpose"))
    price = models.DecimalField(_("Price"), max_digits=19, decimal_places=2, default=0)
    currency = models.ForeignKey('Currency', on_delete=models.SET_DEFAULT, default=Currency.get_default, related_name='items', verbose_name=_("Currency"))
    exchange_rate = models.DecimalField(_("Exchange rate"), max_digits=10, decimal_places=4, default=1.0)
    amount_in_default_currency = models.DecimalField(_("Amount in default currency"), max_digits=19, decimal_places=2, default=0)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='items', verbose_name=_("Salon"))
    current_stock = models.PositiveIntegerField(_("Current stock"), default=0)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.currency != Currency.get_default():
            self.amount_in_default_currency = self.price / self.exchange_rate
        else:
            self.amount_in_default_currency = self.price
        super().save(*args, **kwargs)

    def clean(self):
        if self.price < 0:
            raise ValidationError(_("Price cannot be negative."))

    def get_total_value(self):
        return self.price * self.current_stock

    def get_average_purchase_price(self):
        purchases = self.purchases.aggregate(
            total_cost=Sum(F('purchase_price') * F('quantity')),
            total_quantity=Sum('quantity')
        )
        if purchases['total_quantity']:
            return purchases['total_cost'] / purchases['total_quantity']
        return 0

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")
        unique_together = ['name', 'salon']

class ItemUsed(TimestampMixin):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, verbose_name=_("Item"))
    shave = models.ForeignKey(Shave, on_delete=models.SET_NULL, null=True, related_name='items_used', verbose_name=_("Shave"))
    barber = models.ForeignKey(Barber, on_delete=models.SET_NULL, null=True, verbose_name=_("Barber"))
    quantity = models.PositiveIntegerField(_("Quantity"))
    note = models.TextField(_("Note"), blank=True)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='items_used', verbose_name=_("Salon"))

    def __str__(self):
        return f"{self.item} - {self.quantity}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError(_("Quantity must be positive."))
        if self.item.current_stock < self.quantity:
            raise ValidationError(_("Not enough items in stock."))
        if self.shave and self.shave.status != 'COMPLETED':
            raise ValidationError(_("Items can only be used for completed shaves."))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.item.current_stock -= self.quantity
        self.item.save()

    class Meta:
        unique_together = ('item', 'shave', 'salon')
        verbose_name = _("Item Used")
        verbose_name_plural = _("Items Used")

class ItemPurchase(TimestampMixin):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='purchases', verbose_name=_("Item"))
    quantity = models.PositiveIntegerField(_("Quantity"))
    purchase_price = models.DecimalField(_("Purchase price"), max_digits=19, decimal_places=2)
    currency = models.ForeignKey('Currency', on_delete=models.SET_DEFAULT, default=Currency.get_default, verbose_name=_("Currency"))
    exchange_rate = models.DecimalField(_("Exchange rate"), max_digits=10, decimal_places=4, default=1.0)
    purchase_price_in_default_currency = models.DecimalField(_("Purchase price in default currency"), max_digits=19, decimal_places=2)
    purchase_date = models.DateField(_("Purchase date"), default=timezone.now)
    supplier = models.CharField(_("Supplier"), max_length=255, blank=True)
    cashregister = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name='purchases', verbose_name=_("Cash Register"))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='item_purchases', verbose_name=_("Salon"))

    def save(self, *args, **kwargs):
        if self.currency != Currency.get_default():
            self.purchase_price_in_default_currency = self.purchase_price / self.exchange_rate
        else:
            self.purchase_price_in_default_currency = self.purchase_price
        super().save(*args, **kwargs)
        self.item.current_stock += self.quantity
        self.item.save()

    def clean(self):
        if self.purchase_price <= 0:
            raise ValidationError(_("Purchase price must be positive."))
        if self.quantity <= 0:
            raise ValidationError(_("Quantity must be positive."))

    def __str__(self):
        return f"{self.item.name} - {self.quantity} - {self.purchase_date}"

    class Meta:
        verbose_name = _("Item Purchase")
        verbose_name_plural = _("Item Purchases")

@receiver(post_save, sender=ItemPurchase)
def update_cashregister_balance(sender, instance, created, **kwargs):
    with transaction.atomic():
        if created:
            total_cost = instance.purchase_price * instance.quantity
            instance.cashregister.update_balance(total_cost, 'EXPENSE')

def get_total_inventory_value(salon):
    return sum(item.get_total_value() for item in salon.items.all())
