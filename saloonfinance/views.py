from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import CashRegister, Payment, Transalon
from .forms import (
    CashRegisterForm, PaymentForm, TransalonForm,
    CashRegisterSearchForm, PaymentSearchForm, TransalonSearchForm
)

class HtmxResponseMixin:
    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            return HttpResponse(self.get_htmx_response())
        return super().form_valid(form)

    def get_htmx_response(self):
        return ""

class CashRegisterListView(ListView):
    model = CashRegister
    template_name = 'saloonfinance/cashregister_list.html'
    context_object_name = 'cashregisters'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = CashRegisterSearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            salon = form.cleaned_data.get('salon')
            if name:
                queryset = queryset.filter(name__icontains=name)
            if salon:
                queryset = queryset.filter(salon=salon)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CashRegisterSearchForm(self.request.GET)
        return context

class CashRegisterCreateView(HtmxResponseMixin, CreateView):
    model = CashRegister
    form_class = CashRegisterForm
    template_name = 'saloonfinance/cashregister_form.html'
    success_url = reverse_lazy('cashregister_list')

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Cash register created successfully.</div>")

class CashRegisterUpdateView(HtmxResponseMixin, UpdateView):
    model = CashRegister
    form_class = CashRegisterForm
    template_name = 'saloonfinance/cashregister_form.html'
    success_url = reverse_lazy('cashregister_list')

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Cash register updated successfully.</div>")

class CashRegisterDeleteView(DeleteView):
    model = CashRegister
    success_url = reverse_lazy('cashregister_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse(_("<div class='alert alert-success' role='alert'>Cash register deleted successfully.</div>"))
        return super().delete(request, *args, **kwargs)

class PaymentListView(ListView):
    model = Payment
    template_name = 'saloonfinance/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = PaymentSearchForm(self.request.GET)
        if form.is_valid():
            barber = form.cleaned_data.get('barber')
            payment_type = form.cleaned_data.get('payment_type')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            salon = form.cleaned_data.get('salon')
            if barber:
                queryset = queryset.filter(barber=barber)
            if payment_type:
                queryset = queryset.filter(payment_type=payment_type)
            if start_date:
                queryset = queryset.filter(date_payment__gte=start_date)
            if end_date:
                queryset = queryset.filter(date_payment__lte=end_date)
            if salon:
                queryset = queryset.filter(salon=salon)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PaymentSearchForm(self.request.GET)
        return context

class PaymentCreateView(HtmxResponseMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'saloonfinance/payment_form.html'
    success_url = reverse_lazy('payment_list')

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Payment created successfully.</div>")

class PaymentUpdateView(HtmxResponseMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'saloonfinance/payment_form.html'
    success_url = reverse_lazy('payment_list')

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Payment updated successfully.</div>")

class PaymentDeleteView(DeleteView):
    model = Payment
    success_url = reverse_lazy('payment_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse(_("<div class='alert alert-success' role='alert'>Payment deleted successfully.</div>"))
        return super().delete(request, *args, **kwargs)

class TransalonListView(ListView):
    model = Transalon
    template_name = 'saloonfinance/transalon_list.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = TransalonSearchForm(self.request.GET)
        if form.is_valid():
            trans_name = form.cleaned_data.get('trans_name')
            trans_type = form.cleaned_data.get('trans_type')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            salon = form.cleaned_data.get('salon')
            if trans_name:
                queryset = queryset.filter(trans_name__icontains=trans_name)
            if trans_type:
                queryset = queryset.filter(trans_type=trans_type)
            if start_date:
                queryset = queryset.filter(date_trans__gte=start_date)
            if end_date:
                queryset = queryset.filter(date_trans__lte=end_date)
            if salon:
                queryset = queryset.filter(salon=salon)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = TransalonSearchForm(self.request.GET)
        return context

class TransalonCreateView(HtmxResponseMixin, CreateView):
    model = Transalon
    form_class = TransalonForm
    template_name = 'saloonfinance/transalon_form.html'
    success_url = reverse_lazy('transalon_list')

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Transaction created successfully.</div>")

class TransalonUpdateView(HtmxResponseMixin, UpdateView):
    model = Transalon
    form_class = TransalonForm
    template_name = 'saloonfinance/transalon_form.html'
    success_url = reverse_lazy('transalon_list')

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Transaction updated successfully.</div>")

class TransalonDeleteView(DeleteView):
    model = Transalon
    success_url = reverse_lazy('transalon_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse(_("<div class='alert alert-success' role='alert'>Transaction deleted successfully.</div>"))
        return super().delete(request, *args, **kwargs)
