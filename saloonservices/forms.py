from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from .models import Hairstyle, Shave, HairstyleTariffHistory
from commonapp.models import Currency
from accounts.models import Barber, Client
from saloon.models import Salon
from saloonfinance.models import CashRegister
from config.permissions import is_salon_owner, is_assigned_barber

class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.DateInput, forms.NumberInput, forms.URLInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            
            # Add HTMX attributes for real-time validation
            field.widget.attrs.update({
                'hx-post': 'validate-field',
                'hx-trigger': 'blur',
                'hx-target': f'#{ field_name }-errors',
            })

class HairstyleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Hairstyle
        fields = ['name', 'current_tariff', 'currency', 'salon']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Enter hairstyle name')}),
            'current_tariff': forms.NumberInput(attrs={'step': '0.01'}),
            'currency': forms.Select(attrs={'hx-get': '/currencies/', 'hx-target': '#id_currency'}),
            'salon': forms.Select(attrs={'hx-get': '/salons/', 'hx-target': '#id_salon'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['salon'].queryset = Salon.objects.filter(owner=self.user)

    def clean(self):
        cleaned_data = super().clean()
        if self.user and cleaned_data.get('salon'):
            if not (is_salon_owner(self.user, cleaned_data['salon']) or is_assigned_barber(self.user, cleaned_data['salon'])):
                raise forms.ValidationError(_("You don't have permission to manage hairstyles for this salon."))
        return cleaned_data

class ShaveForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Shave
        fields = ['barber', 'hairstyle', 'amount', 'currency', 'exchange_rate', 'client', 'cashregister', 'date_shave', 'salon', 'status']
        widgets = {
            'barber': forms.Select(attrs={'hx-get': '/barbers/', 'hx-target': '#id_barber'}),
            'hairstyle': forms.Select(attrs={'hx-get': '/hairstyles/', 'hx-target': '#id_hairstyle'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'currency': forms.Select(attrs={'hx-get': '/currencies/', 'hx-target': '#id_currency'}),
            'exchange_rate': forms.NumberInput(attrs={'step': '0.0001'}),
            'client': forms.Select(attrs={'hx-get': '/clients/', 'hx-target': '#id_client'}),
            'cashregister': forms.Select(attrs={'hx-get': '/cashregisters/', 'hx-target': '#id_cashregister'}),
            'date_shave': forms.DateInput(attrs={'type': 'date'}),
            'salon': forms.Select(attrs={'hx-get': '/salons/', 'hx-target': '#id_salon'}),
            'status': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['salon'].queryset = Salon.objects.filter(owner=self.user)
            self.fields['barber'].queryset = Barber.objects.filter(salon__owner=self.user)
            self.fields['hairstyle'].queryset = Hairstyle.objects.filter(salon__owner=self.user)
            self.fields['cashregister'].queryset = CashRegister.objects.filter(salon__owner=self.user)

    def clean(self):
        cleaned_data = super().clean()
        if self.user and cleaned_data.get('salon'):
            if not (is_salon_owner(self.user, cleaned_data['salon']) or is_assigned_barber(self.user, cleaned_data['salon'])):
                raise forms.ValidationError(_("You don't have permission to manage shaves for this salon."))
        return cleaned_data

class HairstyleSearchForm(BootstrapFormMixin, forms.Form):
    name = forms.CharField(
        label=_("Hairstyle Name"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _("Search by name..."), 'hx-get': '/hairstyles/', 'hx-trigger': 'keyup changed delay:500ms', 'hx-target': '#hairstyle-list'})
    )
    salon = forms.ModelChoiceField(
        label=_("Salon"),
        queryset=Salon.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/hairstyles/', 'hx-trigger': 'change', 'hx-target': '#hairstyle-list'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['salon'].queryset = Salon.objects.filter(owner=self.user)

class ShaveSearchForm(BootstrapFormMixin, forms.Form):
    barber = forms.ModelChoiceField(
        label=_("Barber"),
        queryset=Barber.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/shaves/', 'hx-trigger': 'change', 'hx-target': '#shave-list'})
    )
    hairstyle = forms.ModelChoiceField(
        label=_("Hairstyle"),
        queryset=Hairstyle.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/shaves/', 'hx-trigger': 'change', 'hx-target': '#shave-list'})
    )
    client = forms.ModelChoiceField(
        label=_("Client"),
        queryset=Client.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/shaves/', 'hx-trigger': 'change', 'hx-target': '#shave-list'})
    )
    start_date = forms.DateField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'hx-get': '/shaves/', 'hx-trigger': 'change', 'hx-target': '#shave-list'})
    )
    end_date = forms.DateField(
        label=_("End Date"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'hx-get': '/shaves/', 'hx-trigger': 'change', 'hx-target': '#shave-list'})
    )
    salon = forms.ModelChoiceField(
        label=_("Salon"),
        queryset=Salon.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/shaves/', 'hx-trigger': 'change', 'hx-target': '#shave-list'})
    )
    status = forms.ChoiceField(
        label=_("Status"),
        choices=[('', _('All'))] + Shave.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'hx-get': '/shaves/', 'hx-trigger': 'change', 'hx-target': '#shave-list'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['salon'].queryset = Salon.objects.filter(owner=self.user)
            self.fields['barber'].queryset = Barber.objects.filter(salon__owner=self.user)
            self.fields['hairstyle'].queryset = Hairstyle.objects.filter(salon__owner=self.user)
            self.fields['client'].queryset = Client.objects.filter(salon__owner=self.user)

class HairstyleTariffHistoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = HairstyleTariffHistory
        fields = ['hairstyle', 'tariff', 'effective_date']
        widgets = {
            'hairstyle': forms.Select(attrs={'hx-get': '/hairstyles/', 'hx-target': '#id_hairstyle'}),
            'tariff': forms.NumberInput(attrs={'step': '0.01'}),
            'effective_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['hairstyle'].queryset = Hairstyle.objects.filter(salon__owner=self.user)

    def clean(self):
        cleaned_data = super().clean()
        if self.user and cleaned_data.get('hairstyle'):
            salon = cleaned_data['hairstyle'].salon
            if not (is_salon_owner(self.user, salon) or is_assigned_barber(self.user, salon)):
                raise forms.ValidationError(_("You don't have permission to manage tariff history for this hairstyle."))
        return cleaned_data