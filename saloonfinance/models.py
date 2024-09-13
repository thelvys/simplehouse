''' Models for the saloonfinance app '''

from django.db import models, transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db.models import F, Sum
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext_lazy as _
from commonapp.models import TimestampMixin, Currency
from saloon.models import Salon, Barber
from decimal import Decimal
from config.permissions import is_salon_owner, is_assigned_barber

class CashRegister(TimestampMixin):
    name = models.CharField(_("Name"), max_length=255)
    balance = models.DecimalField(_("Balance"), max_digits=10, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='cash_registers')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='cash_registers', verbose_name=_("Salon"))
        
    def __str__(self):
        return self.name

    def update_balance(self, amount, transaction_type):
        if transaction_type == 'INCOME':
            self.balance = F('balance') + amount
        elif transaction_type == 'EXPENSE':
            self.balance = F('balance') - amount
        self.save()

    def get_total_income(self):
        return self.transactions.filter(trans_type='INCOME').aggregate(total=Sum('amount'))['total'] or Decimal('0')

    def get_total_expenses(self):
        return self.transactions.filter(trans_type='EXPENSES').aggregate(total=Sum('amount'))['total'] or Decimal('0')

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user and not (is_salon_owner(user, self.salon) or is_assigned_barber(user, self.salon)):
            raise PermissionDenied(_("You don't have permission to manage cash registers for this salon."))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Cash Register")
        verbose_name_plural = _("Cash Registers")
        unique_together = ['name', 'salon']

class PaymentType(TimestampMixin):
    name = models.CharField(_("Name"), max_length=50, unique=True)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Is active"), default=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_default(cls):
        salary_type, created = cls.objects.get_or_create(
            name='SALARY',
            defaults={'description': 'Regular salary payment'}
        )
        return salary_type

    class Meta:
        verbose_name = _("Payment Type")
        verbose_name_plural = _("Payment Types")

class Payment(TimestampMixin):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, verbose_name=_("Barber"))
    amount = models.DecimalField(_("Amount"), max_digits=19, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, default=Currency.get_default, verbose_name=_("Currency"))
    exchange_rate = models.DecimalField(_("Exchange rate"), max_digits=10, decimal_places=6, default=1.000000)
    amount_in_default_currency = models.DecimalField(_("Amount in default currency"), max_digits=19, decimal_places=2, default=0)
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))
    payment_type = models.ForeignKey(PaymentType, on_delete=models.PROTECT, verbose_name=_("Payment type"), default=PaymentType.get_default)
    cashregister = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name='payments', verbose_name=_("Cash Register"))
    date_payment = models.DateField(_("Payment date"), default=timezone.now)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='payments', verbose_name=_("Salon"))

    def __str__(self):
        return f"{self.barber} - {self.amount} - {self.payment_type}"
    
    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user:
            if not (is_salon_owner(user, self.salon) or is_assigned_barber(user, self.salon)):
                raise PermissionDenied(_("You don't have permission to manage payments for this salon."))
        if self.currency != Currency.get_default():
            self.amount_in_default_currency = self.amount / self.exchange_rate
        else:
            self.amount_in_default_currency = self.amount
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("Start date must be before end date."))
        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero."))

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

class Transalon(TimestampMixin):
    class TransactionType(models.TextChoices):
        INCOME = 'INCOME', _('Income')
        EXPENSES = 'EXPENSES', _('Expenses')

    trans_name = models.CharField(_("Description of Transaction"), max_length=255)
    amount = models.DecimalField(_("Amount"), max_digits=19, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, default=Currency.get_default, verbose_name=_("Currency"))
    exchange_rate = models.DecimalField(_("Exchange rate"), max_digits=10, decimal_places=6, default=1.000000)
    amount_in_default_currency = models.DecimalField(_("Amount in default currency"), max_digits=19, decimal_places=2, default=0)
    date_trans = models.DateField(_("Transaction date"), default=timezone.now)
    trans_type = models.CharField(_("Transaction type"), max_length=10, choices=TransactionType.choices)
    cashregister = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name='transactions', verbose_name=_("Cash Register"))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='transactions', verbose_name=_("Salon"))

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user and not (is_salon_owner(user, self.salon) or is_assigned_barber(user, self.salon)):
            raise PermissionDenied(_("You don't have permission to manage transactions for this salon."))
        if self.currency != Currency.get_default():
            self.amount_in_default_currency = self.amount / self.exchange_rate
        else:
            self.amount_in_default_currency = self.amount
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.trans_name

    def clean(self):
        super().clean()
        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero."))

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        unique_together = ['trans_name', 'salon']

# Signals to update CashRegister balance
@receiver(post_save, sender=Payment)
@receiver(post_save, sender=Transalon)
def update_cashregister_balance(sender, instance, created, **kwargs):
    with transaction.atomic():
        if created:
            if (sender == Transalon and instance.trans_type == 'INCOME'):
                instance.cashregister.update_balance(instance.amount, 'INCOME')
            else:
                instance.cashregister.update_balance(instance.amount, 'EXPENSE')

@receiver(pre_delete, sender=Payment)
@receiver(pre_delete, sender=Transalon)
def revert_cashregister_balance(sender, instance, **kwargs):
    with transaction.atomic():
        if (sender == Transalon and instance.trans_type == 'INCOME'):
            instance.cashregister.update_balance(instance.amount, 'EXPENSE')
        else:
            instance.cashregister.update_balance(instance.amount, 'INCOME')