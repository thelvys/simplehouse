from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Currency, Attachment

class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ['code', 'name', 'is_default']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if len(code) != 3:
            raise forms.ValidationError(_("Currency code must be exactly 3 characters long."))
        return code.upper()

    def clean(self):
        cleaned_data = super().clean()
        is_default = cleaned_data.get('is_default')
        if is_default:
            existing_default = Currency.objects.filter(is_default=True).exclude(pk=self.instance.pk)
            if existing_default.exists():
                self.add_error('is_default', _("There can only be one default currency."))
        return cleaned_data

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            max_size = 5 * 1024 * 1024  # 5 MB
            if file.size > max_size:
                raise forms.ValidationError(_("File size must be no more than 5 MB."))
        return file

class CurrencySearchForm(forms.Form):
    code = forms.CharField(
        label=_("Currency Code"),
        max_length=3,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Search by code...")})
    )
    name = forms.CharField(
        label=_("Currency Name"),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Search by name...")})
    )
    is_default = forms.BooleanField(
        label=_("Is Default"),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class AttachmentSearchForm(forms.Form):
    file_name = forms.CharField(
        label=_("File Name"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Search by file name...")})
    )
    description = forms.CharField(
        label=_("Description"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Search by description...")})
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
