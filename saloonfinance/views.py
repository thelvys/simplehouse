from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import CashRegister, Payment, Transalon
from .forms import (
    CashRegisterForm, PaymentForm, TransalonForm,
    CashRegisterSearchForm, PaymentSearchForm, TransalonSearchForm
)
from saloon.models import Salon
from config.permissions import is_salon_owner, is_salon_manager

class HtmxResponseMixin:
    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            return HttpResponse(self.get_htmx_response())
        return super().form_valid(form)

    def get_htmx_response(self):
        return ""

class SalonPermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        self.salon = get_object_or_404(Salon, pk=self.kwargs['salon_id'])
        if not (is_salon_owner(request.user, self.salon) or is_salon_manager(request.user, self.salon)):
            raise PermissionDenied(_("You don't have permission to access this salon's finances."))
        return super().dispatch(request, *args, **kwargs)

class CashRegisterListView(LoginRequiredMixin, SalonPermissionMixin, ListView):
    model = CashRegister
    template_name = 'saloonfinance/cashregister_list.html'
    context_object_name = 'cashregisters'
    paginate_by = 10

    def get_queryset(self):
        queryset = CashRegister.objects.filter(salon=self.salon)
        form = CashRegisterSearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            if name:
                queryset = queryset.filter(name__icontains=name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CashRegisterSearchForm(self.request.GET)
        context['salon'] = self.salon
        return context

class CashRegisterCreateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, CreateView):
    model = CashRegister
    form_class = CashRegisterForm
    template_name = 'saloonfinance/cashregister_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['salon'] = self.salon
        return kwargs

    def get_success_url(self):
        return reverse_lazy('saloonfinance:cashregister_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Cash register created successfully.')}</div>"

class CashRegisterUpdateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, UpdateView):
    model = CashRegister
    form_class = CashRegisterForm
    template_name = 'saloonfinance/cashregister_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['salon'] = self.salon
        return kwargs

    def get_success_url(self):
        return reverse_lazy('saloonfinance:cashregister_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Cash register updated successfully.')}</div>"

class CashRegisterDeleteView(LoginRequiredMixin, SalonPermissionMixin, DeleteView):
    model = CashRegister
    template_name = 'saloonfinance/cashregister_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloonfinance:cashregister_list', kwargs={'salon_id': self.salon.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponse(f"<div class='alert alert-success'>{_('Cash register deleted successfully.')}</div>")
        return super().delete(request, *args, **kwargs)

class PaymentListView(LoginRequiredMixin, SalonPermissionMixin, ListView):
    model = Payment
    template_name = 'saloonfinance/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        queryset = Payment.objects.filter(salon=self.salon)
        form = PaymentSearchForm(self.request.GET, salon=self.salon)
        if form.is_valid():
            barber = form.cleaned_data.get('barber')
            payment_type = form.cleaned_data.get('payment_type')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            if barber:
                queryset = queryset.filter(barber=barber)
            if payment_type:
                queryset = queryset.filter(payment_type=payment_type)
            if start_date:
                queryset = queryset.filter(date_payment__gte=start_date)
            if end_date:
                queryset = queryset.filter(date_payment__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PaymentSearchForm(self.request.GET, salon=self.salon)
        context['salon'] = self.salon
        return context

class PaymentCreateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'saloonfinance/payment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['salon'] = self.salon
        return kwargs

    def get_success_url(self):
        return reverse_lazy('saloonfinance:payment_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Payment created successfully.')}</div>"

class PaymentUpdateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'saloonfinance/payment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['salon'] = self.salon
        return kwargs

    def get_success_url(self):
        return reverse_lazy('saloonfinance:payment_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Payment updated successfully.')}</div>"

class PaymentDeleteView(LoginRequiredMixin, SalonPermissionMixin, DeleteView):
    model = Payment
    template_name = 'saloonfinance/payment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloonfinance:payment_list', kwargs={'salon_id': self.salon.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponse(f"<div class='alert alert-success'>{_('Payment deleted successfully.')}</div>")
        return super().delete(request, *args, **kwargs)

class TransalonListView(LoginRequiredMixin, SalonPermissionMixin, ListView):
    model = Transalon
    template_name = 'saloonfinance/transalon_list.html'
    context_object_name = 'transalons'
    paginate_by = 10

    def get_queryset(self):
        queryset = Transalon.objects.filter(salon=self.salon)
        form = TransalonSearchForm(self.request.GET)
        if form.is_valid():
            trans_name = form.cleaned_data.get('trans_name')
            trans_type = form.cleaned_data.get('trans_type')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            if trans_name:
                queryset = queryset.filter(trans_name__icontains=trans_name)
            if trans_type:
                queryset = queryset.filter(trans_type=trans_type)
            if start_date:
                queryset = queryset.filter(date_trans__gte=start_date)
            if end_date:
                queryset = queryset.filter(date_trans__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = TransalonSearchForm(self.request.GET)
        context['salon'] = self.salon
        return context

class TransalonCreateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, CreateView):
    model = Transalon
    form_class = TransalonForm
    template_name = 'saloonfinance/transalon_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['salon'] = self.salon
        return kwargs

    def get_success_url(self):
        return reverse_lazy('saloonfinance:transalon_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Transaction created successfully.')}</div>"

class TransalonUpdateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, UpdateView):
    model = Transalon
    form_class = TransalonForm
    template_name = 'saloonfinance/transalon_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['salon'] = self.salon
        return kwargs

    def get_success_url(self):
        return reverse_lazy('saloonfinance:transalon_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Transaction updated successfully.')}</div>"

class TransalonDeleteView(LoginRequiredMixin, SalonPermissionMixin, DeleteView):
    model = Transalon
    template_name = 'saloonfinance/transalon_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloonfinance:transalon_list', kwargs={'salon_id': self.salon.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponse(f"<div class='alert alert-success'>{_('Transaction deleted successfully.')}</div>")
        return super().delete(request, *args, **kwargs)

def validate_field(request):
    field_name = request.POST.get('field_name')
    field_value = request.POST.get('field_value')
    form_class = request.POST.get('form_class')

    form_classes = {
        'CashRegisterForm': CashRegisterForm,
        'PaymentForm': PaymentForm,
        'TransalonForm': TransalonForm,
    }

    FormClass = form_classes.get(form_class)
    if not FormClass:
        return JsonResponse({'error': _("Invalid form class")}, status=400)

    form = FormClass({field_name: field_value}, user=request.user, salon=request.user.salon)
    form.is_valid()
    
    if field_name in form.errors:
        return JsonResponse({'error': form.errors[field_name][0]}, status=400)
    return JsonResponse({'success': _("Field is valid")})
