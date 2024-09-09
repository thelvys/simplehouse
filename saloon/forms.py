from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Salon, SalonAssignment

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'description', 'address', 'phone', 'email', 'parent', 'owner', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SalonAssignmentForm(forms.ModelForm):
    class Meta:
        model = SalonAssignment
        fields = ['salon', 'barber', 'contract', 'start_date', 'end_date', 'is_active']
        widgets = {
            'salon': forms.Select(attrs={'class': 'form-select'}),
            'barber': forms.Select(attrs={'class': 'form-select'}),
            'contract': forms.FileInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(_("Start date must be before end date."))

        return cleaned_data

class SalonSearchForm(forms.Form):
    search = forms.CharField(
        label=_("Search"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Search salons...")})
    )
    is_active = forms.BooleanField(
        label=_("Active only"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class SalonAssignmentSearchForm(forms.Form):
    salon = forms.ModelChoiceField(
        queryset=Salon.objects.all(),
        label=_("Salon"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    barber = forms.CharField(
        label=_("Barber"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Barber name...")})
    )
    is_active = forms.BooleanField(
        label=_("Active only"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    date = forms.DateField(
        label=_("Date"),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
