from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import Currency, Attachment
from .forms import CurrencyForm, AttachmentForm, CurrencySearchForm, AttachmentSearchForm
from saloon.models import Salon
from saloonservices.models import Hairstyle
from config.permissions import (
    CanManageSalonMixin, CanReadSalonMixin, CanManageFinanceMixin,
    is_salon_owner, is_assigned_barber
)

class HomeView(TemplateView):
    template_name = 'commonapp/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Welcome to Saloon Management System")
        context['featured_salons'] = Salon.objects.filter(is_active=True)[:5]
        context['popular_hairstyles'] = Hairstyle.objects.all().order_by('-id')[:6]
        
        user = self.request.user
        if user.is_authenticated:
            salon_id = self.kwargs.get('salon_id')
            context['can_manage_currency'] = is_salon_owner(user, salon_id) or is_assigned_barber(user, salon_id)
            context['can_manage_attachment'] = is_salon_owner(user, salon_id) or is_assigned_barber(user, salon_id)
        
        return context

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        # action that need authentication
        pass

class CurrencyListView(LoginRequiredMixin, CanManageFinanceMixin, ListView):
    model = Currency
    template_name = 'commonapp/partials/currency_list.html'
    context_object_name = 'currencies'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = CurrencySearchForm(self.request.GET)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            name = form.cleaned_data.get('name')
            is_default = form.cleaned_data.get('is_default')
            if code:
                queryset = queryset.filter(code__icontains=code)
            if name:
                queryset = queryset.filter(name__icontains=name)
            if is_default is not None:
                queryset = queryset.filter(is_default=is_default)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CurrencySearchForm(self.request.GET)
        return context

class CurrencyCreateView(LoginRequiredMixin, CanManageFinanceMixin, CreateView):
    model = Currency
    form_class = CurrencyForm
    template_name = 'commonapp/partials/currency_form.html'
    success_url = reverse_lazy('commonapp:currency_list')

class CurrencyUpdateView(LoginRequiredMixin, CanManageFinanceMixin, UpdateView):
    model = Currency
    form_class = CurrencyForm
    template_name = 'commonapp/partials/currency_form.html'
    success_url = reverse_lazy('commonapp:currency_list')

class CurrencyDeleteView(LoginRequiredMixin, CanManageFinanceMixin, DeleteView):
    model = Currency
    success_url = reverse_lazy('commonapp:currency_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse(status=204)

class AttachmentListView(LoginRequiredMixin, CanReadSalonMixin, ListView):
    model = Attachment
    template_name = 'commonapp/partials/attachment_list.html'
    context_object_name = 'attachments'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = AttachmentSearchForm(self.request.GET)
        if form.is_valid():
            file_name = form.cleaned_data.get('file_name')
            description = form.cleaned_data.get('description')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            if file_name:
                queryset = queryset.filter(file__icontains=file_name)
            if description:
                queryset = queryset.filter(description__icontains=description)
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
            if end_date:
                queryset = queryset.filter(created_at__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AttachmentSearchForm(self.request.GET)
        return context

class AttachmentCreateView(LoginRequiredMixin, CanManageSalonMixin, CreateView):
    model = Attachment
    form_class = AttachmentForm
    template_name = 'commonapp/partials/attachment_form.html'
    success_url = reverse_lazy('commonapp:attachment_list')

class AttachmentUpdateView(LoginRequiredMixin, CanManageSalonMixin, UpdateView):
    model = Attachment
    form_class = AttachmentForm
    template_name = 'commonapp/partials/attachment_form.html'
    success_url = reverse_lazy('commonapp:attachment_list')

class AttachmentDeleteView(LoginRequiredMixin, CanManageSalonMixin, DeleteView):
    model = Attachment
    success_url = reverse_lazy('commonapp:attachment_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse(status=204)