from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.DateInput, forms.PasswordInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            
            # Supprimons les attributs HTMX
            # field.widget.attrs.update({
            #     'hx-post': 'validate-field',
            #     'hx-trigger': 'blur',
            #     'hx-target': f'#{field_name}-errors',
            # })

class CustomUserCreationForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

class CustomUserChangeForm(BootstrapFormMixin, UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

class CustomUserLoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

class CustomPasswordResetForm(BootstrapFormMixin, PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

class CustomSetPasswordForm(BootstrapFormMixin, SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

class CustomUserSearchForm(BootstrapFormMixin, forms.Form):
    search = forms.CharField(
        label=_("Search"),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _("Search users..."),
            # Supprimons les attributs HTMX
            # 'hx-post': 'search-users',
            # 'hx-trigger': 'keyup changed delay:500ms',
            # 'hx-target': '#user-list',
        })
    )
