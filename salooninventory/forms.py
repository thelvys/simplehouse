from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Item, ItemUsed, ItemPurchase
from saloonservices.models import Hairstyle
from saloon.models import Salon
from accounts.models import Barber
from saloonfinance.models import Currency, CashRegister

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'item_purpose', 'price', 'currency', 'salon', 'current_stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'item_purpose': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'salon': forms.Select(attrs={'class': 'form-select'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError(_("Price cannot be negative."))
        return price

class ItemUsedForm(forms.ModelForm):
    class Meta:
        model = ItemUsed
        fields = ['item', 'shave', 'barber', 'quantity', 'note', 'salon']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'shave': forms.Select(attrs={'class': 'form-select'}),
            'barber': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'salon': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')
        shave = cleaned_data.get('shave')

        if item and quantity:
            if quantity <= 0:
                raise forms.ValidationError(_("Quantity must be positive."))
            if item.current_stock < quantity:
                raise forms.ValidationError(_("Not enough items in stock."))
        
        if shave and shave.status != 'COMPLETED':
            raise forms.ValidationError(_("Items can only be used for completed shaves."))

        return cleaned_data

class ItemPurchaseForm(forms.ModelForm):
    class Meta:
        model = ItemPurchase
        fields = ['item', 'quantity', 'purchase_price', 'currency', 'purchase_date', 'supplier', 'cashregister', 'salon']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'cashregister': forms.Select(attrs={'class': 'form-select'}),
            'salon': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        purchase_price = cleaned_data.get('purchase_price')
        quantity = cleaned_data.get('quantity')

        if purchase_price and purchase_price <= 0:
            raise forms.ValidationError(_("Purchase price must be positive."))
        if quantity and quantity <= 0:
            raise forms.ValidationError(_("Quantity must be positive."))

        return cleaned_data

class ItemSearchForm(forms.Form):
    name = forms.CharField(
        label=_("Item Name"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Search by name...")})
    )
    hairstyle = forms.ModelChoiceField(
        label=_("Hairstyle"),
        queryset=Hairstyle.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    salon = forms.ModelChoiceField(
        label=_("Salon"),
        queryset=Salon.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class ItemUsedSearchForm(forms.Form):
    item = forms.ModelChoiceField(
        label=_("Item"),
        queryset=Item.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    barber = forms.ModelChoiceField(
        label=_("Barber"),
        queryset=Barber.objects.all(),
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

class ItemPurchaseSearchForm(forms.Form):
    item = forms.ModelChoiceField(
        label=_("Item"),
        queryset=Item.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    supplier = forms.CharField(
        label=_("Supplier"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Search by supplier...")})
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
