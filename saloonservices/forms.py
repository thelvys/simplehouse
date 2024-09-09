from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Hairstyle, Shave, HairstyleTariffHistory
from commonapp.models import Currency
from accounts.models import Barber, Client
from saloon.models import Salon
from saloonfinance.models import CashRegister

class HairstyleForm(forms.ModelForm):
    class Meta:
        model = Hairstyle
        fields = ['name', 'current_tariff', 'currency', 'salon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'current_tariff': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'salon': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_current_tariff(self):
        current_tariff = self.cleaned_data.get('current_tariff')
        if current_tariff < 0:
            raise forms.ValidationError(_("Current tariff cannot be negative."))
        return current_tariff

class ShaveForm(forms.ModelForm):
    class Meta:
        model = Shave
        fields = ['barber', 'hairstyle', 'amount', 'currency', 'exchange_rate', 'client', 'cashregister', 'date_shave', 'salon', 'status']
        widgets = {
            'barber': forms.Select(attrs={'class': 'form-select'}),
            'hairstyle': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'cashregister': forms.Select(attrs={'class': 'form-select'}),
            'date_shave': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salon': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 0:
            raise forms.ValidationError(_("Amount cannot be negative."))
        return amount

class HairstyleSearchForm(forms.Form):
    name = forms.CharField(
        label=_("Hairstyle Name"),
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

class ShaveSearchForm(forms.Form):
    barber = forms.ModelChoiceField(
        label=_("Barber"),
        queryset=Barber.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    hairstyle = forms.ModelChoiceField(
        label=_("Hairstyle"),
        queryset=Hairstyle.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    client = forms.ModelChoiceField(
        label=_("Client"),
        queryset=Client.objects.all(),
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
    status = forms.ChoiceField(
        label=_("Status"),
        choices=[('', _('All'))] + Shave.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class HairstyleTariffHistoryForm(forms.ModelForm):
    class Meta:
        model = HairstyleTariffHistory
        fields = ['hairstyle', 'tariff', 'effective_date']
        widgets = {
            'hairstyle': forms.Select(attrs={'class': 'form-select'}),
            'tariff': forms.NumberInput(attrs={'class': 'form-control'}),
            'effective_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def clean_tariff(self):
        tariff = self.cleaned_data.get('tariff')
        if tariff < 0:
            raise forms.ValidationError(_("Tariff cannot be negative."))
        return tariff

class HairstyleTariffHistorySearchForm(forms.Form):
    hairstyle = forms.ModelChoiceField(
        label=_("Hairstyle"),
        queryset=Hairstyle.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateTimeField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    end_date = forms.DateTimeField(
        label=_("End Date"),
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
