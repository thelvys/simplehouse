from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CashRegister, Payment, Transalon, PaymentType
from commonapp.models import Currency
from saloon.models import Salon, Barber
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

class CashRegisterForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CashRegister
        fields = ['name', 'balance', 'currency']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Enter cash register name')}),
            'balance': forms.NumberInput(attrs={'step': '0.01'}),
            'currency': forms.Select(attrs={'hx-get': '/currencies/', 'hx-target': '#id_currency'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.user and self.salon:
            if not (is_salon_owner(self.user, self.salon) or is_assigned_barber(self.user, self.salon)):
                raise forms.ValidationError(_("You don't have permission to manage cash registers for this salon."))
        return cleaned_data

    def save(self, commit=True):
        cash_register = super().save(commit=False)
        cash_register.salon = self.salon
        if commit:
            cash_register.save(user=self.user)
        return cash_register

class PaymentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['barber', 'amount', 'currency', 'exchange_rate', 'start_date', 'end_date', 'payment_type', 'cashregister', 'date_payment']
        widgets = {
            'barber': forms.Select(attrs={'hx-get': '/barbers/', 'hx-target': '#id_barber'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'currency': forms.Select(attrs={'hx-get': '/currencies/', 'hx-target': '#id_currency'}),
            'exchange_rate': forms.NumberInput(attrs={'step': '0.000001'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_type': forms.Select(attrs={'hx-get': '/payment-types/', 'hx-target': '#id_payment_type'}),
            'cashregister': forms.Select(attrs={'hx-get': '/cashregisters/', 'hx-target': '#id_cashregister'}),
            'date_payment': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        if self.salon:
            self.fields['barber'].queryset = Barber.objects.filter(salon=self.salon)
            self.fields['cashregister'].queryset = CashRegister.objects.filter(salon=self.salon)

    def clean(self):
        cleaned_data = super().clean()
        if self.user and self.salon:
            if not (is_salon_owner(self.user, self.salon) or is_assigned_barber(self.user, self.salon)):
                raise forms.ValidationError(_("You don't have permission to manage payments for this salon."))
        return cleaned_data

    def save(self, commit=True):
        payment = super().save(commit=False)
        payment.salon = self.salon
        if commit:
            payment.save(user=self.user)
        return payment

class TransalonForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Transalon
        fields = ['trans_name', 'amount', 'currency', 'exchange_rate', 'date_trans', 'trans_type', 'cashregister']
        widgets = {
            'trans_name': forms.TextInput(attrs={'placeholder': _('Enter transaction description')}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'currency': forms.Select(attrs={'hx-get': '/currencies/', 'hx-target': '#id_currency'}),
            'exchange_rate': forms.NumberInput(attrs={'step': '0.000001'}),
            'date_trans': forms.DateInput(attrs={'type': 'date'}),
            'trans_type': forms.Select(),
            'cashregister': forms.Select(attrs={'hx-get': '/cashregisters/', 'hx-target': '#id_cashregister'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        if self.salon:
            self.fields['cashregister'].queryset = CashRegister.objects.filter(salon=self.salon)

    def clean(self):
        cleaned_data = super().clean()
        if self.user and self.salon:
            if not (is_salon_owner(self.user, self.salon) or is_assigned_barber(self.user, self.salon)):
                raise forms.ValidationError(_("You don't have permission to manage transactions for this salon."))
        return cleaned_data

    def save(self, commit=True):
        transalon = super().save(commit=False)
        transalon.salon = self.salon
        if commit:
            transalon.save(user=self.user)
        return transalon

class CashRegisterSearchForm(BootstrapFormMixin, forms.Form):
    name = forms.CharField(
        label=_("Cash Register Name"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _("Search by name..."), 'hx-get': '/cashregisters/', 'hx-trigger': 'keyup changed delay:500ms', 'hx-target': '#cashregister-list'})
    )

class PaymentSearchForm(BootstrapFormMixin, forms.Form):
    barber = forms.ModelChoiceField(
        label=_("Barber"),
        queryset=Barber.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/payments/', 'hx-trigger': 'change', 'hx-target': '#payment-list'})
    )
    payment_type = forms.ModelChoiceField(
        label=_("Payment Type"),
        queryset=PaymentType.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/payments/', 'hx-trigger': 'change', 'hx-target': '#payment-list'})
    )
    start_date = forms.DateField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'hx-get': '/payments/', 'hx-trigger': 'change', 'hx-target': '#payment-list'})
    )
    end_date = forms.DateField(
        label=_("End Date"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'hx-get': '/payments/', 'hx-trigger': 'change', 'hx-target': '#payment-list'})
    )

    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        if self.salon:
            self.fields['barber'].queryset = Barber.objects.filter(salon=self.salon)

class TransalonSearchForm(BootstrapFormMixin, forms.Form):
    trans_name = forms.CharField(
        label=_("Transaction Name"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _("Search by transaction name..."), 'hx-get': '/transalons/', 'hx-trigger': 'keyup changed delay:500ms', 'hx-target': '#transalon-list'})
    )
    trans_type = forms.ChoiceField(
        label=_("Transaction Type"),
        choices=[('', _('All'))] + Transalon.TransactionType.choices,
        required=False,
        widget=forms.Select(attrs={'hx-get': '/transalons/', 'hx-trigger': 'change', 'hx-target': '#transalon-list'})
    )
    start_date = forms.DateField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'hx-get': '/transalons/', 'hx-trigger': 'change', 'hx-target': '#transalon-list'})
    )
    end_date = forms.DateField(
        label=_("End Date"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'hx-get': '/transalons/', 'hx-trigger': 'change', 'hx-target': '#transalon-list'})
    )