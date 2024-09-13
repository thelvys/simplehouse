from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Item, ItemUsed, ItemPurchase
from saloonservices.models import Hairstyle
from saloon.models import Salon, Barber
from saloonfinance.models import CashRegister
from config.permissions import is_salon_owner, is_assigned_barber

class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.EmailInput, forms.URLInput, forms.DateInput)):
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
                'hx-target': f'#{field_name}-errors',
            })

class ItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'item_purpose', 'price', 'currency', 'salon', 'current_stock']
        widgets = {
            'item_purpose': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['salon'].queryset = Salon.objects.filter(owner=self.user)
            self.fields['item_purpose'].queryset = Hairstyle.objects.filter(salon__owner=self.user)

    def clean(self):
        cleaned_data = super().clean()
        salon = cleaned_data.get('salon')
        if self.user and salon:
            if not (is_salon_owner(self.user, salon) or is_assigned_barber(self.user, salon)):
                raise ValidationError(_("You don't have permission to manage inventory items for this salon."))
        return cleaned_data

class ItemUsedForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ItemUsed
        fields = ['item', 'shave', 'barber', 'quantity', 'note', 'salon']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['salon'].queryset = Salon.objects.filter(owner=self.user)
            self.fields['item'].queryset = Item.objects.filter(salon__owner=self.user)
            self.fields['barber'].queryset = Barber.objects.filter(salon__owner=self.user)

    def clean(self):
        cleaned_data = super().clean()
        salon = cleaned_data.get('salon')
        if self.user and salon:
            if not (is_salon_owner(self.user, salon) or is_assigned_barber(self.user, salon) or is_assigned_barber(self.user, salon)):
                raise ValidationError(_("You don't have permission to use inventory items for this salon."))
        return cleaned_data

class ItemPurchaseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ItemPurchase
        fields = ['item', 'quantity', 'purchase_price', 'currency', 'purchase_date', 'supplier', 'cashregister', 'salon']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['salon'].queryset = Salon.objects.filter(owner=self.user)
            self.fields['item'].queryset = Item.objects.filter(salon__owner=self.user)
            self.fields['cashregister'].queryset = CashRegister.objects.filter(salon__owner=self.user)

    def clean(self):
        cleaned_data = super().clean()
        salon = cleaned_data.get('salon')
        if self.user and salon:
            if not (is_salon_owner(self.user, salon) or is_assigned_barber(self.user, salon)):
                raise ValidationError(_("You don't have permission to purchase inventory items for this salon."))
        return cleaned_data

class ItemSearchForm(BootstrapFormMixin, forms.Form):
    name = forms.CharField(
        label=_("Item Name"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _("Search by name..."), 'hx-get': '/inventory/items/', 'hx-trigger': 'keyup changed delay:500ms', 'hx-target': '#item-list'})
    )
    hairstyle = forms.ModelChoiceField(
        label=_("Hairstyle"),
        queryset=Hairstyle.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/inventory/items/', 'hx-trigger': 'change', 'hx-target': '#item-list'})
    )
    salon = forms.ModelChoiceField(
        label=_("Salon"),
        queryset=Salon.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/inventory/items/', 'hx-trigger': 'change', 'hx-target': '#item-list'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['salon'].queryset = Salon.objects.filter(owner=self.user)
            self.fields['hairstyle'].queryset = Hairstyle.objects.filter(salon__owner=self.user)

class ItemUsedSearchForm(BootstrapFormMixin, forms.Form):
    item = forms.ModelChoiceField(
        label=_("Item"),
        queryset=Item.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/inventory/items-used/', 'hx-trigger': 'change', 'hx-target': '#item-used-list'})
    )
    barber = forms.ModelChoiceField(
        label=_("Barber"),
        queryset=Barber.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/inventory/items-used/', 'hx-trigger': 'change', 'hx-target': '#item-used-list'})
    )
    start_date = forms.DateField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'hx-get': '/inventory/items-used/', 'hx-trigger': 'change', 'hx-target': '#item-used-list'})
    )
    end_date = forms.DateField(
        label=_("End Date"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'hx-get': '/inventory/items-used/', 'hx-trigger': 'change', 'hx-target': '#item-used-list'})
    )
    salon = forms.ModelChoiceField(
        label=_("Salon"),
        queryset=Salon.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/inventory/items-used/', 'hx-trigger': 'change', 'hx-target': '#item-used-list'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['salon'].queryset = Salon.objects.filter(owner=self.user)
            self.fields['item'].queryset = Item.objects.filter(salon__owner=self.user)
            self.fields['barber'].queryset = Barber.objects.filter(salon__owner=self.user)

class ItemPurchaseSearchForm(BootstrapFormMixin, forms.Form):
    item = forms.ModelChoiceField(
        label=_("Item"),
        queryset=Item.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/inventory/purchases/', 'hx-trigger': 'change', 'hx-target': '#purchase-list'})
    )
    supplier = forms.CharField(
        label=_("Supplier"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _("Search by supplier..."), 'hx-get': '/inventory/purchases/', 'hx-trigger': 'keyup changed delay:500ms', 'hx-target': '#purchase-list'})
    )
    start_date = forms.DateField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'hx-get': '/inventory/purchases/', 'hx-trigger': 'change', 'hx-target': '#purchase-list'})
    )
    end_date = forms.DateField(
        label=_("End Date"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'hx-get': '/inventory/purchases/', 'hx-trigger': 'change', 'hx-target': '#purchase-list'})
    )
    salon = forms.ModelChoiceField(
        label=_("Salon"),
        queryset=Salon.objects.all(),
        required=False,
        widget=forms.Select(attrs={'hx-get': '/inventory/purchases/', 'hx-trigger': 'change', 'hx-target': '#purchase-list'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['salon'].queryset = Salon.objects.filter(owner=self.user)
            self.fields['item'].queryset = Item.objects.filter(salon__owner=self.user)