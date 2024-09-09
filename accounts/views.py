from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, BarberType, Barber, Client
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, BarberTypeForm,
    BarberForm, ClientForm, BarberSignUpForm, ClientSignUpForm
)

class HtmxResponseMixin:
    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            return HttpResponse(self.get_htmx_response())
        return super().form_valid(form)

    def get_htmx_response(self):
        return ""

class BarberSignUpView(HtmxResponseMixin, CreateView):
    form_class = BarberSignUpForm
    template_name = 'accounts/register_barber.html'
    success_url = reverse_lazy('login')

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Registration successful. Please wait for admin approval.</div>")

class ClientSignUpView(HtmxResponseMixin, CreateView):
    form_class = ClientSignUpForm
    template_name = 'accounts/register_client.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Registration successful. You are now logged in.</div>")

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

class CustomLogoutView(LogoutView):
    next_page = 'home'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if request.htmx:
            return HttpResponse(_("<div class='alert alert-info' role='alert'>You have been logged out successfully.</div>"))
        return response

class ProfileUpdateView(HtmxResponseMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Profile updated successfully.</div>")

class BarberTypeListView(ListView):
    model = BarberType
    template_name = 'accounts/barber_type_list.html'
    context_object_name = 'barber_types'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BarberTypeForm()
        return context

class BarberTypeCreateView(HtmxResponseMixin, CreateView):
    model = BarberType
    form_class = BarberTypeForm
    template_name = 'accounts/barber_type_form.html'
    success_url = reverse_lazy('barber_type_list')

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Barber type added successfully.</div>")

class BarberListView(ListView):
    model = Barber
    template_name = 'accounts/barber_list.html'
    context_object_name = 'barbers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BarberForm()
        return context

class BarberCreateView(HtmxResponseMixin, CreateView):
    model = Barber
    form_class = BarberForm
    template_name = 'accounts/barber_form.html'
    success_url = reverse_lazy('barber_list')

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Barber added successfully.</div>")

class ClientListView(ListView):
    model = Client
    template_name = 'accounts/client_list.html'
    context_object_name = 'clients'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ClientForm()
        return context

class ClientCreateView(HtmxResponseMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'accounts/client_form.html'
    success_url = reverse_lazy('client_list')

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Client added successfully.</div>")

class UserDeleteView(UserPassesTestMixin, DeleteView):
    model = CustomUser
    success_url = reverse_lazy('home')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponse(status=204)
        return redirect(success_url)
