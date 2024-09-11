from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Item, ItemUsed, ItemPurchase
from .forms import (
    ItemForm, ItemUsedForm, ItemPurchaseForm,
    ItemSearchForm, ItemUsedSearchForm, ItemPurchaseSearchForm
)
from saloon.models import Salon
from config.permissions import is_salon_owner, is_salon_manager, is_assigned_barber

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
            raise PermissionDenied(_("You don't have permission to access this salon's inventory."))
        return super().dispatch(request, *args, **kwargs)

class ItemListView(LoginRequiredMixin, SalonPermissionMixin, ListView):
    model = Item
    template_name = 'salooninventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_queryset(self):
        queryset = Item.objects.filter(salon=self.salon)
        form = ItemSearchForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            hairstyle = form.cleaned_data.get('hairstyle')
            if name:
                queryset = queryset.filter(name__icontains=name)
            if hairstyle:
                queryset = queryset.filter(item_purpose=hairstyle)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ItemSearchForm(self.request.GET, user=self.request.user)
        context['salon'] = self.salon
        return context

class ItemCreateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'salooninventory/item_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.salon = self.salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('salooninventory:item_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Item created successfully.')}</div>"

class ItemUpdateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'salooninventory/item_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('salooninventory:item_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Item updated successfully.')}</div>"

class ItemDeleteView(LoginRequiredMixin, SalonPermissionMixin, DeleteView):
    model = Item
    template_name = 'salooninventory/item_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('salooninventory:item_list', kwargs={'salon_id': self.salon.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponse(f"<div class='alert alert-success'>{_('Item deleted successfully.')}</div>")
        return super().delete(request, *args, **kwargs)

class ItemUsedListView(LoginRequiredMixin, SalonPermissionMixin, ListView):
    model = ItemUsed
    template_name = 'salooninventory/itemused_list.html'
    context_object_name = 'items_used'
    paginate_by = 10

    def get_queryset(self):
        queryset = ItemUsed.objects.filter(salon=self.salon)
        form = ItemUsedSearchForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            item = form.cleaned_data.get('item')
            barber = form.cleaned_data.get('barber')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            if item:
                queryset = queryset.filter(item=item)
            if barber:
                queryset = queryset.filter(barber=barber)
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
            if end_date:
                queryset = queryset.filter(created_at__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ItemUsedSearchForm(self.request.GET, user=self.request.user)
        context['salon'] = self.salon
        return context

class ItemUsedCreateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, CreateView):
    model = ItemUsed
    form_class = ItemUsedForm
    template_name = 'salooninventory/itemused_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.salon = self.salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('salooninventory:itemused_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Item usage recorded successfully.')}</div>"

class ItemPurchaseListView(LoginRequiredMixin, SalonPermissionMixin, ListView):
    model = ItemPurchase
    template_name = 'salooninventory/itempurchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 10

    def get_queryset(self):
        queryset = ItemPurchase.objects.filter(salon=self.salon)
        form = ItemPurchaseSearchForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            item = form.cleaned_data.get('item')
            supplier = form.cleaned_data.get('supplier')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            if item:
                queryset = queryset.filter(item=item)
            if supplier:
                queryset = queryset.filter(supplier__icontains=supplier)
            if start_date:
                queryset = queryset.filter(purchase_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(purchase_date__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ItemPurchaseSearchForm(self.request.GET, user=self.request.user)
        context['salon'] = self.salon
        return context

class ItemPurchaseCreateView(LoginRequiredMixin, SalonPermissionMixin, HtmxResponseMixin, CreateView):
    model = ItemPurchase
    form_class = ItemPurchaseForm
    template_name = 'salooninventory/itempurchase_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.salon = self.salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('salooninventory:itempurchase_list', kwargs={'salon_id': self.salon.id})

    def get_htmx_response(self):
        return f"<div class='alert alert-success'>{_('Item purchase recorded successfully.')}</div>"

def validate_field(request):
    field_name = request.POST.get('field_name')
    field_value = request.POST.get('field_value')
    form_class = request.POST.get('form_class')

    form_classes = {
        'ItemForm': ItemForm,
        'ItemUsedForm': ItemUsedForm,
        'ItemPurchaseForm': ItemPurchaseForm,
    }

    FormClass = form_classes.get(form_class)
    if not FormClass:
        return JsonResponse({'error': _("Invalid form class")}, status=400)

    form = FormClass({field_name: field_value}, user=request.user)
    form.is_valid()
    
    if field_name in form.errors:
        return JsonResponse({'error': form.errors[field_name][0]}, status=400)
    return JsonResponse({'success': _("Field is valid")})