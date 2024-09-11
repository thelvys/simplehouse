''' Models for the saloonservices app '''

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError, PermissionDenied

from commonapp.models import TimestampMixin, Currency
from saloon.models import Salon, Barber, Client
from saloonfinance.models import CashRegister
from config.permissions import is_salon_owner, is_assigned_barber

class HairstyleTariffHistory(TimestampMixin):
    hairstyle = models.ForeignKey('Hairstyle', on_delete=models.CASCADE, related_name='tariff_history', verbose_name=_("Hairstyle"))
    tariff = models.DecimalField(_("Tariff"), max_digits=19, decimal_places=2)
    effective_date = models.DateTimeField(_("Effective Date"), default=timezone.now)

    class Meta:
        verbose_name = _("Hairstyle Tariff History")
        verbose_name_plural = _("Hairstyle Tariff Histories")
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.hairstyle.name} - {self.tariff} - {self.effective_date}"

class Hairstyle(TimestampMixin):
    name = models.CharField(_("Name"), max_length=255)
    current_tariff = models.DecimalField(_("Current Tariff"), max_digits=19, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, default=Currency.get_default, verbose_name=_("Currency"))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='hairstyles', verbose_name=_("Salon"))

    def __str__(self):
        return self.name

    def clean(self):
        if self.current_tariff < 0:
            raise ValidationError(_("Current tariff cannot be negative."))

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user:
            if not (is_salon_owner(user, self.salon) or is_assigned_barber(user, self.salon)):
                raise PermissionDenied(_("You don't have permission to manage hairstyles for this salon."))
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new or 'current_tariff' in kwargs.get('update_fields', []):
            HairstyleTariffHistory.objects.create(
                hairstyle=self,
                tariff=self.current_tariff,
                effective_date=timezone.now()
            )

    def get_tariff_at_date(self, date):
        tariff_history = self.tariff_history.filter(effective_date__lte=date).order_by('-effective_date').first()
        return tariff_history.tariff if tariff_history else self.current_tariff

    class Meta:
        verbose_name = _("Hairstyle")
        verbose_name_plural = _("Hairstyles")
        unique_together = ['name', 'salon']

class Shave(TimestampMixin):
    STATUS_CHOICES = [
        ('SCHEDULED', _('Scheduled')),
        ('IN_PROGRESS', _('In Progress')),
        ('COMPLETED', _('Completed')),
        ('CANCELLED', _('Cancelled')),
    ]

    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='shaves', verbose_name=_("Barber"))
    hairstyle = models.ForeignKey(Hairstyle, on_delete=models.CASCADE, related_name='shaves', verbose_name=_("Hairstyle"))
    amount = models.DecimalField(_("Amount"), max_digits=19, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, default=Currency.get_default, related_name='shaves', verbose_name=_("Currency"))
    exchange_rate = models.DecimalField(_("Exchange rate"), max_digits=10, decimal_places=4, default=1.0)
    amount_in_default_currency = models.DecimalField(_("Amount in default currency"), max_digits=19, decimal_places=2, default=0)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='shaves', verbose_name=_("Client"))
    cashregister = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name='shaves', verbose_name=_("Cash Register"))
    date_shave = models.DateField(_("Shave date"), default=timezone.now)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='shaves', verbose_name=_("Salon"))
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    def __str__(self):
        return f"{self.barber} - {self.hairstyle}"

    def clean(self):
        if self.amount < 0:
            raise ValidationError(_("Amount cannot be negative."))

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user:
            if not (is_salon_owner(user, self.salon) or is_assigned_barber(user, self.salon)):
                raise PermissionDenied(_("You don't have permission to manage shaves for this salon."))
        if self.currency != Currency.get_default():
            self.amount_in_default_currency = self.amount / self.exchange_rate
        else:
            self.amount_in_default_currency = self.amount
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return self.amount + sum(item_used.item.price * item_used.quantity for item_used in self.items_used.all())

    @property
    def tariff_difference(self):
        tariff_at_shave_date = self.hairstyle.get_tariff_at_date(self.date_shave)
        return self.amount - tariff_at_shave_date

    @classmethod
    def get_total_revenue(cls, salon, start_date=None, end_date=None):
        queryset = cls.objects.filter(salon=salon, status='COMPLETED')
        if start_date:
            queryset = queryset.filter(date_shave__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_shave__lte=end_date)
        return queryset.aggregate(total_revenue=models.Sum('amount_in_default_currency'))['total_revenue'] or 0

    class Meta:
        verbose_name = _("Shave")
        verbose_name_plural = _("Shaves")

# Signals to update CashRegister balance
@receiver(post_save, sender=Shave)
def update_cashregister_balance(sender, instance, created, **kwargs):
    with transaction.atomic():
        if created and instance.status == 'COMPLETED':
            instance.cashregister.update_balance(instance.amount, 'INCOME')

@receiver(pre_delete, sender=Shave)
def revert_cashregister_balance(sender, instance, **kwargs):
    with transaction.atomic():
        if instance.status == 'COMPLETED':
            instance.cashregister.update_balance(instance.amount, 'EXPENSE')