from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib import messages
from .models import CustomUser
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, CustomUserLoginForm, 
    CustomUserSearchForm, CustomPasswordResetForm, CustomSetPasswordForm
)

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Sign up successful. You can now log in."))
        return response

class CustomLoginView(LoginView):
    form_class = CustomUserLoginForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('commonapp:home')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('commonapp:home')

    def get(self, request, *args, **kwargs):
        messages.info(request, _("You have been successfully logged out."))
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        messages.info(request, _("You have been successfully logged out."))
        return super().post(request, *args, **kwargs)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Profile updated successfully."))
        return response

class UserListView(SuperUserRequiredMixin, ListView):
    model = CustomUser
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CustomUserSearchForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        form = CustomUserSearchForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            if search:
                queryset = queryset.filter(
                    models.Q(email__icontains=search) |
                    models.Q(first_name__icontains=search) |
                    models.Q(last_name__icontains=search)
                )
        return queryset

class UserDeleteView(SuperUserRequiredMixin, DeleteView):
    model = CustomUser
    success_url = reverse_lazy('accounts:user_list')
    template_name = 'accounts/user_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("User deleted successfully."))
        return super().delete(request, *args, **kwargs)


from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
