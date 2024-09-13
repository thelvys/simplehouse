from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Salon, Barber, Client, SalonPermission
from accounts.models import CustomUser

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
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})

class SalonSearchForm(BootstrapFormMixin, forms.Form):
    name = forms.CharField(max_length=255, required=False, label=_("Salon Name"))

class SalonForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'description', 'address', 'phone', 'email', 'parent', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.instance.pk:  # If it's an update
            if self.user and not self.user.is_superuser:
                if self.instance.owner != self.user:
                    # If the user is not the owner or a superuser, disable all fields
                    for field in self.fields:
                        self.fields[field].disabled = True
                else:
                    # If the user is the owner but not a superuser, remove the parent field
                    del self.fields['parent']
        else:  # If it's a creation
            # The parent field remains active for all users during creation
            pass

class BarberForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Barber
        fields = ['user', 'barber_type', 'contract', 'phone', 'address', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        existing_barbers = Barber.objects.values_list('user', flat=True)
        self.fields['user'].queryset = CustomUser.objects.exclude(
            id__in=existing_barbers
        ).exclude(is_staff=True)

class ClientForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ['user', 'address', 'phone']

    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        existing_clients = Client.objects.values_list('user', flat=True)
        self.fields['user'].queryset = CustomUser.objects.exclude(
            id__in=existing_clients
        ).exclude(is_staff=True)

class SalonPermissionForm(BootstrapFormMixin, forms.Form):
    user = forms.ModelChoiceField(queryset=None, label=_("User"))
    permission_type = forms.ChoiceField(choices=SalonPermission.PERMISSION_CHOICES, label=_("Permission Type"))
    action = forms.ChoiceField(choices=[('add', _('Add')), ('remove', _('Remove'))], label=_("Action"))

    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        if self.salon:
            self.fields['user'].queryset = self.salon.users.exclude(
                id__in=SalonPermission.objects.filter(salon=self.salon).values_list('user_id', flat=True)
            )
