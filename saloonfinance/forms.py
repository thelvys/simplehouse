from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CashRegister, Payment, Transalon
from commonapp.models import Currency
from accounts.models import Barber
from saloon.models import Salon

class CashRegisterForm(forms.ModelForm):
    class Meta:
        model = CashRegister
        fields = ['name', 'balance', 'currency', 'salon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'salon': forms.Select(attrs={'class': 'form-select'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['barber', 'amount', 'currency', 'exchange_rate', 'start_date', 'end_date', 'payment_type', 'cashregister', 'date_payment', 'salon']
        widgets = {
            'barber': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'cashregister': forms.Select(attrs={'class': 'form-select'}),
            'date_payment': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salon': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        amount = cleaned_data.get("amount")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(_("Start date must be before end date."))
        
        if amount and amount <= 0:
            raise forms.ValidationError(_("Amount must be greater than zero."))

class TransalonForm(forms.ModelForm):
    class Meta:
        model = Transalon
        fields = ['trans_name', 'amount', 'currency', 'exchange_rate', 'date_trans', 'trans_type', 'cashregister', 'salon']
        widgets = {
            'trans_name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_trans': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'trans_type': forms.Select(attrs={'class': 'form-select'}),
            'cashregister': forms.Select(attrs={'class': 'form-select'}),
            'salon': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")

        if amount and amount <= 0:
            raise forms.ValidationError(_("Amount must be greater than zero."))

class CashRegisterSearchForm(forms.Form):
    name = forms.CharField(
        label=_("Cash Register Name"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Search by name...")})
    )
    salon = forms.ModelChoiceField(
        label=_("Salon"),
        queryset=Salon.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class PaymentSearchForm(forms.Form):
    barber = forms.ModelChoiceField(
        label=_("Barber"),
        queryset=Barber.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    payment_type = forms.ChoiceField(
        label=_("Payment Type"),
        choices=[('', _('All'))] + Payment.PAYMENT_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        label=_("End Date"),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    salon = forms.ModelChoiceField(
        label=_("Salon"),
        queryset=Salon.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class TransalonSearchForm(forms.Form):
    trans_name = forms.CharField(
        label=_("Transaction Name"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Search by transaction name...")})
    )
    trans_type = forms.ChoiceField(
        label=_("Transaction Type"),
        choices=[('', _('All'))] + Transalon.TRANS_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        label=_("End Date"),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    salon = forms.ModelChoiceField(
        label=_("Salon"),
        queryset=Salon.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
