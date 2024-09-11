from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Currency, Attachment
from .forms import CurrencyForm, AttachmentForm, CurrencySearchForm, AttachmentSearchForm

class HomeView(TemplateView):
    template_name = 'commonapp/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Welcome to Saloon Management System")
        # You can add more context data here as needed
        return context

class HtmxResponseMixin:
    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            return HttpResponse(self.get_htmx_response())
        return super().form_valid(form)

    def get_htmx_response(self):
        return ""

class CurrencyListView(LoginRequiredMixin, ListView):
    model = Currency
    template_name = 'commonapp/currency_list.html'
    context_object_name = 'currencies'
    paginate_by = 10

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

class CurrencyCreateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, CreateView):
    model = Currency
    form_class = CurrencyForm
    template_name = 'commonapp/currency_form.html'
    success_url = reverse_lazy('commonapp:currency_list')
    permission_required = 'commonapp.add_currency'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Currency created successfully.</div>")

class CurrencyUpdateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, UpdateView):
    model = Currency
    form_class = CurrencyForm
    template_name = 'commonapp/currency_form.html'
    success_url = reverse_lazy('commonapp:currency_list')
    permission_required = 'commonapp.change_currency'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Currency updated successfully.</div>")

class CurrencyDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Currency
    success_url = reverse_lazy('commonapp:currency_list')
    permission_required = 'commonapp.delete_currency'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse(_("<div class='alert alert-success' role='alert'>Currency deleted successfully.</div>"))
        return super().delete(request, *args, **kwargs)

class AttachmentListView(LoginRequiredMixin, ListView):
    model = Attachment
    template_name = 'commonapp/attachment_list.html'
    context_object_name = 'attachments'
    paginate_by = 10

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

class AttachmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, CreateView):
    model = Attachment
    form_class = AttachmentForm
    template_name = 'commonapp/attachment_form.html'
    success_url = reverse_lazy('commonapp:attachment_list')
    permission_required = 'commonapp.add_attachment'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Attachment created successfully.</div>")

class AttachmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, UpdateView):
    model = Attachment
    form_class = AttachmentForm
    template_name = 'commonapp/attachment_form.html'
    success_url = reverse_lazy('commonapp:attachment_list')
    permission_required = 'commonapp.change_attachment'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Attachment updated successfully.</div>")

class AttachmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Attachment
    success_url = reverse_lazy('commonapp:attachment_list')
    permission_required = 'commonapp.delete_attachment'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse(_("<div class='alert alert-success' role='alert'>Attachment deleted successfully.</div>"))
        return super().delete(request, *args, **kwargs)

