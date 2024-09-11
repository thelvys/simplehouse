from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Hairstyle, Shave, HairstyleTariffHistory
from .forms import (
    HairstyleForm, ShaveForm, HairstyleSearchForm, ShaveSearchForm,
    HairstyleTariffHistoryForm
)
from saloon.models import Salon
from config.permissions import is_salon_owner, is_assigned_barber

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
        if not (is_salon_owner(request.user, self.salon) or is_assigned_barber(request.user, self.salon)):
            raise PermissionDenied(_("You don't have permission to access this salon."))
        return super().dispatch(request, *args, **kwargs)

class HairstyleListView(LoginRequiredMixin, SalonPermissionMixin, ListView):
    model = Hairstyle
    template_name = 'saloonservices/hairstyle_list.html'
    context_object_name = 'hairstyles'
    paginate_by = 10

    def get_queryset(self):
        queryset = Hairstyle.objects.filter(salon=self.salon)
        form = HairstyleSearchForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            if name:
                queryset = queryset.filter(name__icontains=name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = HairstyleSearchForm(self.request.GET, user=self.request.user)
        context['salon'] = self.salon
        return context

class HairstyleCreateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, CreateView):
    model = Hairstyle
    form_class = HairstyleForm
    template_name = 'saloonservices/hairstyle_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.salon = self.salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloonservices:hairstyle_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Hairstyle created successfully.')}</div>"

class HairstyleUpdateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, UpdateView):
    model = Hairstyle
    form_class = HairstyleForm
    template_name = 'saloonservices/hairstyle_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('saloonservices:hairstyle_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Hairstyle updated successfully.')}</div>"

class HairstyleDeleteView(LoginRequiredMixin, SalonPermissionMixin, DeleteView):
    model = Hairstyle
    template_name = 'saloonservices/hairstyle_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloonservices:hairstyle_list', kwargs={'salon_id': self.salon.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponse(f"<div class='alert alert-success'>{_('Hairstyle deleted successfully.')}</div>")
        return super().delete(request, *args, **kwargs)

class ShaveListView(LoginRequiredMixin, SalonPermissionMixin, ListView):
    model = Shave
    template_name = 'saloonservices/shave_list.html'
    context_object_name = 'shaves'
    paginate_by = 10

    def get_queryset(self):
        queryset = Shave.objects.filter(salon=self.salon)
        form = ShaveSearchForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            barber = form.cleaned_data.get('barber')
            hairstyle = form.cleaned_data.get('hairstyle')
            client = form.cleaned_data.get('client')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            status = form.cleaned_data.get('status')
            if barber:
                queryset = queryset.filter(barber=barber)
            if hairstyle:
                queryset = queryset.filter(hairstyle=hairstyle)
            if client:
                queryset = queryset.filter(client=client)
            if start_date:
                queryset = queryset.filter(date_shave__gte=start_date)
            if end_date:
                queryset = queryset.filter(date_shave__lte=end_date)
            if status:
                queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ShaveSearchForm(self.request.GET, user=self.request.user)
        context['salon'] = self.salon
        return context

class ShaveCreateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, CreateView):
    model = Shave
    form_class = ShaveForm
    template_name = 'saloonservices/shave_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.salon = self.salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloonservices:shave_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Shave created successfully.')}</div>"

class ShaveUpdateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, UpdateView):
    model = Shave
    form_class = ShaveForm
    template_name = 'saloonservices/shave_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('saloonservices:shave_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Shave updated successfully.')}</div>"

class ShaveDeleteView(LoginRequiredMixin, SalonPermissionMixin, DeleteView):
    model = Shave
    template_name = 'saloonservices/shave_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloonservices:shave_list', kwargs={'salon_id': self.salon.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponse(f"<div class='alert alert-success'>{_('Shave deleted successfully.')}</div>")
        return super().delete(request, *args, **kwargs)

class HairstyleTariffHistoryListView(LoginRequiredMixin, SalonPermissionMixin, ListView):
    model = HairstyleTariffHistory
    template_name = 'saloonservices/hairstyletariffhistory_list.html'
    context_object_name = 'tariff_histories'
    paginate_by = 10

    def get_queryset(self):
        return HairstyleTariffHistory.objects.filter(hairstyle__salon=self.salon)

class HairstyleTariffHistoryCreateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, CreateView):
    model = HairstyleTariffHistory
    form_class = HairstyleTariffHistoryForm
    template_name = 'saloonservices/hairstyletariffhistory_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('saloonservices:hairstyletariffhistory_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Hairstyle tariff history created successfully.')}</div>"

def validate_field(request):
    field_name = request.POST.get('field_name')
    field_value = request.POST.get('field_value')
    form_class = request.POST.get('form_class')

    form_classes = {
        'HairstyleForm': HairstyleForm,
        'ShaveForm': ShaveForm,
        'HairstyleTariffHistoryForm': HairstyleTariffHistoryForm,
    }

    FormClass = form_classes.get(form_class)
    if not FormClass:
        return JsonResponse({'error': _("Invalid form class")}, status=400)

    form = FormClass({field_name: field_value}, user=request.user)
    form.is_valid()
    
    if field_name in form.errors:
        return JsonResponse({'error': form.errors[field_name][0]}, status=400)
    return JsonResponse({'success': _("Field is valid")})