from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Salon, Barber, Client, BarberType, SalonPermission
from config.permissions import is_salon_owner, is_assigned_barber

CustomUser = get_user_model()

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
            
            # Add HTMX attributes for real-time validation
            field.widget.attrs.update({
                'hx-post': 'validate-field',
                'hx-trigger': 'blur',
                'hx-target': f'#{ field_name }-errors',
            })

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
        if self.user and not self.user.is_superuser:
            del self.fields['parent']
            if not is_salon_owner(self.user, self.instance.pk):
                for field in self.fields:
                    self.fields[field].disabled = True

class BarberForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Barber
        fields = ['user', 'barber_type', 'contract', 'phone', 'address', 'start_date', 'end_date', 'is_active',
                  'can_manage_finance', 'can_manage_inventory', 'can_manage_shave', 'can_manage_hairstyle', 'can_manage_barbers']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_finance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_inventory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_shave': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_hairstyle': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_barbers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        if self.salon:
            self.fields['user'].queryset = CustomUser.objects.filter(is_active=True)
            self.fields['barber_type'].queryset = BarberType.objects.all()

class ClientForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ['user', 'address', 'phone']

    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        if self.salon:
            self.fields['user'].queryset = CustomUser.objects.filter(is_active=True)

class SalonSearchForm(BootstrapFormMixin, forms.Form):
    name = forms.CharField(max_length=255, required=False, label=_("Salon Name"))
    address = forms.CharField(max_length=255, required=False, label=_("Address"))
    is_active = forms.BooleanField(required=False, label=_("Is Active"), widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add HTMX attributes for real-time search
        self.fields['name'].widget.attrs.update({
            'hx-post': 'search',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#salon-list',
        })
        self.fields['address'].widget.attrs.update({
            'hx-post': 'search',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#salon-list',
        })
        self.fields['is_active'].widget.attrs.update({
            'hx-post': 'search',
            'hx-trigger': 'change',
            'hx-target': '#salon-list',
        })

class SalonPermissionForm(BootstrapFormMixin, forms.Form):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label=_("User"))
    permission_type = forms.ChoiceField(choices=SalonPermission.PERMISSION_CHOICES, label=_("Permission Type"))
    action = forms.ChoiceField(choices=[('add', _('Add')), ('remove', _('Remove'))], label=_("Action"))

    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        if self.salon:
            self.fields['user'].queryset = CustomUser.objects.exclude(
                id__in=SalonPermission.objects.filter(salon=self.salon).values_list('user_id', flat=True)
            )
        
        # Add HTMX attributes for real-time updates
        self.fields['user'].widget.attrs.update({
            'hx-post': 'update-permissions',
            'hx-trigger': 'change',
            'hx-target': '#permission-list',
        })
        self.fields['permission_type'].widget.attrs.update({
            'hx-post': 'update-permissions',
            'hx-trigger': 'change',
            'hx-target': '#permission-list',
        })
        self.fields['action'].widget.attrs.update({
            'hx-post': 'update-permissions',
            'hx-trigger': 'change',
            'hx-target': '#permission-list',
        })
