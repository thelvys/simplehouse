from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomUserLoginForm, CustomUserSearchForm
from config.permissions import SpecialUserRequiredMixin

class HtmxResponseMixin:
    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            return HttpResponse(self.get_htmx_response())
        return super().form_valid(form)

    def get_htmx_response(self):
        return ""

class SignUpView(HtmxResponseMixin, CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Registration successful. You can now log in.</div>")

class CustomLoginView(LoginView):
    form_class = CustomUserLoginForm
    template_name = 'accounts/login.html'

class CustomLogoutView(LogoutView):
    next_page = 'home'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if request.htmx:
            return HttpResponse(_("<div class='alert alert-info' role='alert'>You have been logged out successfully.</div>"))
        return response

class ProfileUpdateView(LoginRequiredMixin, HtmxResponseMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Profile updated successfully.</div>")

class UserListView(SpecialUserRequiredMixin, ListView):
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
                queryset = queryset.filter(email__icontains=search) | \
                           queryset.filter(first_name__icontains=search) | \
                           queryset.filter(last_name__icontains=search)
        return queryset

    def get_template_names(self):
        if self.request.htmx:
            return ['accounts/partials/user_list.html']
        return [self.template_name]

class UserDeleteView(UserPassesTestMixin, DeleteView):
    model = CustomUser
    success_url = reverse_lazy('user_list')
    template_name = 'accounts/user_confirm_delete.html'

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponse(status=204)
        return redirect(success_url)

def validate_field(request):
    field_name = request.POST.get('name')
    value = request.POST.get('value')
    form = CustomUserCreationForm(data={field_name: value})
    form.is_valid()
    if field_name in form.errors:
        return HttpResponse(f'<div class="invalid-feedback">{form.errors[field_name][0]}</div>')
    return HttpResponse('')
