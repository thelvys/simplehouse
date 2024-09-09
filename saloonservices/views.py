from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Hairstyle, Shave, HairstyleTariffHistory
from .forms import (
    HairstyleForm, ShaveForm, HairstyleSearchForm, ShaveSearchForm,
    HairstyleTariffHistoryForm, HairstyleTariffHistorySearchForm
)

class HtmxResponseMixin:
    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            return HttpResponse(self.get_htmx_response())
        return super().form_valid(form)

    def get_htmx_response(self):
        return ""

class HairstyleListView(LoginRequiredMixin, ListView):
    model = Hairstyle
    template_name = 'saloonservices/hairstyle_list.html'
    context_object_name = 'hairstyles'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = HairstyleSearchForm(self.request.GET)
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
        context['search_form'] = HairstyleSearchForm(self.request.GET)
        return context

class HairstyleCreateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, CreateView):
    model = Hairstyle
    form_class = HairstyleForm
    template_name = 'saloonservices/hairstyle_form.html'
    success_url = reverse_lazy('saloonservices:hairstyle_list')
    permission_required = 'saloonservices.add_hairstyle'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Hairstyle created successfully.</div>")

class HairstyleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, UpdateView):
    model = Hairstyle
    form_class = HairstyleForm
    template_name = 'saloonservices/hairstyle_form.html'
    success_url = reverse_lazy('saloonservices:hairstyle_list')
    permission_required = 'saloonservices.change_hairstyle'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Hairstyle updated successfully.</div>")

class HairstyleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Hairstyle
    success_url = reverse_lazy('saloonservices:hairstyle_list')
    permission_required = 'saloonservices.delete_hairstyle'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse(_("<div class='alert alert-success' role='alert'>Hairstyle deleted successfully.</div>"))
        return super().delete(request, *args, **kwargs)

class ShaveListView(LoginRequiredMixin, ListView):
    model = Shave
    template_name = 'saloonservices/shave_list.html'
    context_object_name = 'shaves'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = ShaveSearchForm(self.request.GET)
        if form.is_valid():
            barber = form.cleaned_data.get('barber')
            hairstyle = form.cleaned_data.get('hairstyle')
            client = form.cleaned_data.get('client')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            salon = form.cleaned_data.get('salon')
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
            if salon:
                queryset = queryset.filter(salon=salon)
            if status:
                queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ShaveSearchForm(self.request.GET)
        return context

class ShaveCreateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, CreateView):
    model = Shave
    form_class = ShaveForm
    template_name = 'saloonservices/shave_form.html'
    success_url = reverse_lazy('saloonservices:shave_list')
    permission_required = 'saloonservices.add_shave'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Shave service created successfully.</div>")

class ShaveUpdateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, UpdateView):
    model = Shave
    form_class = ShaveForm
    template_name = 'saloonservices/shave_form.html'
    success_url = reverse_lazy('saloonservices:shave_list')
    permission_required = 'saloonservices.change_shave'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Shave service updated successfully.</div>")

class ShaveDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Shave
    success_url = reverse_lazy('saloonservices:shave_list')
    permission_required = 'saloonservices.delete_shave'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse(_("<div class='alert alert-success' role='alert'>Shave service deleted successfully.</div>"))
        return super().delete(request, *args, **kwargs)

class HairstyleTariffHistoryListView(LoginRequiredMixin, ListView):
    model = HairstyleTariffHistory
    template_name = 'saloonservices/hairstyletariffhistory_list.html'
    context_object_name = 'tariff_histories'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = HairstyleTariffHistorySearchForm(self.request.GET)
        if form.is_valid():
            hairstyle = form.cleaned_data.get('hairstyle')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            if hairstyle:
                queryset = queryset.filter(hairstyle=hairstyle)
            if start_date:
                queryset = queryset.filter(effective_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(effective_date__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = HairstyleTariffHistorySearchForm(self.request.GET)
        return context

class HairstyleTariffHistoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, CreateView):
    model = HairstyleTariffHistory
    form_class = HairstyleTariffHistoryForm
    template_name = 'saloonservices/hairstyletariffhistory_form.html'
    success_url = reverse_lazy('saloonservices:hairstyletariffhistory_list')
    permission_required = 'saloonservices.add_hairstyletariffhistory'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Hairstyle tariff history created successfully.</div>")

class HairstyleTariffHistoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, UpdateView):
    model = HairstyleTariffHistory
    form_class = HairstyleTariffHistoryForm
    template_name = 'saloonservices/hairstyletariffhistory_form.html'
    success_url = reverse_lazy('saloonservices:hairstyletariffhistory_list')
    permission_required = 'saloonservices.change_hairstyletariffhistory'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Hairstyle tariff history updated successfully.</div>")

class HairstyleTariffHistoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = HairstyleTariffHistory
    success_url = reverse_lazy('saloonservices:hairstyletariffhistory_list')
    permission_required = 'saloonservices.delete_hairstyletariffhistory'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse(_("<div class='alert alert-success' role='alert'>Hairstyle tariff history deleted successfully.</div>"))
        return super().delete(request, *args, **kwargs)